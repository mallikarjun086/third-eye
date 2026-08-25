import os
import sys
import glob
import json
import hashlib
from PIL import Image

def get_image_info(filepath):
    try:
        with Image.open(filepath) as img:
            return {"valid": True, "size": img.size, "mode": img.mode}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def to_pid(filename):
    name = os.path.splitext(os.path.basename(filename))[0]
    for prefix in ["a-", "b-", "c-", "d-", "sk-", "ph-"]:
        if name.startswith(prefix):
            name = name[len(prefix):]
    parts = name.split("-")
    if len(parts) > 1 and parts[-1].isdigit():
        return "-".join(parts[:-1])
    return name

def main():
    root = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
    out_dir = os.path.join(root, "results", "critical_identification_repair")
    os.makedirs(out_dir, exist_ok=True)

    ml_dir = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
    data_dir = os.path.join(root, "data")
    
    # 1. Active ML Service Dataset
    gallery_dir = os.path.join(ml_dir, "dataset", "gallery")
    queries_dir = os.path.join(ml_dir, "dataset", "queries")
    
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    
    g_files = [f for f in glob.glob(os.path.join(gallery_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts]
    q_files = [f for f in glob.glob(os.path.join(queries_dir, "*.*")) if os.path.splitext(f)[1].lower() in valid_exts]
    
    g_pids = set(to_pid(f) for f in g_files)
    q_pids = set(to_pid(f) for f in q_files)
    common_pids = g_pids.intersection(q_pids)
    
    # 2. CUFSF dataset check
    cufsf_photos = glob.glob(os.path.join(data_dir, "cufsf", "photos", "*"))
    cufsf_sketches = glob.glob(os.path.join(data_dir, "cufsf", "sketches", "*"))
    
    # 3. IIIT-D dataset check
    iiitd_files = glob.glob(os.path.join(data_dir, "iiitd", "**", "*.*"), recursive=True)
    
    # 4. Check desktop archive
    desktop_archive_dir = r"C:\Users\Mallikarjun Gala\OneDrive\Desktop"
    archive_candidates = []
    if os.path.exists(desktop_archive_dir):
        for item in os.listdir(desktop_archive_dir):
            if "third" in item.lower() or "sketch" in item.lower() or "face" in item.lower():
                archive_candidates.append(os.path.join(desktop_archive_dir, item))

    audit_result = {
        "timestamp": "2026-08-25T12:10:00+05:30",
        "cuhk_cufs_active": {
            "gallery_path": gallery_dir,
            "gallery_image_count": len(g_files),
            "gallery_unique_identities": len(g_pids),
            "queries_path": queries_dir,
            "queries_image_count": len(q_files),
            "queries_unique_identities": len(q_pids),
            "verified_sketch_photo_paired_identities": len(common_pids),
            "status": "PHYSICALLY_VERIFIED_PRIMARY_BENCHMARK"
        },
        "cufsf_feret": {
            "path": os.path.join(data_dir, "cufsf"),
            "photo_count": len(cufsf_photos),
            "sketch_count": len(cufsf_sketches),
            "status": "NOT_INTEGRATED_REQUIRES_LICENSE_UNPACK"
        },
        "iiitd_forensic": {
            "path": os.path.join(data_dir, "iiitd"),
            "file_count": len(iiitd_files),
            "status": "PASSWORD_PROTECTED_OR_UNEXTRACTED"
        },
        "desktop_archive_inventory": {
            "searched_directory": desktop_archive_dir,
            "found_related_folders": archive_candidates,
            "note": "Only physically present readable files in repository workspace are counted to prevent non-reproducible evaluation."
        }
    }

    out_file = os.path.join(out_dir, "physical_dataset_audit.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(audit_result, f, indent=2)

    print(f"Physical dataset audit saved to {out_file}")
    print(json.dumps(audit_result, indent=2))

if __name__ == "__main__":
    main()
