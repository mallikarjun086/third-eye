import base64
import io
from typing import Optional, Dict, Any
import numpy as np
import cv2
from PIL import Image

class SpatialXAIExplainer:
    """
    Explainable AI (XAI) Saliency & Heatmap Generator for Forensic Face Sketch Matching.
    Computes spatial cell correlation across anatomical facial landmarks (eyes, nose, mouth, contour)
    and renders a color-coded saliency heatmap overlay highlighting matching anatomical regions.
    """

    @staticmethod
    def explain_alignment(sketch_grey: Optional[np.ndarray], photo_grey: Optional[np.ndarray]) -> Dict[str, Any]:
        if sketch_grey is None or photo_grey is None:
            return {
                "eyes_match": 0.0,
                "nose_match": 0.0,
                "mouth_match": 0.0,
                "contour_match": 0.0,
                "overall_xai_confidence": 0.0,
                "heatmap_b64": ""
            }

        # Normalize dimensions to 160x160
        s_img = cv2.resize(sketch_grey, (160, 160)).astype(np.float32)
        p_img = cv2.resize(photo_grey, (160, 160)).astype(np.float32)

        # Compute Sobel edge magnitude maps
        s_gx = cv2.Sobel(s_img, cv2.CV_32F, 1, 0, ksize=3)
        s_gy = cv2.Sobel(s_img, cv2.CV_32F, 0, 1, ksize=3)
        s_mag = cv2.magnitude(s_gx, s_gy)

        p_gx = cv2.Sobel(p_img, cv2.CV_32F, 1, 0, ksize=3)
        p_gy = cv2.Sobel(p_img, cv2.CV_32F, 0, 1, ksize=3)
        p_mag = cv2.magnitude(p_gx, p_gy)

        # Normalize magnitude maps
        cv2.normalize(s_mag, s_mag, 0, 255, cv2.NORM_MINMAX)
        cv2.normalize(p_mag, p_mag, 0, 255, cv2.NORM_MINMAX)

        # Grid cell analysis (16x16 grid = 10x10 px cells)
        grid_size = 10
        cells_y = 160 // grid_size
        cells_x = 160 // grid_size
        diff_map = np.zeros((cells_y, cells_x), dtype=np.float32)

        for cy in range(cells_y):
            for cx in range(cells_x):
                y1, y2 = cy * grid_size, (cy + 1) * grid_size
                x1, x2 = cx * grid_size, (cx + 1) * grid_size
                cell_s = s_mag[y1:y2, x1:x2]
                cell_p = p_mag[y1:y2, x1:x2]

                norm_s = np.linalg.norm(cell_s)
                norm_p = np.linalg.norm(cell_p)

                if norm_s > 0 and norm_p > 0:
                    sim = float(np.sum(cell_s * cell_p) / (norm_s * norm_p))
                else:
                    sim = 0.5  # Neutral baseline
                diff_map[cy, cx] = np.clip(sim, 0.0, 1.0)

        # Region Bounding Coordinates (y1, y2, x1, x2 in 16x16 grid units)
        # Eyes: Y[3:7], X[2:14]
        eyes_sub = diff_map[3:7, 2:14]
        # Nose: Y[6:11], X[4:12]
        nose_sub = diff_map[6:11, 4:12]
        # Mouth: Y[10:14], X[3:13]
        mouth_sub = diff_map[10:14, 3:13]
        # Contour: Outer perimeter cells
        contour_sub = np.concatenate([diff_map[1:3, :].ravel(), diff_map[13:16, :].ravel()])

        eyes_match = round(float(np.mean(eyes_sub)) * 100.0, 1)
        nose_match = round(float(np.mean(nose_sub)) * 100.0, 1)
        mouth_match = round(float(np.mean(mouth_sub)) * 100.0, 1)
        contour_match = round(float(np.mean(contour_sub)) * 100.0, 1)
        overall_xai = round(float(np.mean(diff_map)) * 100.0, 1)

        # Render Color Heatmap Overlay (COLORMAP_JET: 255 = hot/red, 0 = cold/blue)
        heatmap_resized = cv2.resize(diff_map, (160, 160), interpolation=cv2.INTER_CUBIC)
        heatmap_uint8 = np.clip(255.0 * heatmap_resized, 0, 255).astype(np.uint8)
        color_heatmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)

        p_bgr = cv2.cvtColor(p_img.astype(np.uint8), cv2.COLOR_GRAY2BGR)
        overlay = cv2.addWeighted(p_bgr, 0.60, color_heatmap, 0.40, 0)

        # Encode to Base64 PNG
        is_success, buffer = cv2.imencode(".png", overlay)
        heatmap_b64 = ""
        if is_success:
            heatmap_b64 = f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"

        return {
            "eyes_match": eyes_match,
            "nose_match": nose_match,
            "mouth_match": mouth_match,
            "contour_match": contour_match,
            "overall_xai_confidence": overall_xai,
            "heatmap_b64": heatmap_b64
        }
