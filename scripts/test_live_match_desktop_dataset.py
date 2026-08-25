import os
import sys
import json
import numpy as np

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

import app

def main():
    print("======================================================================")
    print("TESTING LIVE MATCHING ACROSS ENLARGED DESKTOP DATASETS (TOP-10)")
    print("======================================================================")

    # 1. Initialize model
    app.load_model()
    
    # 2. Build cache across all registered datasets
    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    print("\n[INFO] Building feature cache for enlarged gallery...")
    app.build_cache(gallery_dir, force=True)

    # 3. Pick a query sketch image (from test set or composite)
    query_sketch = os.path.join(ML_SERVICE, "dataset", "queries", "001.png")
    if not os.path.exists(query_sketch):
        query_sketch = os.path.join(r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\test\sketches", "10132.jpg")

    print(f"\n[QUERY SKETCH]: {query_sketch}")
    with open(query_sketch, "rb") as fh:
        sketch_data = fh.read()

    sketch_grey = app.hog_grey(sketch_data)
    sketch_emb = app.embed_image(sketch_data)
    sketch_hog = app.compute_hog(sketch_grey)

    # 4. Rank candidates across the entire cache
    scored = []
    for rel, feats in app._cache.items():
        face_sim = float(np.dot(sketch_emb, feats["face"]))
        hog_sim = float(np.dot(sketch_hog, feats["hog"]))
        sim = app.hybrid_score(face_sim, hog_sim)
        scored.append((sim, rel))

    scored.sort(reverse=True, key=lambda x: x[0])
    top10 = scored[:10]

    print("\n======================================================================")
    print("TOP-10 HIGHEST ACCURACY MATCHES FROM ENLARGED DATASET:")
    print("======================================================================")
    for rank, (sim, rel) in enumerate(top10, start=1):
        full_path = rel if os.path.isabs(rel) else os.path.join(gallery_dir, rel)
        pct = round(sim * 100.0, 2)
        print(f"Rank #{rank:02d} | Accuracy: {pct:6.2f}% | Name: {os.path.basename(rel)} | Path: {full_path}")

    print("\n[SUCCESS] Live match testing completed successfully!")

if __name__ == "__main__":
    main()
