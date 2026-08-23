"""
ThirdEye v2 — Scalable Production Suspect Gallery Management Engine
"""

import os
import json
import hashlib
import time
import numpy as np

class ProductionGalleryManager:
    def __init__(self, gallery_dir: str, cache_dir: str):
        self.gallery_dir = gallery_dir
        self.cache_dir = cache_dir
        self.index_file = os.path.join(cache_dir, "gallery_index.json")
        self.features_file = os.path.join(cache_dir, "gallery_features.npz")
        self.identities = {}
        self.features = {}
        self.manifest_version = "v2.0-canonical"
        self._load_index()

    def _load_index(self):
        if os.path.exists(self.index_file):
            with open(self.index_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.identities = data.get("identities", {})
                self.manifest_version = data.get("manifest_version", "v2.0-canonical")
        
        if os.path.exists(self.features_file):
            try:
                npz = np.load(self.features_file)
                for k in npz.files:
                    self.features[k] = npz[k]
            except Exception:
                self.features = {}

    def save_index(self):
        os.makedirs(self.cache_dir, exist_ok=True)
        data = {
            "manifest_version": self.manifest_version,
            "total_identities": len(self.identities),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "identities": self.identities
        }
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        if self.features:
            np.savez_compressed(self.features_file, **self.features)

    def add_identity(self, pid: str, name: str, photo_rel_path: str, face_emb: np.ndarray, hog_feat: np.ndarray):
        full_path = os.path.join(self.gallery_dir, os.path.basename(photo_rel_path))
        checksum = "N/A"
        if os.path.exists(full_path):
            with open(full_path, "rb") as f:
                checksum = hashlib.sha256(f.read()).hexdigest()
        
        self.identities[pid] = {
            "name": name,
            "rel_path": photo_rel_path,
            "checksum": checksum,
            "added_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.features[f"{pid}_face"] = face_emb
        self.features[f"{pid}_hog"] = hog_feat
        self.save_index()

    def remove_identity(self, pid: str) -> bool:
        if pid in self.identities:
            del self.identities[pid]
            self.features.pop(f"{pid}_face", None)
            self.features.pop(f"{pid}_hog", None)
            self.save_index()
            return True
        return False

    def validate_gallery(self) -> dict:
        total_images = len(self.identities)
        unique_pids = len(set(self.identities.keys()))
        valid_files = 0
        corrupted = []

        for pid, meta in self.identities.items():
            fname = os.path.basename(meta["rel_path"])
            fpath = os.path.join(self.gallery_dir, fname)
            if os.path.exists(fpath):
                valid_files += 1
            else:
                corrupted.append(pid)

        return {
            "total_images": total_images,
            "unique_identities": unique_pids,
            "valid_files": valid_files,
            "corrupted_count": len(corrupted),
            "corrupted_pids": corrupted,
            "cache_synced": len(self.features) == unique_pids * 2
        }

    def search_top_k(self, q_face: np.ndarray, q_hog: np.ndarray, alpha: float = 0.85, top_k: int = 10) -> list:
        results = []
        for pid, meta in self.identities.items():
            f_key = f"{pid}_face"
            h_key = f"{pid}_hog"
            if f_key in self.features and h_key in self.features:
                f_sim = float(np.dot(q_face, self.features[f_key]))
                h_sim = float(np.dot(q_hog, self.features[h_key]))
                fused = alpha * f_sim + (1.0 - alpha) * h_sim
                results.append({
                    "pid": pid,
                    "name": meta["name"],
                    "path": meta["rel_path"],
                    "score": fused,
                    "deep_score": f_sim,
                    "hog_score": h_sim
                })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
