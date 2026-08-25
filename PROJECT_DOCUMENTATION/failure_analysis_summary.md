# Root-Cause Failure Analysis Summary

## Evaluation Context

* **Test Set**: CUFS Artist Sketches (21 Queries)
* **Total Failures**: **12 queries** (Rank-1 Misses)
* **Rank-1 Accuracy**: **42.86%** (9/21)

## Failure Mode Classification

1. **SKETCH_PHOTO_DOMAIN_GAP** (12 queries):

   - Severe non-linear stroke distortions causing deep feature distance to exceed impostor margin.
   - Ground-truth photo appeared at Rank 2 and Rank 3.
