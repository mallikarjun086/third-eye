import os

class CUFSAdapter:
    """Adapter for CUHK Face Sketch Database (CUFS)."""
    
    def __init__(self, base_dir):
        self.base_dir = base_dir

    def load_manifest(self):
        gallery_dir = os.path.join(self.base_dir, "dataset", "gallery")
        queries_dir = os.path.join(self.base_dir, "dataset", "queries")
        
        records = []
        if os.path.exists(gallery_dir):
            for f in os.listdir(gallery_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    pid = f.split('.')[0]
                    records.append({
                        "dataset_name": "CUFS",
                        "identity_id": pid,
                        "image_path": os.path.join(gallery_dir, f),
                        "modality": "PHOTO"
                    })
        if os.path.exists(queries_dir):
            for f in os.listdir(queries_dir):
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    pid = f.split('-sz1')[0] if '-sz1' in f else f.split('.')[0]
                    records.append({
                        "dataset_name": "CUFS",
                        "identity_id": pid,
                        "image_path": os.path.join(queries_dir, f),
                        "modality": "ARTIST_SKETCH" if "-sz1" in f else "COMPOSITE_SKETCH"
                    })
        return records
