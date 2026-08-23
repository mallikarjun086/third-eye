# LIVING DOCUMENTATION MAINTENANCE PROTOCOL

**Project Code Name**: `ThirdEye v2`  
**Purpose**: Standard Operating Procedure (SOP) for maintaining living documentation across code, model, dataset, and configuration changes.

---

## 1. Documentation Update Rules

Whenever any contributor or developer modifies the repository, the following protocol MUST be executed:

1. **Code Modifications (Java or Python)**:
   - If API endpoints change: Update `PROJECT_COMPONENTS.md`, `DEPENDENCY_GRAPH.md`, `00_START_HERE.md`, `VIVA_DEFENSE_GUIDE.md`, and `FINAL_PROJECT_REPORT.md`.
   - If ML pipeline or feature extraction changes: Update `01_CANONICAL_PROJECT_FACTS.md`, `CLAIM_EVIDENCE_MATRIX.md`, `app.py` constants, and run `python scripts/check_documentation_consistency.py`.

2. **Model Training & Benchmark Updates**:
   - If a model is re-trained or weights are updated: Update `FINAL_CANONICAL_METRICS.json`, `01_CANONICAL_PROJECT_FACTS.md`, `AUTOMATED_TEST_RUN_REPORT.md`, `FINAL_PROJECT_REPORT.md`, and `03_CHANGELOG.md`.

3. **Dependency Changes**:
   - If packages are added/updated: Update `ml_service/requirements.txt`, `ENVIRONMENT_REQUIREMENTS.md`, `pom.xml`, and run unit test suite `run_tests.py`.

4. **Security or Database Schema Changes**:
   - Update `SECURITY_MIGRATION_PLAN.md`, `BUG_DATABASE.md`, `SuspectDatabase.java`, and `connectdb.java`.
