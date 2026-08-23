# LARGE FILE POLICY & ASSET AUDIT

**Policy Date**: August 23, 2026  

---

## 1. Classification & Storage Guidelines

| Category | File Examples | Policy / Action | Rationale |
| :--- | :--- | :--- | :--- |
| **TRACK IN GIT** | `best_cross_modal_model.weights.h5` (685 KB) | **Tracked directly in Git** | Essential model weights for 128-d cross-modal projection head. Small size (< 1 MB). |
| **TRACK IN GIT** | `Logo.jpg` (129 KB), element PNGs | **Tracked directly in Git** | Application UI assets. Small (< 1 MB each). |
| **DO NOT TRACK (EXTERNAL/GENERATED)** | `target/`, `__pycache__/`, `.venv/` | **Ignored via `.gitignore`** | Temporary build and virtual environment outputs. |
| **DO NOT TRACK (DEPRECATED BARS)** | `aws-java-sdk-1.11.777.jar` (155.43 MB) | **DELETED** | Unnecessary third-party JAR sitting inside source tree; caused past Git push failures. |
| **DESIGN ASSET (OFFLINE)** | `element softcopy.psd` (91.14 MB) | **Relocated to Media Directory** | Source Photoshop graphic design asset; moved to `Third-Eye-Final-Year-Project/Face Sketch Elements/`. |
