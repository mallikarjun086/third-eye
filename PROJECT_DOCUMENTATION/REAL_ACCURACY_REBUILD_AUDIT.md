# THIRDEYE V2 — REAL ACCURACY REBUILD FORENSIC AUDIT

**Audit Date**: August 24, 2026  
**Auditor**: Lead Computer Vision Research Engineer & Senior Software Architect  
**Repository**: `https://github.com/mallikarjun086/third-eye.git`  

---

## 1. EXECUTIVE DIAGNOSIS: THE REAL PHOTO FAILURE SCENARIO

### Root Cause Analysis of Low Photo Similarity (~15%)

When a user uploads a real photograph of a face to ThirdEye v2:

1. **Modality Mis-routing**: The backend `/match` endpoint previously processed ALL queries through the `CROSS_MODAL_SKETCH` pipeline.
2. **Projection Head Distortion**: The 512-d FaceNet embedding of the real photo was passed through `_proj_model` (a 2-layer MLP trained on sketch-photo pairs). Because the projection head was trained to map sketch features into a joint space, applying it to a real photograph distorts the photo's feature vector, causing similarity against gallery photos to collapse to ~15-25%.
3. **Absence of Query Modality Routing**: The system lacked an automatic query modality classifier to distinguish between `PHOTO`, `ARTIST_SKETCH`, `COMPOSITE_FORENSIC_SKETCH`, and `UNKNOWN_OR_LOW_QUALITY`.
4. **Closed-Set Assumption**: The legacy matching engine forced the highest scoring candidate to appear as a match even when similarity was as low as 15%, lacking an **Open-Set Rejection Mechanism** (`NO RELIABLE MATCH FOUND IN CURRENT GALLERY`).

---

## 2. REPOSITORY CORE COMPONENTS AUDIT

| Component Area | File Path | Current Status | Mandatory Rebuild Action |
| :--- | :--- | :--- | :--- |
| **JavaFX Desktop UI** | `src/thirdeye/v2/Upload_sketchController.java` | Closed-set score display | Render Query Type, Selected Pipeline, Match Decision (`POSSIBLE MATCH` vs `NO RELIABLE MATCH`) |
| **JDK REST Client** | `src/thirdeye/v2/DeepMatchClient.java` | Parses `name`, `path`, `similarity` | Extend `Match` object to parse `queryModality`, `selectedPipeline`, `matchDecision`, `calibratedScore` |
| **FastAPI ML Service** | `ml_service/app.py` | Single sketch pipeline for all inputs | Integrate `QueryRouter`, route `PHOTO` to `PHOTO_TO_PHOTO` pipeline, apply open-set thresholds |
| **Query Modality Router** | `ml_service/query_router.py` | **[MISSING]** | **[CREATE]** Image domain classifier (saturation, grayscale variance, edge density, vector structure) |
| **Ground-Truth Manifests** | `ml_service/demo_ground_truth.json` | **[MISSING]** | **[CREATE]** Ground-truth mapping for known demo queries and open-set test queries |
| **Evaluation Suite** | `scripts/run_real_accuracy_evaluation.py` | **[MISSING]** | **[CREATE]** 5-part evaluation runner (Photo, Artist Sketch, Composite Sketch, Open-Set, E2E) |

---

## 3. PHYSICAL DATASET INVENTORY TRUTH

| Dataset | Physical Location | Unique PIDs | Image Count | Legal / License Status | Integration Status |
| :--- | :--- | :---: | :---: | :--- | :--- |
| **CUFS (CUHK)** | `ml_service/dataset/` | **190 PIDs** | 381 | Open Academic | **INTEGRATED (Track A)** |
| **ThirdEye Composite** | `ml_service/dataset/queries/` | **2 PIDs** | 2 | Internal Benchmark | **INTEGRATED (Track A)** |
| **CUFSF (FERET)** | `data/cufsf/` | 0 | 0 | Signed EULA Required | `NOT INTEGRATED — ACCESS PENDING` |
| **IIIT-D Forensic** | `data/iiitd/` | 0 | 0 | IPAG EULA Required | `NOT INTEGRATED — ACCESS PENDING` |

---

## 4. SCIENTIFIC REBUILD STRATEGY

1. **Implement `ml_service/query_router.py`**: Automatically detect query modality using image features.
2. **Dedicated Photo-to-Photo Pipeline**: For `PHOTO` queries, route directly to raw 512-d FaceNet cosine matching.
3. **Open-Set Decision Logic**: If $\text{Top Similarity} < \text{Threshold}$, return `NO RELIABLE MATCH FOUND IN CURRENT GALLERY`.
4. **Score Calibration & UI Transparency**: Display calibrated match confidence and clear pipeline explanations in JavaFX.
