import os

class CUFSFAdapter:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        self.photos_dir = os.path.join(self.base_dir, "photos")
        self.sketches_dir = os.path.join(self.base_dir, "sketches")
        
    def is_available(self):
        return os.path.exists(self.photos_dir) and len(os.listdir(self.photos_dir)) > 0
        
    def get_pairs(self):
        if not self.is_available():
            return []
        pairs = []
        for p in os.listdir(self.photos_dir):
            if p.lower().endswith(('.jpg', '.png')):
                pid = os.path.splitext(p)[0]
                sketch_name = f"{pid}-sz1.jpg"
                sketch_path = os.path.join(self.sketches_dir, sketch_name)
                photo_path = os.path.join(self.photos_dir, p)
                if os.path.exists(sketch_path):
                    pairs.append({
                        "identity_id": f"CUFSF:{pid}",
                        "photo_path": photo_path,
                        "sketch_path": sketch_path,
                        "dataset": "CUFSF"
                    })
        return pairs
