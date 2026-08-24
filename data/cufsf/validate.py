import os
import json
import hashlib
from PIL import Image

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_OUT = os.path.join(DATASET_DIR, "dataset_manifest.json")

def validate_cufsf():
    photos_dir = os.path.join(DATASET_DIR, "photos")
    sketches_dir = os.path.join(DATASET_DIR, "sketches")
    
    if not os.path.exists(photos_dir) or not os.path.exists(sketches_dir):
        return {
            "dataset_name": "CUFSF",
            "source": "CUHK MMLab FERET",
            "license_access_status": "NOT INTEGRATED — ACCESS PENDING",
            "identity_count": 0,
            "sketch_count": 0,
            "photo_count": 0,
            "paired_identity_count": 0,
            "modality": "Viewed Shape-Distorted Sketch",
            "status": "ACCESS_PENDING_NO_PHYSICAL_DATA"
        }
        
    photo_files = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.jpg', '.png'))]
    sketch_files = [f for f in os.listdir(sketches_dir) if f.lower().endswith(('.jpg', '.png'))]
    
    valid_photos = 0
    for p in photo_files:
        try:
            with Image.open(os.path.join(photos_dir, p)) as img:
                img.verify()
            valid_photos += 1
        except Exception:
            pass
            
    valid_sketches = 0
    for s in sketch_files:
        try:
            with Image.open(os.path.join(sketches_dir, s)) as img:
                img.verify()
            valid_sketches += 1
        except Exception:
            pass
            
    manifest = {
        "dataset_name": "CUFSF",
        "source": "CUHK MMLab FERET",
        "license_access_status": "INTEGRATED" if (valid_photos > 0 and valid_sketches > 0) else "NOT INTEGRATED — ACCESS PENDING",
        "identity_count": min(valid_photos, valid_sketches),
        "sketch_count": valid_sketches,
        "photo_count": valid_photos,
        "paired_identity_count": min(valid_photos, valid_sketches),
        "modality": "Viewed Shape-Distorted Sketch",
        "status": "VALIDATED" if (valid_photos > 0 and valid_sketches > 0) else "ACCESS_PENDING"
    }
    
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2)
        
    return manifest

if __name__ == "__main__":
    res = validate_cufsf()
    print("CUFSF Validation Status:", res["status"])
