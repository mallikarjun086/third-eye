# REPOSITORY CLEANUP PLAN & VERIFICATION MATRIX

**Plan Date**: August 23, 2026  

---

## 1. Action Classifications

| Action Item | Current Path | Size | Reason for Action | Risk Level | Verification Method |
| :--- | :--- | :---: | :--- | :---: | :--- |
| **SAFE DELETE** | `ThirdEye v2/src/thirdeye/v2/elements/aws-java-sdk-1.11.777.jar` | 155.43 MB | Obsolete legacy JAR; ThirdEye v2 uses local FastAPI microservice. | **LOW** | `mvn clean compile` passes cleanly without this JAR. |
| **SAFE DELETE** | `ThirdEye v2/src/thirdeye/v2/elements/sqlite-jdbc-3.30.1.jar` | 5.81 MB | Duplicate JDBC driver; managed by Maven `pom.xml`. | **LOW** | `mvn clean compile` passes cleanly. |
| **SAFE DELETE** | `ThirdEye v2/src/thirdeye/v2/elements/mail-1.4.7.jar` | 0.50 MB | Duplicate JavaMail JAR; managed by Maven `pom.xml`. | **LOW** | `mvn clean compile` passes cleanly. |
| **SAFE DELETE** | `ThirdEye v2/src/thirdeye/v2/elements/activation.jar` | 0.12 MB | Duplicate Activation JAR; managed by Maven `pom.xml`. | **LOW** | `mvn clean compile` passes cleanly. |
| **SAFE DELETE** | `ThirdEye v2/lib/` | 6.43 MB | Obsolete duplicate lib folder. | **LOW** | `mvn clean compile` passes cleanly. |
| **SAFE MOVE** | `ThirdEye v2/src/thirdeye/v2/elements/sketch elements/element softcopy.psd` | 91.14 MB | Photoshop design asset; not read by JavaFX. Move out of src asset directory. | **LOW** | Verify JavaFX canvas loads element PNGs without error. |
| **ARCHIVE** | `ThirdEye_FaceMatch/` | — | Superseded AWS Swing prototype; retained as historical reference. | **ZERO** | Label README as legacy component. |
