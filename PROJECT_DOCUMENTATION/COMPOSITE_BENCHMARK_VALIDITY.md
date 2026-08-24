# THIRDEYE COMPOSITE SKETCH BENCHMARK REPORT

**Audit Timestamp**: August 24, 2026  
**Auditor**: Lead Computer Vision Researcher & Technical Auditor  
**Dataset**: ThirdEye Composite Benchmark (`dataset/queries/a-sharukh-1.jpg`, `dataset/queries/a-sharukh-2.jpg`)  
**Gallery Size**: 189 Suspect Photos (`dataset/gallery/`)

---

## 1. COMPOSITE SKETCH PERFORMANCE MATRIX

| Query ID | Query File | Target Suspect PID | Target Rank | Similarity Score | Latency (ms) | Benchmark Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `COMP-001` | `a-sharukh-1.jpg` | `a-sharukh` | **#1** | **67.93%** | 154.5 ms | **PASSED** |
| `COMP-002` | `a-sharukh-2.jpg` | `a-sharukh` | **#1** | **68.44%** | 167.5 ms | **PASSED** |

---

## 2. SAMPLE SIZE DISCLAIMER

> [!NOTE]
> **Sample Size & Acceptance Criteria Statement**:
> The current internal composite benchmark consists of **2 ground-truth composite queries**.
> Achieving Rank #1 on 2/2 queries confirms system readiness and functional integration, but is labeled as **INTERNAL COMPOSITE ACCEPTANCE RESULT (Sample N=2)** rather than general 100% forensic recognition accuracy.
