import os
import sys
import glob
import json
import csv
import numpy as np

def main():
    root = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
    ml_dir = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
    sys.path.insert(0, ml_dir)

    import app
    import evaluation_engine as ee

    out_dir = os.path.join(root, "results", "cross_modal_repair")
    os.makedirs(out_dir, exist_ok=True)

    gallery_dir = os.path.join(ml_dir, "dataset", "gallery")
    queries_dir = os.path.join(ml_dir, "dataset", "queries")

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    gallery_files = sorted([f for f in glob.glob(os.path.join(gallery_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])
    query_files = sorted([f for f in glob.glob(os.path.join(queries_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])

    app.load_model()
    app.build_cache(gallery_dir, force=False)

    # 1. Dataset Manifest CSV
    manifest_records = []
    for g in gallery_files:
        manifest_records.append({
            "filepath": g,
            "filename": os.path.basename(g),
            "pid": ee.to_pid(g),
            "modality": "PHOTO",
            "type": "GALLERY"
        })
    for q in query_files:
        manifest_records.append({
            "filepath": q,
            "filename": os.path.basename(q),
            "pid": ee.to_pid(q),
            "modality": "SKETCH",
            "type": "QUERY"
        })

    manifest_csv = os.path.join(out_dir, "dataset_manifest.csv")
    with open(manifest_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=manifest_records[0].keys())
        writer.writeheader()
        writer.writerows(manifest_records)

    # 2. Extract feature embeddings
    gallery_data = []
    for g in gallery_files:
        c = app._cache.get(os.path.basename(g)) or app._cache.get(os.path.relpath(g, gallery_dir))
        if not c:
            for k, v in app._cache.items():
                if os.path.basename(k) == os.path.basename(g):
                    c = v
                    break
        if c and c.get("face") is not None:
            g_emb = c["face"] / (np.linalg.norm(c["face"]) + 1e-10)
            g_hog = c.get("hog")
            if g_hog is not None:
                g_hog = g_hog / (np.linalg.norm(g_hog) + 1e-10)
            gallery_data.append({
                "path": g,
                "pid": ee.to_pid(g),
                "emb": g_emb,
                "hog": g_hog
            })

    queries_data = []
    for q in query_files:
        q_pid = ee.to_pid(q)
        try:
            with open(q, "rb") as fh:
                raw = fh.read()
            emb = app.embed_image(raw)
            hog = app.compute_hog(app.hog_grey(raw))
            if emb is not None:
                queries_data.append({
                    "path": q,
                    "pid": q_pid,
                    "emb": emb / (np.linalg.norm(emb) + 1e-10),
                    "hog": hog / (np.linalg.norm(hog) + 1e-10) if hog is not None else None
                })
        except Exception:
            continue

    # 3. Evaluate Authoritative Metrics
    per_query_records = []
    failure_records = []
    rank1, rank5, rank10 = 0, 0, 0
    mrr_sum = 0.0

    for q in queries_data:
        scores = []
        for g in gallery_data:
            deep_sim = float(np.dot(q["emb"], g["emb"]))
            if q["hog"] is not None and g["hog"] is not None:
                hog_sim = float(np.dot(q["hog"], g["hog"]))
            else:
                hog_sim = 0.0

            fused_sim = app.FACE_WEIGHT * deep_sim + (1.0 - app.FACE_WEIGHT) * hog_sim
            scores.append((fused_sim, g["pid"], g["path"]))

        scores.sort(key=lambda x: x[0], reverse=True)
        top1_match_pid = scores[0][1]
        top1_match_path = scores[0][2]
        top1_score = round(scores[0][0], 4)

        rank = None
        for r_idx, (s, g_pid, g_path) in enumerate(scores):
            if g_pid == q["pid"]:
                rank = r_idx + 1
                break

        if rank is not None:
            mrr_sum += 1.0 / rank
            if rank == 1:
                rank1 += 1
            if rank <= 5:
                rank5 += 1
            if rank <= 10:
                rank10 += 1

        rec = {
            "query_filename": os.path.basename(q["path"]),
            "ground_truth_pid": q["pid"],
            "rank": rank if rank is not None else "NOT_FOUND",
            "top1_matched_pid": top1_match_pid,
            "top1_matched_filename": os.path.basename(top1_match_path),
            "top1_score": top1_score,
            "status": "CORRECT" if rank == 1 else "FAILED"
        }
        per_query_records.append(rec)

        if rank != 1:
            failure_records.append({
                "query_filename": os.path.basename(q["path"]),
                "ground_truth_pid": q["pid"],
                "actual_rank": rank,
                "top1_incorrect_match": os.path.basename(top1_match_path),
                "top1_incorrect_pid": top1_match_pid,
                "incorrect_score": top1_score,
                "failure_category": "CROSS_MODAL_DOMAIN_GAP" if rank and rank <= 10 else "HIGH_NOISE_OR_DISTORTION"
            })

    N = len(queries_data)
    authoritative_metrics = {
        "timestamp": "2026-08-25T12:32:00+05:30",
        "evaluator_name": "Authoritative_Single_Evaluator",
        "total_queries_evaluated": N,
        "gallery_candidates_count": len(gallery_data),
        "rank1_hits": f"{rank1}/{N}",
        "rank1_accuracy_pct": round(rank1 / N * 100.0, 2) if N else 0.0,
        "rank5_hits": f"{rank5}/{N}",
        "rank5_accuracy_pct": round(rank5 / N * 100.0, 2) if N else 0.0,
        "rank10_hits": f"{rank10}/{N}",
        "rank10_accuracy_pct": round(rank10 / N * 100.0, 2) if N else 0.0,
        "mrr": round(mrr_sum / N, 4) if N else 0.0
    }

    # Save Authoritative Metrics JSON
    with open(os.path.join(out_dir, "authoritative_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(authoritative_metrics, f, indent=2)

    # Save per_query_results.csv
    with open(os.path.join(out_dir, "per_query_results.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=per_query_records[0].keys())
        writer.writeheader()
        writer.writerows(per_query_records)

    # Save failure_cases.csv
    with open(os.path.join(out_dir, "failure_cases.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=failure_records[0].keys())
        writer.writeheader()
        writer.writerows(failure_records)

    print(f"Authoritative evaluation completed: {authoritative_metrics['rank1_hits']} ({authoritative_metrics['rank1_accuracy_pct']}%) Rank-1.")
    print(json.dumps(authoritative_metrics, indent=2))

if __name__ == "__main__":
    main()
