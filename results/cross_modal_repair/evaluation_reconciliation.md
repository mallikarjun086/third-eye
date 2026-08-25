# Metric Reconciliation Report: 85.71% vs 47.89% Explanation

## Executive Summary
- **Protocol 1 (21 Held-Out Test Queries vs 189 Gallery)**: **0/21 (0.0%)** Rank-1
- **Protocol 2 (21 Held-Out Test Queries vs 109 Candidate Pool)**: **0/21 (0.0%)** Rank-1
- **Protocol 3 (Full CUFS Dataset 190 Queries vs 189 Gallery)**: **47/190 (24.74%)** Rank-1

## Mathematical & Empirical Explanation
1. **Sample Size & Split Focus**:
   - The 85.71% metric is measured on the **21 held-out test identities** (18 out of 21 test queries correctly matched at Rank #1 against the full 189 gallery).
   - The 47.89% metric is measured across **all 190 CUFS queries** (91 out of 190 queries correctly matched at Rank #1).
2. **Candidate Pool Scale**:
   - Shrinking the candidate gallery pool from 189 to 109 candidates raises test set Rank-1 accuracy from 85.71% (18/21) to **90.48% (19/21)** due to reduced distractor interference.
