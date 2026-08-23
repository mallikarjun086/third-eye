"""
ThirdEye v2 — Modality-Aware Forensic Query Quality Assessment Module
"""

import os
import io
import cv2
import numpy as np
from PIL import Image

def detect_modality(image_bytes: bytes) -> str:
    """
    Classifies input query modality into:
    - PHOTO
    - HAND_DRAWN_SKETCH
    - FORENSIC_SKETCH
    - THIRDEYE_COMPOSITE_SKETCH
    - UNKNOWN
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return "UNKNOWN"
        
        h, w, c = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Check standard deviation of color channels (Photos have high color variance)
        b, g, r = cv2.split(img)
        color_diff = np.mean(np.abs(b.astype(float) - g.astype(float))) + np.mean(np.abs(g.astype(float) - r.astype(float)))
        
        # Check background whiteness (Composite sketches have pure white backgrounds)
        white_pixels = np.sum(gray > 240) / (h * w)
        
        # Edge density (Vector composites have high contrast thin lines)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (h * w)
        
        if color_diff > 15.0:
            return "PHOTO"
        elif white_pixels > 0.40 and edge_density > 0.01:
            return "THIRDEYE_COMPOSITE_SKETCH"
        elif color_diff < 5.0 and white_pixels > 0.20:
            return "FORENSIC_SKETCH"
        elif color_diff < 10.0:
            return "HAND_DRAWN_SKETCH"
        else:
            return "UNKNOWN"
    except Exception:
        return "UNKNOWN"

def evaluate_query_quality(image_bytes: bytes) -> dict:
    """
    Evaluates query quality using modality-specific rules.
    Does NOT reject sketches solely because a photo-trained face detector misses.
    """
    modality = detect_modality(image_bytes)
    warnings = []
    quality_accepted = True
    quality_score = 1.0
    
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {
                "query_accepted": False,
                "quality_score": 0.0,
                "warnings": ["Corrupted or unparseable image file."],
                "detected_modality": "UNKNOWN",
                "reason": "Image decoding failed."
            }
        
        h, w = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Resolution Check
        if h < 80 or w < 80:
            warnings.append(f"Low image resolution ({w}x{h}). Minimum recommended is 80x80.")
            quality_score -= 0.25
            if h < 40 or w < 40:
                quality_accepted = False
        
        # 2. Contrast Check
        std_dev = float(np.std(gray))
        if std_dev < 15.0:
            warnings.append(f"Extremely low image contrast (std dev: {std_dev:.1f}).")
            quality_score -= 0.20
        
        # 3. Blur Check (Laplacian Variance)
        laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if laplacian_var < 10.0 and modality == "PHOTO":
            warnings.append(f"Image is blurred (Laplacian variance: {laplacian_var:.1f}).")
            quality_score -= 0.20
        
        # 4. Modality-Specific Checks
        if modality in ["THIRDEYE_COMPOSITE_SKETCH", "FORENSIC_SKETCH", "HAND_DRAWN_SKETCH"]:
            # Detector miss is expected on clean vector drawings or pencil sketches
            warnings.append(f"Modality detected as {modality}. Sketch-aware feature extraction enabled.")
        
        quality_score = max(0.0, min(1.0, quality_score))
        
        reason = "Query quality is acceptable for forensic comparison."
        if not quality_accepted:
            reason = "Query image quality is insufficient for reliable comparison."
        elif len(warnings) > 0:
            reason = f"Query accepted with {len(warnings)} warning(s)."
        
        return {
            "query_accepted": quality_accepted,
            "quality_score": round(quality_score, 2),
            "warnings": warnings,
            "detected_modality": modality,
            "resolution": f"{w}x{h}",
            "reason": reason
        }
    except Exception as e:
        return {
            "query_accepted": True,
            "quality_score": 0.50,
            "warnings": [f"Quality evaluation error: {str(e)}"],
            "detected_modality": "UNKNOWN",
            "reason": "Exploratory search permitted."
        }
