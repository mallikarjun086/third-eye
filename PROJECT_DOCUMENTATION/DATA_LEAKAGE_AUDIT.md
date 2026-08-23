# DATA LEAKAGE AUDIT REPORT

**Audit Date**: August 23, 2026  
**Auditor**: Automated Forensic Audit Suite  
**Manifest Audited**: `ml_service/split_manifest.json`  

---

## 1. Split Isolation Analysis

To guarantee scientific validity and prevent data leakage, identity IDs (`pids`) were verified across the three dataset splits in `split_manifest.json`:

* **Training Set (`train_pids`)**: 60 distinct identities
* **Validation Set (`val_pids`)**: 20 distinct identities
* **Test Set (`test_pids`)**: 21 distinct identities

### Set Intersection Audit

1. $\text{train\_pids} \cap \text{val\_pids} = \emptyset$ (0 overlapping identities) $\to$ **PASSED**
2. $\text{train\_pids} \cap \text{test\_pids} = \emptyset$ (0 overlapping identities) $\to$ **PASSED**
3. $\text{val\_pids} \cap \text{test\_pids} = \emptyset$ (0 overlapping identities) $\to$ **PASSED**

---

## 2. Conclusion

No identity overlap or data leakage exists between the training set used for the Keras Projection Head (`exp05_cross_modal`), the validation set used for score fusion weight tuning (`exp06_fusion`), and the held-out test set used for canonical benchmark evaluations (`exp07_final_eval` & `audit_pipeline.py`).
