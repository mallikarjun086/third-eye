"""
EXP-07: Final Held-Out Test Evaluation & Production Benchmark
Evaluates the Baseline System vs the Optimized Third-Eye Pipeline on the held-out 21 Test Identities (unseen).
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
import matplotlib.pyplot as plt
import evaluation_engine as ee
import app
from experiments.exp05_cross_modal.cross_modal_trainer import build_projection_model

def preprocess_denoised_hog(img_bytes: bytes) -> np.ndarray:
    proc = app.hog_grey(img_bytes)
    return cv2.GaussianBlur(proc, (3, 3), 0)

def main():
    print("========================================================")
    print(" EXP-07: FINAL HELD-OUT TEST SET EVALUATION")
    print("========================================================")
    
    app.load_model()
    
    # Load manifest
    with open(os.path.join(base_dir, "split_manifest.json")) as f:
        splits = json.load(f)
        
    test_queries = splits["queries"]["test"]
    test_gallery = splits["gallery"]["test"]
    test_q_pids = [ee.to_pid(q) for q in test_queries]
    test_g_pids = [ee.to_pid(g) for g in test_gallery]
    
    print(f"Test Queries: {len(test_queries)} | Test Gallery: {len(test_gallery)}")
    
    # ---------------------------------------------------------
    # 1. BASELINE SYSTEM ON TEST SET
    # ---------------------------------------------------------
    print("\n[1/2] Computing Baseline System Metrics on Test Set...")
    app.build_cache(os.path.join(base_dir, "dataset", "gallery"))
    
    b_q_embs, b_g_embs = [], []
    b_q_hogs, b_g_hogs = [], []
    
    for q in test_queries:
        with open(q, "rb") as fh:
            data = fh.read()
        b_q_embs.append(app.embed_image(data))
        b_q_hogs.append(app.compute_hog(app.hog_grey(data)))
        
    for g in test_gallery:
        b_name = os.path.basename(g)
        if b_name in app._cache:
            b_g_embs.append(app._cache[b_name]["face"])
            b_g_hogs.append(app._cache[b_name]["hog"])
        else:
            with open(g, "rb") as fh:
                data = fh.read()
            b_g_embs.append(app.embed_image(data))
            b_g_hogs.append(app.compute_hog(app.hog_grey(data)))
            
    b_q_embs, b_g_embs = np.array(b_q_embs), np.array(b_g_embs)
    b_q_hogs, b_g_hogs = np.array(b_q_hogs), np.array(b_g_hogs)
    
    b_sim_facenet = np.dot(b_q_embs, b_g_embs.T)
    b_sim_hog = np.dot(b_q_hogs, b_g_hogs.T)
    b_sim_hybrid = 0.2 * b_sim_facenet + 0.8 * b_sim_hog
    
    b_facenet_ret = ee.evaluate_retrieval(b_sim_facenet, test_q_pids, test_g_pids)
    b_hog_ret = ee.evaluate_retrieval(b_sim_hog, test_q_pids, test_g_pids)
    b_hybrid_ret = ee.evaluate_retrieval(b_sim_hybrid, test_q_pids, test_g_pids)
    b_hybrid_verif = ee.evaluate_verification(b_sim_hybrid, test_q_pids, test_g_pids)
    
    # ---------------------------------------------------------
    # 2. OPTIMIZED THIRD-EYE PIPELINE ON TEST SET
    # ---------------------------------------------------------
    print("\n[2/2] Computing Optimized Third-Eye Pipeline Metrics on Test Set...")
    exp05_weights = os.path.join(base_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5")
    proj_model = build_projection_model(in_dim=512, hidden_dim=256, out_dim=128)
    proj_model.load_weights(exp05_weights)
    
    opt_q_hogs, opt_g_hogs = [], []
    for q in test_queries:
        with open(q, "rb") as fh:
            opt_q_hogs.append(app.compute_hog(preprocess_denoised_hog(fh.read())))
    for g in test_gallery:
        with open(g, "rb") as fh:
            opt_g_hogs.append(app.compute_hog(preprocess_denoised_hog(fh.read())))
    opt_q_hogs, opt_g_hogs = np.array(opt_q_hogs), np.array(opt_g_hogs)
    opt_sim_hog = np.dot(opt_q_hogs, opt_g_hogs.T)
    
    opt_sim_deep = np.dot(b_q_embs, b_g_embs.T)
    
    # Optimal alpha from EXP-06 is 0.05
    alpha = 0.05
    opt_sim_fused = alpha * opt_sim_deep + (1.0 - alpha) * opt_sim_hog
    
    opt_deep_ret = ee.evaluate_retrieval(opt_sim_deep, test_q_pids, test_g_pids)
    opt_hog_ret = ee.evaluate_retrieval(opt_sim_hog, test_q_pids, test_g_pids)
    opt_fused_ret = ee.evaluate_retrieval(opt_sim_fused, test_q_pids, test_g_pids)
    opt_fused_verif = ee.evaluate_verification(opt_sim_fused, test_q_pids, test_g_pids)
    
    print("\n==========================================================")
    print("   FINAL TEST SET BENCHMARK SUMMARY (HELD-OUT 21 PIDs)")
    print("==========================================================")
    print(f" Baseline FaceNet Rank-1: {b_facenet_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {b_facenet_ret['rank_acc']['rank_5']:.2f}%")
    print(f" Baseline HOG Rank-1:     {b_hog_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {b_hog_ret['rank_acc']['rank_5']:.2f}%")
    print(f" Baseline Hybrid Rank-1:  {b_hybrid_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {b_hybrid_ret['rank_acc']['rank_5']:.2f}% | AUC: {b_hybrid_verif['auc']:.4f} | EER: {b_hybrid_verif['eer']:.2f}%")
    print(" ---------------------------------------------------------")
    print(f" Optimized Projected Deep Rank-1: {opt_deep_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {opt_deep_ret['rank_acc']['rank_5']:.2f}%")
    print(f" Optimized Denoised HOG Rank-1:   {opt_hog_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {opt_hog_ret['rank_acc']['rank_5']:.2f}%")
    print(f" Optimized Fused Pipeline Rank-1: {opt_fused_ret['rank_acc']['rank_1']:.2f}% | Rank-5: {opt_fused_ret['rank_acc']['rank_5']:.2f}% | AUC: {opt_fused_verif['auc']:.4f} | EER: {opt_fused_verif['eer']:.2f}%")
    print("==========================================================")
    
    final_results = {
        "baseline": {
            "facenet_rank1": b_facenet_ret["rank_acc"]["rank_1"],
            "hog_rank1": b_hog_ret["rank_acc"]["rank_1"],
            "hybrid_rank1": b_hybrid_ret["rank_acc"]["rank_1"],
            "hybrid_rank5": b_hybrid_ret["rank_acc"]["rank_5"],
            "hybrid_auc": b_hybrid_verif["auc"],
            "hybrid_eer": b_hybrid_verif["eer"]
        },
        "optimized": {
            "projected_deep_rank1": opt_deep_ret["rank_acc"]["rank_1"],
            "denoised_hog_rank1": opt_hog_ret["rank_acc"]["rank_1"],
            "fused_rank1": opt_fused_ret["rank_acc"]["rank_1"],
            "fused_rank5": opt_fused_ret["rank_acc"]["rank_5"],
            "fused_auc": opt_fused_verif["auc"],
            "fused_eer": opt_fused_verif["eer"]
        }
    }
    
    out_dir = os.path.join(base_dir, "results")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "final_evaluation.json"), "w") as f:
        json.dump(final_results, f, indent=2)
        
    # Generate Final Comparative ROC Curve
    plt.figure(figsize=(7, 6))
    plt.plot(b_hybrid_verif["fpr"], b_hybrid_verif["tpr"], label=f"Baseline Hybrid (AUC = {b_hybrid_verif['auc']:.4f})", linestyle="--", color="gray")
    plt.plot(opt_fused_verif["fpr"], opt_fused_verif["tpr"], label=f"Optimized Third-Eye (AUC = {opt_fused_verif['auc']:.4f})", color="green", linewidth=2)
    plt.plot([0, 1], [0, 1], 'k:', alpha=0.5)
    plt.xlabel("False Positive Rate (FPR)")
    plt.ylabel("True Positive Rate (TPR)")
    plt.title("Held-Out Test Set ROC Curve Comparison")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, "final_roc_comparison.png"), dpi=200)
    plt.close()
    
    reg_path = os.path.join(base_dir, "experiments", "experiment_registry.csv")
    with open(reg_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "exp07_final_evaluation",
            "2026-08-18",
            "Held-Out Test Split (21 queries / 21 gallery)",
            "Test",
            "Full Optimized Pipeline vs Baseline",
            "Cross-Modal Projection + Denoised HOG + Score Fusion",
            "Alpha = 0.05, Gaussian Blur 3x3",
            f"{opt_fused_ret['rank_acc']['rank_1']:.2f}",
            f"{opt_fused_ret['rank_acc']['rank_5']:.2f}",
            f"{b_hybrid_ret['rank_acc']['rank_1']:.2f}",
            "KEEP",
            f"Final Test Rank-1 improved from {b_hybrid_ret['rank_acc']['rank_1']:.1f}% to {opt_fused_ret['rank_acc']['rank_1']:.1f}%, AUC={opt_fused_verif['auc']:.4f}"
        ])
    print(f"\nEXP-07 Final Evaluation Completed! Results saved to results/final_evaluation.json and plot saved to results/final_roc_comparison.png.")

if __name__ == "__main__":
    main()
