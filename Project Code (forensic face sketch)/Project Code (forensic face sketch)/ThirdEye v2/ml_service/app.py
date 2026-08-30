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
import cv2
import jwt
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from demographic_filter import DemographicEstimator
from xai_explainer import XAIExplainer
from element_recommender import ElementRecommender


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("thirdeye-ml")

app = FastAPI(title="ThirdEye ML Service", version="1.2.0 (JWT Secured)")

# JWT Authentication Config
JWT_SECRET_KEY = os.environ.get("THIRDEYE_JWT_SECRET", "thirdeye_v2_forensic_secure_jwt_secret_key_2026")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_SECONDS = 86400  # 24 hours

security = HTTPBearer(auto_error=False)


class TokenRequest(BaseModel):
    client_id: str = "thirdeye_desktop_client"
    secret_key: Optional[str] = None


class TokenResponse(BaseModel):
    status: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    to_encode = data.copy()
    expire = time.time() + (expires_delta or JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": int(expire)})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid HTTP Authorization Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="JWT token has expired. Please authenticate again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid JWT token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Lazy-loaded FaceNet model and Cross-Modal Projection Head
_model = None
_proj_model = None
_model_error: Optional[str] = None

# In-memory cache: relative path -> dict(face=128d projected embedding, hog=HOG vector)
_cache: Dict[str, Dict[str, np.ndarray]] = {}
_cache_mtime: Optional[float] = None
_cache_dir: Optional[str] = None

CACHE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CACHE_FILE = "dataset_embeddings.npy"
CACHE_VERSION = "v7_multi_ethnic_indian_and_foreign_v1"

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
from faiss_index_manager import FAISSIndexManager
from generative_synth import GenerativeSynthesizer

faiss_indexer = FAISSIndexManager(dimension=128)

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
    demographic_filter_applied: Optional[bool] = False
    gender_filter: Optional[str] = "ALL"
    candidates_evaluated: Optional[int] = 0
    candidates_pruned: Optional[int] = 0


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


_face_cascade = None

def get_face_cascade():
    global _face_cascade
    if _face_cascade is None:
        import cv2
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                _face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception:
            _face_cascade = None
    return _face_cascade


def crop_face(img_rgb: np.ndarray, target_size: int = 160) -> np.ndarray:
    """
    Robust Pro-Level Face Detector & Border Trimmer for Forensic Face Sketches & Photos.
    Combines OpenCV Haar Cascade detection with non-white canvas trimming to ensure
    1:1 facial alignment across modalities.
    """
    import cv2
    if img_rgb is None or img_rgb.size == 0:
        return np.zeros((target_size, target_size, 3), dtype=np.uint8)
    h, w = img_rgb.shape[:2]
    if h == 0 or w == 0:
        return np.zeros((target_size, target_size, 3), dtype=np.uint8)

    grey = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY) if len(img_rgb.shape) == 3 else img_rgb
    
    # 1. Try Haar Cascade Face Detector for exact facial alignment
    cascade = get_face_cascade()
    if cascade is not None:
        try:
            faces = cascade.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=4, minSize=(35, 35))
            if len(faces) > 0:
                # Pick largest detected face
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                fx, fy, fw, fh = faces[0]
                margin_x = int(fw * 0.20)
                margin_y = int(fh * 0.20)
                x1 = max(0, fx - margin_x)
                y1 = max(0, fy - margin_y)
                x2 = min(w, fx + fw + margin_x)
                y2 = min(h, fy + fh + margin_y)
                face_crop = img_rgb[y1:y2, x1:x2]
                
                hc, wc = face_crop.shape[:2]
                min_dim = min(hc, wc)
                sy = (hc - min_dim) // 2
                sx = (wc - min_dim) // 2
                sq_crop = face_crop[sy:sy + min_dim, sx:sx + min_dim]
                return cv2.resize(sq_crop, (target_size, target_size), interpolation=cv2.INTER_AREA)
        except Exception:
            pass

    # 2. Fallback: Detect non-white border bounding box if image has white canvas padding
    _, thresh = cv2.threshold(grey, 245, 255, cv2.THRESH_BINARY_INV)
    coords = cv2.findNonZero(thresh)

    if coords is not None:
        x, y, bw, bh = cv2.boundingRect(coords)
        if bw > 30 and bh > 30:
            margin_x = int(bw * 0.08)
            margin_y = int(bh * 0.08)
            x1 = max(0, x - margin_x)
            y1 = max(0, y - margin_y)
            x2 = min(w, x + bw + margin_x)
            y2 = min(h, y + bh + margin_y)
            img_crop = img_rgb[y1:y2, x1:x2]
            h_c, w_c = img_crop.shape[:2]
        else:
            img_crop = img_rgb
            h_c, w_c = h, w
    else:
        img_crop = img_rgb
        h_c, w_c = h, w

    # 3. Square crop from center preserving 1:1 facial feature aspect ratio
    min_dim = min(h_c, w_c)
    start_y = (h_c - min_dim) // 2
    start_x = (w_c - min_dim) // 2
    square_crop = img_crop[start_y:start_y + min_dim, start_x:start_x + min_dim]

    return cv2.resize(square_crop, (target_size, target_size), interpolation=cv2.INTER_AREA)


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

    arr = np.asarray(img)
    cropped_face = crop_face(arr, target_size=HOG_SIZE)
    gray = cv2.cvtColor(cropped_face, cv2.COLOR_RGB2GRAY)
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
    if n > 0:
        desc = desc / n
        desc = np.sqrt(np.clip(desc, 0.0, None))  # L2-Hys hysteresis square-root normalization
        n2 = np.linalg.norm(desc)
        return desc / n2 if n2 > 0 else desc
    return desc


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
    """Pro-Level Multi-Metric Fusion: 88% Deep Metric Embedding + 8% Spatial HOG + 4% Texture LBP."""
    return 0.88 * face_sim + 0.08 * hog_sim + 0.04 * lbp_sim


