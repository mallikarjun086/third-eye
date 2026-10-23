import urllib.request
import json
import os

base_url = "http://127.0.0.1:8000"

print("1. Testing /health...")
try:
    with urllib.request.urlopen(f"{base_url}/health", timeout=5) as resp:
        print("Health status code:", resp.status)
        health_data = json.loads(resp.read().decode())
        print("Health response:", json.dumps(health_data, indent=2))
except Exception as e:
    print("Health check failed:", e)

print("\n2. Testing /auth/token with empty JSON...")
token = None
try:
    req = urllib.request.Request(f"{base_url}/auth/token", data=b"{}", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Auth status code:", resp.status)
        token_data = json.loads(resp.read().decode())
        token = token_data.get("access_token")
        print("Token acquired successfully:", token[:20], "...")
except Exception as e:
    print("Auth check failed:", e)

print("\n3. Testing /auth/token with {'client_id': 'thirdeye_desktop_client'}...")
try:
    req = urllib.request.Request(
        f"{base_url}/auth/token", 
        data=b'{"client_id": "thirdeye_desktop_client"}', 
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        print("Auth client_id status code:", resp.status)
        token_data = json.loads(resp.read().decode())
        print("Token acquired:", token_data.get("access_token")[:20], "...")
except Exception as e:
    print("Auth client_id failed:", e)

print("\n4. Testing /match endpoint...")
import mimetypes

def post_multipart(url, fields, files, token=None):
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    body = bytearray()
    for key, value in fields.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode())
        body.extend(f"{value}\r\n".encode())
    for key, (filename, file_bytes) in files.items():
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"\r\n'.encode())
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(file_bytes)
        body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode())

    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=bytes(body), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.status, resp.read().decode()

root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
gallery_dir = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "dataset", "gallery")
query_file = os.path.join(root, "Project Code (forensic face sketch)", "Project Code (forensic face sketch)", "ThirdEye v2", "ml_service", "dataset", "queries", "F2-005-01-sz1.jpg")

with open(query_file, "rb") as f:
    query_bytes = f.read()

try:
    status, result = post_multipart(
        f"{base_url}/match",
        fields={"dataset_dir": gallery_dir, "top_n": 5, "gender_filter": "ALL", "min_age_filter": 0, "max_age_filter": 100},
        files={"file": ("query.jpg", query_bytes)},
        token=token
    )
    print("Match status code:", status)
    match_data = json.loads(result)
    print("Match decision:", match_data.get("match_decision"))
    print("Candidate count:", match_data.get("count"))
    for idx, r in enumerate(match_data.get("results", [])):
        print(f"  #{idx+1}: {r.get('name')} | score: {r.get('calibrated_score')}% | path: {r.get('path')}")
except Exception as e:
    print("Match request failed:", e)
