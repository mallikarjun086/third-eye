"""
Third-Eye ML Service Automated Test & Regression Runner
======================================================
Executes comprehensive unit, integration, and regression checks across the
FastAPI endpoints, model loading, feature extraction, and benchmark locks.
"""

import os
import sys
import json
import io
import unittest
import numpy as np
from PIL import Image

# Add current directory to path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

import app
from fastapi.testclient import TestClient

client = TestClient(app.app)


class TestThirdEyeMLService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.load_model()

    def test_01_health_endpoint(self):
        """Verify GET /health response schema and status flags."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["api_status"], "UP")
        self.assertTrue(data["model_loaded"])
        self.assertIsNone(data["model_error"])

    def test_02_empty_image_validation(self):
        """Verify POST /embed rejects empty or invalid byte payloads with HTTP 422 when authenticated."""
        token = app.create_access_token({"sub": "test_client"})
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/embed", files={"file": ("empty.jpg", b"", "image/jpeg")}, headers=headers)
        self.assertEqual(response.status_code, 422)

        response_corrupt = client.post("/embed", files={"file": ("bad.jpg", b"NOT_AN_IMAGE_PAYLOAD", "image/jpeg")}, headers=headers)
        self.assertEqual(response_corrupt.status_code, 422)

    def test_03_crop_face_fallback(self):
        """Verify crop_face fallback handling on empty arrays."""
        blank = np.zeros((0, 0, 3), dtype=np.uint8)
        cropped = app.crop_face(blank, target_size=160)
        self.assertEqual(cropped.shape, (160, 160, 3))

    def test_04_embedding_generation(self):
        """Verify 128-d L2-normalized embedding extraction for a valid synthetic image."""
        img = Image.new("RGB", (160, 160), color=(128, 128, 128))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        emb = app.embed_image(raw_bytes)
        self.assertIsNotNone(emb)
        assert emb is not None
        self.assertEqual(emb.shape, (128,))
        norm = np.linalg.norm(emb)
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_05_hog_feature_computation(self):
        """Verify Sobel HOG descriptor extraction and face-weight masking."""
        arr = np.random.randint(50, 200, (160, 160, 3), dtype=np.uint8)
        img = Image.fromarray(arr, "RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        raw_bytes = buf.getvalue()

        grey = app.hog_grey(raw_bytes)
        self.assertEqual(grey.shape, (160, 160))
        hog = app.compute_hog(grey)
        self.assertGreater(len(hog), 0)
        norm = np.linalg.norm(hog)
        self.assertAlmostEqual(norm, 1.0, places=4)

    def test_06_hybrid_score_calculation(self):
        """Verify hybrid similarity score weighting (alpha = 0.05)."""
        score = app.hybrid_score(face_sim=1.0, hog_sim=1.0)
        self.assertAlmostEqual(score, 1.0, places=4)
        score_mix = app.hybrid_score(face_sim=0.8, hog_sim=0.4)
        expected = app.FACE_WEIGHT * 0.8 + (1.0 - app.FACE_WEIGHT) * 0.4
        self.assertAlmostEqual(score_mix, expected, places=4)

    def test_07_regression_baseline_lock(self):
        """Verify locked model checkpoint hash against ML_REGRESSION_BASELINE.json."""
        baseline_path = os.path.join(base_dir, "ML_REGRESSION_BASELINE.json")
        self.assertTrue(os.path.exists(baseline_path))

        with open(baseline_path) as f:
            lock = json.load(f)

        import hashlib
        weights_path = os.path.join(base_dir, "experiments", "exp05_cross_modal", "best_cross_modal_model.weights.h5")
        self.assertTrue(os.path.exists(weights_path))

        with open(weights_path, "rb") as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()

        self.assertEqual(current_hash, lock["model_checkpoint_lock"]["sha256"])

    def test_08_jwt_authentication_flow(self):
        """Verify JWT token issuance, HTTP 401 on unauthenticated access, and successful auth."""
        # 1. Unauthenticated request to /embed should return 401
        unauth_resp = client.post("/embed", files={"file": ("empty.jpg", b"", "image/jpeg")})
        self.assertEqual(unauth_resp.status_code, 401)

        # 2. Request token from /auth/token
        token_resp = client.post("/auth/token", json={"client_id": "test_client"})
        self.assertEqual(token_resp.status_code, 200)
        token_data = token_resp.json()
        self.assertEqual(token_data["status"], "ok")
        self.assertIn("access_token", token_data)
        token = token_data["access_token"]

        # 3. Invalid token should return 401
        invalid_resp = client.post(
            "/embed",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
            headers={"Authorization": "Bearer invalid_token_123"}
        )
        self.assertEqual(invalid_resp.status_code, 401)

        # 4. Valid token should bypass authentication check (validation error 422 for empty file instead of 401)
        valid_resp = client.post(
            "/embed",
            files={"file": ("empty.jpg", b"", "image/jpeg")},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(valid_resp.status_code, 422)

    def test_09_xai_explainer_flow(self):
        """Verify SpatialXAIExplainer computes regional match confidence and base64 heatmap PNG."""
        from xai_explainer import SpatialXAIExplainer
        import numpy as np

        sketch_dummy = np.random.randint(0, 255, (160, 160), dtype=np.uint8)
        photo_dummy = np.random.randint(0, 255, (160, 160), dtype=np.uint8)

        xai_res = SpatialXAIExplainer.explain_alignment(sketch_dummy, photo_dummy)
        self.assertIn("eyes_match", xai_res)
        self.assertIn("nose_match", xai_res)
        self.assertIn("mouth_match", xai_res)
        self.assertIn("contour_match", xai_res)
        self.assertIn("overall_xai_confidence", xai_res)
        self.assertIn("heatmap_b64", xai_res)
        self.assertTrue(xai_res["heatmap_b64"].startswith("data:image/png;base64,"))

    def test_10_element_recommender_flow(self):
        """Verify ElementRecommender and /recommend_elements endpoint return anatomical recommendations."""
        from element_recommender import ElementRecommender
        rec = ElementRecommender.get_recommendations({"face_shape": "OVAL", "eyes_style": "almond_eyes_01"})
        self.assertEqual(rec["status"], "ok")
        self.assertEqual(rec["detected_face_shape"], "OVAL")
        self.assertIn("recommended_noses", rec)
        self.assertIn("recommended_mouths", rec)
        self.assertIn("recommended_chins", rec)

        # Test authenticated REST endpoint
        token_resp = client.post("/auth/token", json={"client_id": "test_client"})
        token = token_resp.json()["access_token"]
        api_resp = client.post(
            "/recommend_elements",
            json={"face_shape": "SQUARE", "eyes_style": "wide_eyes"},
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(api_resp.status_code, 200)
        res_data = api_resp.json()
        self.assertEqual(res_data["detected_face_shape"], "SQUARE")
        self.assertEqual(res_data["eye_spacing_category"], "WIDE_SET")

    def test_11_skin_tone_colorization_flow(self):
        """Verify GenerativeSynthesizer generates colorized PNG renderings for all skin tone palettes."""
        from generative_synth import GenerativeSynthesizer
        from PIL import Image
        import io

        # Create 160x160 white image with black circle as dummy sketch
        img = Image.new("RGB", (160, 160), color="white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        sketch_bytes = buf.getvalue()

        for tone in ["FAIR", "MEDIUM", "WARM_BROWN", "DEEP_BROWN"]:
            png_bytes = GenerativeSynthesizer.synthesize_photo_from_sketch(sketch_bytes, skin_tone=tone)
            self.assertTrue(len(png_bytes) > 50)
            res_img = Image.open(io.BytesIO(png_bytes))
            self.assertEqual(res_img.mode, "RGB")


if __name__ == "__main__":
    unittest.main()