def hybrid_score(face_sim: float, hog_sim: float) -> float:
    """Dynamic multi-stream hybrid score using FACE_WEIGHT."""
    return FACE_WEIGHT * face_sim + (1.0 - FACE_WEIGHT) * hog_sim


# ─────────────────────────────── Dataset indexing ────────────────────────────

def _list_images(dataset_dir: str) -> List[str]:
    images = []
    if os.path.exists(dataset_dir):
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
    base_ml_dir = os.path.dirname(os.path.abspath(__file__))
    alt_path_gallery = os.path.join(base_ml_dir, "dataset", "gallery")
    alt_path_all = os.path.join(base_ml_dir, "dataset", "gallery_all")

    if not os.path.exists(dataset_dir) or not os.path.isdir(dataset_dir):
        alt_path_1 = os.path.join(base_ml_dir, dataset_dir)
        folder_name = os.path.basename(os.path.normpath(dataset_dir))
        alt_path_2 = os.path.join(base_ml_dir, "dataset", folder_name)

        if os.path.exists(alt_path_gallery) and os.path.isdir(alt_path_gallery):
            dataset_dir = alt_path_gallery
        elif os.path.exists(alt_path_1) and os.path.isdir(alt_path_1):
            dataset_dir = alt_path_1
        elif os.path.exists(alt_path_2) and os.path.isdir(alt_path_2):
            dataset_dir = alt_path_2
        elif os.path.exists(alt_path_all) and os.path.isdir(alt_path_all):
            dataset_dir = alt_path_all
        else:
            raise HTTPException(status_code=400, detail=f"dataset_dir not found or invalid: {dataset_dir}")

    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    if not force and _cache:
        return

    images = _list_images(dataset_dir)
    cache_file = _cache_path(dataset_dir)

    # Load existing cache if present
    if not force and os.path.exists(cache_file):
        try:
            data = np.load(cache_file, allow_pickle=True).item()
            cached = data.get("features", None)
            version = data.get("version", "")
            if cached is not None and len(cached) > 0 and version == CACHE_VERSION:
                _cache = cached
                _cache_dir = dataset_dir
                faiss_indexer.build_index(_cache)
                log.info("Using cached features (%d faces, version %s, FAISS index ready).", len(_cache), version)
                return
        except Exception as e:  # noqa: BLE001
            log.info("Rebuilding cache due to load error or version mismatch: %s", e)
            _cache = {}

    log.info("Building feature cache for %d images...", len(images))
    features: Dict[str, Dict[str, np.ndarray]] = {}
    for path in images:
        rel = os.path.relpath(path, dataset_dir)
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            grey = hog_grey(raw)
            emb_raw = embed_image_raw(raw)
            if emb_raw is not None and _proj_model is not None:
                import tensorflow as tf
                emb = _proj_model(tf.convert_to_tensor([emb_raw], dtype=tf.float32), training=False).numpy()[0]
            else:
                emb = emb_raw
            hog = compute_hog(grey)
            lbp = compute_lbp(grey)
            
            try:
                g_arr = np.frombuffer(raw, np.uint8)
                g_img_bgr = cv2.imdecode(g_arr, cv2.IMREAD_COLOR)
                g_img_rgb = cv2.cvtColor(g_img_bgr, cv2.COLOR_BGR2RGB) if g_img_bgr is not None else None
                attr = DemographicEstimator.estimate_attributes(g_img_rgb, filename=path)
            except Exception as e:
                log.error("Demographic error for %s: %s", path, e)
                attr = {"gender": "UNKNOWN", "gender_conf": 0.0, "age_est": 30, "age_conf": 0.0}

            if emb is not None:
                features[rel] = {"face": emb, "face_raw": emb_raw, "hog": hog, "lbp": lbp, "attr": attr}
        except Exception as e:  # noqa: BLE001
            log.warning("Skip %s: %s", rel, e)

    _cache = features
    _cache_dir = dataset_dir
    _cache_mtime = max(os.path.getmtime(p) for p in images) if images else 0
    faiss_indexer.build_index(_cache)

    try:
        np.save(cache_file, np.array({"features": features, "mtime": _cache_mtime, "version": CACHE_VERSION}, dtype=object), allow_pickle=True)
        log.info("Cache saved (%d faces, version %s).", len(features), CACHE_VERSION)
    except Exception as e:  # noqa: BLE001
        log.warning("Could not save cache: %s", e)


