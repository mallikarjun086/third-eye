import os
import sys
import time
import requests

def main():
    print("======================================================================")
    print("TESTING FAST LIVE HTTP MATCH ENDPOINT")
    print("======================================================================")

    url = "http://127.0.0.1:8000/match"
    workspace = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye"
    sketch_path = os.path.join(workspace, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "dataset", "queries", "a-sharukh-1.jpg")
    dataset_dir = r"c:\Users\Mallikarjun Gala\OneDrive\Desktop\Third-Eye\Project Code (forensic face sketch)\Project Code (forensic face sketch)\ThirdEye v2\ml_service\dataset\gallery"

    t0 = time.time()
    with open(sketch_path, "rb") as fh:
        files = {"file": ("001.png", fh, "image/png")}
        data = {"dataset_dir": dataset_dir, "top_n": "10"}
        resp = requests.post(url, files=files, data=data, timeout=10)

    elapsed_ms = (time.time() - t0) * 1000.0
    print(f"HTTP Status: {resp.status_code}")
    print(f"Elapsed Time: {elapsed_ms:.2f} ms")

    if resp.status_code == 200:
        res = resp.json()
        print(f"Query Modality: {res.get('query_modality')}")
        print(f"Match Decision: {res.get('match_decision')}")
        print("\nTOP-10 RESULTS:")
        for r in res.get("results", []):
            print(f" Rank #{r['rank']} | Score: {r['calibrated_score']}% | Suspect: {r['name']} | Path: {r['path']}")
    else:
        print(f"Error Response: {resp.text}")

if __name__ == "__main__":
    main()
