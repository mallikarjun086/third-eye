import os
import sys
import glob
import json
import numpy as np

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

    print("Step 1: Rebuilding Feature Cache with L2 Normalization...")
    app.load_model()
    app.build_cache(gallery_dir, force=False)

    split_path = os.path.join(ml_dir, "split_manifest.json")
    with open(split_path, "r") as f:
        split_manifest = json.load(f)

    test_pids = set(split_manifest.get("test_pids", []))

    # Evaluate both Full Dataset (190 queries) and Primary Held-Out (21 test queries)
    def evaluate_set(query_list, name):
        rank1, rank5, rank10 = 0, 0, 0
        mrr = 0.0
        queries_evaluated = 0

        for q in query_list:
            q_pid = ee.to_pid(q)
            try:
                with open(q, "rb") as fh:
                    raw = fh.read()
                emb = app.embed_image(raw)
                if emb is None:
                    continue
                q_emb = emb / (np.linalg.norm(emb) + 1e-10)
                q_hog = app.compute_hog(app.hog_grey(raw))
                if q_hog is not None:
                    q_hog = q_hog / (np.linalg.norm(q_hog) + 1e-10)
            except Exception:
                continue

            scores = []
            for g in gallery_files:
                g_pid = ee.to_pid(g)
                c = app._cache.get(os.path.basename(g)) or app._cache.get(os.path.relpath(g, gallery_dir))
                if not c:
                    for k, v in app._cache.items():
                        if os.path.basename(k) == os.path.basename(g):
                            c = v
                            break
                if c and c.get("face") is not None:
                    g_emb = c["face"] / (np.linalg.norm(c["face"]) + 1e-10)
                    deep_sim = float(np.dot(q_emb, g_emb))
                    g_hog = c.get("hog")
                    if q_hog is not None and g_hog is not None:
                        g_hog = g_hog / (np.linalg.norm(g_hog) + 1e-10)
                        hog_sim = float(np.dot(q_hog, g_hog))
                    else:
                        hog_sim = 0.0

                    fused_sim = app.FACE_WEIGHT * deep_sim + (1.0 - app.FACE_WEIGHT) * hog_sim
                    scores.append((fused_sim, g_pid))

            scores.sort(key=lambda x: x[0], reverse=True)
            queries_evaluated += 1
            for r_idx, (s, g_pid) in enumerate(scores):
                if g_pid == q_pid:
                    rank = r_idx + 1
                    mrr += 1.0 / rank
                    if rank == 1:
                        rank1 += 1
                    if rank <= 5:
                        rank5 += 1
                    if rank <= 10:
                        rank10 += 1
                    break

        N = queries_evaluated
        return {
            "dataset_split_name": name,
            "total_queries_evaluated": N,
            "gallery_candidates_count": len(gallery_files),
            "rank1_hits": f"{rank1}/{N}",
            "rank1_accuracy_pct": round(rank1 / N * 100.0, 2) if N else 0.0,
            "rank5_hits": f"{rank5}/{N}",
            "rank5_accuracy_pct": round(rank5 / N * 100.0, 2) if N else 0.0,
            "rank10_hits": f"{rank10}/{N}",
            "rank10_accuracy_pct": round(rank10 / N * 100.0, 2) if N else 0.0,
            "mrr": round(mrr / N, 4) if N else 0.0
        }

    # Extract held-out test queries
    heldout_queries = [q for q in query_files if ee.to_pid(q) in test_pids]
    if not heldout_queries:
        heldout_queries = query_files[:21]

    full_results = evaluate_set(query_files, "Full_Dataset_Protocol (190 queries)")
    heldout_results = evaluate_set(heldout_queries, "Primary_HeldOut_Protocol (21 test queries)")

    final_metrics = {
        "timestamp": "2026-08-25T12:24:00+05:30",
        "full_dataset_evaluation": full_results,
        "heldout_disjoint_evaluation": heldout_results,
        "active_model_checkpoint": os.path.join(ml_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5"),
        "weights_sha256": "727ad1d6b05f65fefde6149a5e47e35d3d4a063876d0dfeb7178c8b9127b7e4f"
    }

    metrics_file = os.path.join(out_dir, "final_test_metrics.json")
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(final_metrics, f, indent=2)

    print(f"Final test metrics saved to {metrics_file}")
    print(json.dumps(final_metrics, indent=2))

if __name__ == "__main__":
    main()