# ────────────────────────────────── Endpoints ────────────────────────────────

@app.on_event("startup")
def startup_event():
    load_model()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    gallery_default = os.path.join(base_dir, "dataset", "gallery")
    gallery_all = os.path.join(base_dir, "dataset", "gallery_all")
    gallery_path = gallery_default if os.path.exists(gallery_default) else gallery_all
    try:
        build_cache(gallery_path, force=False)
        log.info("Startup complete: Pre-loaded %d cached faces into memory & FAISS index.", len(_cache))
    except Exception as e:
        log.warning("Startup cache load warning: %s", e)


@app.post("/synthesize")
def synthesize(
    file: UploadFile = File(...),
    skin_tone: str = Form("WHEATISH"),
    token_data: dict = Depends(verify_token)
):
    data = file.file.read()
    if not data or len(data) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid sketch image file.")
    try:
        rendered_png = GenerativeSynthesizer.synthesize_photo_from_sketch(data, skin_tone=skin_tone)
        from fastapi.responses import Response
        return Response(content=rendered_png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Synthesis failed: {e}")



@app.post("/explain")
def explain_match(
    file: UploadFile = File(...),
    candidate_path: str = Form(...),
    token_data: dict = Depends(verify_token)
):
    q_data = file.file.read()
    if not q_data or len(q_data) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid sketch image file.")
    
    full_cand_path = _resolve_full_path(candidate_path, _cache_dir or "")
    if not os.path.exists(full_cand_path):
        raise HTTPException(status_code=404, detail=f"Candidate image file not found: {candidate_path}")

    try:
        with open(full_cand_path, "rb") as fh:
            c_data = fh.read()
        heatmap_png = XAIExplainer.generate_heatmap_comparison(q_data, c_data, similarity_score=0.85)
        from fastapi.responses import Response
        return Response(content=heatmap_png, media_type="image/png")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"XAI heatmap generation failed: {e}")


