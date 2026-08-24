# CUFSF (CUHK Face Sketch FERET Database) Acquisition Instructions

**License / Access Requirement**: Official CUHK MMLab Research License Agreement / EULA  
**Status**: `NOT INTEGRATED — ACCESS PENDING`

## Acquisition Steps:
1. Request access from the official CUHK MMLab site (http://mmlab.ie.cuhk.edu.hk/archive/cufs/).
2. Submit signed academic EULA.
3. Download `cufsf.zip`.
4. Extract files into this directory: `data/cufsf/`.
5. Expected files: `photos/` (1,194 images) and `sketches/` (1,194 images).
6. Run `python data/cufsf/validate.py` to auto-verify image integrity and generate `dataset_manifest.json`.
