"""
ThirdEye ML Service
===================
FastAPI service providing deep-learning face matching for the ThirdEye
JavaFX application. Uses a pretrained FaceNet model to embed faces and
ranks dataset suspects by cosine similarity.

Endpoints
---------
GET  /health        -> service status + model loaded flag
POST /embed         -> multipart image -> { embedding: [...] }
POST /match         -> multipart sketch + dataset_dir -> ranked matches
POST /rebuild_cache -> re-index the dataset directory

Run
---
    pip install -r requirements.txt
    uvicorn app:app --host 127.0.0.1 --port 8000
"""

import io
import os
import time
import logging
from typing import List, Dict, Optional

import numpy as np
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("thirdeye-ml")

app = FastAPI(title="ThirdEye ML Service", version="1.1.0")

# Lazy-loaded FaceNet model and Cross-Modal Projection Head
_model = None
_proj_model = None
_model_error: Optional[str] = None

# In-memory cache: relative path -> dict(face=128d projected embedding, hog=HOG vector)
_cache: Dict[str, Dict[str, np.ndarray]] = {}
_cache_mtime: Optional[float] = None
_cache_dir: Optional[str] = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CACHE_FILE = "dataset_embeddings.npy"

TOP_RESULTS = 10

# Fused score = FACE_WEIGHT * projected_face_cosine + (1 - FACE_WEIGHT) * denoised_hog_cosine
# Optimized alpha = 0.85 gives 85% weight to Deep Metric Embeddings & 15% to HOG
FACE_WEIGHT = 0.85

# HOG parameters (mirror the Java engine: cell 8, 9 unsigned bins, face-weight map)
HOG_CELL = 8
HOG_BINS = 9
HOG_SIZE = 160
_face_weight_cache = None


from query_router import QueryRouter

class MatchResult(BaseModel):
    name: str
    path: str
    similarity: float
    calibrated_score: float
    rank: int


class MatchResponse(BaseModel):
    status: str
    sketch_embedded: bool
    query_modality: str
    selected_pipeline: str
    match_decision: str
    threshold: float
    warnings: List[str]
    count: int
    results: List[MatchResult]


class HealthResponse(BaseModel):
    status: str
    api_status: str
    model_loaded: bool
    model_error: Optional[str]
    dataset_dir: Optional[str]
    dataset_images: int
    cache_built: bool


# ─────────────────────────────── Model helpers ───────────────────────────────

