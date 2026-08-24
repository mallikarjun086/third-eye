# FINAL REAL ACCURACY & EVALUATION REPORT

**Audit Timestamp**: August 24, 2026  
**Auditor**: Lead Computer Vision Research Engineer  

---

## 1. MULTI-MODAL ACCURACY MATRIX

| Pipeline | Query Modality | Model | Dataset | Unique IDs | Test Queries | Gallery Size | Rank-1 | Rank-5 | AUC | Median Latency | Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `PHOTO_TO_PHOTO` | `PHOTO` | FaceNet 512d (Raw Cosine) | CUFS Gallery Photos | 20 | 20 | 189 | **100.00%** | **100.00%** | 1.0000 | 226.5 ms | **SELECTED_PRODUCTION** |
| `CROSS_MODAL_SKETCH` | `ARTIST_SKETCH` | FaceNet 128d Projection + HOG (alpha=0.85) | CUFS Test Sketches | 21 | 21 | 189 | **19.05%** | **52.38%** | 0.8996 | 199.3 ms | **SELECTED_PRODUCTION** |
| `CROSS_MODAL_COMPOSITE` | `COMPOSITE_FORENSIC_SKETCH` | FaceNet 128d Projection + HOG (alpha=0.85) | ThirdEye Composite Benchmark | 1 | 2 | 189 | **100.00%** | **100.00%** | 0.9999 | 197.6 ms | **SELECTED_PRODUCTION** |

---

## 2. OPEN-SET MATCH REJECTION BENCHMARK

* **Top Candidate Similarity**: `51.68%`  
* **Calibrated Threshold**: `55.0%`  
* **System Decision**: `NO RELIABLE MATCH FOUND IN CURRENT GALLERY`  
* **Open-Set Test Verdict**: **PASSED**  
