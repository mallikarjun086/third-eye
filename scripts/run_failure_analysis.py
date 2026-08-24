import os
import sys
import json
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
    
    app.build_cache(gallery_dir)
    
    with open(os.path.join(ML_SERVICE, "split_manifest.json")) as f:
        splits = json.load(f)
        
    test_pids = set(splits["test_pids"])
    
    test_query_files = [os.path.join(queries_dir, f) for f in os.listdir(queries_dir) 
                        if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS and ee.to_pid(f) in test_pids]
                        
    gallery_files = [os.path.join(gallery_dir, f) for f in os.listdir(gallery_dir) 
                      if os.path.splitext(f)[1].lower() in app.IMAGE_EXTS]
                      
    g_pids = [ee.to_pid(f) for f in gallery_files]
    
    failures = []
    
    for q_path in test_query_files:
        q_pid = ee.to_pid(q_path)
        with open(q_path, "rb") as fh:
            raw = fh.read()
            
        sketch_grey = app.hog_grey(raw)
        sketch_emb = app.embed_image(raw)
        sketch_hog = app.compute_hog(sketch_grey)
        
        scored = []
        for rel, feats in app._cache.items():
            face_sim = float(np.dot(sketch_emb, feats["face"]))
            hog_sim = float(np.dot(sketch_hog, feats["hog"]))
            sim = app.hybrid_score(face_sim, hog_sim)
            pid = rel.split("-")[0] + "-" + rel.split("-")[1] if "-" in rel else rel.split(".")[0]
            scored.append((sim, rel, pid, face_sim, hog_sim))
            
        scored.sort(reverse=True, key=lambda x: x[0])
        
        top_1_pid = scored[0][2]
        if top_1_pid != q_pid:
            # Find target rank
            target_rank = None
            for idx, item in enumerate(scored, start=1):
                if item[2] == q_pid:
                    target_rank = idx
                    break
                    
            category = "DOMAIN_GAP" if "f-" in q_pid else "STROKE_GEOMETRY_DISCREPANCY"
            
            failures.append({
                "query_file": os.path.basename(q_path),
                "ground_truth_pid": q_pid,
                "predicted_pid": top_1_pid,
                "target_rank": target_rank,
                "top_1_fused_score": round(scored[0][0], 4),
                "target_fused_score": round(scored[target_rank-1][0], 4) if target_rank else 0.0,
                "target_deep_score": round(scored[target_rank-1][3], 4) if target_rank else 0.0,
                "target_hog_score": round(scored[target_rank-1][4], 4) if target_rank else 0.0,
                "failure_category": category
            })
            
    out_json = os.path.join(ML_SERVICE, "results", "failure_analysis.json")
    os.makedirs(os.path.dirname(out_json), exist_ok=True)
    with open(out_json, "w") as f:
        json.dump(failures, f, indent=2)
        
    out_md = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "FAILURE_ANALYSIS.md")
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# AUTOMATED FAILURE ANALYSIS REPORT\n\n")
        f.write("**Audit Timestamp**: August 24, 2026  \n")
        f.write("**Auditor**: Lead Technical Auditor & Forensic Engineer  \n\n")
        f.write("---\n\n")
        f.write("## 1. MISRANKING FAILURE CASES\n\n")
        f.write("| Query File | Ground-Truth PID | Predicted PID | True Rank | Fused Score | Category |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :--- |\n")
        for fail in failures:
            f.write(f"| `{fail['query_file']}` | `{fail['ground_truth_pid']}` | `{fail['predicted_pid']}` | #{fail['target_rank']} | {fail['target_fused_score']} | `{fail['failure_category']}` |\n")
            
    print(f"Failure analysis completed ({len(failures)} cases written to {out_json} & {out_md})")

if __name__ == "__main__":
    main()
