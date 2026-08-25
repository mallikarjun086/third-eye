import os
import sys
import json
import hashlib
from PIL import Image

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def verify_dataset_location(path, name):
    if not os.path.exists(path):
        return {
            "dataset_name": name,
            "status": "NOT_INTEGRATED",
            "physical_path": path,
            "total_files": 0,
            "valid_images": 0,
            "corrupt_images": 0,
            "unique_identities": 0
        }
    
    files = [os.path.join(path, f) for f in os.listdir(path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    valid = 0
    corrupt = 0
    pids = set()

    for f in files:
        try:
            with Image.open(f) as img:
                img.verify()
            valid += 1
            base = os.path.basename(f)
            pid = base.split('-sz1')[0].split('-01')[0].split('.')[0]
            pids.add(pid)
        except Exception:
            corrupt += 1

    return {
        "dataset_name": name,
        "status": "PHYSICALLY_VERIFIED" if valid > 0 else "NOT_INTEGRATED",
        "physical_path": path,
        "total_files": len(files),
        "valid_images": valid,
        "corrupt_images": corrupt,
        "unique_identities": len(pids)
    }

def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    ml_service = os.path.join(repo_root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
    
    cufs_gallery = os.path.join(ml_service, "dataset", "gallery")
    cufs_queries = os.path.join(ml_service, "dataset", "queries")
    cufsf_dir = os.path.join(repo_root, "data", "cufsf")
    iiitd_dir = os.path.join(repo_root, "data", "iiitd")

    registry = {
        "CUFS_Gallery": verify_dataset_location(cufs_gallery, "CUFS_Gallery"),
        "CUFS_Queries": verify_dataset_location(cufs_queries, "CUFS_Queries"),
        "CUFSF": verify_dataset_location(cufsf_dir, "CUFSF"),
        "IIITD": verify_dataset_location(iiitd_dir, "IIITD")
    }

    registry_path = os.path.join(repo_root, "data", "dataset_registry.json")
    os.makedirs(os.path.dirname(registry_path), exist_ok=True)
    with open(registry_path, "w") as f:
        json.dump(registry, f, indent=2)

    print("==================================================")
    print("   PHYSICAL DATASET VERIFICATION GATE REPORT")
    print("==================================================")
    for k, v in registry.items():
        print(f"[{v['status']}] {k}: {v['valid_images']} valid images, {v['unique_identities']} unique PIDs")

    print("\n[SUCCESS] Physical dataset verification completed successfully!")

if __name__ == "__main__":
    main()
