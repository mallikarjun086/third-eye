import os
import sys
import json
import glob
import hashlib
from PIL import Image

def get_sha256(filepath):
    if not os.path.exists(filepath):
        return None
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def main():
    root = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
    ml_dir = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
    
    out_dir = os.path.join(root, "results", "critical_identification_repair")
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. Inspect Python entry points & models
    app_py = os.path.join(ml_dir, "app.py")
    exp_weights = os.path.join(ml_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5")
    cache_npy = os.path.join(ml_dir, "dataset", "dataset_embeddings.npy")
    
    gallery_dir = os.path.join(ml_dir, "dataset", "gallery")
    queries_dir = os.path.join(ml_dir, "dataset", "queries")
    
    gallery_files = glob.glob(os.path.join(gallery_dir, "*.*"))
    query_files = glob.glob(os.path.join(queries_dir, "*.*"))
    
    # Check data/ folder datasets
    data_dir = os.path.join(root, "data")
    cufsf_dir = os.path.join(data_dir, "cufsf")
    iiitd_dir = os.path.join(data_dir, "iiitd")
    lfw_dir = os.path.join(data_dir, "lfw")
    
    # Audit physical files
    truth = {
        "timestamp": "2026-08-25T12:00:00+05:30",
        "active_backend": {
            "entry_point": app_py,
            "exists": os.path.exists(app_py),
            "weights_path": exp_weights,
            "weights_exists": os.path.exists(exp_weights),
            "weights_sha256": get_sha256(exp_weights),
            "cache_path": cache_npy,
            "cache_exists": os.path.exists(cache_npy),
            "cache_sha256": get_sha256(cache_npy)
        },
        "ml_service_dataset": {
            "gallery_dir": gallery_dir,
            "gallery_count": len(gallery_files),
            "queries_dir": queries_dir,
            "queries_count": len(query_files)
        },
        "root_data_datasets": {
            "cufsf": {
                "path": cufsf_dir,
                "photos": len(glob.glob(os.path.join(cufsf_dir, "photos", "*"))),
                "sketches": len(glob.glob(os.path.join(cufsf_dir, "sketches", "*")))
            },
            "iiitd": {
                "path": iiitd_dir,
                "files": len(glob.glob(os.path.join(iiitd_dir, "**", "*"), recursive=True))
            },
            "lfw": {
                "path": lfw_dir,
                "files": len(glob.glob(os.path.join(lfw_dir, "**", "*"), recursive=True))
            }
        }
    }
    
    truth_file = os.path.join(out_dir, "current_system_truth.json")
    with open(truth_file, "w", encoding="utf-8") as f:
        json.dump(truth, f, indent=2)
        
    print(f"System truth saved to {truth_file}")
    print(json.dumps(truth, indent=2))

if __name__ == "__main__":
    main()
