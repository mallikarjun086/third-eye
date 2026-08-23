# 03 — CHANGELOG & AUDIT HISTORY

## [v2.1.0] - 2026-08-23

### Added

* Added automated test suite `run_tests.py` with 7 unit & API integration test cases.
* Added `httpx` to virtual environment dependencies and `ml_service/requirements.txt`.
* Added `mediapipe` and `matplotlib` to `ml_service/requirements.txt` for clean-room reproducibility.
* Added null safety check for `trapz_fn` in `evaluation_engine.py`.
* Added non-null assertion for `app._model` in `audit_pipeline.py`.
* Added `import cv2.data` in `exp01_alignment.py`.
* Added automated documentation consistency script `scripts/check_documentation_consistency.py`.

### Changed

* Updated `hybrid_eval.py` to use `Image.Resampling.LANCZOS` for Pillow 10+ compatibility.
* Updated `exp01_alignment.py` to safely resolve MediaPipe FaceMesh via `getattr(mp, 'solutions', None)`.
* Reordered CSS declarations in `dashboard.css`, `menu.css`, and `upload_sketch.css` to place standard properties after `-fx-` vendor prefixes.
* Migrated living documentation system to `PROJECT_DOCUMENTATION/` in repository root.

### Fixed

* Fixed 24 IDE module resolution errors by installing dependencies into `.venv`.
* Fixed 4 Python type safety errors.
* Fixed 21 CSS linter warnings.
