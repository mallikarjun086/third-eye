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
    print("TOP-10 HIGHEST ACCURACY MATCHED IMAGES FROM ADDED DESKTOP DATASETS")
    print("======================================================================")

    # 1. Load model
    app.load_model()

    # 2. Pick sample images from added datasets to build a fast target cache
    added_photo_dirs = [
        r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\test\photos",
        r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\val\photos",
        r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive (1)\actors_dataset\Indian_actors_faces"
    ]

    target_images = []
    for d in added_photo_dirs:
        if os.path.exists(d):
            for root, _, files in os.walk(d):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS:
                        target_images.append(os.path.join(root, f))
                        if len(target_images) >= 500:
                            break
                if len(target_images) >= 500:
                    break

    print(f"\n[INFO] Extracting embeddings for {len(target_images)} sample images from added datasets...")

    features = {}
    for p in target_images:
        try:
            with open(p, "rb") as fh:
                raw = fh.read()
            grey = app.hog_grey(raw)
            emb = app.embed_image(raw)
            hog = app.compute_hog(grey)
            if emb is not None:
                features[p] = {"face": emb, "hog": hog}
        except Exception:
            pass

    # 3. Query sketch
    query_sketch = r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\test\sketches\10132.jpg"
    if not os.path.exists(query_sketch):
        query_sketch = os.path.join(ML_SERVICE, "dataset", "queries", "001.png")

    print(f"\n[QUERY SKETCH]: {query_sketch}")
    with open(query_sketch, "rb") as fh:
        sketch_raw = fh.read()

    sketch_grey = app.hog_grey(sketch_raw)
    sketch_emb = app.embed_image(sketch_raw)
    sketch_hog = app.compute_hog(sketch_grey)

    # 4. Rank candidates
    scored = []
    for path, feats in features.items():
        face_sim = float(np.dot(sketch_emb, feats["face"]))
        hog_sim = float(np.dot(sketch_hog, feats["hog"]))
        sim = app.hybrid_score(face_sim, hog_sim)
        scored.append((sim, path))

    scored.sort(reverse=True, key=lambda x: x[0])
    top10 = scored[:10]

    report = []
    print("\n" + "="*80)
    print("RANK | ACCURACY SCORE | MATCHED SUSPECT IMAGE NAME | PHYSICAL FILE PATH")
    print("="*80)

    for rank, (sim, path) in enumerate(top10, start=1):
        pct = round(sim * 100.0, 2)
        name = os.path.basename(path)
        print(f" #{rank:02d} |    {pct:6.2f}%     | {name:26s} | {path}")
        report.append({
            "rank": rank,
            "accuracy_percentage": pct,
            "image_name": name,
            "physical_path": path
        })

    print("="*80)

    out_json = os.path.join(WORKSPACE, "results", "top10_matches_report.json")
    with open(out_json, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[SUCCESS] Top-10 match report saved to: {out_json}")

if __name__ == "__main__":
    main()
