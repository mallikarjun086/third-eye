import os
from .base_adapter import BaseAdapter

class CompositeAdapter(BaseAdapter):
    """Adapter for ThirdEye Internal Composite Sketches."""

    def load_manifest(self):
        records = []
        if not self.base_dir:
            return records
        
        queries_dir = os.path.join(self.base_dir, "dataset", "queries")
        if os.path.exists(queries_dir):
            for f in os.listdir(queries_dir):
                if f.startswith("a-sharukh"):
                    records.append({
                        "identity_id": "a-sharukh",
                        "image_id": f,
                        "image_path": os.path.join(queries_dir, f),
                        "dataset_name": "ThirdEye_Composite",
                        "source": "INTERNAL_COMPOSITE",
                        "modality": "COMPOSITE_SKETCH",
                        "sketch_type": "THIRDEYE_VECTOR",
                        "original_filename": f,
                        "split": "TEST"
                    })
        return records
