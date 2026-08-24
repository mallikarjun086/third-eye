import os
import json
import hashlib
from PIL import Image

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
JSON_OUT = os.path.join(WORKSPACE, "data", "DATASET_PHYSICAL_INVENTORY.json")
MD_OUT = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "DATASET_PHYSICAL_INVENTORY.md")

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def scan_directory(dir_path, dataset_name):
    if not os.path.exists(dir_path):
        return {
            "dataset_name": dataset_name,
            "physical_path": os.path.relpath(dir_path, WORKSPACE),
            "status": "DIRECTORY_NOT_FOUND",
            "file_count": 0,
            "valid_image_count": 0,
            "corrupt_image_count": 0,
            "unique_identity_count": 0,
            "photo_count": 0,
            "sketch_count": 0,
            "paired_identity_count": 0,
            "duplicate_checksum_count": 0,
            "checksums": {}
        }
    
    file_count = 0
    valid_count = 0
    corrupt_count = 0
    photo_count = 0
    sketch_count = 0
    pids = set()
    sketch_pids = set()
    photo_pids = set()
    checksum_map = {}
    
    for root, _, files in os.walk(dir_path):
        for f in files:
            file_count += 1
            ext = os.path.splitext(f)[1].lower()
            if ext in IMAGE_EXTS:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, WORKSPACE)
                # Test validity
                try:
                    with Image.open(full) as img:
                        img.verify()
                    valid_count += 1
                    sha = compute_sha256(full)
                    checksum_map[rel] = sha
                    
                    # PID classification
                    fname = f.lower()
                    if "gallery" in root.lower() or "photo" in root.lower() or fname.startswith("m-") or fname.startswith("f-") or fname.startswith("m1-") or fname.startswith("f1-") or fname.startswith("a-"):
                        photo_count += 1
                        # extract pid base name
                        pid = f.split("-")[0] + "-" + f.split("-")[1] if "-" in f else f.split(".")[0]
                        photo_pids.add(pid)
                        pids.add(pid)
                    if "queries" in root.lower() or "sketch" in root.lower() or fname.endswith("-sz1.jpg") or "-1.jpg" in fname or "-2.jpg" in fname:
                        sketch_count += 1
                        pid = f.split("-")[0] + "-" + f.split("-")[1] if "-" in f else f.split(".")[0]
                        sketch_pids.add(pid)
                        pids.add(pid)
                except Exception:
                    corrupt_count += 1

    paired_pids = len(photo_pids.intersection(sketch_pids))
    return {
        "dataset_name": dataset_name,
        "physical_path": os.path.relpath(dir_path, WORKSPACE),
        "status": "PHYSICALLY_PRESENT" if valid_count > 0 else "EMPTY_OR_CORRUPT",
        "file_count": file_count,
        "valid_image_count": valid_count,
        "corrupt_image_count": corrupt_count,
        "unique_identity_count": len(pids),
        "photo_count": photo_count,
        "sketch_count": sketch_count,
        "paired_identity_count": paired_pids,
        "duplicate_checksum_count": len(checksum_map) - len(set(checksum_map.values()))
    }

def main():
    target_dirs = [
        ("CUFS (CUHK)", os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "dataset")),
        ("CUFSF (FERET)", os.path.join(WORKSPACE, "data", "cufsf")),
        ("IIIT-D Forensic", os.path.join(WORKSPACE, "data", "iiitd")),
        ("ThirdEye Composite", os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "dataset", "queries"))
    ]
    
    results = {}
    for name, path in target_dirs:
        results[name] = scan_directory(path, name)
        
    os.makedirs(os.path.dirname(JSON_OUT), exist_ok=True)
    with open(JSON_OUT, "w") as f:
        json.dump(results, f, indent=2)
        
    os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
    with open(MD_OUT, "w") as f:
        f.write("# DATASET PHYSICAL INVENTORY AUDIT REPORT\n\n")
        f.write("**Audit Timestamp**: August 24, 2026  \n")
        f.write("**Auditor**: Lead Technical Auditor  \n\n")
        f.write("---\n\n")
        f.write("## PHYSICAL INVENTORY MATRIX\n\n")
        f.write("| Dataset Name | Physical Path | Access / Physical Status | Total Files | Valid Images | Corrupt Files | Unique PIDs | Sketches | Photos | Paired PIDs | Duplicates |\n")
        f.write("| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        for name, data in results.items():
            f.write(f"| **{data['dataset_name']}** | `{data['physical_path']}` | `{data['status']}` | {data['file_count']} | {data['valid_image_count']} | {data['corrupt_image_count']} | **{data['unique_identity_count']}** | {data['sketch_count']} | {data['photo_count']} | **{data['paired_identity_count']}** | {data['duplicate_checksum_count']} |\n")

    print(f"Inventory written to {JSON_OUT} and {MD_OUT}")

if __name__ == "__main__":
    main()
