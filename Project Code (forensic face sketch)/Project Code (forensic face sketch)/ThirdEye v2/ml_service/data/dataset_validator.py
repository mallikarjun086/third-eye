import os
import hashlib
from PIL import Image

class DatasetValidator:
    @staticmethod
    def validate_image(image_path):
        if not os.path.exists(image_path):
            return False, "File not found"
        try:
            with Image.open(image_path) as img:
                img.verify()
            return True, "Valid"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def compute_sha256(image_path):
        h = hashlib.sha256()
        with open(image_path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
