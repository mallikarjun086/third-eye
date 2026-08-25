"""Evaluate sketch-to-photo retrieval accuracy on the indexed gallery."""
import os
import sys
import numpy as np
import app

base_dir = os.path.dirname(os.path.abspath(__file__))
default_gallery = os.path.join(base_dir, "dataset", "gallery")
default_queries = os.path.join(base_dir, "dataset", "queries")

GALLERY = sys.argv[1] if len(sys.argv) > 1 else default_gallery
QUERIES = sys.argv[2] if len(sys.argv) > 2 else default_queries
TOP = int(sys.argv[3]) if len(sys.argv) > 3 else 5

app.load_model()
if app._model is None:
    sys.exit("Model load failed: " + str(app._model_error))

app.build_cache(GALLERY)
queries = []
if os.path.exists(QUERIES):
    for root, _dirs, files in os.walk(QUERIES):
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS:
                queries.append(os.path.join(root, f))

correct = 0
topk_hits = {k: 0 for k in range(1, TOP + 1)}
total = 0

def to_pid(name):
    return name.replace("-01-sz1", "").replace("-01", "")

for q in queries:
    qid = to_pid(os.path.splitext(os.path.basename(q))[0])  # e.g. "f-039"
    with open(q, "rb") as fh:
        data = fh.read()
    emb = app.embed_image(data)
    if emb is None:
        continue
    hog = app.compute_hog(app.hog_grey(data))
    scored = sorted(
        (
            (app.hybrid_score(float(np.dot(emb, f["face"])), float(np.dot(hog, f["hog"]))), rel)
            for rel, f in app._cache.items()
        ),
        reverse=True,
    )
    rank = 1
    for sim, rel in scored:
        rid = to_pid(os.path.splitext(os.path.basename(rel))[0])
        if rid == qid:
            if rank == 1:
                correct += 1
            for k in range(rank, TOP + 1):
                topk_hits[k] += 1
            break
        rank += 1
    total += 1

print(f"Queries tested: {total}")
print(f"Hybrid (FaceNet w={app.FACE_WEIGHT} + HOG):")
print(f"Rank-1 accuracy: {100 * correct / total:.1f}%")
for k, v in topk_hits.items():
    if k > 1:
        print(f"Rank-{k} accuracy: {100 * v / total:.1f}%")
