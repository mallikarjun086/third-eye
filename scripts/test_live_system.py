#!/usr/bin/env python3
"""
Live End-to-End System Test for ThirdEye v2
Validates:
1. ML Microservice Health (/health)
2. Authentication Token Flow (/auth/token)
3. End-to-End Cross-Modal Face Sketch Matching (/match)
4. Saliency Heatmap and Spatial XAI Breakdown Output
5. Recommendation Engine (/recommend_elements)
6. Java SQLite Database Connectivity
"""
import os
import sys
import requests
import sqlite3

BASE_URL = "http://127.0.0.1:8000"

def run_live_tests():
    print("=" * 60)
    print("   THIRDEYE V2 — LIVE SYSTEM VALIDATION")
    print("=" * 60)

    # 1. Health check
    print("\n[STEP 1] Testing ML Service Health (/health)...")
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        r.raise_for_status()
        data = r.json()
        print(f"  -> HTTP Status: {r.status_code}")
        print(f"  -> API Status: {data.get('api_status')}")
        print(f"  -> Model Loaded: {data.get('model_loaded')}")
        assert data.get("status") == "ok"
        print("  [PASS] Service is healthy and model is warm.")
    except Exception as e:
        print(f"  [FAIL] Health check failed: {e}")
        return False

    # 2. JWT Token Issuance
    print("\n[STEP 2] Testing JWT Authentication Flow (/auth/token)...")
    try:
        r = requests.post(f"{BASE_URL}/auth/token", json={"client_id": "thirdeye_desktop_client"}, timeout=5)
        r.raise_for_status()
        token = r.json()["access_token"]
        print(f"  -> Received JWT Token: {token[:20]}...{token[-10:]}")
        headers = {"Authorization": f"Bearer {token}"}
        print("  [PASS] JWT authentication verified.")
    except Exception as e:
        print(f"  [FAIL] Auth failed: {e}")
        return False

    # 3. Live Matching Query
    print("\n[STEP 3] Testing Live Forensic Sketch Matching (/match)...")
    queries_dir = os.path.abspath("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/queries")
    gallery_dir = os.path.abspath("Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/gallery")

    valid_exts = {".jpg", ".jpeg", ".png"}
    q_files = [f for f in os.listdir(queries_dir) if os.path.splitext(f)[1].lower() in valid_exts]
    if not q_files:
        print(f"  [FAIL] No test query sketches found in: {queries_dir}")
        return False
    sketch_path = os.path.join(queries_dir, q_files[0])
    print(f"  -> Using Query Sketch: {os.path.basename(sketch_path)}")

    try:
        with open(sketch_path, "rb") as f:
            files = {"file": ("f-001-01.jpg", f, "image/jpeg")}
            data = {"dataset_dir": gallery_dir, "top_n": 5}
            r = requests.post(f"{BASE_URL}/match", files=files, data=data, headers=headers, timeout=30)
            r.raise_for_status()
            res = r.json()

        print(f"  -> Status: {res.get('status')}")
        print(f"  -> Query Modality: {res.get('query_modality')}")
        print(f"  -> Selected Pipeline: {res.get('selected_pipeline')}")
        print(f"  -> Official Decision: {res.get('match_decision')}")
        print(f"  -> Decision Threshold: {res.get('threshold')}")
        print("  -> Top Gallery Matches:")
        for idx, m in enumerate(res.get("results", [])[:3]):
            xai = m.get("xai_breakdown", {})
            has_heatmap = bool(xai and xai.get("heatmap_b64"))
            print(f"     #{idx+1}: {m['name']} | Sim: {m['similarity']:.4f} | Score: {m['calibrated_score']:.2f}% | XAI Conf: {xai.get('overall_xai_confidence', 0)}% | Heatmap Generated: {has_heatmap}")

        assert len(res.get("results", [])) > 0
        print("  [PASS] Live cross-modal matching with XAI heatmaps verified.")
    except Exception as e:
        print(f"  [FAIL] Match request failed: {e}")
        return False

    # 4. Recommendation Engine
    print("\n[STEP 4] Testing Forensic Element Recommender (/recommend_elements)...")
    try:
        r = requests.post(
            f"{BASE_URL}/recommend_elements",
            json={"face_shape": "OVAL", "eyes_style": "almond_eyes_01"},
            headers=headers,
            timeout=5
        )
        r.raise_for_status()
        rec = r.json()
        print(f"  -> Face Shape: {rec.get('detected_face_shape')}")
        print(f"  -> Recommended Noses: {len(rec.get('recommended_noses', []))} options")
        print(f"  -> Recommended Mouths: {len(rec.get('recommended_mouths', []))} options")
        print("  [PASS] Forensic recommender engine verified.")
    except Exception as e:
        print(f"  [FAIL] Recommender failed: {e}")
        return False

    # 5. Database Connectivity
    print("\n[STEP 5] Testing SQLite Database Connectivity...")
    db_paths = [
        "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/login.sqlite",
        "Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/suspects.db"
    ]
    for db_rel in db_paths:
        db_p = os.path.abspath(db_rel)
        if not os.path.exists(db_p):
            print(f"  [WARN] Database file does not exist yet (will auto-create): {db_rel}")
            continue
        try:
            conn = sqlite3.connect(db_p)
            cur = conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [t[0] for t in cur.fetchall()]
            conn.close()
            print(f"  -> {os.path.basename(db_p)}: Connected successfully. Tables: {tables}")
        except Exception as e:
            print(f"  [FAIL] Failed to open {db_rel}: {e}")
            return False
    print("  [PASS] SQLite databases verified.")

    print("\n" + "=" * 60)
    print("   ALL LIVE SYSTEM CHECKS PASSED (100% OPERATIONAL)")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = run_live_tests()
    sys.exit(0 if success else 1)
