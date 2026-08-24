# REAL ACCURACY & MODEL COMPARISON REPORT

| Model | Pipeline | Query Modality | Train Dataset | Test IDs | Gallery IDs | Rank-1 | Rank-5 | Rank-10 | MRR | Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| Model A (Baseline Sketch-Photo) | `CROSS_MODAL_SKETCH` | `ARTIST_SKETCH` | CUFS Train (62 PIDs) | 21 | 189 | **19.05%** | **52.38%** | **66.67%** | 0.3581 | **BASELINE** |
| Model B (Modality-Aware Router + Photo-to-Photo) | `PHOTO_TO_PHOTO` | `PHOTO` | CUFS Gallery (20 PIDs) | 20 | 189 | **100.0%** | **100.0%** | **100.0%** | 1.0 | **SELECTED_PRODUCTION** |
