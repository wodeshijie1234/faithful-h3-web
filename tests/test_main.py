import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import main
from app.main import app, runtime


class ApiContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_status_reports_model_state_without_loading_model(self):
        response = self.client.get("/api/status")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["loaded"])
        self.assertIn(payload["backend"], {"quanto", "gguf"})
        self.assertIsInstance(payload["ready"], bool)
        self.assertIsInstance(payload["missing"], list)
        if payload["ready"]:
            self.assertEqual([], payload["missing"])
        else:
            self.assertEqual("9b", payload["selected_model"])
            self.assertEqual({"4b", "9b"}, {item["id"] for item in payload["models"]})
            self.assertIn("Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors", payload["missing"])

    def test_model_can_be_selected_without_loading_it(self):
        with patch.object(main.runtime, "select") as select:
            response = self.client.post("/api/model", json={"model_id": "4b"})
        self.assertEqual(200, response.status_code)
        select.assert_called_once_with("4b")

    def test_download_worker_keeps_the_model_selected_when_started(self):
        with patch.object(main, "download_gguf") as download:
            main._download_worker("4b")
        download.assert_called_once_with(main.GGUF_ROOT, main.MODEL_SPECS["4b"])

    def test_unknown_action_returns_safe_client_error(self):
        response = self.client.post("/api/generate", json={"action": "invalid", "text": "prompt"})
        self.assertEqual(400, response.status_code)
        self.assertEqual("Unknown action.", response.json()["detail"])

    def test_release_endpoint_reports_runtime_result(self):
        original_release = runtime.release
        runtime.release = lambda: {"released": True, "loaded": False}
        try:
            response = self.client.post("/api/release")
        finally:
            runtime.release = original_release
        self.assertEqual(200, response.status_code)
        self.assertEqual({"released": True, "loaded": False}, response.json())

    def test_vision_caption_releases_the_text_model_before_analysis(self):
        with patch.object(main.runtime, "release", return_value={"released": True, "loaded": False}) as release:
            with patch.object(main.vision_runtime, "caption", return_value="Only visible facts.") as caption:
                response = self.client.post(
                    "/api/vision/caption",
                    json={
                        "image_data_url": "data:image/png;base64,iVBORw0KGgo=",
                        "instruction": "Focus on subject positions.",
                        "language": "en",
                    },
                )

        self.assertEqual(200, response.status_code)
        self.assertEqual("Only visible facts.", response.json()["output"])
        release.assert_called_once_with()
        caption.assert_called_once_with(
            "data:image/png;base64,iVBORw0KGgo=",
            "Focus on subject positions.",
            "en",
        )

    def test_removed_module_actions_are_rejected(self):
        for action in ("decompose", "convert_modules"):
            response = self.client.post(
                "/api/generate",
                json={"action": action, "text": "modules", "mode": "ref2va"},
            )
            self.assertEqual(400, response.status_code)
            self.assertEqual("Unknown action.", response.json()["detail"])

    def test_both_gguf_models_support_explicit_existing_file_paths(self):
        source = (main.ROOT / "app" / "main.py").read_text(encoding="utf-8")
        self.assertIn("FAITHFUL_H3_GGUF_4B_PATH", source)
        self.assertIn("FAITHFUL_H3_GGUF_9B_PATH", source)


if __name__ == "__main__":
    unittest.main()
