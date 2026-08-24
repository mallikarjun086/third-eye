import os
import json

DATASET_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST_OUT = os.path.join(DATASET_DIR, "dataset_manifest.json")

def validate_iiitd():
    viewed_dir = os.path.join(DATASET_DIR, "viewed")
    
    if not os.path.exists(viewed_dir):
        manifest = {
            "dataset_name": "IIIT-D Forensic",
            "source": "IIIT-Delhi IPAG",
            "license_access_status": "NOT INTEGRATED — ACCESS PENDING",
            "identity_count": 0,
            "sketch_count": 0,
            "photo_count": 0,
            "paired_identity_count": 0,
            "modality": "Forensic / Semi-Forensic Sketch",
            "status": "ACCESS_PENDING_NO_PHYSICAL_DATA"
        }
    else:
        manifest = {
            "dataset_name": "IIIT-D Forensic",
            "source": "IIIT-Delhi IPAG",
            "license_access_status": "INTEGRATED",
            "identity_count": 0,
            "sketch_count": 0,
            "photo_count": 0,
            "paired_identity_count": 0,
            "modality": "Forensic / Semi-Forensic Sketch",
            "status": "VALIDATED"
        }
        
    with open(MANIFEST_OUT, "w") as f:
        json.dump(manifest, f, indent=2)
        
    return manifest

if __name__ == "__main__":
    res = validate_iiitd()
    print("IIIT-D Validation Status:", res["status"])
