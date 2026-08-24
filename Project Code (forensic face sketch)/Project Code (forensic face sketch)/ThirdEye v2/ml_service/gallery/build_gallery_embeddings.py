import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app

def build(gallery_dir):
    app.load_model()
    app.build_cache(gallery_dir, force=True)
    return len(app._cache)
