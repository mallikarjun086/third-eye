"""Compare detection-based extract() vs raw embeddings() on identical photos."""
import os
import sys
import numpy as np
from keras_facenet import FaceNet

model = FaceNet()
gallery = sys.argv[1]

files = sorted(os.path.join(gallery, f) for f in os.listdir(gallery)
               if f.lower().endswith((".jpg", ".jpeg", ".png")))[:10]

from PIL import Image

def raw_emb(path):
    img = Image.open(path).convert("RGB")
    arr = np.asarray(img)
    h, w = arr.shape[:2]
    if h < 160 or w < 160:
        scale = 160 / min(h, w)
        arr = np.asarray(img.resize((int(w*scale), int(h*scale)), Image.LANCZOS))
    e = model.embeddings(np.expand_dims(arr, axis=0))[0]
    return e / (np.linalg.norm(e) + 1e-9)

def extract_emb(path):
    img = np.asarray(Image.open(path).convert("RGB"))
    try:
        dets, embs = model.extract(img, threshold=0.90)
    except Exception as ex:
        print("  extract failed:", ex)
        return None
    if embs is None or len(embs) == 0:
        return None
    e = embs[0]
    return e / (np.linalg.norm(e) + 1e-9)

print("=== raw embeddings() on identical photos ===")
raws = [raw_emb(f) for f in files]
for i in range(min(5, len(files))):
    print(f"  photo {i} vs {i}: {float(np.dot(raws[i], raws[i])):.3f}")

print("=== extract() embeddings on identical photos ===")
exts = []
for i, f in enumerate(files):
    e = extract_emb(f)
    print(f"  photo {i}: {'OK' if e is not None else 'NO FACE DETECTED'}")
    exts.append(e)

ok = [e for e in exts if e is not None]
if len(ok) > 1:
    print(f"  mean self-sim: {np.mean([float(np.dot(ok[i], ok[i])) for i in range(len(ok))]):.3f}")
    # pairwise between different photos to sanity check
    sims = [float(np.dot(ok[0], ok[j])) for j in range(1, len(ok))]
    print(f"  photo0 vs others (should be low): {[round(s,3) for s in sims[:5]]}")
