import hashlib

class DuplicateAudit:
    @staticmethod
    def audit_duplicates(records):
        hashes = {}
        duplicates = []
        for r in records:
            path = r.get("image_path")
            if not path:
                continue
            h = hashlib.sha256()
            with open(path, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            digest = h.hexdigest()
            if digest in hashes:
                duplicates.append({"original": hashes[digest], "duplicate": path})
            else:
                hashes[digest] = path
        return {
            "unique_checksums": len(hashes),
            "duplicate_count": len(duplicates),
            "duplicates": duplicates
        }
