import os
import sys
import json
import time
import numpy as np

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

import app

def main():
    app.load_model()
    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    queries_dir = os.path.join(ML_SERVICE, "dataset", "queries")
    
    app.build_cache(gallery_dir)
    
    composite_queries = [
        ("a-sharukh-1.jpg", "a-sharukh"),
        ("a-sharukh-2.jpg", "a-sharukh")
    ]
    
    results = []
    for q_file, target_pid in composite_queries:
        q_path = os.path.join(queries_dir, q_file)
        if not os.path.exists(q_path):
            continue
            
        with open(q_path, "rb") as fh:
            data = fh.read()
            
        t0 = time.time()
        sketch_grey = app.hog_grey(data)
        sketch_emb = app.embed_image(data)
        sketch_hog = app.compute_hog(sketch_grey)
        
        scored = []
        for rel, feats in app._cache.items():
            face_sim = float(np.dot(sketch_emb, feats["face"]))
            hog_sim = float(np.dot(sketch_hog, feats["hog"]))
            sim = app.hybrid_score(face_sim, hog_sim)
            pid = rel.split("-")[0] + "-" + rel.split("-")[1] if "-" in rel else rel.split(".")[0]
            scored.append((sim, rel, pid))
            
        scored.sort(reverse=True, key=lambda x: x[0])
        latency_ms = (time.time() - t0) * 1000.0
        
        target_rank = None
        target_score = 0.0
        for rank_idx, (sim, rel, pid) in enumerate(scored, start=1):
            if pid == target_pid or target_pid in rel:
                target_rank = rank_idx
                target_score = sim
                break
                
        results.append({
            "query_file": q_file,
            "target_pid": target_pid,
            "target_rank": target_rank,
            "target_score_pct": round(target_score * 100.0, 2),
            "top_1_match": scored[0][1],
            "top_1_score_pct": round(scored[0][0] * 100.0, 2),
            "latency_ms": round(latency_ms, 1)
        })
        
    out_path = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "COMPOSITE_BENCHMARK_RESULTS.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
        
    print("Composite Benchmark Completed!")
    for r in results:
        print(f"Query: {r['query_file']} -> Target Rank: #{r['target_rank']} ({r['target_score_pct']}%) | Latency: {r['latency_ms']}ms")

if __name__ == "__main__":
    main()
