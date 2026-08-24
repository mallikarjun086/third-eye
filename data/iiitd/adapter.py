import os

class IIITDAdapter:
    def __init__(self, base_dir=None):
        self.base_dir = base_dir or os.path.dirname(os.path.abspath(__file__))
        
    def is_available(self):
        return os.path.exists(os.path.join(self.base_dir, "viewed"))
        
    def get_pairs(self):
        if not self.is_available():
            return []
        return []
