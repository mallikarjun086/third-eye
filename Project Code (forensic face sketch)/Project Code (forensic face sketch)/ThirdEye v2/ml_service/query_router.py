"""
ThirdEye Query Modality Router
==============================
Deterministic and visual feature analyzer for classifying face image queries into:
- PHOTO (Real photographic face)
- ARTIST_SKETCH (Hand-drawn pencil/charcoal sketch)
- COMPOSITE_FORENSIC_SKETCH (Digital/vector facial composite)
- UNKNOWN_OR_LOW_QUALITY (Low resolution, corrupt, or unusable image)

Does NOT rely on file extensions. Uses RGB/grayscale distribution, color saturation,
edge density, background uniformity, and structural gradient analysis.
"""

import io
import cv2
import numpy as np
from PIL import Image
from typing import Dict, Any, List


class QueryRouter:
    
    @staticmethod
    def analyze_image_bytes(image_bytes: bytes) -> Dict[str, Any]:
        """Analyze raw image bytes and return modality classification, quality, and routing pipeline."""
        warnings: List[str] = []
        
        if not image_bytes or len(image_bytes) < 10:
            return {
                "modality": "UNKNOWN_OR_LOW_QUALITY",
                "confidence": 0.0,
                "quality_score": 0.0,
                "warnings": ["Empty or invalid image byte payload."],
                "selected_pipeline": "REJECTED_LOW_QUALITY"
            }
            
        try:
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            img_np = np.array(pil_img)
        except Exception as e:
            return {
                "modality": "UNKNOWN_OR_LOW_QUALITY",
                "confidence": 0.0,
                "quality_score": 0.0,
                "warnings": [f"Image decoding failed: {e}"],
                "selected_pipeline": "REJECTED_LOW_QUALITY"
            }
            
        return QueryRouter.analyze_numpy_image(img_np)

    @staticmethod
    def analyze_numpy_image(img_rgb: np.ndarray) -> Dict[str, Any]:
        """Classify RGB numpy image array."""
        warnings: List[str] = []
        h, w = img_rgb.shape[:2]
        
        # 1. Quality & Resolution Check
        min_dim = min(h, w)
        quality_score = min(1.0, float(min_dim) / 160.0)
        
        if min_dim < 48:
            warnings.append(f"Low image resolution ({w}x{h}). Recognition accuracy may drop.")
            return {
                "modality": "UNKNOWN_OR_LOW_QUALITY",
                "confidence": 0.3,
                "quality_score": quality_score,
                "warnings": warnings,
                "selected_pipeline": "REJECTED_LOW_QUALITY"
            }
            
        # 2. Color Saturation & Channel Variance Analysis
        hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
        sat = hsv[:, :, 1]
        mean_sat = float(np.mean(sat))
        max_sat = float(np.max(sat))
        
        r, g, b = img_rgb[:, :, 0], img_rgb[:, :, 1], img_rgb[:, :, 2]
        color_std = float(np.std([np.mean(r), np.mean(g), np.mean(b)]))
        
        # 3. Grayscale & Background Analysis
        gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        blur_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        if blur_val < 15.0:
            warnings.append("Image appears blurry or out of focus.")
            
        # Edge density (Sobel)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        edge_mag = np.sqrt(sobelx**2 + sobely**2)
        edge_density = float(np.mean(edge_mag))
        
        # Background lightness (Outer 10% perimeter)
        border_mask = np.ones((h, w), dtype=bool)
        border_mask[int(h*0.1):int(h*0.9), int(w*0.1):int(w*0.9)] = False
        bg_mean = float(np.mean(gray[border_mask])) if np.any(border_mask) else float(np.mean(gray))
        
        # 4. Decision Rules
        
        # A. PHOTO: High color saturation and RGB variance
        if mean_sat > 25.0 or color_std > 8.0:
            return {
                "modality": "PHOTO",
                "confidence": round(min(0.99, 0.70 + (mean_sat / 100.0)), 2),
                "quality_score": round(quality_score, 2),
                "warnings": warnings,
                "selected_pipeline": "PHOTO_TO_PHOTO"
            }
            
        # B. COMPOSITE_FORENSIC_SKETCH: Clean white/light background (>210) & sharp edge features
        if bg_mean > 210.0 and edge_density > 18.0:
            return {
                "modality": "COMPOSITE_FORENSIC_SKETCH",
                "confidence": round(min(0.98, 0.75 + (bg_mean / 500.0)), 2),
                "quality_score": round(quality_score, 2),
                "warnings": warnings,
                "selected_pipeline": "CROSS_MODAL_COMPOSITE"
            }
            
        # C. ARTIST_SKETCH: Monochromatic/Grayscale with continuous pencil shading
        if mean_sat <= 25.0 and color_std <= 8.0:
            return {
                "modality": "ARTIST_SKETCH",
                "confidence": 0.90,
                "quality_score": round(quality_score, 2),
                "warnings": warnings,
                "selected_pipeline": "CROSS_MODAL_ARTIST_SKETCH"
            }
            
        # D. Default Fallback
        return {
            "modality": "UNKNOWN_OR_LOW_QUALITY",
            "confidence": 0.50,
            "quality_score": round(quality_score, 2),
            "warnings": warnings + ["Ambiguous image modality."],
            "selected_pipeline": "FALLBACK_CROSS_MODAL"
        }


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            res = QueryRouter.analyze_image_bytes(f.read())
            print("Router Output:", res)
