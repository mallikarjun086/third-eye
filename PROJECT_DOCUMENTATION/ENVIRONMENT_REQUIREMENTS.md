# ENVIRONMENT REQUIREMENTS & DEPENDENCIES AUDIT

---

## 1. Java Environment Requirements

* **JDK Version**: Java 17+ (Java 21 recommended)
* **Build Tool**: Apache Maven 3.8+
* **Dependencies (via `pom.xml`)**:
  * `org.openjfx:javafx-controls:21`
  * `org.openjfx:javafx-fxml:21`
  * `org.openjfx:javafx-graphics:21`
  * `org.xerial:sqlite-jdbc:3.45.1.0`
  * `com.google.code.gson:gson:2.10.1`

---

## 2. Python Environment Requirements

* **Python Version**: Python 3.9 – 3.13 (Python 3.13 tested and verified)
* **Dependencies (via `ml_service/requirements.txt`)**:
  * `fastapi == 0.141.1`
  * `uvicorn[standard] == 0.52.4`
  * `httpx == 0.28.1`
  * `tensorflow == 2.21.0`
  * `keras-facenet == 0.3.2`
  * `scipy == 1.18.1`
  * `opencv-python == 5.0.0.93`
  * `numpy == 2.5.2`
  * `pillow == 12.3.0`
  * `python-multipart == 0.0.32`
  * `mediapipe == 1.0.1`
  * `matplotlib == 3.11.1`
