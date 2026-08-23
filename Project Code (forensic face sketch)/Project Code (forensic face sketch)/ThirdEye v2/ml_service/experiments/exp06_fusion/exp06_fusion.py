"""
EXP-06: Hybrid Score Fusion Optimization
Grid searches fusion weight alpha in [0.0, 1.0] between Projected FaceNet Cosine Similarity and Denoised HOG Cosine Similarity.
"""
import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import json
import csv
import cv2
import numpy as np
import tensorflow as tf
import evaluation_engine as ee
import app
from experiments.exp05_cross_modal.cross_modal_trainer import build_projection_model

def preprocess_denoised_hog(img_bytes: bytes) -> np.ndarray:
    proc = app.hog_grey(img_bytes)
    return cv2.GaussianBlur(proc, (3, 3), 0)

def main():
    print("========================================================")
    print(" EXP-06: HYBRID SCORE FUSION OPTIMIZATION")
    print("========================================================")
    
    app.load_model()
    
    # Load best cross-modal projection model
    exp05_weights = os.path.join(base_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5")
    proj_model = build_projection_model(in_dim=512, hidden_dim=256, out_dim=128)
    proj_model.load_weights(exp05_weights)
    print(f"Loaded trained cross-modal projection weights from {exp05_weights}")
    
    with open(os.path.join(base_dir, "split_manifest.json")) as f:
        splits = json.load(f)
        
    val_queries = splits["queries"]["val"]
    val_gallery = splits["gallery"]["val"]
    val_q_pids = [ee.to_pid(q) for q in val_queries]
    val_g_pids = [ee.to_pid(g) for g in val_gallery]
    
    # Compute Validation Denoised HOG features
    val_q_hogs, val_g_hogs = [], []
    for q in val_queries:
        with open(q, "rb") as fh:
            val_q_hogs.append(app.compute_hog(preprocess_denoised_hog(fh.read())))
    for g in val_gallery:
        with open(g, "rb") as fh:
            val_g_hogs.append(app.compute_hog(preprocess_denoised_hog(fh.read())))
    val_q_hogs = np.array(val_q_hogs)
    val_g_hogs = np.array(val_g_hogs)
    sim_hog = np.dot(val_q_hogs, val_g_hogs.T)
    
    # Compute Validation Deep Projected features
    val_q_embs = []
    for q in val_queries:
        with open(q, "rb") as fh:
            val_q_embs.append(app.embed_image(fh.read()))
    val_g_embs = []
    for g in val_gallery:
        b_name = os.path.basename(g)
        if b_name in app._cache:
            val_g_embs.append(app._cache[b_name]["face"])
        else:
            with open(g, "rb") as fh:
                val_g_embs.append(app.embed_image(fh.read()))
    val_q_embs = np.array(val_q_embs)
    val_g_embs = np.array(val_g_embs)
    
    proj_q = proj_model(tf.convert_to_tensor(val_q_embs, dtype=tf.float32), training=False).numpy()
    proj_g = proj_model(tf.convert_to_tensor(val_g_embs, dtype=tf.float32), training=False).numpy()
    sim_deep = np.dot(proj_q, proj_g.T)
    
    # Grid search alpha in [0.0, 1.0] step 0.05
    best_alpha = 0.0
    best_rank1 = 0.0
    grid_results = {}
    
    print("\n--- GRID SEARCHING FUSION WEIGHT ALPHA ---")
    alphas = np.linspace(0.0, 1.0, 21)
    for alpha in alphas:
        alpha = float(np.round(alpha, 2))
        sim_fused = alpha * sim_deep + (1.0 - alpha) * sim_hog
        
        ret = ee.evaluate_retrieval(sim_fused, val_q_pids, val_g_pids)
        verif = ee.evaluate_verification(sim_fused, val_q_pids, val_g_pids)
        
        r1 = ret["rank_acc"]["rank_1"]
        r5 = ret["rank_acc"]["rank_5"]
        grid_results[str(alpha)] = {
            "rank1": r1,
            "rank5": r5,
            "auc": verif["auc"],
            "eer": verif["eer"]
        }
        print(f"  alpha = {alpha:.2f} | Rank-1: {r1:.2f}% | Rank-5: {r5:.2f}% | AUC: {verif['auc']:.4f} | EER: {verif['eer']:.2f}%")
        
        if r1 > best_rank1 or (r1 == best_rank1 and verif["auc"] > grid_results.get(str(best_alpha), {}).get("auc", 0)):
            best_rank1 = r1
            best_alpha = alpha
            
    print(f"\nOPTIMAL FUSION WEIGHT: alpha* = {best_alpha:.2f} with Validation Rank-1 = {best_rank1:.2f}%")
    
    out_dir = os.path.join(base_dir, "experiments", "exp06_fusion")
    os.makedirs(out_dir, exist_ok=True)
    summary = {
        "best_alpha": best_alpha,
        "best_rank1": best_rank1,
        "best_metrics": grid_results[str(best_alpha)],
        "grid": grid_results
    }
    with open(os.path.join(out_dir, "exp06_results.json"), "w") as f:
        json.dump(summary, f, indent=2)
        
    reg_path = os.path.join(base_dir, "experiments", "experiment_registry.csv")
    with open(reg_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "exp06_fusion",
            "2026-08-18",
            "Validation Split (20 queries / 20 gallery)",
            "Validation",
            "Hybrid Fusion Model",
            f"Alpha Grid Search [0.0 - 1.0]",
            f"Optimal alpha* = {best_alpha:.2f}",
            f"{best_rank1:.2f}",
            f"{grid_results[str(best_alpha)]['rank5']:.2f}",
            "46.3",
            "KEEP" if best_rank1 > 46.3 else "REJECT",
            f"Optimal fusion alpha*={best_alpha:.2f} achieved {best_rank1:.1f}% Rank-1 on Val"
        ])
    print(f"\nEXP-06 Completed! Results saved to exp06_results.json and registry.")

if __name__ == "__main__":
    main()
