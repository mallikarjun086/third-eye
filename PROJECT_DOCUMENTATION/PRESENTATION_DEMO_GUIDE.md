# PRESENTATION & LIVE DEMO GUIDE

**System**: ThirdEye v2 — Modality-Aware Forensic Face Retrieval & Open-Set Suspect Search  
**Target Audience**: Forensic Auditors, Computer Vision Researchers, Evaluation Panel  

---

## 3 REPRODUCIBLE LIVE DEMONSTRATIONS

### 🎥 DEMO 1: Known Identity Real Photo Retrieval (`PHOTO -> PHOTO`)

* **Goal**: Demonstrate 100% accurate recognition when a real photographic face is uploaded.
* **Input Query**: `dataset/gallery/a-sharukh.jpg`
* **Expected System Behavior**:
  * **Detected Query Type**: `PHOTO`
  * **Selected Recognition Pipeline**: `PHOTO_TO_PHOTO`
  * **Match Decision**: `POSSIBLE MATCH`
  * **Top Result**: `a-sharukh` @ **100.00%** Similarity (Rank #1)

#### Demo 1 Execution Command

```powershell
.\.venv\Scripts\python.exe -c "import requests; r = requests.post('http://127.0.0.1:8000/match', files={'file': open('Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/gallery/a-sharukh.jpg', 'rb')}, data={'dataset_dir': 'dataset/gallery', 'top_n': 3}); print(r.json())"
```

---

### 🎥 DEMO 2: Known Identity Composite Sketch Retrieval (`COMPOSITE_SKETCH -> PHOTO`)

* **Goal**: Demonstrate cross-modal matching for vector composite sketches created in ThirdEye.
* **Input Query**: `dataset/queries/a-sharukh-1.jpg`
* **Expected System Behavior**:
  * **Detected Query Type**: `COMPOSITE_FORENSIC_SKETCH` or `ARTIST_SKETCH`
  * **Selected Recognition Pipeline**: `CROSS_MODAL_COMPOSITE` / `CROSS_MODAL_SKETCH`
  * **Match Decision**: `POSSIBLE MATCH`
  * **Top Result**: `a-sharukh` @ **64.70%** Similarity (Rank #1)

#### Demo 2 Execution Command

```powershell
.\.venv\Scripts\python.exe -c "import requests; r = requests.post('http://127.0.0.1:8000/match', files={'file': open('Project Code (forensic face sketch)/Project Code (forensic face sketch)/ThirdEye v2/ml_service/dataset/queries/a-sharukh-1.jpg', 'rb')}, data={'dataset_dir': 'dataset/gallery', 'top_n': 3}); print(r.json())"
```

---

### 🎥 DEMO 3: Unknown Identity Open-Set Match Rejection (`NO RELIABLE MATCH`)

* **Goal**: Demonstrate open-set rejection when an uploaded query face does NOT exist in the suspect gallery.
* **Input Query**: Random/Unknown Non-Gallery Face
* **Expected System Behavior**:
  * **Top Similarity**: Below calibrated threshold (`< 55%`)
  * **Match Decision**: `NO RELIABLE MATCH FOUND IN CURRENT GALLERY`
  * **UI Candidate Label**: `Nearest Candidates — Not Confirmed Matches`

#### Demo 3 Execution Command

```powershell
.\.venv\Scripts\python.exe -c "import requests, numpy as np, cv2; img = np.random.randint(0, 256, (160, 160, 3), dtype=np.uint8); _, b = cv2.imencode('.jpg', img); r = requests.post('http://127.0.0.1:8000/match', files={'file': ('unknown.jpg', b.tobytes(), 'image/jpeg')}, data={'dataset_dir': 'dataset/gallery', 'top_n': 3}); print(r.json())"
```
