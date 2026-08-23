# DOCUMENTATION CONTRADICTION AUDIT & CORRECTION LOG

---

## 1. Contradiction Resolution Log

| Issue ID | Old / Conflicting Claim | Location Found | Verified Codebase Fact | Action Taken |
| :--- | :--- | :--- | :--- | :--- |
| **CONT-001** | AWS Rekognition claimed as current recognition engine. | `Third-Eye-Final-Year-Project/README.md` | `ThirdEye v2` uses local FastAPI microservice with custom Keras projection head & CLAHE HOG. | Corrected; labeled AWS Rekognition as legacy Phase 1 prototype. |
| **CONT-002** | Fusion weight quoted as $\alpha = 0.20$ for production runtime. | Legacy notes | Production `app.py` line 53 sets `FACE_WEIGHT = 0.05`. $\alpha=0.20$ was used in 100-pair evaluation scripts. | Standardized production weight to $\alpha^*=0.05$ across all docs. |
| **CONT-003** | HOG dimensions quoted as 11,552-d for production. | `exp03` notes | Production `app.py` uses custom Sobel HOG ($20 \times 20$ cells $\times 9$ bins = **3,600-d**). 11,552-d was used in OpenCV multi-block experiment. | Documented 3,600-d for production and 11,552-d for OpenCV experiments. |
| **CONT-004** | Password security claimed as `password_hash`. | UI headers | `Login_screenController.java` line 67 executes plaintext queries `WHERE email = ? AND password = ?`. | Corrected; created `SECURITY_MIGRATION_PLAN.md`. |
