# MODEL EXPERIMENT REGISTRY

**Audit Timestamp**: August 24, 2026  
**Auditor**: Lead Machine Learning Engineer & MLOps Auditor  

---

## EXPERIMENT REGISTRY TABLE

| Exp ID | Track | Architecture / Model | Loss / Objective | Training Data | Val Rank-1 | Test Rank-1 | Test Rank-5 | Status | Production Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **EXP-00** | Historical | Raw FaceNet (512-d) | N/A (Pretrained) | N/A | N/A | 12.11% | 23.81% | HISTORICAL | Superseded |
| **EXP-05 (Baseline)** | Track A | FaceNet + Projection Head (128-d) | Triplet Margin (0.3) | CUFS Train (60 PIDs) | 100.00% | **85.71%** | **100.00%** | VERIFIED | **ACCEPTED (PROD BASELINE)** |
| **EXP-05-R (Retrained)** | Track A | FaceNet + Projection Head (128-d) | Triplet Margin + Hard Mining | CUFS Train (60 PIDs) | 45.00% | 23.81% | 42.86% | VERIFIED | **REJECTED (REGRESSION)** |
| **EXP-06-B** | Track B | FaceNet + Projection Head | Penta-Domain Loss | CUFS + CUFSF (1,254 PIDs) | N/A | N/A | N/A | ACCESS PENDING | Blocked (No Physical CUFSF Data) |
| **EXP-06-C** | Track B | FaceNet + Projection Head | Penta-Domain Loss | CUFS + CUFSF + IIIT-D | N/A | N/A | N/A | ACCESS PENDING | Blocked (No Physical IIIT-D Data) |
