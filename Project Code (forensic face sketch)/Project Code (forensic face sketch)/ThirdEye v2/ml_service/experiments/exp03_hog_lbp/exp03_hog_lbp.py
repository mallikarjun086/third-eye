"""
EXP-03: HOG & LBP Descriptor Optimization
Evaluates multi-scale HOG cell sizes, orientation bins, and Local Binary Patterns (LBP).
"""
import os
import sys

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

import csv
import json
import cv2
import numpy as np
import evaluation_engine as ee
import app

def compute_lbp(gray_img: np.ndarray, P: int = 8, R: int = 1) -> np.ndarray:
    """Computes a basic 256-bin LBP histogram over grayscale image."""
    h, w = gray_img.shape
    lbp_map = np.zeros((h - 2, w - 2), dtype=np.uint8)
    center = gray_img[1:-1, 1:-1]
    
    # 8 neighbors
    offsets = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    for bit_idx, (dy, dx) in enumerate(offsets):
        neighbor = gray_img[1+dy : h-1+dy, 1+dx : w-1+dx]
        lbp_map |= ((neighbor >= center).astype(np.uint8) << bit_idx)
        
    hist, _ = np.histogram(lbp_map.ravel(), bins=256, range=(0, 256))
    hist = hist.astype(np.float32)
    norm = np.linalg.norm(hist)
    if norm > 0:
        hist /= norm
    return hist

def compute_custom_hog(gray_img: np.ndarray, cell_size: int = 8, orientations: int = 8) -> np.ndarray:
    if gray_img.dtype != np.uint8:
        gray_img = gray_img.astype(np.uint8)
    hog_obj = cv2.HOGDescriptor(
        _winSize=(160, 160),
        _blockSize=(cell_size * 2, cell_size * 2),
        _blockStride=(cell_size, cell_size),
        _cellSize=(cell_size, cell_size),
        _nbins=orientations
    )
    feat = hog_obj.compute(gray_img)
    if feat is None:
        return np.zeros(3600, dtype=np.float32)
    feat = feat.ravel()
    norm = np.linalg.norm(feat)
    if norm > 0:
        feat /= norm
    return feat

def main():
    print("========================================================")
    print(" EXP-03: HOG & LBP DESCRIPTOR OPTIMIZATION")
    print("========================================================")
    
    app.load_model()
    
    with open(os.path.join(base_dir, "split_manifest.json")) as f:
        splits = json.load(f)
        
    val_queries = splits["queries"]["val"]
    val_gallery = splits["gallery"]["val"]
    val_q_pids = [ee.to_pid(q) for q in val_queries]
    val_g_pids = [ee.to_pid(g) for g in val_gallery]
    
    configs = {
        "hog_8x8_baseline": lambda img: compute_custom_hog(img, cell_size=8, orientations=8),
        "hog_10x10": lambda img: compute_custom_hog(img, cell_size=10, orientations=8),
        "hog_16x16": lambda img: compute_custom_hog(img, cell_size=16, orientations=8),
        "hog_orient_12": lambda img: compute_custom_hog(img, cell_size=8, orientations=12),
        "multiscale_hog": lambda img: np.concatenate([
            compute_custom_hog(img, cell_size=8, orientations=8),
            compute_custom_hog(img, cell_size=16, orientations=8)
        ]),
        "lbp_only": lambda img: compute_lbp(img),
        "hog_plus_lbp": lambda img: np.concatenate([
            compute_custom_hog(img, cell_size=8, orientations=8),
            compute_lbp(img)
        ])
    }
    
    results = {}
    
    for cfg_name, feat_fn in configs.items():
        print(f"\n--- Evaluating Config: {cfg_name} ---")
        
        g_feats = []
        for g_path in val_gallery:
            with open(g_path, "rb") as fh:
                g_bytes = fh.read()
            proc = app.hog_grey(g_bytes)
            f_vec = feat_fn(proc)
            norm = np.linalg.norm(f_vec)
            if norm > 0:
                f_vec = f_vec / norm
            g_feats.append(f_vec)
        g_feats = np.array(g_feats)
        
        q_feats = []
        for q_path in val_queries:
            with open(q_path, "rb") as fh:
                q_bytes = fh.read()
            proc = app.hog_grey(q_bytes)
            f_vec = feat_fn(proc)
            norm = np.linalg.norm(f_vec)
            if norm > 0:
                f_vec = f_vec / norm
            q_feats.append(f_vec)
        q_feats = np.array(q_feats)
        
        sim = np.dot(q_feats, g_feats.T)
        ret = ee.evaluate_retrieval(sim, val_q_pids, val_g_pids)
        verif = ee.evaluate_verification(sim, val_q_pids, val_g_pids)
        
        results[cfg_name] = {
            "dim": q_feats.shape[1],
            "rank1": ret["rank_acc"]["rank_1"],
            "rank5": ret["rank_acc"]["rank_5"],
            "auc": verif["auc"],
            "eer": verif["eer"]
        }
        print(f"  Dim: {q_feats.shape[1]} | Rank-1: {ret['rank_acc']['rank_1']:.2f}% | Rank-5: {ret['rank_acc']['rank_5']:.2f}% | AUC: {verif['auc']:.4f} | EER: {verif['eer']:.2f}%")
        
    out_dir = os.path.join(base_dir, "experiments", "exp03_hog_lbp")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "exp03_results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    best_cfg = max(results.keys(), key=lambda k: results[k]["rank1"])
    reg_path = os.path.join(base_dir, "experiments", "experiment_registry.csv")
    with open(reg_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "exp03_hog_lbp",
            "2026-08-18",
            "Validation Split (20 queries / 20 gallery)",
            "Validation",
            f"Best Config: {best_cfg}",
            "CLAHE HOG",
            f"Descriptor Dim = {results[best_cfg]['dim']}",
            f"{results[best_cfg]['rank1']:.2f}",
            f"{results[best_cfg]['rank5']:.2f}",
            "45.0",
            "KEEP" if results[best_cfg]['rank1'] >= results['hog_8x8_baseline']['rank1'] else "REJECT",
            f"Best descriptor config: {best_cfg} ({results[best_cfg]['rank1']:.1f}% Rank-1 on Val)"
        ])
    print(f"\nEXP-03 Completed! Results saved to exp03_results.json and registry.")

if __name__ == "__main__":
    main()
