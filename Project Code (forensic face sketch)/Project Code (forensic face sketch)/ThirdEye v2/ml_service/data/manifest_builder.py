import os
import json
from PIL import Image
from .adapters.cufs_adapter import CUFSAdapter
from .adapters.composite_adapter import CompositeAdapter
from .dataset_validator import DatasetValidator

def build_manifests(ml_service_dir, output_dir):
    cufs = CUFSAdapter(ml_service_dir)
    comp = CompositeAdapter(ml_service_dir)
    
    records = []
    records.extend(cufs.load_manifest())
    records.extend(comp.load_manifest())

    valid_records = []
    for r in records:
        valid, msg = DatasetValidator.validate_image(r["image_path"])
        if valid:
            with Image.open(r["image_path"]) as img:
                w, h = img.size
            r["width"] = w
            r["height"] = h
            r["valid"] = True
            r["checksum"] = DatasetValidator.compute_sha256(r["image_path"])
            valid_records.append(r)

    os.makedirs(output_dir, exist_ok=True)
    manifest_path = os.path.join(output_dir, "dataset_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(valid_records, f, indent=2)

    return len(valid_records)
