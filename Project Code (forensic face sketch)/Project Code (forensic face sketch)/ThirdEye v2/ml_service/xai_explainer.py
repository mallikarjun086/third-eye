import io
import cv2
import numpy as np
from PIL import Image

class XAIExplainer:
    """
    Explainable AI (XAI) Visual Heatmap Generator for Forensic Face Matching.
    Generates side-by-side spatial saliency heatmaps highlighting matching facial regions
    (eyes, nose, mouth, chin/jawline) between query sketch and candidate photo.
    """

    @staticmethod
    def crop_and_normalize(img_bytes: bytes, size: int = 160) -> np.ndarray:
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        arr = np.asarray(img)
        # Try Haar face crop or resize
        try:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            cascade = cv2.CascadeClassifier(cascade_path)
            grey = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
            faces = cascade.detectMultiScale(grey, 1.1, 4, minSize=(30, 30))
            if len(faces) > 0:
                faces = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)
                fx, fy, fw, fh = faces[0]
                arr = arr[fy:fy+fh, fx:fx+fw]
        except Exception:
            pass
        return cv2.resize(arr, (size, size), interpolation=cv2.INTER_AREA)

    @classmethod
    def generate_heatmap_comparison(cls, query_bytes: bytes, candidate_bytes: bytes, similarity_score: float = 0.85) -> bytes:
        q_img = cls.crop_and_normalize(query_bytes, size=160)
        c_img = cls.crop_and_normalize(candidate_bytes, size=160)

        # Convert to greyscale & apply CLAHE enhancement
        q_gray = cv2.cvtColor(q_img, cv2.COLOR_RGB2GRAY)
        c_gray = cv2.cvtColor(c_img, cv2.COLOR_RGB2GRAY)

        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        q_enhanced = clahe.apply(q_gray)
        c_enhanced = clahe.apply(c_gray)

        # Compute cell-wise feature gradient difference map (20x20 cells of 8x8 pixels)
        cell_size = 8
        grid_h, grid_w = 160 // cell_size, 160 // cell_size
        sim_map = np.zeros((grid_h, grid_w), dtype=np.float32)

        for cy in range(grid_h):
            for cx in range(grid_w):
                y1, y2 = cy * cell_size, (cy + 1) * cell_size
                x1, x2 = cx * cell_size, (cx + 1) * cell_size
                
                q_cell = q_enhanced[y1:y2, x1:x2].astype(np.float32)
                c_cell = c_enhanced[y1:y2, x1:x2].astype(np.float32)

                # Localized gradient correlation
                gx_q = cv2.Sobel(q_cell, cv2.CV_32F, 1, 0, ksize=3)
                gy_q = cv2.Sobel(q_cell, cv2.CV_32F, 0, 1, ksize=3)
                mag_q = np.hypot(gx_q, gy_q)

                gx_c = cv2.Sobel(c_cell, cv2.CV_32F, 1, 0, ksize=3)
                gy_c = cv2.Sobel(c_cell, cv2.CV_32F, 0, 1, ksize=3)
                mag_c = np.hypot(gx_c, gy_c)

                norm_q = np.linalg.norm(mag_q)
                norm_c = np.linalg.norm(mag_c)

                if norm_q > 0 and norm_c > 0:
                    dot = np.sum((mag_q / norm_q) * (mag_c / norm_c))
                    sim_map[cy, cx] = float(np.clip(dot, 0.0, 1.0))
                else:
                    sim_map[cy, cx] = 0.5

        # Upscale heatmap map to 160x160 using bicubic interpolation
        heatmap_large = cv2.resize(sim_map, (160, 160), interpolation=cv2.INTER_CUBIC)
        heatmap_large = np.clip(heatmap_large * 255.0, 0, 255).astype(np.uint8)

        # Apply JET colormap (Red = High match, Blue = Low match)
        heatmap_color = cv2.applyColorMap(heatmap_large, cv2.COLORMAP_JET)
        heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

        # Blend candidate photo with heatmap overlay
        blended = cv2.addWeighted(c_img, 0.65, heatmap_color, 0.35, 0)

        # Create side-by-side composite visualization (Sketch | Candidate + Heatmap)
        margin = 10
        canvas_h = 160 + 40  # 40px bottom bar for labels
        canvas_w = 160 + margin + 160
        canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8) + 245  # light background

        canvas[0:160, 0:160] = q_img
        canvas[0:160, 170:330] = blended

        # Draw labels and scores using OpenCV putText
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(canvas, "QUERY SKETCH", (15, 185), font, 0.45, (30, 30, 30), 1, cv2.LINE_AA)
        cv2.putText(canvas, f"MATCH: {similarity_score*100.0:.1f}%", (180, 185), font, 0.45, (0, 120, 0), 1, cv2.LINE_AA)

        # Encode side-by-side result to PNG format
        success, buf = cv2.imencode(".png", cv2.cvtColor(canvas, cv2.COLOR_RGB2BGR))
        if not success:
            raise ValueError("Could not encode XAI heatmap visualization.")
        return buf.tobytes()
