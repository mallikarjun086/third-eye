"""
EXP-01: FACIAL LANDMARK ALIGNMENT EXPERIMENT
Evaluates the impact of 5-point facial landmark alignment (MediaPipe Face Mesh)
on cross-modal forensic sketch-to-photo matching accuracy.

Evaluates 4 Conditions:
1. Baseline: Unaligned Gallery + Unaligned Queries (Reference: 46.3% Rank-1)
2. EXP-01A: Aligned Gallery + Unaligned Queries
3. EXP-01B: Unaligned Gallery + Aligned Queries
4. EXP-01C: Aligned Gallery + Aligned Queries
"""

import os
import sys
import time
import io
import json
import csv
import numpy as np
import cv2
import cv2.data
from PIL import Image

# Ensure ml_service directory is in python path
ml_service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ml_service_dir not in sys.path:
    sys.path.insert(0, ml_service_dir)

# Import feature extraction functions from app.py
from app import load_model, embed_image, HOG_SIZE, hog_grey, _face_weight_map

# Global MediaPipe FaceMesh detector instance
mp_face_mesh = None

def init_landmark_detector():
    global mp_face_mesh
    try:
        import mediapipe as mp
        solutions = getattr(mp, 'solutions', None)
        if solutions is not None and hasattr(solutions, 'face_mesh'):
            mp_face_mesh = solutions.face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.3
            )
            print("[INFO] MediaPipe Face Mesh detector initialized successfully.")
        else:
            print("[WARNING] MediaPipe solutions.face_mesh not found. Will use OpenCV Eye Cascade fallback.")
            mp_face_mesh = None
    except Exception as e:
        print(f"[WARNING] MediaPipe initialization failed: {e}. Will use OpenCV Eye Cascade fallback.")
        mp_face_mesh = None


def detect_and_align_face(img_rgb: np.ndarray, target_size: int = 160):
    """
    Detect facial landmarks (eyes) using MediaPipe FaceMesh or OpenCV Fallback.
    Calculates rotation angle, scale, and translation to crop a geometrically
    aligned 160x160 face image with eyes level at y=60.8 (38% height) and IPD=48px (30% width).

    Returns:
        aligned_img (np.ndarray): 160x160 RGB face array
        success (bool): True if landmark alignment succeeded, False if fallback used
        fallback_used (bool): True if fallback was triggered
        details (dict): Landmark coordinates and alignment transformation metadata
    """
    h, w = img_rgb.shape[:2]
    
    left_eye, right_eye = None, None
    success = False

    if mp_face_mesh is not None:
        try:
            results = mp_face_mesh.process(img_rgb)
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0].landmark
                # Left Eye Mesh Indices: 33, 133, 159, 145
                lx = np.mean([landmarks[idx].x * w for idx in [33, 133, 159, 145]])
                ly = np.mean([landmarks[idx].y * h for idx in [33, 133, 159, 145]])
                left_eye = np.array([lx, ly])

                # Right Eye Mesh Indices: 362, 263, 386, 374
                rx = np.mean([landmarks[idx].x * w for idx in [362, 263, 386, 374]])
                ry = np.mean([landmarks[idx].y * h for idx in [362, 263, 386, 374]])
                right_eye = np.array([rx, ry])

                success = True
        except Exception as e:
            success = False

    # OpenCV Cascade Fallback if MediaPipe undetected
    if not success:
        try:
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            eyes = eye_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            if len(eyes) >= 2:
                eyes = sorted(eyes, key=lambda e: e[0])
                left_eye = np.array([eyes[0][0] + eyes[0][2]/2.0, eyes[0][1] + eyes[0][3]/2.0])
                right_eye = np.array([eyes[1][0] + eyes[1][2]/2.0, eyes[1][1] + eyes[1][3]/2.0])
                success = True
        except Exception:
            success = False

    if success and left_eye is not None and right_eye is not None:
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        ipd = np.hypot(dx, dy)

        if ipd >= 10.0:  # Valid inter-pupillary distance threshold
            angle = np.degrees(np.arctan2(dy, dx))
            eye_center = ((left_eye[0] + right_eye[0]) / 2.0, (left_eye[1] + right_eye[1]) / 2.0)

            # Target geometry on target_size x target_size canvas
            target_ipd = 0.30 * target_size
            scale = target_ipd / ipd

            # Compute Affine Rotation & Scale Matrix
            M = cv2.getRotationMatrix2D(eye_center, angle, scale)

            # Adjust translation so eye center maps to (0.5 * target_size, 0.38 * target_size)
            M[0, 2] += (0.5 * target_size - eye_center[0])
            M[1, 2] += (0.38 * target_size - eye_center[1])

            aligned_img = cv2.warpAffine(
                img_rgb, M, (target_size, target_size),
                flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE
            )

            details = {
                "left_eye": [float(left_eye[0]), float(left_eye[1])],
                "right_eye": [float(right_eye[0]), float(right_eye[1])],
                "angle": float(angle),
                "ipd": float(ipd),
                "scale": float(scale)
            }
            return aligned_img, True, False, details

    # Fallback: Canonical Lanczos resize without rotation
    aligned_img = cv2.resize(img_rgb, (target_size, target_size), interpolation=cv2.INTER_LANCZOS4)
    details = {"fallback_reason": "No valid landmarks detected or IPD too small"}
    return aligned_img, False, True, details