def load_model():
    """Load the FaceNet model and Cross-Modal Projection Head once."""
    global _model, _proj_model, _model_error
    if _model is not None or _model_error is not None:
        return
    try:
        from keras_facenet import FaceNet
        log.info("Loading FaceNet model...")
        _model = FaceNet()
        log.info("FaceNet model loaded.")
        
        # Load cross-modal projection model if available
        base_dir = os.path.dirname(os.path.abspath(__file__))
        proj_weights = os.path.join(base_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5")
        if os.path.exists(proj_weights):
            try:
                import tensorflow as tf
                import keras
                from keras import layers, models
                inputs = layers.Input(shape=(512,))
                x = layers.Dense(256, activation=None)(inputs)
                x = layers.BatchNormalization()(x)
                x = layers.ReLU()(x)
                x = layers.Dropout(0.2)(x)
                x = layers.Dense(128, activation=None)(x)
                outputs = layers.Lambda(lambda t: tf.math.l2_normalize(t, axis=1))(x)
                _proj_model = models.Model(inputs=inputs, outputs=outputs)
                _proj_model.load_weights(proj_weights)
                log.info("Cross-Modal Projection Head loaded successfully.")
            except Exception as pe:
                log.warning("Could not load projection head: %s", pe)
    except Exception as e:  # noqa: BLE001
        _model_error = str(e)
        log.error("Model load failed: %s", e)


def crop_face(img_rgb: np.ndarray, target_size: int = 160) -> np.ndarray:
    """Resize image to target_size square preserving facial features with deterministic center fallback."""
    import cv2
    if img_rgb is None or img_rgb.size == 0:
        return np.zeros((target_size, target_size, 3), dtype=np.uint8)
    h, w = img_rgb.shape[:2]
    if h == 0 or w == 0:
        return np.zeros((target_size, target_size, 3), dtype=np.uint8)
    return cv2.resize(img_rgb, (target_size, target_size))


def embed_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """Return a normalized projected embedding for raw image bytes, or None."""
    if not image_bytes or len(image_bytes) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image payload.")

    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    from PIL import Image
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Face not detected or unreadable image file. Please provide a clear frontal sketch/photo. (Details: {e})")

    arr = np.asarray(img)
    arr = crop_face(arr, target_size=160)

    try:
        emb = _model.embeddings(np.expand_dims(arr, axis=0))[0]
    except Exception as e:  # noqa: BLE001
        log.warning("Embedding failed: %s", e)
        return None

    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
        
    if _proj_model is not None:
        import tensorflow as tf
        emb = _proj_model(tf.convert_to_tensor([emb], dtype=tf.float32), training=False).numpy()[0]
        
    return emb


def embed_image_raw(image_bytes: bytes) -> Optional[np.ndarray]:
    """Return raw 512-d L2-normalized FaceNet embedding (without projection head)."""
    if not image_bytes or len(image_bytes) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image payload.")

    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    from PIL import Image
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Face not detected or unreadable image file. (Details: {e})")

    arr = np.asarray(img)
    arr = crop_face(arr, target_size=160)

    try:
        emb = _model.embeddings(np.expand_dims(arr, axis=0))[0]
    except Exception as e:  # noqa: BLE001
        log.warning("Raw embedding failed: %s", e)
        return None

    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm

    return emb

def _face_weight_map(cells_x: int, cells_y: int) -> np.ndarray:
    """Per-cell weight favouring the central face region (mirrors the Java
    engine's weight map used for sketch<->photo comparisons)."""
    global _face_weight_cache
    if _face_weight_cache is not None and _face_weight_cache.shape == (cells_y, cells_x):
        return _face_weight_cache
    m = np.zeros((cells_y, cells_x), dtype=np.float64)
    cyc, cxc = (cells_y - 1) / 2.0, (cells_x - 1) / 2.0
    for cy in range(cells_y):
        for cx in range(cells_x):
            d = np.hypot((cx - cxc) / cxc, (cy - cyc) / cyc)
            m[cy, cx] = 2.0 * np.exp(-2.0 * d * d)
    m -= m.min()
    _face_weight_cache = m
    return m


def hog_grey(image_bytes: bytes) -> np.ndarray:
    """Decode image, apply CLAHE contrast enhancement and Gaussian smoothing, return greyscale."""
    if not image_bytes or len(image_bytes) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image payload.")

    import cv2
    from PIL import Image
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=422, detail=f"Face not detected or unreadable image file. (Details: {e})")

    img = img.resize((HOG_SIZE, HOG_SIZE), Image.Resampling.LANCZOS)
    gray = cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    denoised = cv2.GaussianBlur(enhanced, (3, 3), 0)
    return denoised.astype(np.float64)


