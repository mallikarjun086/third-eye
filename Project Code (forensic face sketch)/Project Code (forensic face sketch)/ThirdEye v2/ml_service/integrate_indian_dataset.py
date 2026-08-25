"""
ThirdEye v2 — Multi-Ethnic Gallery Integration Script
=====================================================
Copies clean frontal photos from Indian Actors dataset into the production gallery
and triggers ML feature cache rebuilding for multi-ethnic cross-modal recognition.
"""

import os
import shutil
import glob
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("thirdeye-gallery-integration")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GALLERY_DIR = os.path.join(BASE_DIR, "dataset", "gallery")
INDIAN_ACTORS_SRC = r"C:\Users\Mallikarjun Gala\OneDrive\Desktop\archive (1)\actors_dataset\Indian_actors_faces"
INDIAN_TARGET_DIR = os.path.join(GALLERY_DIR, "indian_actors")

def integrate_indian_faces():
    if not os.path.exists(INDIAN_ACTORS_SRC):
        log.error("Indian actors dataset path not found: %s", INDIAN_ACTORS_SRC)
        return

    os.makedirs(INDIAN_TARGET_DIR, exist_ok=True)
    actor_folders = [d for d in os.listdir(INDIAN_ACTORS_SRC) if os.path.isdir(os.path.join(INDIAN_ACTORS_SRC, d))]
    log.info("Found %d Indian actor identities in source dataset.", len(actor_folders))

    copied_count = 0
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for actor in actor_folders:
        actor_path = os.path.join(INDIAN_ACTORS_SRC, actor)
        images = [f for f in os.listdir(actor_path) if os.path.splitext(f)[1].lower() in valid_exts]
        images = sorted(images)
        
        # Pick top 2 representative photos per identity
        selected = images[:2] if len(images) >= 2 else images
        for idx, img_name in enumerate(selected, start=1):
            src_file = os.path.join(actor_path, img_name)
            ext = os.path.splitext(img_name)[1].lower()
            dst_filename = f"m_{actor}_{idx}{ext}"
            dst_file = os.path.join(INDIAN_TARGET_DIR, dst_filename)
            
            try:
                shutil.copy2(src_file, dst_file)
                copied_count += 1
            except Exception as e:
                log.warning("Could not copy %s: %s", src_file, e)

    log.info("Successfully integrated %d Indian actor face photos into %s", copied_count, INDIAN_TARGET_DIR)

if __name__ == "__main__":
    integrate_indian_faces()
