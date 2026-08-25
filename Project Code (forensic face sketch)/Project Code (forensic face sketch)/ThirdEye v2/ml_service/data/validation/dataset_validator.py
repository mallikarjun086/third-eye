import os
import hashlib
from PIL import Image

class DatasetValidator:
    @staticmethod
    def validate_image(filepath):
        if not os.path.exists(filepath):
            return False, "File does not exist"
        try:
            with Image.open(filepath) as img:
                img.verify()
            return True, "Valid"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def compute_sha256(filepath):
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
