import os
import json
from .dataset_loader import DatasetLoader
from .dataset_validator import DatasetValidator
from .leakage_audit import LeakageAudit

def build_all_manifests(ml_service_dir):
    loader = DatasetLoader(ml_service_dir)
    records = loader.load_all_records()
    valid_records = []

    for rec in records:
        valid, msg = DatasetValidator.validate_image(rec["image_path"])
        if valid:
            rec["checksum_sha256"] = DatasetValidator.compute_sha256(rec["image_path"])
            valid_records.append(rec)

    manifest_path = os.path.join(ml_service_dir, "dataset_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(valid_records, f, indent=2)

    return len(valid_records)
