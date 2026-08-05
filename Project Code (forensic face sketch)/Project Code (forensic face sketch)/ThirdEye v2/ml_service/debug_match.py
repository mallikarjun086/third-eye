"""Debug: does query 0 match gallery 0 at rank 1?"""
import os, sys, numpy as np, app
G = sys.argv[1]; Q = sys.argv[2]
app.load_model(); app.build_cache(G)
q0 = sorted(app._list_images(Q))[0]
with open(q0, "rb") as fh:
    qemb = app.embed_image(fh.read())
scored = sorted(((float(np.dot(qemb, e)), rel) for rel, e in app._embedding_cache.items()), reverse=True)
print("query:", q0)
for i, (sim, rel) in enumerate(scored[:5]):
    print(f"  rank{i+1}: {rel} sim={sim:.4f}")
qid = os.path.splitext(os.path.basename(q0))[0]
for i, (sim, rel) in enumerate(scored):
    if os.path.splitext(os.path.basename(rel))[0] == qid:
        print(f"correct id '{qid}' found at rank {i+1} sim={sim:.4f}")
        break