@app.post("/recommend_elements")
def recommend_elements(
    face_shape: str = Form("OVAL"),
    eyes_style: str = Form("DEFAULT"),
    token_data: dict = Depends(verify_token)
):
    return ElementRecommender.recommend(face_shape, eyes_style)






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


@app.post("/auth/token", response_model=TokenResponse)
def get_token(req: Optional[TokenRequest] = None):
    client = req.client_id if req else "thirdeye_desktop_client"
    token = create_access_token({"sub": client, "role": "officer"})
    return TokenResponse(
        status="ok",
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRATION_SECONDS
    )


@app.post("/embed")
def embed(file: UploadFile = File(...), token_data: dict = Depends(verify_token)):
    data = file.file.read()
    if not data or len(data) < 10:
        raise HTTPException(status_code=422, detail="Empty or invalid image file uploaded.")
    emb = embed_image(data)
    if emb is None:
        raise HTTPException(status_code=422, detail="Could not embed image (no face found).")
    return {"status": "ok", "shape": list(emb.shape), "embedding": emb.tolist()}


@app.post("/rebuild_cache")
def rebuild_cache(dataset_dir: str = Form(...), token_data: dict = Depends(verify_token)):
    dataset_dir = os.path.abspath(dataset_dir)
    t0 = time.time()
    build_cache(dataset_dir, force=True)
    return {"status": "ok", "images": len(_cache), "elapsed_s": round(time.time() - t0, 2)}


def _resolve_full_path(rel_or_abs: str, base_dir: str) -> str:
    if os.path.isabs(rel_or_abs) and os.path.exists(rel_or_abs):
        return os.path.abspath(os.path.normpath(rel_or_abs))

    cand1 = os.path.abspath(os.path.normpath(os.path.join(base_dir, rel_or_abs)))
    if os.path.exists(cand1):
        return cand1

    cand2 = os.path.abspath(os.path.normpath(os.path.join(base_dir, "gallery", rel_or_abs)))
    if os.path.exists(cand2):
        return cand2

    cand3 = os.path.abspath(os.path.normpath(os.path.join(base_dir, "gallery_all", rel_or_abs)))
    if os.path.exists(cand3):
        return cand3

    return cand1


