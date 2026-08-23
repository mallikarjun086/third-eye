"""
Precompute dataset embeddings into a .npy cache without starting the server.

Usage
-----
    python precompute.py C:/path/to/dataset_dir

The cache file `dataset_embeddings.npy` is written into the dataset directory
so the running service can load it instantly on the first /match call.
"""

import os
import sys
import app  # reuse the service code in-process


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    dataset_dir = os.path.abspath(sys.argv[1])
    if not os.path.isdir(dataset_dir):
        print(f"Dataset directory not found: {dataset_dir}")
        sys.exit(1)

    app.load_model()
    if app._model is None:
        print(f"Model failed to load: {app._model_error}")
        sys.exit(1)

    app.build_cache(dataset_dir, force=True)
    print(f"Precomputed embeddings for {len(app._cache)} faces in:")
    print(dataset_dir)


if __name__ == "__main__":
    main()