import unittest

from fastapi.testclient import TestClient

from app.main import app, runtime


class ApiContractTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_status_reports_model_state_without_loading_model(self):
        response = self.client.get("/api/status")
        self.assertEqual(200, response.status_code)
        payload = response.json()
        self.assertFalse(payload["loaded"])
        self.assertIsInstance(payload["ready"], bool)
        self.assertIsInstance(payload["missing"], list)
        if payload["ready"]:
            self.assertEqual([], payload["missing"])
        else:
            self.assertIn("Qwen3.5-9B-Abliterated_v2_quanto_bf16_int8.safetensors", payload["missing"])

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

    def test_convert_modules_requires_no_plain_text_contract_change(self):
        from app.main import service

        original = service.convert_modules
        service.convert_modules = lambda modules, mode: {"output": "ok", "modules": modules, "mode": mode}
        try:
            response = self.client.post(
                "/api/generate",
                json={"action": "convert_modules", "text": "modules", "mode": "ref2va", "modules": {"scene": "x"}},
            )
        finally:
            service.convert_modules = original
        self.assertEqual(200, response.status_code)
        self.assertEqual("x", response.json()["modules"]["scene"])
        self.assertEqual("ref2va", response.json()["mode"])


if __name__ == "__main__":
    unittest.main()
