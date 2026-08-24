import os
import json

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
SPLIT_MANIFEST = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "split_manifest.json")
REPORT_OUT = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "DATA_LEAKAGE_AUDIT.md")

def main():
    with open(SPLIT_MANIFEST, "r") as f:
        splits = json.load(f)
        
    train_pids = set(splits.get("train_pids", []))
    val_pids = set(splits.get("val_pids", []))
    test_pids = set(splits.get("test_pids", []))
    
    tv_overlap = train_pids.intersection(val_pids)
    tt_overlap = train_pids.intersection(test_pids)
    vt_overlap = val_pids.intersection(test_pids)
    
    total_leakage = len(tv_overlap) + len(tt_overlap) + len(vt_overlap)
    
    os.makedirs(os.path.dirname(REPORT_OUT), exist_ok=True)
    with open(REPORT_OUT, "w", encoding="utf-8") as f:
        f.write("# DATA LEAKAGE & IDENTITY DISJOINTNESS AUDIT REPORT\n\n")
        f.write("**Audit Timestamp**: August 24, 2026  \n")
        f.write("**Auditor**: Lead Machine Learning Engineer & Technical Auditor  \n\n")
        f.write("---\n\n")
        f.write("## 1. IDENTITY SPLIT VERIFICATION\n\n")
        f.write(f"* **Train PIDs Count**: **{len(train_pids)}**  \n")
        f.write(f"* **Validation PIDs Count**: **{len(val_pids)}**  \n")
        f.write(f"* **Held-Out Test PIDs Count**: **{len(test_pids)}**  \n")
        f.write(f"* **Train ∩ Validation Overlap**: **{len(tv_overlap)}**  \n")
        f.write(f"* **Train ∩ Test Overlap**: **{len(tt_overlap)}**  \n")
        f.write(f"* **Validation ∩ Test Overlap**: **{len(vt_overlap)}**  \n\n")
        f.write("## 2. AUDIT VERDICT\n\n")
        if total_leakage == 0:
            f.write("> **VERDICT: PASSED (ZERO IDENTITY LEAKAGE)**  \n")
            f.write("> All training, validation, and held-out test sets are strictly identity-disjoint. Models trained on `train_pids` have zero prior exposure to validation or held-out test identities.\n")
        else:
            f.write(f"> **VERDICT: FAILED ({total_leakage} IDENTITY OVERLAPS DETECTED)**  \n")
            
    print(f"Leakage audit written to {REPORT_OUT} (Leakage: {total_leakage})")

if __name__ == "__main__":
    main()
