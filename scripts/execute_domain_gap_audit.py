import os
import sys
import glob
import json

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

import evaluation_engine as ee

def main():
    print("======================================================================")
    print("PHASE 1 — EXECUTING DATASET & SPLIT AUDIT FOR DOMAIN GAP REPAIR")
    print("======================================================================")

    out_dir = os.path.join(WORKSPACE, "results", "domain_gap_repair")
    os.makedirs(out_dir, exist_ok=True)

    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    queries_dir = os.path.join(ML_SERVICE, "dataset", "queries")

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    gallery_files = sorted([f for f in glob.glob(os.path.join(gallery_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])
    query_files = sorted([f for f in glob.glob(os.path.join(queries_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts])

    g_pids = sorted(list(set(ee.to_pid(f) for f in gallery_files)))
    q_pids = sorted(list(set(ee.to_pid(f) for f in query_files)))

    split_path = os.path.join(ML_SERVICE, "split_manifest.json")
    with open(split_path, "r") as f:
        splits = json.load(f)

    train_pids = set(splits.get("train_pids", []))
    val_pids = set(splits.get("val_pids", []))
    test_pids = set(splits.get("test_pids", []))

    # Check identity leakage across splits
    leak_train_val = len(train_pids.intersection(val_pids))
    leak_train_test = len(train_pids.intersection(test_pids))
    leak_val_test = len(val_pids.intersection(test_pids))

    dataset_audit = {
        "timestamp": "2026-08-25T13:34:00+05:30",
        "primary_cufs_dataset": {
            "gallery_path": gallery_dir,
            "queries_path": queries_dir,
            "gallery_images": len(gallery_files),
            "gallery_unique_pids": len(g_pids),
            "query_images": len(query_files),
            "query_unique_pids": len(q_pids),
            "paired_identities": len(set(g_pids).intersection(q_pids))
        },
        "desktop_archive_dataset": {
            "path": r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive",
            "total_images": 44668,
            "paired_sample_count": 22334
        }
    }

    split_audit = {
        "timestamp": "2026-08-25T13:34:00+05:30",
        "split_manifest_path": split_path,
        "train_pids_count": len(train_pids),
        "val_pids_count": len(val_pids),
        "test_pids_count": len(test_pids),
        "identity_leakage_checks": {
            "train_val_overlap": leak_train_val,
            "train_test_overlap": leak_train_test,
            "val_test_overlap": leak_val_test,
            "is_identity_disjoint": (leak_train_val == 0 and leak_train_test == 0 and leak_val_test == 0)
        }
    }

    with open(os.path.join(out_dir, "dataset_audit.json"), "w", encoding="utf-8") as f:
        json.dump(dataset_audit, f, indent=2)

    with open(os.path.join(out_dir, "split_audit.json"), "w", encoding="utf-8") as f:
        json.dump(split_audit, f, indent=2)

    print(f"Dataset & split audit saved to {out_dir}")
    print(json.dumps(split_audit, indent=2))

if __name__ == "__main__":
    main()
