import hashlib

class DuplicateDetector:
    @staticmethod
    def detect_duplicates(file_paths):
        seen = {}
        duplicates = []
        for path in file_paths:
            if not path:
                continue
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            digest = h.hexdigest()
            if digest in seen:
                duplicates.append({"original": seen[digest], "duplicate": path})
            else:
                seen[digest] = path
        return duplicates
