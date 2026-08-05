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

app = FastAPI(title="ThirdEye ML Service", version="1.0.0")

# Lazy-loaded FaceNet model (keras-facenet bundles a pretrained model)
_model = None
_model_error: Optional[str] = None

# In-memory embedding cache: relative path -> normalized 512-d vector
_embedding_cache: Dict[str, np.ndarray] = {}
_cache_mtime: Optional[float] = None
_cache_dir: Optional[str] = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CACHE_FILE = "dataset_embeddings.npy"

TOP_RESULTS = 10


class MatchResult(BaseModel):
    name: str
    path: str
    similarity: float


class MatchResponse(BaseModel):
    status: str
    sketch_embedded: bool
    count: int
    results: List[MatchResult]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_error: Optional[str]
    dataset_dir: Optional[str]
    dataset_images: int
    cache_built: bool


# ─────────────────────────────── Model helpers ───────────────────────────────

def load_model():
    """Load the FaceNet model once. Returns None on failure (records error)."""
    global _model, _model_error
    if _model is not None or _model_error is not None:
        return
    try:
        from keras_facenet import FaceNet
        log.info("Loading FaceNet model...")
        _model = FaceNet()
        log.info("FaceNet model loaded.")
    except Exception as e:  # noqa: BLE001
        _model_error = str(e)
        log.error("Model load failed: %s", e)


def embed_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """Return a normalized 512-d embedding for raw image bytes, or None."""
    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    from PIL import Image
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Bad image: {e}")

    arr = np.asarray(img)
    # FaceNet expects >= (160,160). Upscale small inputs.
    min_dim = 160
    h, w = arr.shape[:2]
    if h < min_dim or w < min_dim:
        scale = min_dim / min(h, w)
        new_size = (int(w * scale), int(h * scale))
        arr = np.asarray(img.resize(new_size, Image.LANCZOS))

    try:
        emb = _model.embeddings(np.expand_dims(arr, axis=0))[0]
    except Exception as e:  # noqa: BLE001
        log.warning("Embedding failed: %s", e)
        return None

    norm = np.linalg.norm(emb)
    if norm > 0:
        emb = emb / norm
    return emb


# ─────────────────────────────── Dataset indexing ────────────────────────────

def _list_images(dataset_dir: str) -> List[str]:
    images = []
    for root, _dirs, files in os.walk(dataset_dir):
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                images.append(os.path.join(root, f))
    return images


def _cache_path(dataset_dir: str) -> str:
    return os.path.join(dataset_dir, CACHE_FILE)


def build_cache(dataset_dir: str, force: bool = False):
    """Embed every image in the dataset directory and persist to a .npy cache."""
    global _embedding_cache, _cache_mtime, _cache_dir
    if not os.path.isdir(dataset_dir):
        raise HTTPException(status_code=400, detail=f"dataset_dir not found: {dataset_dir}")

    load_model()
    if _model is None:
        raise HTTPException(status_code=503, detail=f"Model not loaded: {_model_error}")

    images = _list_images(dataset_dir)
    cache_file = _cache_path(dataset_dir)

    # Load existing cache if present and dataset unchanged
    if not force and os.path.exists(cache_file):
        try:
            data = np.load(cache_file, allow_pickle=True).item()
            _embedding_cache = data.get("embeddings", {})
            _cache_mtime = data.get("mtime", 0)
            _cache_dir = dataset_dir
            cached = _list_images(dataset_dir)
            mtime = max(os.path.getmtime(p) for p in cached) if cached else 0
            if _cache_mtime == mtime and set(_embedding_cache.keys()) == set(cached):
                log.info("Using cached embeddings (%d faces).", len(_embedding_cache))
                return
        except Exception as e:  # noqa: BLE001
            log.warning("Cache load failed, rebuilding: %s", e)

    log.info("Building embedding cache for %d images...", len(images))
    embeddings: Dict[str, np.ndarray] = {}
    for path in images:
        rel = os.path.relpath(path, dataset_dir)
        try:
            with open(path, "rb") as fh:
                emb = embed_image(fh.read())
            if emb is not None:
                embeddings[rel] = emb
        except Exception as e:  # noqa: BLE001
            log.warning("Skip %s: %s", rel, e)

    _embedding_cache = embeddings
    _cache_dir = dataset_dir
    _cache_mtime = max(os.path.getmtime(p) for p in images) if images else 0

    try:
        np.save(cache_file, {"embeddings": embeddings, "mtime": _cache_mtime}, allow_pickle=True)
        log.info("Cache saved (%d faces).", len(embeddings))
    except Exception as e:  # noqa: BLE001
        log.warning("Could not save cache: %s", e)


# ────────────────────────────────── Endpoints ────────────────────────────────

@app.get("/health", response_model=HealthResponse)
def health():
    dataset_dir = _cache_dir
    images = _list_images(dataset_dir) if dataset_dir else []
    return HealthResponse(
        status="ok",
        model_loaded=_model is not None,
        model_error=_model_error,
        dataset_dir=dataset_dir,
        dataset_images=len(images),
        cache_built=_cache_dir is not None,
    )


@app.post("/embed")
def embed(file: UploadFile = File(...)):
    data = file.file.read()
    emb = embed_image(data)
    if emb is None:
        raise HTTPException(status_code=422, detail="Could not embed image (no face found).")
    return {"status": "ok", "shape": list(emb.shape), "embedding": emb.tolist()}


@app.post("/rebuild_cache")
def rebuild_cache(dataset_dir: str = Form(...)):
    t0 = time.time()
    build_cache(dataset_dir, force=True)
    return {"status": "ok", "images": len(_embedding_cache), "elapsed_s": round(time.time() - t0, 2)}


@app.post("/match", response_model=MatchResponse)
def match(file: UploadFile = File(...), dataset_dir: str = Form(...), top_n: int = Form(TOP_RESULTS)):
    data = file.file.read()
    sketch_emb = embed_image(data)
    if sketch_emb is None:
        raise HTTPException(status_code=422, detail="Could not embed sketch (no face found).")

    build_cache(dataset_dir)
    if not _embedding_cache:
        raise HTTPException(status_code=422, detail="No faces could be embedded in the dataset.")

    scored = []
    for rel, emb in _embedding_cache.items():
        sim = float(np.dot(sketch_emb, emb))  # both normalized -> cosine similarity
        scored.append((sim, rel))

    scored.sort(reverse=True, key=lambda x: x[0])
    top = scored[:max(1, min(top_n, len(scored)))]

    results = [
        MatchResult(
            name=os.path.splitext(os.path.basename(rel))[0],
            path=os.path.join(dataset_dir, rel),
            similarity=round(sim, 4),
        )
        for sim, rel in top
    ]
    return MatchResponse(
        status="ok",
        sketch_embedded=True,
        count=len(results),
        results=results,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000)
