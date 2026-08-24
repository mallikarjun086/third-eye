# DATASET INTEGRATION TRUTH & TRACK SEPARATION REPORT

**Audit Timestamp**: August 24, 2026  
**Auditor**: Lead Technical Auditor & MLOps Engineer  

---

## 1. SCIENTIFIC TRACK SEPARATION DIRECTIVE

To prevent misleading generalization claims from small datasets, evaluation is split into two explicit tracks:

* **TRACK A — CURRENT VERIFIED DATA ONLY**: Utilizes physically present CUFS benchmark (190 PIDs, 189 paired) + 2 internal composite queries.
* **TRACK B — EXPANDED VERIFIED DATA**: Reserved for when CUFSF (1,194 PIDs) and IIIT-D (459 PIDs) datasets are physically downloaded and validated.

---

## 2. DATASET INTEGRATION TRUTH MATRIX

| Dataset Name | Physical Path | Legal Access Status | Integration Status | Track | Unique PIDs | Sketches | Photos | Paired PIDs |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **CUFS (CUHK)** | `ml_service/dataset/` | Open Academic Research | `INTEGRATED` | `TRACK A — CURRENT VERIFIED DATA ONLY` | **190** | 191 | 190 | **189** |
| **CUFSF (FERET)** | `data/cufsf/` | CUHK MMLab Research License Required | `NOT INTEGRATED — ACCESS PENDING` | `TRACK B — EXPANDED VERIFIED DATA` | **0** | 0 | 0 | **0** |
| **IIIT-D Forensic** | `data/iiitd/` | IIIT-Delhi IPAG Research License Required | `NOT INTEGRATED — ACCESS PENDING` | `TRACK B — EXPANDED VERIFIED DATA` | **0** | 0 | 0 | **0** |
| **ThirdEye Composite** | `ml_service/dataset/queries/` | Internal Project Benchmark | `INTEGRATED` | `TRACK A — CURRENT VERIFIED DATA ONLY` | **2** | 2 | 0 | **2** |
