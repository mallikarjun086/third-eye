# ACCURACY PIPELINE FORENSIC AUDIT REPORT

**Audit Timestamp**: August 24, 2026  
**Auditor**: Lead ML Engineer, Computer Vision Research Engineer & Forensic Technical Auditor  
**Repository**: `https://github.com/mallikarjun086/third-eye.git`  

---

## 1. END-TO-END PRODUCTION PIPELINE TRACE

The exact execution trace of the live sketch-to-photo matching system is documented below:

```
[1. JavaFX UI: Upload_sketchController.java]
    │ User selects/assembles composite sketch (.jpg / .png)
    ▼
[2. Java Client: DeepMatchClient.java]
    │ Constructs JDK HttpClient multipart POST request to http://127.0.0.1:8000/match
    ▼
[3. FastAPI Server: ml_service/app.py -> /match]
    │ Receives raw sketch bytes & dataset_dir parameter
    ▼
[4. Preprocessing & Embedding: hog_grey() + crop_face()]
    │ Re-sizes to 160x160 RGB array, CLAHE contrast enhancement & Gaussian blur
    ▼
[5. Feature Extraction & Cross-Modal Projection]
    │ FaceNet (Inception-ResNet-v1): raw image -> 512-d base embedding
    │ Projection Head (2-layer MLP): 512-d -> 256-d -> 128-d L2-normalized deep feature
    │ Spatial Sobel HOG: 160x160 greyscale -> 3,600-d normalized structural vector
    ▼
[6. Multi-Metric Score Fusion: hybrid_score()]
    │ Fused Score = FACE_WEIGHT * Cosine(Deep_q, Deep_g) + (1 - FACE_WEIGHT) * Cosine(HOG_q, HOG_g)
    │ Verified Optimal Alpha = 0.85 (85% Deep Metric / 15% Spatial HOG)
    ▼
[7. Gallery Search & Top-K Ranking]
    │ Ranks all suspect gallery items by fused similarity score descending
    ▼
[8. Response Serialization & JavaFX Card Rendering]
    │ Returns JSON array of Top-N suspect results to JavaFX client UI
```

## 2. STAGE-BY-STAGE PIPELINE SPECIFICATION

| Pipeline Stage | Source File | Function / Class | Input Shape / Type | Output Shape / Type | Underlying Model / Algorithm | Used in Prod? | Tested? |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: |
| **1. UI Trigger** | `Upload_sketchController.java` | `computeSimilarity()` | User File Path | HTTP Multipart Request | JavaFX Event Handler | YES | YES |
| **2. REST Transport** | `DeepMatchClient.java` | `match()` | File, datasetDir, topN | List<Match> JSON | JDK 11 HttpClient | YES | YES |
| **3. HTTP Handler** | `app.py` | `match()` | Multipart File Upload | `MatchResponse` JSON | FastAPI Router | YES | YES |
| **4. Image Preprocessing** | `app.py` | `crop_face()`, `hog_grey()` | Raw Bytes (`bytes`) | `160x160x3 RGB`, `160x160 Float` | OpenCV CLAHE + Gaussian Blur | YES | YES |
| **5. Base Face Embedding** | `app.py` | `embed_image()` | `160x160x3 RGB` | `(512,) Float32` | `keras_facenet.FaceNet()` | YES | YES |
| **6. Projection Head** | `app.py` | `embed_image()` | `(512,) Float32` | `(128,) Float32` | 2-Layer MLP Projection Network | YES | YES |
| **7. Spatial HOG** | `app.py` | `compute_hog()` | `160x160 Float64` | `(3600,) Float64` | Sobel Gradients + Elliptical Weight Map | YES | YES |
| **8. Score Fusion** | `app.py` | `hybrid_score()` | `face_sim`, `hog_sim` | `Float (0.0 - 1.0)` | $\alpha \cdot S_{\text{deep}} + (1-\alpha) S_{\text{hog}}$ | YES | YES |
| **9. Gallery Search** | `app.py` | `match()` | Fused Scores, Cached Feats | Sorted `MatchResult` List | Linear Top-K Cosine Dot-Product | YES | YES |

## 3. REPOSITORY RECURSIVE COMPONENT CLASSIFICATION

Total Workspace Files Audited: **2004**

| Category | File Count | Key Component Examples |
| :--- | :---: | :--- |
| **DATA** | 383 | `...` |
| **DOCUMENTATION** | 58 | `...` |
| **EXPERIMENT / TRAINING** | 53 | `...` |
| **GENERATED / MANIFEST** | 14 | `...` |
| **LEGACY** | 781 | `...` |
| **PRODUCTION** | 3 | `...` |
| **PRODUCTION MODEL** | 1 | `...` |
| **SOURCE CODE** | 703 | `...` |
| **TEMPORARY / INTERNAL** | 1 | `...` |
| **TEST** | 7 | `...` |
