import os
import sys
import glob
import json
import time
import requests
import csv
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

def main():
    root = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
    ml_dir = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
    sys.path.insert(0, ml_dir)
    
    import app
    import evaluation_engine as ee

    out_dir = os.path.join(root, "results", "critical_identification_repair")
    os.makedirs(out_dir, exist_ok=True)

    gallery_dir = os.path.join(ml_dir, "dataset", "gallery")
    queries_dir = os.path.join(ml_dir, "dataset", "queries")

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    gallery_files = sorted([f for f in glob.glob(os.path.join(gallery_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])
    query_files = sorted([f for f in glob.glob(os.path.join(queries_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])

    print(f"Loaded {len(gallery_files)} valid gallery image files and {len(query_files)} query image files.")

    app.load_model()
    app.build_cache(gallery_dir)

    # 1. Build cache lookup map
    def get_cached(path):
        base = os.path.basename(path)
        if base in app._cache:
            return app._cache[base]
        rel = os.path.relpath(path, gallery_dir)
        if rel in app._cache:
            return app._cache[rel]
        for k, v in app._cache.items():
            if os.path.basename(k) == base:
                return v
        # compute on the fly safely
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
            emb = app.embed_image(raw)
            hog = app.compute_hog(app.hog_grey(raw))
        except Exception as e:
            emb = None
            hog = None
        entry = {"face": emb, "hog": hog}
        app._cache[base] = entry
        return entry

    gal_vectors = []
    gal_paths = []
    gal_pids = []

    for g in gallery_files:
        c = get_cached(g)
        if c["face"] is not None:
            # L2 normalize
            norm_f = c["face"] / (np.linalg.norm(c["face"]) + 1e-10)
            gal_vectors.append(norm_f)
            gal_paths.append(g)
            gal_pids.append(ee.to_pid(g))

    gal_vectors = np.array(gal_vectors)

    # --- TEST A: Exact physical gallery image vector matching ---
    test_a_results = []
    for idx, g in enumerate(gallery_files):
        c = get_cached(g)
        if c["face"] is None:
            continue
        q_vec = c["face"] / (np.linalg.norm(c["face"]) + 1e-10)
        sims = np.dot(gal_vectors, q_vec)
        top_idx = np.argmax(sims)
        matched_g = gal_paths[top_idx]
        is_pass = (matched_g == g)
        test_a_results.append({
            "query": g,
            "matched": matched_g,
            "rank1_sim": float(sims[top_idx]),
            "pass": is_pass
        })

    test_a_pass_count = sum(1 for r in test_a_results if r["pass"])
    test_a_acc = (test_a_pass_count / len(test_a_results)) * 100.0 if test_a_results else 0.0

    # --- TEST B: Same image reloaded from disk ---
    test_b_results = []
    for g in gallery_files[:50]:  # sample 50
        with open(g, "rb") as fh:
            raw = fh.read()
        emb = app.embed_image(raw)
        if emb is None:
            continue
        q_vec = emb / (np.linalg.norm(emb) + 1e-10)
        sims = np.dot(gal_vectors, q_vec)
        top_idx = np.argmax(sims)
        matched_g = gal_paths[top_idx]
        is_pass = (matched_g == g)
        test_b_results.append({
            "query": g,
            "matched": matched_g,
            "rank1_sim": float(sims[top_idx]),
            "pass": is_pass
        })

    test_b_pass_count = sum(1 for r in test_b_results if r["pass"])
    test_b_acc = (test_b_pass_count / len(test_b_results)) * 100.0 if test_b_results else 0.0

    # --- TEST C: HTTP REST API Matching ---
    test_c_results = []
    api_url = "http://127.0.0.1:8000/match"
    api_available = False
    try:
        r = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if r.status_code == 200:
            api_available = True
    except Exception:
        api_available = False

    if api_available:
        for g in gallery_files[:20]:
            with open(g, "rb") as fh:
                resp = requests.post(api_url, files={"file": ("img.png", fh, "image/png")}, data={"dataset_dir": gallery_dir, "top_n": "5"}, timeout=10)
            if resp.status_code == 200:
                res_data = resp.json()
                results = res_data.get("results", [])
                top_match = results[0]["path"] if results else None
                is_pass = (os.path.basename(top_match) == os.path.basename(g)) if top_match else False
                test_c_results.append({"query": g, "matched": top_match, "pass": is_pass})
    
    test_c_pass_count = sum(1 for r in test_c_results if r["pass"])
    test_c_acc = (test_c_pass_count / len(test_c_results)) * 100.0 if test_c_results else 0.0

    # --- TEST E: Controlled Transformations ---
    test_e_results = []
    for g in gallery_files[:20]:
        img = Image.open(g).convert("RGB")
        # Transformations
        t_blur = img.filter(ImageFilter.GaussianBlur(radius=1.5))
        t_blur_path = os.path.join(out_dir, "temp_blur.jpg")
        t_blur.save(t_blur_path)
        
        with open(t_blur_path, "rb") as fh:
            raw = fh.read()
        emb = app.embed_image(raw)
        if emb is not None:
            q_vec = emb / (np.linalg.norm(emb) + 1e-10)
            sims = np.dot(gal_vectors, q_vec)
            top_idx = np.argmax(sims)
            matched_g = gal_paths[top_idx]
            is_pass = (matched_g == g)
            test_e_results.append({"query": g, "matched": matched_g, "pass": is_pass})
        if os.path.exists(t_blur_path):
            os.remove(t_blur_path)

    test_e_pass_count = sum(1 for r in test_e_results if r["pass"])
    test_e_acc = (test_e_pass_count / len(test_e_results)) * 100.0 if test_e_results else 0.0

    # --- TEST F: Sketch to Photo Matching ---
    test_f_records = []
    sketch_rank1_hits = 0
    sketch_rank5_hits = 0
    sketch_rank10_hits = 0
    mrr_sum = 0.0
    valid_query_count = 0

    for q in query_files:
        q_pid = ee.to_pid(q)
        with open(q, "rb") as fh:
            raw = fh.read()
        
        # Dual-stream query processing
        emb = app.embed_image(raw)
        if emb is None:
            continue

        q_proj = emb / (np.linalg.norm(emb) + 1e-10)
        q_hog = app.compute_hog(app.hog_grey(raw))

        # Compare against gallery
        scores = []
        for idx, g in enumerate(gal_paths):
            g_pid = gal_pids[idx]
            c = get_cached(g)
            g_emb = c["face"]
            if g_emb is None:
                continue
            g_proj = g_emb / (np.linalg.norm(g_emb) + 1e-10)

            g_hog = c["hog"]

            # Compute similarities
            deep_sim = float(np.dot(q_proj, g_proj))
            
            # HOG Cosine
            if q_hog is not None and g_hog is not None:
                q_hog_norm = q_hog / (np.linalg.norm(q_hog) + 1e-10)
                g_hog_norm = g_hog / (np.linalg.norm(g_hog) + 1e-10)
                hog_sim = float(np.dot(q_hog_norm, g_hog_norm))
            else:
                hog_sim = 0.0

            # Late fusion alpha = 0.05
            fused_score = 0.05 * deep_sim + 0.95 * hog_sim
            scores.append((fused_score, g_pid, g))

        # Sort descending
        scores.sort(key=lambda x: x[0], reverse=True)
        
        # Find true rank of q_pid
        rank = None
        for r_idx, (s, g_pid, g_path) in enumerate(scores):
            if g_pid == q_pid:
                rank = r_idx + 1
                break

        valid_query_count += 1
        if rank is not None:
            mrr_sum += 1.0 / rank
            if rank == 1:
                sketch_rank1_hits += 1
            if rank <= 5:
                sketch_rank5_hits += 1
            if rank <= 10:
                sketch_rank10_hits += 1

        test_f_records.append({
            "query_path": os.path.basename(q),
            "ground_truth_pid": q_pid,
            "rank": rank if rank else "NOT_FOUND",
            "top1_predicted_pid": scores[0][1] if scores else None,
            "top1_score": round(scores[0][0], 4) if scores else 0.0
        })

    rank1_acc = (sketch_rank1_hits / valid_query_count * 100.0) if valid_query_count else 0.0
    rank5_acc = (sketch_rank5_hits / valid_query_count * 100.0) if valid_query_count else 0.0
    rank10_acc = (sketch_rank10_hits / valid_query_count * 100.0) if valid_query_count else 0.0
    mrr = (mrr_sum / valid_query_count) if valid_query_count else 0.0

    summary = {
        "TEST_A_exact_same_image": {"total": len(test_a_results), "passed": test_a_pass_count, "accuracy_pct": round(test_a_acc, 2)},
        "TEST_B_reloaded_from_disk": {"total": len(test_b_results), "passed": test_b_pass_count, "accuracy_pct": round(test_b_acc, 2)},
        "TEST_C_http_api_same_image": {"total": len(test_c_results), "passed": test_c_pass_count, "accuracy_pct": round(test_c_acc, 2) if api_available else "API_OFFLINE"},
        "TEST_E_controlled_transformations": {"total": len(test_e_results), "passed": test_e_pass_count, "accuracy_pct": round(test_e_acc, 2)},
        "TEST_F_sketch_to_photo_matching": {
            "total_queries": valid_query_count,
            "rank1_hits": sketch_rank1_hits,
            "rank1_accuracy_pct": round(rank1_acc, 2),
            "rank5_hits": sketch_rank5_hits,
            "rank5_accuracy_pct": round(rank5_acc, 2),
            "rank10_hits": sketch_rank10_hits,
            "rank10_accuracy_pct": round(rank10_acc, 2),
            "mrr": round(mrr, 4)
        }
    }

    # Save JSON results
    with open(os.path.join(out_dir, "sanity_test_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save CSV per query ranks
    csv_path = os.path.join(out_dir, "per_query_ranks.csv")
    if test_f_records:
        keys = test_f_records[0].keys()
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(test_f_records)

    # Save Markdown report
    report_md = f"""# Sanity Test Suite Execution Report

## Executive Summary
- **TEST A (Exact Gallery Image Vector Matching)**: {test_a_pass_count}/{len(test_a_results)} ({test_a_acc:.2f}%)
- **TEST B (Reloaded Image from Disk)**: {test_b_pass_count}/{len(test_b_results)} ({test_b_acc:.2f}%)
- **TEST C (HTTP REST API Match)**: {test_c_pass_count}/{len(test_c_results)} ({test_c_acc:.2f}%)
- **TEST E (Controlled Transformations - Blur)**: {test_e_pass_count}/{len(test_e_results)} ({test_e_acc:.2f}%)
- **TEST F (Sketch-to-Photo Cross-Modal Matching)**:
  - Total Queries: {valid_query_count}
  - **Rank-1 Accuracy**: {sketch_rank1_hits}/{valid_query_count} (**{rank1_acc:.2f}%**)
  - **Rank-5 Accuracy**: {sketch_rank5_hits}/{valid_query_count} ({rank5_acc:.2f}%)
  - **Rank-10 Accuracy**: {sketch_rank10_hits}/{valid_query_count} ({rank10_acc:.2f}%)
  - **Mean Reciprocal Rank (MRR)**: {mrr:.4f}
"""
    with open(os.path.join(out_dir, "sanity_test_report.md"), "w", encoding="utf-8") as f:
        f.write(report_md)

    print("Sanity tests completed successfully.")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
