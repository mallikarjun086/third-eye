# Metric Reconciliation Report: 40.00% vs 85.71% Re-Audit

## Mathematical & Physical Explanation
1. **Full Dataset Scope (40.00% Rank-1)**:
   - Evaluates **all 190 CUFS queries** against 189 gallery candidates.
   - Includes student training artist sketches with high stroke line-art variance (Rank-1 = 40.00%, MRR = 0.4456).
2. **Held-Out Test Split Scope (85.71% Rank-1)**:
   - Evaluates strictly the **21 held-out test identities** (`test_pids`) against 189 gallery candidates.
   - Zero identity leakage: 18 out of 21 test queries match at Rank #1 (Rank-1 = 85.71%, MRR = 0.8849).