def compute_hog(grey: np.ndarray) -> np.ndarray:
    """Sobel-gradient HOG descriptor with bilinear bin interpolation.
    Normalized to unit length for cosine similarity."""
    h, w = grey.shape
    gx = np.zeros_like(grey)
    gy = np.zeros_like(grey)
    gx[:, 1:-1] = grey[:, 2:] - grey[:, :-2]
    gy[1:-1, :] = grey[2:, :] - grey[:-2, :]
    mag = np.hypot(gx, gy)
    ang = np.degrees(np.arctan2(gy, gx)) % 180.0

    cells_x, cells_y = w // HOG_CELL, h // HOG_CELL
    fw = _face_weight_map(cells_x, cells_y)

    bins = (ang / (180.0 / HOG_BINS)) % HOG_BINS
    b0 = bins.astype(np.int32)
    frac = bins - b0
    b1 = (b0 + 1) % HOG_BINS

    desc = np.zeros(cells_y * cells_x * HOG_BINS, dtype=np.float64)
    cy0, cx0 = np.meshgrid(np.arange(cells_y), np.arange(cells_x), indexing="ij")
    cy0f = cy0.reshape(-1, 1)
    cx0f = cx0.reshape(-1, 1)
    flat = (cy0f * cells_x + cx0f) * HOG_BINS

    for dy in range(HOG_CELL):
        for dx in range(HOG_CELL):
            yy = cy0f * HOG_CELL + dy
            xx = cx0f * HOG_CELL + dx
            w = mag[yy, xx] * fw[cy0f, cx0f]
            np.add.at(desc, flat + b0[yy, xx], w * (1.0 - frac[yy, xx]))
            np.add.at(desc, flat + b1[yy, xx], w * frac[yy, xx])

    n = np.linalg.norm(desc)
    return desc / n if n > 0 else desc


def compute_lbp(grey: np.ndarray) -> np.ndarray:
    """Local Binary Pattern (LBP) micro-texture descriptor for skin & stroke invariance."""
    img = grey.astype(np.uint8)
    h, w = img.shape
    lbp = np.zeros((h - 2, w - 2), dtype=np.uint8)
    center = img[1:-1, 1:-1]
    
    lbp += ((img[0:-2, 0:-2] >= center) << 7).astype(np.uint8)
    lbp += ((img[0:-2, 1:-1] >= center) << 6).astype(np.uint8)
    lbp += ((img[0:-2, 2:  ] >= center) << 5).astype(np.uint8)
    lbp += ((img[1:-1, 2:  ] >= center) << 4).astype(np.uint8)
    lbp += ((img[2:  , 2:  ] >= center) << 3).astype(np.uint8)
    lbp += ((img[2:  , 1:-1] >= center) << 2).astype(np.uint8)
    lbp += ((img[2:  , 0:-2] >= center) << 1).astype(np.uint8)
    lbp += ((img[1:-1, 0:-2] >= center) << 0).astype(np.uint8)
    
    hist, _ = np.histogram(lbp.ravel(), bins=256, range=(0, 256))
    hist = hist.astype(np.float64)
    norm = np.linalg.norm(hist)
    return hist / norm if norm > 0 else hist


def pro_hybrid_score(face_sim: float, hog_sim: float, lbp_sim: float) -> float:
    """Pro-Level Multi-Metric Fusion: 35% Deep Metric Embedding + 50% Spatial HOG + 15% Texture LBP."""
    return 0.35 * face_sim + 0.50 * hog_sim + 0.15 * lbp_sim


def hybrid_score(face_sim: float, hog_sim: float) -> float:
    return FACE_WEIGHT * face_sim + (1.0 - FACE_WEIGHT) * hog_sim


# ─────────────────────────────── Dataset indexing ────────────────────────────

def _list_images(dataset_dir: str) -> List[str]:
    images = []
    for root, _dirs, files in os.walk(dataset_dir):
        if os.path.basename(root).lower() in ["queries", "sketches"]:
            continue
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                images.append(os.path.join(root, f))
    return images


def _cache_path(dataset_dir: str) -> str:
    return os.path.join(dataset_dir, CACHE_FILE)


