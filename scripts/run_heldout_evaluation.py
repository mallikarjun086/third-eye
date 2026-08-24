import os
import sys
import json
import time
import numpy as np

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

import app
import evaluation_engine as ee

def main():
    app.load_model()
    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    queries_dir = os.path.join(ML_SERVICE, "dataset", "queries")
    
    app.build_cache(gallery_dir, force=True)
    
    with open(os.path.join(ML_SERVICE, "split_manifest.json")) as f:
        splits = json.load(f)
        
    test_pids = set(splits["test_pids"])
    distractor_pids = set(splits.get("distractor_pids", []))
    
    test_query_files = [os.path.join(queries_dir, f) for f in os.listdir(queries_dir) 
                        if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS and ee.to_pid(f) in test_pids]
                        
    gallery_files = [os.path.join(gallery_dir, f) for f in os.listdir(gallery_dir) 
                      if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS]
                      
    test_q_pids = [ee.to_pid(f) for f in test_query_files]
    g_pids = [ee.to_pid(f) for f in gallery_files]
    
    # 1. Evaluate Current Fused Model
    t0 = time.time()
    scores = []
    latencies = []
    
    for q in test_query_files:
        with open(q, "rb") as fh:
            raw = fh.read()
        t_start = time.time()
        sketch_grey = app.hog_grey(raw)
        sketch_emb = app.embed_image(raw)
        sketch_hog = app.compute_hog(sketch_grey)
        
        q_scores = []
        for rel, feats in app._cache.items():
            face_sim = float(np.dot(sketch_emb, feats["face"]))
            hog_sim = float(np.dot(sketch_hog, feats["hog"]))
            fused = app.hybrid_score(face_sim, hog_sim)
            q_scores.append(fused)
            
        latencies.append((time.time() - t_start) * 1000.0)
        scores.append(q_scores)
        
    score_matrix = np.array(scores)
    
    ret_metrics = ee.evaluate_retrieval(score_matrix, test_q_pids, g_pids)
    verif_metrics = ee.evaluate_verification(score_matrix, test_q_pids, g_pids)
    
    results = {
        "dataset": "CUFS Held-Out Test Set",
        "query_count": len(test_query_files),
        "gallery_size": len(gallery_files),
        "rank_1": ret_metrics["rank_acc"]["rank_1"],
        "rank_5": ret_metrics["rank_acc"]["rank_5"],
        "rank_10": ret_metrics["rank_acc"]["rank_10"],
        "mrr": ret_metrics["mrr"],
        "auc": verif_metrics["auc"],
        "eer": verif_metrics["eer"],
        "median_latency_ms": float(np.median(latencies)),
        "mean_latency_ms": float(np.mean(latencies))
    }
    
    res_path = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "HELDOUT_EVALUATION_RESULTS.json")
    os.makedirs(os.path.dirname(res_path), exist_ok=True)
    with open(res_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print("Held-Out Evaluation Completed!")
    print(f"Rank-1: {results['rank_1']:.2f}% | Rank-5: {results['rank_5']:.2f}% | AUC: {results['auc']:.4f} | Latency: {results['median_latency_ms']:.1f}ms")

if __name__ == "__main__":
    main()
