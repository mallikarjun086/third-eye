# METRIC LINEAGE & BASELINE COMPARISON REPORT

**Audit Date**: August 24, 2026  
**Audited Systems**: `HISTORICAL_PRE_REBUILD`, `FROZEN_EXPERIMENT_BASELINE`, `FINAL_SELECTED_PRODUCTION`  

---

## 1. RECONCILIATION OF CONTRADICTORY METRICS

The three historical metrics referenced across documentation versions correspond to distinct development stages:

1. **`HISTORICAL_PRE_REBUILD` ($\alpha = 0.35$ or $0.05$)**:

   - **Composite Match Result**: Rank #10 at 41.12% (or Rank #189 at 26.97%).
   - **Explanation**: In early demo code, `FACE_WEIGHT` was hardcoded to $0.35$ or $0.05$. Spatial Sobel HOG gradient noise on clean vector line drawings dragged down the fused match score, allowing an impostor's background correlation ($46.00\%$) to take Rank #1.
2. **`FROZEN_EXPERIMENT_BASELINE` ($\alpha = 0.85$)**:

   - **Composite Match Result**: Rank #1 at 64.70%.
   - **Explanation**: Setting $\alpha = 0.85$ (85% Deep Projection + 15% HOG) enabled the Cross-Modal FaceNet Projection Head ($71.77\%$ similarity) to drive matching, elevating the true target to Rank #1 while retaining $15\%$ HOG as a structural regularizer.
3. **`FINAL_SELECTED_PRODUCTION` ($\alpha = 0.85$)**:

   - **Composite Match Result**: Rank #1 at 64.70%.
   - **Explanation**: The locked production engine incorporating modality-aware query quality validation and scalable gallery indexing.

---

## 2. LINEAGE COMPARISON MATRIX

| Lineage Version | Commit | Fusion Alpha | Deep Weight | HOG Weight | Query `a-sharukh-1` Rank | Fused Score | Deep Score | HOG Score | Held-Out Test Rank-1 |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `HISTORICAL_PRE_REBUILD` | `8f2a1b0` | `0.35` | 35% | 65% | #10 | 41.12% | 71.77% | 24.61% | 45.00% |
| `FROZEN_EXPERIMENT_BASELINE` | `ff5c0db` | `0.85` | 85% | 15% | **#1** | **64.70%** | **71.77%** | **24.61%** | **85.71%** |
| `FINAL_SELECTED_PRODUCTION` | `7ab70f3` | `0.85` | 85% | 15% | **#1** | **64.70%** | **71.77%** | **24.61%** | **85.71%** |
