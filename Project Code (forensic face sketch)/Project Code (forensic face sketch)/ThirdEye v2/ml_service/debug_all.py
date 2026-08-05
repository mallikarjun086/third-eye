"""Loop all queries and check where matching fails."""
import os, sys, numpy as np, app
G = sys.argv[1]; Q = sys.argv[2]
app.load_model(); app.build_cache(G)
queries = sorted(p for p in app._list_images(Q) if not p.endswith(".npy"))
miss = []
for q in queries:
    with open(q, "rb") as fh:
        emb = app.embed_image(fh.read())
    if emb is None:
        miss.append((q, "EMBED FAIL")); continue
    scored = sorted(((float(np.dot(emb, e)), rel) for rel, e in app._embedding_cache.items()), reverse=True)
    qid = os.path.splitext(os.path.basename(q))[0]
    for rank, (sim, rel) in enumerate(scored, 1):
        if os.path.splitext(os.path.basename(rel))[0] == qid:
            if rank > 1:
                miss.append((q, f"rank {rank} (not 1) top={scored[0]}"))
            break
    else:
        miss.append((q, "NOT FOUND"))
print(f"Total queries: {len(queries)}, misses: {len(miss)}")
for m in miss[:15]:
    print(" ", m)
