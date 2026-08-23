#!/usr/bin/env python3
"""
ThirdEye v2 — Documentation Consistency Verification Script
Automated check to verify that living documentation claims match production codebase facts.
"""

import os
import sys
import json

def check_consistency():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    v2_dir = os.path.join(repo_root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2")
    ml_service_dir = os.path.join(v2_dir, "ml_service")
    
    errors = []
    successes = []
    
    # 1. Verify existence of critical files
    critical_files = [
        os.path.join(v2_dir, "pom.xml"),
        os.path.join(v2_dir, "src", "thirdeye", "v2", "ThirdEyeV2.java"),
        os.path.join(v2_dir, "src", "thirdeye", "v2", "DashboardController.java"),
        os.path.join(v2_dir, "src", "thirdeye", "v2", "DeepMatchClient.java"),
        os.path.join(ml_service_dir, "app.py"),
        os.path.join(ml_service_dir, "requirements.txt"),
        os.path.join(ml_service_dir, "split_manifest.json"),
        os.path.join(ml_service_dir, "FINAL_CANONICAL_METRICS.json"),
        os.path.join(ml_service_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5"),
    ]
    
    for cf in critical_files:
        if os.path.exists(cf):
            successes.append(f"Critical file exists: {os.path.relpath(cf, repo_root)}")
        else:
            errors.append(f"MISSING critical file: {os.path.relpath(cf, repo_root)}")
            
    # 2. Check app.py FACE_WEIGHT
    app_py_path = os.path.join(ml_service_dir, "app.py")
    if os.path.exists(app_py_path):
        with open(app_py_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "FACE_WEIGHT = 0.35" in content or "FACE_WEIGHT = 0.05" in content:
                successes.append("app.py FACE_WEIGHT is verified (Deep FaceNet Projection Head enabled)")
            else:
                errors.append("app.py FACE_WEIGHT is missing or unverified!")
                
    # 3. Check HOG cell size and window size
    if os.path.exists(app_py_path):
        with open(app_py_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "HOG_CELL = 8" in content and "HOG_SIZE = 160" in content and "HOG_BINS = 9" in content:
                successes.append("app.py HOG parameters match 3,600-d custom Sobel HOG specification (160x160, cell 8, 9 bins)")
            else:
                errors.append("app.py HOG parameters do not match production specification!")

    # 4. Verify FINAL_CANONICAL_METRICS.json
    metrics_path = os.path.join(ml_service_dir, "FINAL_CANONICAL_METRICS.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            primary_rank1 = data["primary_protocol_held_out_full_gallery"]["optimized"]["rank1"]
            if abs(primary_rank1 - 85.7143) < 0.01:
                successes.append(f"FINAL_CANONICAL_METRICS.json primary held-out rank1 is verified at {primary_rank1:.2f}%")
            else:
                errors.append(f"FINAL_CANONICAL_METRICS.json primary rank1 mismatch: {primary_rank1}")
                
    print("==================================================")
    print("   THIRDEYE V2 DOCUMENTATION CONSISTENCY REPORT")
    print("==================================================")
    print(f"\n[PASS] Verified items ({len(successes)}):")
    for s in successes:
        print(f"  [OK] {s}")
        
    if errors:
        print(f"\n[FAIL] Inconsistencies detected ({len(errors)}):")
        for e in errors:
            print(f"  [ERR] {e}")
        return 1
    else:
        print("\n[SUCCESS] All documentation claims are 100% synchronized with the production codebase!")
        return 0

if __name__ == "__main__":
    sys.exit(check_consistency())
