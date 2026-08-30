"""
ThirdEye v2 — Enterprise FAISS Sub-Millisecond Vector Indexing Engine
====================================================================
Provides scalable, high-speed similarity search for face embeddings across
large-scale suspect galleries using Facebook AI Similarity Search (FAISS).
"""

import time
import logging
from typing import List, Tuple, Dict, Optional
import numpy as np
import faiss

log = logging.getLogger("thirdeye-faiss")

class FAISSIndexManager:
    """Manages L2-normalized Inner Product FAISS indices for vector search."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)
        self.id_to_path: Dict[int, str] = {}
        self.path_to_id: Dict[str, int] = {}
        self.is_built: bool = False

    def build_index(self, features_dict: Dict[str, Dict[str, np.ndarray]]):
        """Build FAISS index from in-memory features cache."""
        t0 = time.time()
        paths = []
        vectors = []

        for idx, (rel_path, feat_map) in enumerate(features_dict.items()):
            vec = feat_map.get("face")
            if vec is not None and len(vec) == self.dimension:
                paths.append(rel_path)
                vectors.append(vec)

        if not vectors:
            log.warning("FAISS: No valid embeddings found to build index.")
            self.is_built = False
            return

        mat = np.ascontiguousarray(np.vstack(vectors).astype(np.float32))
        
        # Ensure L2 normalization for Inner Product cosine equivalence
        norms = np.linalg.norm(mat, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        mat = mat / norms

        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(mat)

        self.id_to_path = {idx: path for idx, path in enumerate(paths)}
        self.path_to_id = {path: idx for idx, path in enumerate(paths)}
        self.is_built = True

        elapsed = (time.time() - t0) * 1000.0
        log.info("FAISS index built: %d vectors in %.2f ms.", self.index.ntotal, elapsed)

    def search(self, query_vec: np.ndarray, top_k: int = 10) -> List[Tuple[float, str]]:
        """
        Execute sub-millisecond vector search against FAISS index.
        Returns list of (cosine_similarity, relative_path) tuples.
        """
        if not self.is_built or self.index.ntotal == 0:
            return []

        q = np.ascontiguousarray(query_vec.reshape(1, -1).astype(np.float32))
        norm = np.linalg.norm(q)
        if norm > 0:
            q = q / norm

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(q, k)

        results = []
        for sim, idx in zip(scores[0], indices[0]):
            if idx in self.id_to_path:
                results.append((float(sim), self.id_to_path[idx]))

        return results