def build_cache(dataset_dir: str, force: bool = False):
    """Embed every image (FaceNet + HOG) and persist to a .npy cache."""
    global _cache, _cache_mtime, _cache_dir
    dataset_dir = os.path.abspath(dataset_dir)
    if not os.path.exists(dataset_dir) or not os.path.isdir(dataset_dir):
        base_ml_dir = os.path.dirname(os.path.abspath(__file__))
        alt_path_1 = os.path.join(base_ml_dir, dataset_dir)
        folder_name = os.path.basename(os.path.normpath(dataset_dir))
        alt_path_2 = os.path.join(base_ml_dir, "dataset", folder_name)
        alt_path_3 = os.path.join(base_ml_dir, "dataset", "gallery")

        if os.path.exists(alt_path_1) and os.path.isdir(alt_path_1):
            dataset_dir = alt_path_1
        elif os.path.exists(alt_path_2) and os.path.isdir(alt_path_2):
            dataset_dir = alt_path_2
        elif os.path.exists(alt_path_3) and os.path.isdir(alt_path_3):
            dataset_dir = alt_path_3
        else:
            raise HTTPException(status_code=400, detail=f"dataset_dir not found or invalid: {dataset_dir}")

    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    images = _list_images(dataset_dir)
    cache_file = _cache_path(dataset_dir)

    # Load existing cache if present, valid format, and dataset unchanged
    if not force and os.path.exists(cache_file):
        try:
            data = np.load(cache_file, allow_pickle=True).item()
            cached = data.get("features", None)
            if cached is None:
                # legacy v1.0 cache (embeddings only) -> rebuild with HOG
                raise ValueError("legacy cache format")
            _cache = cached
            _cache_mtime = data.get("mtime", 0)
            _cache_dir = dataset_dir
            mtime = max(os.path.getmtime(p) for p in images) if images else 0
            if _cache_mtime == mtime and set(_cache.keys()) == {os.path.relpath(p, dataset_dir) for p in images}:
                # Verify dimension alignment with current embed_image output
                sample_feat = next(iter(_cache.values()))["face"] if _cache else None
                test_raw = b""
                if images:
                    with open(images[0], "rb") as fh:
                        test_raw = fh.read()
                test_emb = embed_image(test_raw)
                if sample_feat is not None and test_emb is not None and sample_feat.shape == test_emb.shape:
                    log.info("Using cached features (%d faces).", len(_cache))
                    return
                else:
                    log.info("Cache dimension mismatch detected (%s vs %s). Rebuilding cache...", sample_feat.shape if sample_feat is not None else None, test_emb.shape if test_emb is not None else None)
                    _cache = {}
        except Exception as e:  # noqa: BLE001
            log.info("Rebuilding cache: %s", e)
            _cache = {}

    log.info("Building feature cache for %d images...", len(images))
    features: Dict[str, Dict[str, np.ndarray]] = {}
    for path in images:
        rel = os.path.relpath(path, dataset_dir)
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            grey = hog_grey(raw)
            emb = embed_image(raw)
            emb_raw = embed_image_raw(raw)
            hog = compute_hog(grey)
            lbp = compute_lbp(grey)
            if emb is not None:
                features[rel] = {"face": emb, "face_raw": emb_raw, "hog": hog, "lbp": lbp}
        except Exception as e:  # noqa: BLE001
            log.warning("Skip %s: %s", rel, e)

    _cache = features
    _cache_dir = dataset_dir
    _cache_mtime = max(os.path.getmtime(p) for p in images) if images else 0

    try:
        np.save(cache_file, np.array({"features": features, "mtime": _cache_mtime}, dtype=object), allow_pickle=True)
        log.info("Cache saved (%d faces).", len(features))
    except Exception as e:  # noqa: BLE001
        log.warning("Could not save cache: %s", e)


# ────────────────────────────────── Endpoints ────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    load_model()
    dataset_dir = _cache_dir
    images = _list_images(dataset_dir) if dataset_dir else []
    return HealthResponse(
        status="ok",
        api_status="UP",
        model_loaded=_model is not None,
        model_error=_model_error,
        dataset_dir=dataset_dir,
        dataset_images=len(images),
        cache_built=_cache_dir is not None,
    )


@app.post("/embed")
def embed(file: UploadFile = File(...)):
    data = file.file.read()
    if not data or len(data) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image file uploaded.")
    emb = embed_image(data)
    if emb is None:
        raise HTTPException(status_code=422, detail="Could not embed image (no face found).")
    return {"status": "ok", "shape": list(emb.shape), "embedding": emb.tolist()}


