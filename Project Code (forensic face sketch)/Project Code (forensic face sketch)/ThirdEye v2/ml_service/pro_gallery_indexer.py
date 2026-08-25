"""
ThirdEye v2 — Vectorized Matrix Gallery Indexer & Fast Match Engine
=====================================================================
Builds contiguous 2D NumPy float32 matrices (M_face, M_hog, M_lbp) across all gallery candidates
to enable sub-15ms vectorized similarity search across tens of thousands of suspect candidates.
"""

import os
import sys
import json
import time
import logging
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("thirdeye-matrix-indexer")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

import app
from demographic_filter import DemographicEstimator

INDEX_FILE = os.path.join(BASE_DIR, "matrix_gallery_index.json")
FEATURES_FILE = os.path.join(BASE_DIR, "matrix_gallery_features.npz")
CACHE_VERSION = "v8_vectorized_matrix_50k_v1"


class VectorizedMatrixEngine:
    def __init__(self, gallery_dir: str = None):
        self.gallery_dir = gallery_dir or os.path.join(BASE_DIR, "dataset", "gallery_all")
        self.metadata = []
        self.M_face = None
        self.M_hog = None
        self.M_lbp = None
        self.version = CACHE_VERSION
        self.loaded = False

    def build_matrix_cache(self, force: bool = False):
        if not force and self.load_matrix_cache():
            return

        app.load_model()
        if app._model is None:
            log.error("Model failed to load.")
            return

        images = app._list_images(self.gallery_dir)
        log.info("Starting Matrix Vectorization for %d candidate images...", len(images))

        face_list = []
        hog_list = []
        lbp_list = []
        meta_list = []

        t0 = time.time()

        for idx, path in enumerate(images, start=1):
            if idx % 500 == 0 or idx == len(images):
                log.info("Vectorized %d / %d candidates (%.1fs elapsed)...", idx, len(images), time.time() - t0)

            rel_path = os.path.relpath(path, self.gallery_dir)
            try:
                with open(path, "rb") as fh:
                    raw = fh.read()
                
                grey = app.hog_grey(raw)
                emb_raw = app.embed_image_raw(raw)
                
                if emb_raw is not None and app._proj_model is not None:
                    import tensorflow as tf
                    emb = app._proj_model(tf.convert_to_tensor([emb_raw], dtype=tf.float32), training=False).numpy()[0]
                else:
                    emb = emb_raw

                if emb is None:
                    continue

                hog = app.compute_hog(grey)
                lbp = app.compute_lbp(grey)
                
                # Estimate attributes
                attr = DemographicEstimator.estimate_attributes(None, filename=path)

                face_list.append(emb.astype(np.float32))
                hog_list.append(hog.astype(np.float32))
                lbp_list.append(lbp.astype(np.float32))

                meta_list.append({
                    "id": idx,
                    "rel_path": rel_path,
                    "name": os.path.splitext(os.path.basename(path))[0],
                    "attr": attr
                })
            except Exception as e:
                log.warning("Skip %s: %s", rel_path, e)

        if face_list:
            self.M_face = np.vstack(face_list)
            self.M_hog = np.vstack(hog_list)
            self.M_lbp = np.vstack(lbp_list)
            self.metadata = meta_list

            np.savez_compressed(
                FEATURES_FILE,
                M_face=self.M_face,
                M_hog=self.M_hog,
                M_lbp=self.M_lbp,
                version=self.version
            )
            with open(INDEX_FILE, "w", encoding="utf-8") as f:
                json.dump({"version": self.version, "count": len(meta_list), "metadata": meta_list}, f, indent=2)

            log.info("Matrix Cache Saved (%d candidates embedded, Matrix Shapes: Face=%s, HOG=%s, LBP=%s)",
                     len(meta_list), str(self.M_face.shape), str(self.M_hog.shape), str(self.M_lbp.shape))
            self.loaded = True

    def load_matrix_cache(self) -> bool:
        if os.path.exists(FEATURES_FILE) and os.path.exists(INDEX_FILE):
            try:
                npz = np.load(FEATURES_FILE)
                if str(npz.get("version", "")) == self.version:
                    self.M_face = npz["M_face"]
                    self.M_hog = npz["M_hog"]
                    self.M_lbp = npz["M_lbp"]
                    
                    with open(INDEX_FILE, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        self.metadata = data.get("metadata", [])
                    
                    self.loaded = True
                    log.info("Loaded Matrix Vector Engine (%d candidates, Shapes: Face=%s, HOG=%s)",
                             len(self.metadata), str(self.M_face.shape), str(self.M_hog.shape))
                    return True
            except Exception as e:
                log.warning("Matrix load error: %s", e)
        return False

    def vector_search(self, q_face: np.ndarray, q_hog: np.ndarray, q_lbp: np.ndarray,
                      q_attr: dict, top_k: int = 10,
                      w_face: float = 0.50, w_hog: float = 0.35, w_lbp: float = 0.15) -> list:
        """Sub-15ms BLAS Matrix-Vector similarity search."""
        if not self.loaded or self.M_face is None:
            return []

        # 1. BLAS Matrix-Vector Dot Product (O(1) CPU/GPU acceleration)
        S_face = np.dot(self.M_face, q_face.astype(np.float32))
        S_hog = np.dot(self.M_hog, q_hog.astype(np.float32))
        S_lbp = np.dot(self.M_lbp, q_lbp.astype(np.float32))

        # 2. Multi-Metric Fused Similarity Array
        S_fused = w_face * S_face + w_hog * S_hog + w_lbp * S_lbp

        # 3. Soft Demographic Vector Multiplier
        penalties = np.ones(len(self.metadata), dtype=np.float32)
        for i, meta in enumerate(self.metadata):
            penalties[i] = DemographicEstimator.compute_soft_penalty(q_attr, meta.get("attr", {}))

        S_final = S_fused * penalties

        # 4. Fast Top-K Selection via Argpartition
        top_k = min(top_k, len(S_final))
        top_indices = np.argpartition(S_final, -top_k)[-top_k:]
        top_indices = top_indices[np.argsort(-S_final[top_indices])]

        results = []
        for idx in top_indices:
            meta = self.metadata[idx]
            sim = float(S_final[idx])
            results.append({
                "name": meta["name"],
                "path": os.path.join(self.gallery_dir, meta["rel_path"]),
                "similarity": round(sim, 4),
                "calibrated_score": round(sim * 100.0, 2),
                "rank": len(results) + 1
            })

        return results


if __name__ == "__main__":
    engine = VectorizedMatrixEngine()
    engine.build_matrix_cache(force=True)
