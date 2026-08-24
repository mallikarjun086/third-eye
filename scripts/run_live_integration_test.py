import os
import sys
import io
import json
import time

WORKSPACE = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
ML_SERVICE = os.path.join(WORKSPACE, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service")
sys.path.insert(0, ML_SERVICE)

from fastapi.testclient import TestClient
import app as ml_app

def main():
    client = TestClient(ml_app.app)
    
    print("========================================================")
    print(" LIVE API & END-TO-END INTEGRATION TEST SUITE")
    print("========================================================")
    
    # 1. Test /health
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print("[OK] GET /health -> Status 200 OK | Model Loaded:", health_data["model_loaded"])
    
    # 2. Test /embed
    sample_sketch = os.path.join(ML_SERVICE, "dataset", "queries", "a-sharukh-1.jpg")
    with open(sample_sketch, "rb") as f:
        img_bytes = f.read()
        
    res = client.post("/embed", files={"file": ("sketch.jpg", img_bytes, "image/jpeg")})
    assert res.status_code == 200, f"Embed failed: {res.text}"
    embed_data = res.json()
    print(f"[OK] POST /embed -> Status 200 OK | Shape: {embed_data['shape']}")
    
    # 3. Test /match
    gallery_dir = os.path.join(ML_SERVICE, "dataset", "gallery")
    res = client.post("/match", files={"file": ("sketch.jpg", img_bytes, "image/jpeg")}, data={"dataset_dir": gallery_dir, "top_n": 5})
    assert res.status_code == 200, f"Match failed: {res.text}"
    match_data = res.json()
    print(f"[OK] POST /match -> Status 200 OK | Results Count: {match_data['count']}")
    top_1 = match_data["results"][0]
    print(f"    Top Match: {top_1['name']} | Similarity: {top_1['similarity']}")
    
    # 4. Test /rebuild_cache
    res = client.post("/rebuild_cache", data={"dataset_dir": gallery_dir})
    assert res.status_code == 200, f"Rebuild cache failed: {res.text}"
    print(f"[OK] POST /rebuild_cache -> Status 200 OK | Images Indexed: {res.json()['images']}")
    
    # 5. Output JSON Evidence
    evidence = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "health_check": "PASS",
        "embed_check": "PASS",
        "match_check": "PASS",
        "rebuild_cache_check": "PASS",
        "top_match_name": top_1['name'],
        "top_match_similarity": top_1['similarity']
    }
    
    out_file = os.path.join(WORKSPACE, "PROJECT_DOCUMENTATION", "LIVE_API_INTEGRATION_EVIDENCE.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(evidence, f, indent=2)
        
    print("\nALL LIVE INTEGRATION TESTS PASSED 100% SUCCESSFUL!")

if __name__ == "__main__":
    main()
