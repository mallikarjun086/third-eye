from abc import ABC, abstractmethod

class BaseAdapter(ABC):
    """Abstract Base Class for Dataset Ingestion Adapters."""
    
    def __init__(self, base_dir=None):
        self.base_dir = base_dir

    @abstractmethod
    def load_manifest(self):
        """Must return a list of dicts following the canonical schema."""
        pass
