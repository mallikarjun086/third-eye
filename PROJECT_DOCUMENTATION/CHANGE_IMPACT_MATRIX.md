# CHANGE IMPACT MATRIX

---

| CHANGE TYPE | DIRECT CODE FILES | DOCUMENTATION FILES THAT MUST BE UPDATED | VERIFICATION COMMAND |
| :--- | :--- | :--- | :--- |
| **ML Inference Algorithm Change** | `ml_service/app.py` | `01_CANONICAL_PROJECT_FACTS.md`, `CLAIM_EVIDENCE_MATRIX.md`, `FINAL_PROJECT_REPORT.md`, `VIVA_DEFENSE_GUIDE.md` | `python scripts/check_documentation_consistency.py` |
| **Model Weight Retraining** | `exp05_cross_modal/best_cross_modal_model.weights.h5` | `FINAL_CANONICAL_METRICS.json`, `01_CANONICAL_PROJECT_FACTS.md`, `AUTOMATED_TEST_RUN_REPORT.md`, `03_CHANGELOG.md` | `python ml_service/run_tests.py` |
| **Python Dependency Update** | `ml_service/requirements.txt` | `ENVIRONMENT_REQUIREMENTS.md`, `00_START_HERE.md`, `03_CHANGELOG.md` | `pip install -r requirements.txt` |
| **Java UI / Endpoint Change** | `DeepMatchClient.java`, `Upload_sketchController.java` | `PROJECT_COMPONENTS.md`, `DEPENDENCY_GRAPH.md`, `00_START_HERE.md`, `FINAL_PROJECT_REPORT.md` | `mvn clean compile` |
| **Database Schema Change** | `SuspectDatabase.java`, `connectdb.java` | `SECURITY_MIGRATION_PLAN.md`, `BUG_DATABASE.md`, `FINAL_PROJECT_REPORT.md` | `mvn clean test` |
