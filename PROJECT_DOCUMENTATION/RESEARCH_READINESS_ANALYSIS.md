# RESEARCH PAPER READINESS & PUBLISHABILITY ANALYSIS

**Project Title**: AI-Based Forensic Face Sketch and Recognition System (`ThirdEye v2`)  
**Assessment Date**: August 23, 2026  
**Evaluator Role**: Computer Vision Researcher & Peer Reviewer  

---

## 1. Overall Readiness Verdict

* **Overall Readiness Rating**: **Conference-Ready after Formal Ablation & Multi-Dataset Validation**
* **Publishability Classification**: **Workshop / Regional IEEE Conference Level** (Current State) $\to$ **Scopus / Q2 Journal Level** (With Recommended Additions).

---

## 2. Technical Novelty Assessment

### Strengths

1. **Empirically Proven Hybrid Fusion**: The combination of a metric-learned 128-d projection head with spatially masked CLAHE HOG features provides a clear, quantitative boost over standard FaceNet (Rank-1 accuracy increases from **12.11% to 85.71%** on the primary 189-candidate gallery and **90.48%** on the test pool protocol).
2. **Modular Architecture**: The codebase demonstrates rigorous engineering practices, including clear dataset splits (`exp01` through `exp07`), automated quality control (`audit_and_qc.py`), canonical metric tracking (`FINAL_CANONICAL_METRICS.json`), and eager model warmup handlers.

### Weaknesses / Gaps in Novelty

1. **Incremental Architecture**: The projection head uses a 2-Dense-layer MLP with Triplet Loss, which is a known metric-learning pattern rather than a radically new neural network operator.
2. **Single Primary Dataset Benchmark**: Primary quantitative results rely on the CUFS benchmark. Validating across multiple independent datasets (e.g., e-PRIP, IIIT-D Sketch Database) is required for tier-1 computer vision conferences (e.g., CVPR, ICCV, IEEE T-PAMI).

---

## 3. Required Enhancements for High-Impact Publication

| Deficiencies in Current Implementation | Required Research Action | Estimated Effort |
| :--- | :--- | :--- |
| **Dataset Diversity** | Evaluate pipeline on additional datasets: IIIT-D Forensic Sketch, e-PRIP Wild Sketches. | 2–3 Days |
| **Deep Learning Baselines** | Compare hybrid model against ArcFace / InsightFace embeddings alongside FaceNet. | 1–2 Days |
| **Statistical Significance** | Compute 95% Confidence Intervals and $p$-values (paired $t$-test / Wilcoxon signed-rank test). | 1 Day |
| **Generative Sketch Pipeline** | Compare manual composite sketch matching accuracy vs AI-generated sketch matching (ControlNet). | 3–4 Days |

---

## 4. Publication Submission Roadmap

```text
[ Current State ] ──> [ Step 1: Benchmark on IIIT-D Dataset ]
                           │
                           ▼
                      [ Step 2: Add ArcFace Baseline Comparison ]
                           │
                           ▼
                      [ Step 3: Formalize Paper Draft (IEEE Template) ]
                           │
                           ▼
                      [ Target: IEEE International Conference on Image Processing (ICIP) / Pattern Recognition (ICPR) ]
```
