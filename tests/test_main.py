import unittest
import tempfile
from pathlib import Path
from unittest.mock import PropertyMock, patch

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

    def test_top_download_starts_only_the_models_selected_by_the_user(self):
        original_gguf = dict(main.GGUF_PATHS)
        original_vision_root = main.VISION_ROOT
        original_vision_roots = dict(main.VISION_ROOTS)
        with tempfile.TemporaryDirectory() as directory:
            main.GGUF_PATHS["4b"] = Path(directory) / "missing-4b.gguf"
            main.GGUF_PATHS["9b"] = Path(directory) / "missing-9b.gguf"
            main.VISION_ROOT = Path(directory) / "missing-vision"
            main.VISION_ROOTS["fast"] = main.VISION_ROOT
            try:
                with patch.object(main, "_start_daemon") as start_daemon:
                    response = self.client.post("/api/download", json={"models": ["4b", "vision"]})
            finally:
                main.GGUF_PATHS.update(original_gguf)
                main.VISION_ROOT = original_vision_root
                main.VISION_ROOTS.update(original_vision_roots)

        self.assertEqual(200, response.status_code)
        self.assertTrue(response.json()["started"])
        self.assertEqual(2, start_daemon.call_count)
        start_daemon.assert_any_call(main._download_worker, "4b")
        start_daemon.assert_any_call(main._vision_download_worker, "fast")
        self.assertNotIn("9b", response.json()["requested"])

    def test_unknown_action_returns_safe_client_error(self):
        response = self.client.post("/api/generate", json={"action": "invalid", "text": "prompt"})
        self.assertEqual(400, response.status_code)
        self.assertEqual("Unknown action.", response.json()["detail"])

    def test_release_endpoint_reports_runtime_result(self):
        original_release = runtime.release
        runtime.release = lambda: {"released": True, "loaded": False}
        try:
            with patch.object(main, "_memory_snapshot", side_effect=[
                {"ram": {"used_mib": 12000, "total_mib": 32000}, "vram": {"used_mib": 6000, "total_mib": 12288}},
                {"ram": {"used_mib": 11000, "total_mib": 32000}, "vram": {"used_mib": 3500, "total_mib": 12288}},
            ]):
                response = self.client.post("/api/release")
        finally:
            runtime.release = original_release
        self.assertEqual(200, response.status_code)
        self.assertEqual({"released": True, "loaded": False, "memory": {
            "ram": {"released_mib": 1000, "used_mib": 11000, "total_mib": 32000},
            "vram": {"released_mib": 2500, "used_mib": 3500, "total_mib": 12288},
        }}, response.json())

    def test_progress_endpoint_reports_live_token_throughput(self):
        with patch.object(type(main.vision_runtime), "progress", new_callable=PropertyMock, return_value={
            "active": True,
            "generated_tokens": 24,
            "tokens_per_second": 18.75,
            "elapsed_seconds": 1.28,
        }):
            response = self.client.get("/api/progress")

        self.assertEqual(200, response.status_code)
        self.assertEqual(24, response.json()["generated_tokens"])
        self.assertEqual(18.75, response.json()["tokens_per_second"])

    def test_resources_endpoint_reports_system_and_gpu_metrics(self):
        sample = {
            "available": True,
            "cpu_percent": 46.4,
            "ram": {"used_gib": 34.2, "total_gib": 63.7, "percent": 53.7},
            "disk": {"read_mb_s": 5.0, "write_mb_s": 4.7},
            "gpu_percent": 26.0,
            "vram": {"used_gib": 2.7, "total_gib": 12.0, "percent": 22.8},
        }
        with patch.object(main.resource_monitor, "snapshot", return_value=sample):
            response = self.client.get("/api/resources")

        self.assertEqual(200, response.status_code)
        self.assertEqual(sample, response.json())

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

    def test_status_lists_fast_and_accurate_vision_models(self):
        response = self.client.get("/api/status")

        self.assertEqual(200, response.status_code)
        models = response.json()["vision_models"]
        self.assertEqual({"fast", "accurate"}, {item["id"] for item in models})

    def test_storyboard_endpoint_uses_the_requested_vision_model(self):
        expected = {"title": "Test", "shots": [{"number": 1, "start_seconds": 0.0}]}
        accurate = main.vision_runtimes["accurate"]
        with patch.object(main.runtime, "release", return_value={"released": True, "loaded": False}) as release, \
             patch.object(main, "_activate_vision_runtime", return_value=accurate), \
             patch.object(accurate, "storyboard", return_value=expected) as storyboard:
            response = self.client.post("/api/storyboard/generate", json={
                "image_data_url": "data:image/png;base64,iVBORw0KGgo=",
                "task_type": "comic_panels",
                "goal": "Keep reading order.",
                "language": "en",
                "model_id": "accurate",
                "panel_boxes": [{"x": 0, "y": 0, "width": 1, "height": 1}],
            })

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response.json()["output"])
        release.assert_called_once_with()
        storyboard.assert_called_once()

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
