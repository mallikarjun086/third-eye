import os
import json
import hashlib

def ingest(gallery_dir, output_manifest_path):
    manifest = []
    if os.path.exists(gallery_dir):
        for f in os.listdir(gallery_dir):
            if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                filepath = os.path.join(gallery_dir, f)
                h = hashlib.sha256()
                with open(filepath, "rb") as fh:
                    while chunk := fh.read(8192):
                        h.update(chunk)
                pid = f.split('-01')[0].split('.')[0]
                manifest.append({
                    "identity_id": pid,
                    "filename": f,
                    "sha256": h.hexdigest(),
                    "modality": "PHOTO"
                })
    with open(output_manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    return len(manifest)
