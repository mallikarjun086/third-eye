# BUG DATABASE & REMEDIATION LOG

---

## Registered Bugs & Repairs

### BUG-001: Missing `httpx` Dependency for FastAPI TestClient
* **Component**: `ml_service/run_tests.py`
* **Severity**: HIGH
* **Symptom**: `RuntimeError: The starlette.testclient module requires the httpx package to be installed.` when running `run_tests.py`.
* **Root Cause**: `httpx` was not listed in `requirements.txt` as a test dependency.
* **Fix Applied**: Installed `httpx == 0.28.1` into `.venv` and updated `ml_service/requirements.txt`.
* **Status**: **FIXED AND VERIFIED** (all 7 unit tests pass).

---

### BUG-002: Null Callable Warning on `trapz_fn` in NumPy Integration
* **Component**: `ml_service/evaluation_engine.py` line 164
* **Severity**: MEDIUM
* **Symptom**: `Object of type None is not callable` in static analysis.
* **Root Cause**: `getattr(np, 'trapezoid', getattr(np, 'trapz', None))` allowed `trapz_fn` to be inferred as `None`.
* **Fix Applied**: Added explicit `if trapz_fn is None: raise AttributeError(...)` check before calling `trapz_fn`.
* **Status**: **FIXED AND VERIFIED**

---

### BUG-003: Unchecked Null Pointer Access on `app._model.embeddings`
* **Component**: `ml_service/experiments/validation_audit/audit_pipeline.py` lines 157 & 296
* **Severity**: MEDIUM
* **Symptom**: `Attribute embeddings is not defined on None in union None | Unknown`
* **Root Cause**: `app._model` was declared as optional/lazy-loaded `None`.
* **Fix Applied**: Added `assert app._model is not None, "FaceNet model is not loaded"` before property access.
* **Status**: **FIXED AND VERIFIED**

---

### BUG-004: Deprecated `Image.LANCZOS` Reference in Pillow 10+
* **Component**: `ml_service/hybrid_eval.py` lines 87 & 97
* **Severity**: LOW
* **Symptom**: `Attribute LANCZOS is not defined on <module 'PIL.Image'>`
* **Root Cause**: Pillow 10+ moved `LANCZOS` under `Image.Resampling.LANCZOS`.
* **Fix Applied**: Replaced `Image.LANCZOS` with `Image.Resampling.LANCZOS`.
* **Status**: **FIXED AND VERIFIED**

---

### BUG-005: CSS Vendor Prefix Declaration Ordering Warnings
* **Component**: `dashboard.css`, `menu.css`, `upload_sketch.css`
* **Severity**: COSMETIC
* **Symptom**: Linter warning `'background-color' should be listed after '-fx-background-color'`.
* **Root Cause**: Standard CSS fallbacks were listed before JavaFX `-fx-` properties.
* **Fix Applied**: Reordered declarations so standard properties appear after vendor-prefixed properties.
* **Status**: **FIXED AND VERIFIED**
