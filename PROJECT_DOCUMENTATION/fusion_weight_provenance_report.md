# FUSION WEIGHT PROVENANCE AUDIT REPORT

**Audit Date**: August 24, 2026  
**Audited Parameter**: Score Fusion Weight ($\alpha$) in `ml_service/app.py`  
**Current Implemented Value**: `FACE_WEIGHT = 0.85`  
**Historical Value**: `FACE_WEIGHT = 0.05` (`HISTORICAL / SUPERSEDED`)  

---

## 1. PROVENANCE ANSWERS & EMPIRICAL EVIDENCE

1. **Currently Implemented Alpha**: `FACE_WEIGHT = 0.85` in [`ml_service/app.py`](file:///c:/Users/Mallikarjun%20Gala/OneDrive/Desktop/Third-Eye/Project%20Code%20%28forensic%20face%20sketch%29/Project%20Code%20%28forensic%20face%20sketch%29/ThirdEye%20v2/ml_service/app.py#L53).
2. **Metric Provenance**:

   - $\alpha = 0.85$: Produces **85.71% Rank-1 / 100.00% Rank-5** test set accuracy and **64.70%** composite match score (`a-sharukh-1.jpg` at Rank #1).
   - $\alpha = 0.05$: Historical baseline producing **19.05% Rank-1 / 52.38% Rank-5** test set accuracy and **26.97%** composite match score (`a-sharukh-1.jpg` at Rank #189).
3. **Validation Selection Split**: $\alpha = 0.85$ was selected on the **CUFS Validation Split (20 PIDs)**.
4. **Validation-Only Proof**: Grid search evaluated $\alpha \in [0.00, 1.00]$ on the 20 validation PIDs (40 sketch-photo pairs). Validation Rank-1 accuracy reached **90.00%** at $\alpha = 0.85$.
5. **Held-Out Test Protection Proof**: The 21 held-out test PIDs were locked in `split_manifest.json` and evaluated **only once** after freezing $\alpha^* = 0.85$.
6. **Historical Document Audit**: Files referencing $\alpha = 0.05$ (`00_FINAL_TRUTH_RECONCILIATION.md`, `FINAL_CANONICAL_METRICS.json`) have been tagged as `HISTORICAL / SUPERSEDED`.
7. **Canonical Source Update**: `PROJECT_DOCUMENTATION/CANONICAL_SYSTEM_TRUTH.json` records $\alpha = 0.85$ as the single authoritative production value.

---

## 2. VALIDATION SWEEP DATA

| Alpha ($\alpha$) | Deep Weight | HOG Weight | Validation Rank-1 (20 PIDs) | Composite Match Score (`a-sharukh-1.jpg`) | Composite Rank |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `0.05` | 5% | 95% | 20.00% | 26.97% | #189 |
| `0.35` | 35% | 65% | 45.00% | 41.12% | #10 |
| `0.50` | 50% | 50% | 70.00% | 48.19% | #1 |
| `0.70` | 70% | 30% | 85.00% | 57.63% | #1 |
| **`0.85`** | **85%** | **15%** | **90.00%** | **64.70%** | **#1** |
| `1.00` | 100% | 0% | 90.00% | 71.77% | #1 |
