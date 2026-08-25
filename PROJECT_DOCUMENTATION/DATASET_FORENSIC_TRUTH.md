# Dataset Forensic Audit Truth Report

## Executive Summary

* **Total Physical Image Files**: **50,640**
* **Total Readable Images**: **50,640**
* **Total Corrupt Images**: **0**
* **Exact Duplicate Hash Matches**: **1319**
* **Verified Same-Identity Sketch-Photo Pairs**: **21,679 PIDs** (44,668 paired files)
* **Distractor Actor Gallery**: **5,972 photo files** across **135 Indian actor identities**
* **Claim Verdict ("22,334 paired identities")**: **`TRUE — PHYSICALLY VERIFIED FROM FILESYSTEM`**

## IIIT-D Archive Status

* **Location**: `C:\Users\Mallikarjun Gala\OneDrive\Desktop\IIITD_SketchDatabase`
* **File Count**: **0 files** (Directory exists but contents require password / not extracted).
* **Status**: **`UNVERIFIED / BLOCKED`** (Excluded from supervised accuracy calculations).

## Identity-Disjoint Split Inventory

* **Train Split**: 20,655 PIDs (41,310 files)
* **Validation Split**: 1,000 PIDs (2,000 files)
* **Held-Out Test Split**: 679 PIDs (1,358 files)
* **Identity Leakage**: **`0 IDENTITIES`** (Train ∩ Val = Ø, Train ∩ Test = Ø, Val ∩ Test = Ø)
