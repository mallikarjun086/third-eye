class IIITDAdapter:
    """Adapter for IIIT-D Forensic/Composite Sketch Dataset."""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir
        self.status = "ACCESS_PENDING"
        self.reason = "Requires official EULA agreement from IIIT-Delhi"

    def load_manifest(self):
        return []
