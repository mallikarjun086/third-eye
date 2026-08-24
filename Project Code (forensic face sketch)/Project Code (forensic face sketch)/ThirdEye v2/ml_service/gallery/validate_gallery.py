import os
from PIL import Image

def validate(gallery_dir):
    valid_count = 0
    invalid_count = 0
    if os.path.exists(gallery_dir):
        for f in os.listdir(gallery_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(gallery_dir, f)
                try:
                    with Image.open(filepath) as img:
                        img.verify()
                    valid_count += 1
                except Exception:
                    invalid_count += 1
    return {"valid": valid_count, "invalid": invalid_count}