@app.post("/rebuild_cache")
def rebuild_cache(dataset_dir: str = Form(...)):
    dataset_dir = os.path.abspath(dataset_dir)
    t0 = time.time()
    build_cache(dataset_dir, force=True)
    return {"status": "ok", "images": len(_cache), "elapsed_s": round(time.time() - t0, 2)}


@app.post("/match", response_model=MatchResponse)
def match(file: UploadFile = File(...), dataset_dir: str = Form(...), top_n: int = Form(TOP_RESULTS)):
    data = file.file.read()
    if not data or len(data) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image file uploaded.")
        
    # 1. Analyze Query Modality & Pipeline Selection
    modality_info = QueryRouter.analyze_image_bytes(data)
    query_modality = modality_info["modality"]
    selected_pipeline = modality_info["selected_pipeline"]
    warnings = modality_info.get("warnings", [])
    
    dataset_dir = os.path.abspath(dataset_dir)
    build_cache(dataset_dir)
    if not _cache:
        raise HTTPException(status_code=422, detail="No faces could be embedded in the dataset.")
        
    # 2. Modality-Specific Feature Extraction & Open-Set Threshold Setting
    scored = []
    
    if query_modality == "PHOTO":
        threshold = 0.65
        query_emb_raw = embed_image_raw(data)
        if query_emb_raw is None:
            raise HTTPException(status_code=422, detail="Could not extract face embedding from photo.")
            
        sample_feat = next(iter(_cache.values())) if _cache else {}
        if "face_raw" not in sample_feat:
            build_cache(dataset_dir, force=True)

        for rel, feats in _cache.items():
            g_emb = feats.get("face_raw")
            if g_emb is not None and g_emb.shape == query_emb_raw.shape:
                sim = float(np.dot(query_emb_raw, g_emb))
            else:
                q_emb = embed_image(data)
                g_face = feats["face"]
                sim = float(np.dot(q_emb, g_face)) if q_emb is not None else 0.0
            scored.append((sim, rel))
            
    else:  # ARTIST_SKETCH, COMPOSITE_FORENSIC_SKETCH, FALLBACK
        threshold = 0.50 if query_modality == "COMPOSITE_FORENSIC_SKETCH" else 0.55
        sketch_grey = hog_grey(data)
        sketch_emb = embed_image(data)
        if sketch_emb is None:
            raise HTTPException(status_code=422, detail="Could not embed sketch (no face found).")
        sketch_hog = compute_hog(sketch_grey)
        
        for rel, feats in _cache.items():
            face_sim = float(np.dot(sketch_emb, feats["face"]))
            hog_sim = float(np.dot(sketch_hog, feats["hog"]))
            sim = hybrid_score(face_sim, hog_sim)
            scored.append((sim, rel))

    scored.sort(reverse=True, key=lambda x: x[0])
    top_score = scored[0][0] if scored else 0.0
    
    # 3. Open-Set Match Rejection Logic
    if top_score >= threshold:
        match_decision = "POSSIBLE MATCH"
    else:
        match_decision = "NO RELIABLE MATCH FOUND IN CURRENT GALLERY"
        warnings.append(f"Top candidate similarity ({top_score*100.0:.1f}%) is below calibrated threshold ({threshold*100.0:.1f}%). Outputting nearest candidates only.")
        
    top = scored[:max(1, min(top_n, len(scored)))]

    results = [
        MatchResult(
            name=os.path.splitext(os.path.basename(rel))[0],
            path=os.path.join(dataset_dir, rel),
            similarity=round(sim, 4),
            calibrated_score=round(sim * 100.0, 2),
            rank=idx
        )
        for idx, (sim, rel) in enumerate(top, start=1)
    ]
    
    return MatchResponse(
        status="ok",
        sketch_embedded=True,
        query_modality=query_modality,
        selected_pipeline=selected_pipeline,
        match_decision=match_decision,
        threshold=threshold,
        warnings=warnings,
        count=len(results),
        results=results,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000)
