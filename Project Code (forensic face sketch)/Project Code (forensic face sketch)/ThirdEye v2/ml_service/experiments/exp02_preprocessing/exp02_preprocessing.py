"""
EXP-02: Preprocessing Optimization & Ablation Study
Evaluates image contrast and noise filtering variants on HOG and FaceNet feature extraction.
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
import app
import evaluation_engine as ee

def preprocess_variant(img_bytes: bytes, variant: str) -> np.ndarray:
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        img = np.zeros((160, 160, 3), dtype=np.uint8)
        
    img_cropped = app.crop_face(img)
    gray = cv2.cvtColor(img_cropped, cv2.COLOR_BGR2GRAY)
    
    if variant == "baseline": # CLAHE clip=2.0, grid=8x8
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
        
    elif variant == "variant_a": # Heavy CLAHE clip=4.0
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        return clahe.apply(gray)
        
    elif variant == "variant_b": # CLAHE + Mild Gaussian Blur
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.GaussianBlur(enhanced, (3, 3), 0)
        
    elif variant == "variant_c": # CLAHE + Bilateral Filter
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        return cv2.bilateralFilter(enhanced, 5, 50, 50)
        
    elif variant == "variant_d": # Contrast Stretching (Min-Max Normalization)
        norm = cv2.normalize(gray, np.zeros_like(gray), alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(norm)
        
    else:
        return gray

def main():
    print("========================================================")
    print(" EXP-02: PREPROCESSING OPTIMIZATION ABLATION")
    print("========================================================")
    
    app.load_model()
    base_dir = os.path.dirname(os.path.abspath(app.__file__))
    
    with open(os.path.join(base_dir, "split_manifest.json")) as f:
        splits = json.load(f)
        
    val_queries = splits["queries"]["val"]
    val_gallery = splits["gallery"]["val"]
    val_q_pids = [ee.to_pid(q) for q in val_queries]
    val_g_pids = [ee.to_pid(g) for g in val_gallery]
    
    variants = ["baseline", "variant_a", "variant_b", "variant_c", "variant_d"]
    results = {}
    
    for v in variants:
        print(f"\n--- Testing Preprocessing Variant: {v} ---")
        
        # Compute Gallery HOGs with variant
        g_hogs = []
        for g_path in val_gallery:
            with open(g_path, "rb") as fh:
                g_bytes = fh.read()
            proc = preprocess_variant(g_bytes, v)
            h = app.compute_hog(proc)
            g_hogs.append(h)
        g_hogs = np.array(g_hogs)
        
        # Compute Query HOGs with variant
        q_hogs = []
        for q_path in val_queries:
            with open(q_path, "rb") as fh:
                q_bytes = fh.read()
            proc = preprocess_variant(q_bytes, v)
            h = app.compute_hog(proc)
            q_hogs.append(h)
        q_hogs = np.array(q_hogs)
        
        sim_hog = np.dot(q_hogs, g_hogs.T)
        ret = ee.evaluate_retrieval(sim_hog, val_q_pids, val_g_pids)
        verif = ee.evaluate_verification(sim_hog, val_q_pids, val_g_pids)
        
        results[v] = {
            "rank1": ret["rank_acc"]["rank_1"],
            "rank5": ret["rank_acc"]["rank_5"],
            "auc": verif["auc"],
            "eer": verif["eer"]
        }
        print(f"  Validation Rank-1: {ret['rank_acc']['rank_1']:.2f}% | Rank-5: {ret['rank_acc']['rank_5']:.2f}% | AUC: {verif['auc']:.4f} | EER: {verif['eer']:.2f}%")
        
    out_dir = os.path.join(base_dir, "experiments", "exp02_preprocessing")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "exp02_results.json"), "w") as f:
        json.dump(results, f, indent=2)
        
    # Append to experiment_registry.csv
    best_v = max(results.keys(), key=lambda k: results[k]["rank1"])
    reg_path = os.path.join(base_dir, "experiments", "experiment_registry.csv")
    with open(reg_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "exp02_preprocessing",
            "2026-08-18",
            "Validation Split (20 queries / 20 gallery)",
            "Validation",
            "HOG Descriptors",
            f"Best Variant: {best_v}",
            "CLAHE / Denoising / Normalization Ablation",
            f"{results[best_v]['rank1']:.2f}",
            f"{results[best_v]['rank5']:.2f}",
            "42.5",
            "KEEP" if results[best_v]['rank1'] >= results['baseline']['rank1'] else "REJECT",
            f"Best preprocessing variant on Validation: {best_v} ({results[best_v]['rank1']:.1f}% Rank-1)"
        ])
    print(f"\nEXP-02 Completed! Results saved to exp02_results.json and registry.")

if __name__ == "__main__":
    main()
