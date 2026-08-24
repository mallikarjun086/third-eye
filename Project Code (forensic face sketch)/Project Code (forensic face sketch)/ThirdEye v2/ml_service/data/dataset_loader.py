import os
from .adapters.cufs_adapter import CUFSAdapter
from .adapters.cufsf_adapter import CUFSFAdapter
from .adapters.iiitd_adapter import IIITDAdapter

class DatasetLoader:
    def __init__(self, ml_service_dir):
        self.ml_service_dir = ml_service_dir
        self.cufs = CUFSAdapter(ml_service_dir)
        self.cufsf = CUFSFAdapter(ml_service_dir)
        self.iiitd = IIITDAdapter(ml_service_dir)

    def load_all_records(self):
        records = []
        records.extend(self.cufs.load_manifest())
        records.extend(self.cufsf.load_manifest())
        records.extend(self.iiitd.load_manifest())
        return records
