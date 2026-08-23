"""ThirdEye v2 — Dataset Management & Ingestion Script.

Allows adding suspect photo records or forensic sketches to the dataset repository
and triggering feature cache pre-building.
"""

import os
import sys
import shutil
import argparse

# ── Dynamic Path Setup ──
script_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.dirname(script_dir)
ml_service_dir = os.path.join(
    repo_root,
    "Project Code (forensic face sketch)",
    "Project Code (forensic face sketch)",
    "ThirdEye v2",
    "ml_service",
)

if ml_service_dir not in sys.path:
    sys.path.insert(0, ml_service_dir)

import importlib

app = importlib.import_module("app")


def add_image_to_dataset(image_path: str, target_type: str = "gallery") -> bool:
    """Copies an image to dataset/gallery or dataset/queries and updates the feature cache."""
    if not os.path.exists(image_path):
        print(f"[ERROR] Source image file not found: {image_path}")
        return False

    target_dir = os.path.join(ml_service_dir, "dataset", target_type)
    os.makedirs(target_dir, exist_ok=True)

    filename = os.path.basename(image_path)
    dest_path = os.path.join(target_dir, filename)

    shutil.copy2(image_path, dest_path)
    print(f"[OK] Ingested '{filename}' into {target_type} dataset.")

    # Rebuild cache if adding to gallery
    if target_type == "gallery":
        print("[INFO] Rebuilding feature cache...")
        app.build_cache(target_dir, force=True)
        print("[OK] Feature cache successfully updated.")

    return True


def main():
    parser = argparse.ArgumentParser(description="ThirdEye v2 Dataset Ingestion Tool")
    parser.add_argument("--image", required=True, help="Path to input image file")
    parser.add_argument("--type", choices=["gallery", "queries"], default="gallery", help="Target dataset type")
    args = parser.parse_args()

    add_image_to_dataset(args.image, args.type)


if __name__ == "__main__":
    main()
