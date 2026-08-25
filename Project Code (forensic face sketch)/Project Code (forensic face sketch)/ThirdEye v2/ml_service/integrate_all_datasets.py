"""
ThirdEye v2 — Multi-Dataset Ingestion Script
=============================================
Integrates all available suspect dataset sources into a unified gallery directory:
1. Indian Actors & People Dataset (5,972 images)
2. Paired Archive Photos (22,334 images: train/val/test)
3. CUFS International Gallery (189 images)
"""

import os
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("thirdeye-multi-dataset")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GALLERY_ALL = os.path.join(BASE_DIR, "dataset", "gallery_all")

SOURCES = {
    "cufs": os.path.join(BASE_DIR, "dataset", "gallery"),
    "indian_actors": r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive (1)\actors_dataset\Indian_actors_faces",
    "archive_train": r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\train\photos",
    "archive_val": r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\val\photos",
    "archive_test": r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive\test\photos",
}

VALID_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

def build_unified_gallery():
    os.makedirs(GALLERY_ALL, exist_ok=True)
    total_added = 0

    # 1. CUFS Gallery
    cufs_dir = SOURCES["cufs"]
    if os.path.exists(cufs_dir):
        for f in os.listdir(cufs_dir):
            if f == "indian_actors" or f == "dataset_embeddings.npy":
                continue
            if os.path.splitext(f)[1].lower() in VALID_EXTS:
                src = os.path.join(cufs_dir, f)
                dst = os.path.join(GALLERY_ALL, f"cufs_{f}")
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)
                total_added += 1
        log.info("CUFS Gallery processed. Active count: %d", total_added)

    # 2. Indian Actors Dataset
    indian_dir = SOURCES["indian_actors"]
    if os.path.exists(indian_dir):
        indian_count = 0
        for actor in os.listdir(indian_dir):
            actor_path = os.path.join(indian_dir, actor)
            if os.path.isdir(actor_path):
                imgs = [i for i in os.listdir(actor_path) if os.path.splitext(i)[1].lower() in VALID_EXTS]
                for idx, img in enumerate(imgs[:3], start=1):  # Top 3 clear photos per actor
                    src = os.path.join(actor_path, img)
                    ext = os.path.splitext(img)[1].lower()
                    dst = os.path.join(GALLERY_ALL, f"indian_m_{actor}_{idx}{ext}")
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                    indian_count += 1
        total_added += indian_count
        log.info("Indian Actors Dataset processed (%d photos). Active total: %d", indian_count, total_added)

    # 3. Archive Photos (train/val/test)
    archive_count = 0
    for key in ["archive_train", "archive_val", "archive_test"]:
        p_dir = SOURCES[key]
        if os.path.exists(p_dir):
            for img in os.listdir(p_dir):
                if os.path.splitext(img)[1].lower() in VALID_EXTS:
                    src = os.path.join(p_dir, img)
                    dst = os.path.join(GALLERY_ALL, f"{key}_{img}")
                    if not os.path.exists(dst):
                        shutil.copy2(src, dst)
                    archive_count += 1
    total_added += archive_count
    log.info("Archive Paired Photos processed (%d photos). Active total: %d", archive_count, total_added)

    log.info("Unified Multi-Dataset Suspect Gallery ready at %s (Total Candidates: %d)", GALLERY_ALL, total_added)
    return GALLERY_ALL

if __name__ == "__main__":
    build_unified_gallery()