def extract_features_for_image(img_path: str, apply_alignment: bool = False):
    """
    Extract FaceNet embedding and HOG descriptor for an image file path.
    Applies facial alignment if apply_alignment is True.
    """
    t0 = time.perf_counter()
    img_pil = Image.open(img_path).convert("RGB")
    img_rgb = np.asarray(img_pil)

    landmark_success, fallback_used = False, False
    alignment_details = {}

    if apply_alignment:
        img_rgb, landmark_success, fallback_used, alignment_details = detect_and_align_face(img_rgb, target_size=160)
    else:
        img_rgb = cv2.resize(img_rgb, (160, 160), interpolation=cv2.INTER_LANCZOS4)

    # Encode back to PNG bytes for app pipeline extractors
    is_success, buffer = cv2.imencode(".png", cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR))
    img_bytes = buffer.tobytes()

    emb = embed_image(img_bytes)
    
    # Extract HOG vector with CLAHE contrast enhancement
    grey = hog_grey(img_bytes)
    h_hog, w_hog = grey.shape
    cells_y, cells_x = h_hog // 8, w_hog // 8
    
    # Compute Sobel gradients
    gx = cv2.Sobel(grey, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(grey, cv2.CV_64F, 0, 1, ksize=3)
    mag = np.hypot(gx, gy)
    ori = np.arctan2(gy, gx) * (180.0 / np.pi) % 180.0

    orientations = 9
    bin_width = 180.0 / orientations
    cell_descs = np.zeros((cells_y, cells_x, orientations), dtype=np.float64)

    for cy in range(cells_y):
        for cx in range(cells_x):
            m_c = mag[cy*8:(cy+1)*8, cx*8:(cx+1)*8]
            o_c = ori[cy*8:(cy+1)*8, cx*8:(cx+1)*8]
            for b in range(orientations):
                b_min, b_max = b * bin_width, (b + 1) * bin_width
                mask = (o_c >= b_min) & (o_c < b_max)
                cell_descs[cy, cx, b] = m_c[mask].sum()

    w_map = _face_weight_map(cells_x, cells_y)
    weighted_descs = cell_descs * w_map[:, :, np.newaxis]
    hog_vec = weighted_descs.ravel()
    hog_norm = np.linalg.norm(hog_vec)
    if hog_norm > 0:
        hog_vec = hog_vec / hog_norm

    t1 = time.perf_counter()
    latency_ms = (t1 - t0) * 1000.0

    return {
        "emb": emb,
        "hog": hog_vec,
        "landmark_success": landmark_success,
        "fallback_used": fallback_used,
        "latency_ms": latency_ms,
        "aligned_img": img_rgb,
        "details": alignment_details
    }


def to_pid(filename: str) -> str:
    base = os.path.splitext(os.path.basename(filename))[0]
    return base.replace("-01-sz1", "").replace("-01", "")


def run_evaluation_condition(
    condition_name: str,
    gallery_files: list,
    query_files: list,
    gallery_dir: str,
    query_dir: str,
    align_gallery: bool,
    align_query: bool,
    output_dir: str
):
    print(f"\n========================================================")
    print(f" Running Evaluation: {condition_name}")
    print(f" Gallery Aligned: {align_gallery} | Queries Aligned: {align_query}")
    print(f"========================================================")

    gallery_features = []
    gal_landmarks_success = 0
    gal_fallbacks = 0
    gal_latencies = []

    for f in gallery_files:
        path = os.path.join(gallery_dir, f)
        res = extract_features_for_image(path, apply_alignment=align_gallery)
        gallery_features.append({
            "filename": f,
            "pid": to_pid(f),
            "emb": res["emb"],
            "hog": res["hog"]
        })
        if res["landmark_success"]:
            gal_landmarks_success += 1
        if res["fallback_used"]:
            gal_fallbacks += 1
        gal_latencies.append(res["latency_ms"])

    rank_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    query_landmarks_success = 0
    query_fallbacks = 0
    query_latencies = []

    log_rows = []

    for idx, qf in enumerate(query_files):
        qpath = os.path.join(query_dir, qf)
        qpid = to_pid(qf)
        qres = extract_features_for_image(qpath, apply_alignment=align_query)
        qemb, qhog = qres["emb"], qres["hog"]

        if qres["landmark_success"]:
            query_landmarks_success += 1
        if qres["fallback_used"]:
            query_fallbacks += 1
        query_latencies.append(qres["latency_ms"])

        log_rows.append({
            "condition": condition_name,
            "filename": qf,
            "identity": qpid,
            "image_type": "query_sketch",
            "landmark_detection_success": qres["landmark_success"],
            "alignment_applied": align_query and qres["landmark_success"],
            "fallback_used": qres["fallback_used"],
            "latency_ms": round(qres["latency_ms"], 2)
        })

        # Save Visual Sample for first 5 queries
        if idx < 5:
            example_dir = os.path.join(output_dir, "alignment_examples")
            os.makedirs(example_dir, exist_ok=True)
            orig_pil = Image.open(qpath).convert("RGB")
            orig_arr = cv2.resize(np.asarray(orig_pil), (160, 160))
            vis = np.hstack([orig_arr, qres["aligned_img"]])
            vis_bgr = cv2.cvtColor(vis, cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(example_dir, f"{qpid}_{condition_name}_before_after.jpg"), vis_bgr)

        # Match against Gallery
        scores = []
        for g in gallery_features:
            gpid = g["pid"]
            s_face = np.dot(qemb, g["emb"]) if (qemb is not None and g["emb"] is not None) else 0.0
            s_hog = np.dot(qhog, g["hog"]) if (qhog is not None and g["hog"] is not None) else 0.0
            s_hybrid = 0.2 * s_face + 0.8 * s_hog
            scores.append((gpid, s_hybrid, g["filename"]))

        scores.sort(key=lambda x: x[1], reverse=True)
        top5_pids = [s[0] for s in scores[:5]]

        for r in range(1, 6):
            if qpid in top5_pids[:r]:
                rank_counts[r] += 1

    num_queries = len(query_files)
    metrics = {
        "condition": condition_name,
        "num_queries": num_queries,
        "num_gallery": len(gallery_files),
        "rank1_accuracy": round((rank_counts[1] / num_queries) * 100.0, 2),
        "rank2_accuracy": round((rank_counts[2] / num_queries) * 100.0, 2),
        "rank3_accuracy": round((rank_counts[3] / num_queries) * 100.0, 2),
        "rank4_accuracy": round((rank_counts[4] / num_queries) * 100.0, 2),
        "rank5_accuracy": round((rank_counts[5] / num_queries) * 100.0, 2),
        "gallery_landmark_success_rate": round((gal_landmarks_success / len(gallery_files)) * 100.0, 2),
        "query_landmark_success_rate": round((query_landmarks_success / num_queries) * 100.0, 2),
        "query_fallback_rate": round((query_fallbacks / num_queries) * 100.0, 2),
        "avg_query_latency_ms": round(float(np.mean(query_latencies)), 2)
    }

    print(f" Metrics for {condition_name}:")
    print(f"   Rank-1: {metrics['rank1_accuracy']}%")
    print(f"   Rank-5: {metrics['rank5_accuracy']}%")
    print(f"   Query Landmark Success: {metrics['query_landmark_success_rate']}%")
    print(f"   Avg Query Latency: {metrics['avg_query_latency_ms']} ms")

    return metrics, log_rows


def main():
    load_model()
    init_landmark_detector()

    # Base directory is ml_service
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    gallery_dir = os.path.join(base_dir, "dataset", "gallery")
    query_dir = os.path.join(base_dir, "dataset", "queries")

    exp_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(exp_dir, exist_ok=True)
    os.makedirs(os.path.join(exp_dir, "failure_cases"), exist_ok=True)

    gallery_files = sorted([f for f in os.listdir(gallery_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    query_files = sorted([f for f in os.listdir(query_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])

    print(f"Loaded {len(gallery_files)} gallery photos and {len(query_files)} query sketches.")

    all_logs = []

    # Condition 1: BASELINE (Unaligned Gallery + Unaligned Queries)
    res_base, log_base = run_evaluation_condition(
        "Baseline", gallery_files, query_files, gallery_dir, query_dir,
        align_gallery=False, align_query=False, output_dir=exp_dir
    )
    all_logs.extend(log_base)
    with open(os.path.join(exp_dir, "baseline_results.json"), "w") as f:
        json.dump(res_base, f, indent=2)

    # Condition 2: EXP-01A (Aligned Gallery + Unaligned Queries)
    res_01a, log_01a = run_evaluation_condition(
        "EXP-01A", gallery_files, query_files, gallery_dir, query_dir,
        align_gallery=True, align_query=False, output_dir=exp_dir
    )
    all_logs.extend(log_01a)
    with open(os.path.join(exp_dir, "exp01A_results.json"), "w") as f:
        json.dump(res_01a, f, indent=2)

    # Condition 3: EXP-01B (Unaligned Gallery + Aligned Queries)
    res_01b, log_01b = run_evaluation_condition(
        "EXP-01B", gallery_files, query_files, gallery_dir, query_dir,
        align_gallery=False, align_query=True, output_dir=exp_dir
    )
    all_logs.extend(log_01b)
    with open(os.path.join(exp_dir, "exp01B_results.json"), "w") as f:
        json.dump(res_01b, f, indent=2)

    # Condition 4: EXP-01C (Aligned Gallery + Aligned Queries)
    res_01c, log_01c = run_evaluation_condition(
        "EXP-01C", gallery_files, query_files, gallery_dir, query_dir,
        align_gallery=True, align_query=True, output_dir=exp_dir
    )
    all_logs.extend(log_01c)
    with open(os.path.join(exp_dir, "exp01C_results.json"), "w") as f:
        json.dump(res_01c, f, indent=2)

    # Save alignment_log.csv
    csv_log_path = os.path.join(exp_dir, "alignment_log.csv")
    with open(csv_log_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "condition", "filename", "identity", "image_type",
            "landmark_detection_success", "alignment_applied", "fallback_used", "latency_ms"
        ])
        writer.writeheader()
        writer.writerows(all_logs)

    # Save comparison.csv
    comp_path = os.path.join(exp_dir, "comparison.csv")
    results_list = [res_base, res_01a, res_01b, res_01c]
    with open(comp_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "condition", "rank1_accuracy", "rank2_accuracy", "rank3_accuracy",
            "rank4_accuracy", "rank5_accuracy", "gallery_landmark_success_rate",
            "query_landmark_success_rate", "query_fallback_rate", "avg_query_latency_ms"
        ])
        writer.writeheader()
        for r in results_list:
            writer.writerow({
                "condition": r["condition"],
                "rank1_accuracy": r["rank1_accuracy"],
                "rank2_accuracy": r["rank2_accuracy"],
                "rank3_accuracy": r["rank3_accuracy"],
                "rank4_accuracy": r["rank4_accuracy"],
                "rank5_accuracy": r["rank5_accuracy"],
                "gallery_landmark_success_rate": r["gallery_landmark_success_rate"],
                "query_landmark_success_rate": r["query_landmark_success_rate"],
                "query_fallback_rate": r["query_fallback_rate"],
                "avg_query_latency_ms": r["avg_query_latency_ms"]
            })

    print(f"\n========================================================")
    print(" EXP-01 COMPARISON SUMMARY")
    print(f"========================================================")
    print(f" Condition   | Rank-1  | Rank-5  | Query Landmark Success | Latency")
    print(f" ------------|---------|---------|------------------------|---------")
    for r in results_list:
        print(f" {r['condition']:<11} | {r['rank1_accuracy']:>5.1f}%  | {r['rank5_accuracy']:>5.1f}%  | {r['query_landmark_success_rate']:>20.1f}%   | {r['avg_query_latency_ms']:>5.1f}ms")
    print(f"========================================================\n")


if __name__ == "__main__":
    main()
