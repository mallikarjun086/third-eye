import os
import sys
import time

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ml_service_dir = os.path.join(base_dir, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ml_service_dir)

from app import build_cache, _cache_path

if __name__ == "__main__":
    gallery_dir = os.path.join(ml_service_dir, "dataset", "gallery")
    print(f"Pre-building cache for: {gallery_dir}")
    t0 = time.time()
    build_cache(gallery_dir, force=True)
    print(f"Cache build complete in {round(time.time() - t0, 2)} seconds. Saved to {_cache_path(gallery_dir)}")
