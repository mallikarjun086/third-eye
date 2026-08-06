"""Prototype: fuse FaceNet embedding similarity with HOG/edge similarity.

Grid-searches the fusion weight w in  combined = w*faceNet + (1-w)*hog
and reports Rank-1..Top accuracy for each weight.
"""
import os
import sys
import numpy as np
import app

GALLERY = sys.argv[1] if len(sys.argv) > 1 else "dataset/gallery"
QUERIES = sys.argv[2] if len(sys.argv) > 2 else "dataset/queries"
TOP = int(sys.argv[3]) if len(sys.argv) > 3 else 5

HOG_CELL = 8
HOG_BINS = 9
COMPARE = 160

app.load_model()
if app._model is None:
    sys.exit("Model load failed: " + str(app._model_error))

app.build_cache(GALLERY)

# Face weight map: higher weight in the eye/nose/central face region
# (mimics the Java engine's per-cell weighting).
_fwmap = None

def _make_face_weight_map(cells_x, cells_y):
    map_ = np.zeros((cells_y, cells_x), dtype=np.float64)
    cyc, cxc = (cells_y - 1) / 2.0, (cells_x - 1) / 2.0
    for cy in range(cells_y):
        for cx in range(cells_x):
            # Gaussian falloff from centre; slightly favoured upper region (eyes)
            d = np.hypot((cx - cxc) / cxc, (cy - cyc) / cyc)
            map_[cy, cx] = 2.0 * np.exp(-2.0 * d * d)
    map_ -= map_.min()
    return map_


def hog_descriptor(grey):
    """Sobel-based HOG, cells of HOG_CELL, HOG_BINS unsigned bins with
    bilinear bin interpolation (mirrors the Java engine)."""
    grey = grey.astype(np.float64)
    h, w = grey.shape
    gx = np.zeros_like(grey)
    gy = np.zeros_like(grey)
    gx[:, 1:-1] = grey[:, 2:] - grey[:, :-2]
    gy[1:-1, :] = grey[2:, :] - grey[:-2, :]
    mag = np.hypot(gx, gy)
    ang = np.degrees(np.arctan2(gy, gx)) % 180.0

    cells_x, cells_y = w // HOG_CELL, h // HOG_CELL
    global _fwmap
    if _fwmap is None or _fwmap.shape != (cells_y, cells_x):
        _fwmap = _make_face_weight_map(cells_x, cells_y)

    bins = (ang / (180.0 / HOG_BINS)) % HOG_BINS
    b0 = bins.astype(np.int32)
    frac = bins - b0
    b1 = (b0 + 1) % HOG_BINS

    desc = np.zeros(cells_y * cells_x * HOG_BINS, dtype=np.float64)
    cy0, cx0 = np.meshgrid(np.arange(cells_y), np.arange(cells_x), indexing="ij")
    oy = cy0.reshape(-1, 1) * HOG_CELL
    ox = cx0.reshape(-1, 1) * HOG_CELL

    # accumulate votes per cell with bilinear interpolation
    for dy in range(HOG_CELL):
        for dx in range(HOG_CELL):
            yy, xx = oy + dy, ox + dx
            w = mag[yy, xx] * _fwmap[cy0.reshape(-1, 1), cx0.reshape(-1, 1)]
            bb0 = b0[yy, xx]
            bb1 = b1[yy, xx]
            ff = frac[yy, xx]
            flat = (cy0.reshape(-1, 1) * cells_x + cx0.reshape(-1, 1)) * HOG_BINS
            np.add.at(desc, flat + bb0, w * (1.0 - ff))
            np.add.at(desc, flat + bb1, w * ff)

    n = np.linalg.norm(desc)
    return desc / n if n > 0 else desc


def load_grey(path, size=COMPARE):
    from PIL import Image
    img = Image.open(path).convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float64)
    return arr.mean(axis=2)


def prep_image_bytes(data):
    """Resize to the same canonical 160x160 used for the gallery HOG."""
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(data)).convert("RGB")
    img = img.resize((COMPARE, COMPARE), Image.LANCZOS)
    arr = np.asarray(img).astype(np.float64)
    return arr.mean(axis=2)


# ---- build gallery HOG once ----
gal_rels = sorted(app._embedding_cache.keys())
print(f"Indexing {len(gal_rels)} gallery faces (HOG)...")
gal_hog = {}
for rel in gal_rels:
    p = os.path.join(GALLERY, rel)
    gal_hog[rel] = hog_descriptor(load_grey(p))
print("HOG gallery built.")

queries = sorted(p for p in app._list_images(QUERIES) if not p.endswith(".npy"))
print(f"Queries: {len(queries)}")

emb_cache = app._embedding_cache
weights = np.arange(0.0, 0.31, 0.05)
print(f"\n{'w':>5} | " + " ".join(f"R{k:<5}" for k in range(1, TOP + 1)))
for w in weights:
    correct = {k: 0 for k in range(1, TOP + 1)}
    total = 0
    for q in queries:
        qid = os.path.splitext(os.path.basename(q))[0]
        with open(q, "rb") as fh:
            data = fh.read()
        femb = app.embed_image(data)
        if femb is None:
            continue
        fsim = {rel: float(np.dot(femb, e)) for rel, e in emb_cache.items()}
        grey = prep_image_bytes(data)
        qhog = hog_descriptor(grey)
        hsim = {rel: float(np.dot(qhog, gh)) for rel, gh in gal_hog.items()}
        combined = {rel: w * fsim[rel] + (1 - w) * hsim[rel] for rel in fsim}
        scored = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        rank = 1
        for rel, _ in scored:
            rid = os.path.splitext(os.path.basename(rel))[0]
            if rid == qid:
                for k in range(rank, TOP + 1):
                    correct[k] += 1
                break
            rank += 1
        total += 1
    row = " ".join(f"{100 * correct[k] / total:5.1f}%" for k in range(1, TOP + 1))
    print(f"{w:5.1f} | {row}")
