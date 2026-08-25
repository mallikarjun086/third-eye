# FINAL IIIT-D REAL ACCURACY EVALUATION REPORT

**Execution Timestamp**: `2026-08-24T14:41:37Z`  
**IIIT-D Status**: `BLOCKED â€” IIIT-D FILES NOT PRESENT IN LOCAL FILESYSTEM`  

## 1. Honest Accuracy Comparison Table

| Model | Real Training IDs | Dataset | Modality | Test IDs | Gallery IDs | Rank-1 | Rank-5 | MRR | Latency | Status |
| :--- | :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Candidate A (Baseline)** | 62 | CUFS | Artist Sketch | 21 | 189 | **85.71%** | **100.00%** | 0.9024 | 145 ms | Frozen Baseline |
| **Candidate B (Retrained)** | 62 | CUFS | Artist Sketch | 21 | 189 | **85.71%** | **100.00%** | 0.9024 | 145 ms | Validated |
| **Candidate D (ArcFace/FaceNet)** | 20 | CUFS | Real Photo | 20 | 189 | **100.00%** | **100.00%** | 1.0000 | 95 ms | Active Photo Baseline |
| **Candidate F (Selected Production)** | 62 | CUFS+Composite | Cross-Modal | 21 | 189 | **85.71%** | **100.00%** | 0.9024 | 145 ms | **SELECTED_PRODUCTION** |

## 2. Before vs. After IIIT-D Integration Summary

* **New Real Identities Added**: `0` (IIIT-D files physically absent in `data/iiitd` due to encrypted zip archive)
* **New Real Sketch-Photo Pairs Added**: `0`
* **CUFS Artist Sketch Rank-1**: **85.71%** (Unchanged baseline)
* **Photo-to-Photo Rank-1**: **100.00%**
* **ThirdEye Composite Rank-1**: **100.00%**
* **Production Verdict**: `NO VERIFIED SKETCH-TO-PHOTO ACCURACY IMPROVEMENT FROM IIIT-D (ARCHIVE UNEXTRACTED / 0 FILES PRESENT)`
