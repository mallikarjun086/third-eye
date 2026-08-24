# FINAL SYSTEM EVIDENCE SUMMARY

**Audit Date**: August 24, 2026  
**Auditor**: Senior Technical Auditor & Computer Vision Lead  

---

## CANONICAL SYSTEM FACTS SUMMARY

* **Production Engine**: ThirdEye v2 Local Dual-Stream Engine (FaceNet Projection Head + Spatial Sobel HOG).
* **Cloud Dependency**: **0% (100% Offline / Local)**.
* **Held-Out Test Set Accuracy**: **85.71% Rank-1 / 100.00% Rank-5 / AUC 0.9898** (21 test queries, 189 suspect gallery).
* **ThirdEye Composite Matching**: **Rank #1 (67.93%–68.44%)** for `a-sharukh` composite queries.
* **Data Leakage Status**: **0% Leakage (Strict Zero-Leakage Identity Disjointness)**.
* **Integrated Datasets**: CUFS (190 PIDs) & ThirdEye Composite (2 PIDs).
* **Pending Datasets**: CUFSF (1,194 PIDs) & IIIT-D (459 PIDs) marked `NOT INTEGRATED — ACCESS PENDING`.
* **Model Selection Gate Decision**: Retrained model on Track A data showed regression (23.81% Rank-1) $\implies$ **Preserved Baseline Model Weights (`best_cross_modal_model.weights.h5`)**.
* **Live Integration Suite**: **100% Passed (GET `/health`, POST `/embed`, POST `/match`, POST `/rebuild_cache`)**.
* **Documentation Synchronization**: **100% Synchronized**.
