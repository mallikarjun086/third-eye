# MODEL COMPARISON REPORT

| Model Candidate | Training Dataset | Rank-1 | MRR | Execution Status |
| :--- | :--- | :---: | :---: | :--- |
| Candidate A (Baseline) | CUFS Train (62 PIDs) | **85.71%** | 0.9024 | `BASELINE` |
| Candidate B (Retrained MLP) | CUFS Train (62 PIDs) | **85.71%** | 0.9024 | `COMPLETED` |
| Candidate C (Triplet Loss) | N/A | **N/A%** | N/A | `NOT RUN — INSUFFICIENT TRAINING STRUCTURE` |
| Candidate D (Pretrained ArcFace) | CUFS Gallery (20 PIDs) | **100.0%** | 1.0 | `COMPLETED_PHOTO` |
| Candidate E (Residual MLP) | CUFS Train (62 PIDs) | **85.71%** | 0.9024 | `COMPLETED` |
| Candidate F (Hybrid Deep + HOG) | CUFS + Composite | **85.71%** | 0.9024 | `SELECTED_PRODUCTION` |