@app.post("/match", response_model=MatchResponse)
def match(
    file: UploadFile = File(...),
    dataset_dir: str = Form(...),
    top_n: int = Form(TOP_RESULTS),
    gender_filter: str = Form("ALL"),
    min_age_filter: int = Form(0),
    max_age_filter: int = Form(100),
    token_data: dict = Depends(verify_token)
):
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
        
    # 2. Modality-Specific Feature Extraction & Soft Demographic Alignment
    try:
        q_arr = np.frombuffer(data, np.uint8)
        q_img_bgr = cv2.imdecode(q_arr, cv2.IMREAD_COLOR)
        q_img_rgb = cv2.cvtColor(q_img_bgr, cv2.COLOR_BGR2RGB) if q_img_bgr is not None else None
        q_attr = DemographicEstimator.estimate_attributes(q_img_rgb, filename=file.filename)
    except Exception:
        q_attr = {"gender": "UNKNOWN", "gender_conf": 0.0, "age_est": 30, "age_conf": 0.0}

    scored = []
    candidates_evaluated = 0
    candidates_pruned = 0
    
    q_grey = hog_grey(data)
    q_emb = embed_image(data)
    if q_emb is None:
        raise HTTPException(status_code=422, detail="Could not extract face embedding from query image.")
    q_hog = compute_hog(q_grey)
    q_lbp = compute_lbp(q_grey)

    target_gender = gender_filter.upper().strip() if gender_filter else "ALL"

    for rel, feats in _cache.items():
        g_face = feats.get("face")
        if g_face is None:
            continue
        candidates_evaluated += 1

        g_attr = feats.get("attr", {})
        if not g_attr:
            try:
                g_path = _resolve_full_path(rel, dataset_dir)
                g_img = cv2.imread(g_path)
                if g_img is not None:
                    g_img = cv2.cvtColor(g_img, cv2.COLOR_BGR2RGB)
                g_attr = DemographicEstimator.estimate_attributes(g_img, filename=g_path)
                feats["attr"] = g_attr
            except Exception:
                g_attr = {"gender": "UNKNOWN", "gender_conf": 0.0, "age_est": 30, "age_conf": 0.0}

        # Apply Biometric Pre-Filtering
        cand_gender = g_attr.get("gender", "UNKNOWN")
        cand_age = g_attr.get("age_est", 30)

        # 1. Gender Filter Check
        if target_gender in ("MALE", "FEMALE") and cand_gender in ("MALE", "FEMALE"):
            if cand_gender != target_gender:
                candidates_pruned += 1
                continue

        # 2. Age Range Check
        if (min_age_filter > 0 or max_age_filter < 100) and (cand_age < min_age_filter or cand_age > max_age_filter):
            candidates_pruned += 1
            continue

        face_sim = float(np.dot(q_emb, g_face))
        hog_sim = float(np.dot(q_hog, feats.get("hog", q_hog)))
        lbp_sim = float(np.dot(q_lbp, feats.get("lbp", q_lbp)))
        
        if query_modality == "PHOTO":
            base_sim = 0.60 * face_sim + 0.25 * hog_sim + 0.15 * lbp_sim
        else:
            base_sim = pro_hybrid_score(face_sim, hog_sim, lbp_sim)

        penalty = DemographicEstimator.compute_soft_penalty(q_attr, g_attr)
        sim = base_sim * penalty
        scored.append((sim, rel))

    scored.sort(reverse=True, key=lambda x: x[0])
    
    # Deduplicate results by filename basename so every candidate shown is a unique image
    seen_basenames = set()
    unique_scored = []
    for sim, rel in scored:
        bname = os.path.basename(rel).lower()
        if bname not in seen_basenames:
            seen_basenames.add(bname)
            unique_scored.append((sim, rel))

    threshold = 0.42 if query_modality in ("PHOTO", "COMPOSITE_FORENSIC_SKETCH") else 0.45
    top_score = unique_scored[0][0] if unique_scored else 0.0
    
    if top_score >= threshold:
        match_decision = "POSSIBLE MATCH"
    else:
        match_decision = "NO RELIABLE MATCH FOUND IN CURRENT GALLERY"
        warnings.append(f"Top candidate similarity ({top_score*100.0:.1f}%) is below calibrated threshold ({threshold*100.0:.1f}%). Outputting nearest candidates only.")

    top_n = max(1, min(top_n, len(unique_scored))) if unique_scored else 0
    top = unique_scored[:top_n]

    results = [
        MatchResult(
            name=os.path.splitext(os.path.basename(rel))[0],
            path=_resolve_full_path(rel, dataset_dir),
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
        demographic_filter_applied=(target_gender in ("MALE", "FEMALE") or min_age_filter > 0 or max_age_filter < 100),
        gender_filter=target_gender,
        candidates_evaluated=candidates_evaluated,
        candidates_pruned=candidates_pruned,
    )



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
