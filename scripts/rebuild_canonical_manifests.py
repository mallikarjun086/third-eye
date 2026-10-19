#!/usr/bin/env python3
"""
Rebuild Canonical Manifests with Defect-Free Identity Parsing
Uses the corrected evaluation_engine.to_pid() to eliminate substring replacement bugs.
"""
import os
import sys
import json
import hashlib

WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

import importlib.util

_engine_path = os.path.join(ML_SERVICE, "evaluation_engine.py")
_spec = importlib.util.spec_from_file_location("evaluation_engine", _engine_path)
if _spec and _spec.loader:
    _ee = importlib.util.module_from_spec(_spec)
    sys.modules["evaluation_engine"] = _ee
    _spec.loader.exec_module(_ee)
    to_pid = _ee.to_pid
else:
    import re
    def to_pid(name: str) -> str:
        base = os.path.splitext(os.path.basename(name))[0].lower()
        base = re.sub(r'(-01)?(-sz\d+)?$', '', base)
        base = re.sub(r'(-\d+)?$', '', base)
        base = re.sub(r'(_\d+)?$', '', base)
        if base.startswith("f2-"):
            base = "f-" + base[3:]
        elif base.startswith("m2-"):
            base = "m-" + base[3:]
        return base

def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    queries_dir = os.path.join(ML_SERVICE, "dataset", "queries")
    valid_exts = {".jpg", ".jpeg", ".png", ".webp"}

    gallery_files = sorted([f for f in os.listdir(gallery_dir) if os.path.splitext(f)[1].lower() in valid_exts])
    query_files = sorted([f for f in os.listdir(queries_dir) if os.path.splitext(f)[1].lower() in valid_exts])

    print(f"Auditing {len(gallery_files)} gallery files and {len(query_files)} query files...")

    # Build gallery manifest
    gallery_manifest = []
    for f in gallery_files:
        full_p = os.path.join(gallery_dir, f)
        pid = to_pid(f)
        gallery_manifest.append({
            "identity_id": pid,
            "image_filename": f,
            "sha256": sha256_file(full_p),
            "modality": "PHOTO",
            "source_dataset": "CUFS" if not f.startswith(("m_", "f_")) else "EXTENDED_INDIAN"
        })

    gal_out = os.path.join(WORKSPACE, "gallery_manifest.json")
    with open(gal_out, "w", encoding="utf-8") as f:
        json.dump(gallery_manifest, f, indent=2)
    print(f"[OK] Wrote {len(gallery_manifest)} gallery records to {gal_out}")

    # Re-verify train / val / test splits
    # Load existing manifests and update any mangled pids
    for split_name, manifest_file in [("TRAIN", "train_manifest.json"), ("VAL", "validation_manifest.json"), ("TEST", "test_manifest.json")]:
        man_path = os.path.join(WORKSPACE, manifest_file)
        if os.path.exists(man_path):
            with open(man_path, "r", encoding="utf-8") as mf:
                records = json.load(mf)
            fixed_records = []
            for r in records:
                old_pid = r["pid"]
                new_pid = to_pid(old_pid)
                fixed_records.append({"pid": new_pid, "split": split_name})
            # Sort uniquely
            fixed_records.sort(key=lambda x: x["pid"])
            with open(man_path, "w", encoding="utf-8") as mf:
                json.dump(fixed_records, mf, indent=2)
            print(f"[OK] Normalized {len(fixed_records)} records in {manifest_file}")

if __name__ == "__main__":
    main()
