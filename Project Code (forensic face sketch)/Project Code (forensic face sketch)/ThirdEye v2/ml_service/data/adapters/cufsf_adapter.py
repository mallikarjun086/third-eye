class CUFSFAdapter:
    """Adapter for CUHK FERET Face Sketch Database (CUFSF)."""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir
        self.status = "ACCESS_PENDING"
        self.reason = "Requires official EULA approval from CUHK/FERET"

    def load_manifest(self):
        return []
