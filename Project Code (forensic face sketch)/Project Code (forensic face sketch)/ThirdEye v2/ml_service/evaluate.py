"""Evaluate sketch-to-photo retrieval accuracy on the indexed gallery."""
import os
import sys
import numpy as np
import app

GALLERY = sys.argv[1] if len(sys.argv) > 1 else "dataset/gallery"
QUERIES = sys.argv[2] if len(sys.argv) > 2 else "dataset/queries"
TOP = int(sys.argv[3]) if len(sys.argv) > 3 else 5

app.load_model()
if app._model is None:
    sys.exit("Model load failed: " + str(app._model_error))

app.build_cache(GALLERY)
queries = sorted(p for p in app._list_images(QUERIES)
                 if not p.endswith(".npy"))

correct = 0
topk_hits = {k: 0 for k in range(1, TOP + 1)}
total = 0

for q in queries:
    qid = os.path.splitext(os.path.basename(q))[0]  # e.g. "12"
    with open(q, "rb") as fh:
        emb = app.embed_image(fh.read())
    if emb is None:
        continue
    scored = sorted(((float(np.dot(emb, e)), rel) for rel, e in app._embedding_cache.items()),
                    reverse=True)
    rank = 1
    for sim, rel in scored:
        rid = os.path.splitext(os.path.basename(rel))[0]
        if rid == qid:
            if rank == 1:
                correct += 1
            for k in range(rank, TOP + 1):
                topk_hits[k] += 1
            break
        rank += 1
    total += 1

print(f"Queries tested: {total}")
print(f"Rank-1 accuracy: {100 * correct / total:.1f}%")
for k, v in topk_hits.items():
    print(f"Rank-{k} accuracy: {100 * v / total:.1f}%")
