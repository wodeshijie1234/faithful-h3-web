import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.gguf_runtime import GgufRuntime


class GgufRuntimeTests(unittest.TestCase):
    def test_health_requires_the_selected_model_path(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / "selected.gguf"
            model.write_bytes(b"gguf")
            runtime = GgufRuntime(model)

            class FakeResponse:
                status = 200
                def __enter__(self): return self
                def __exit__(self, *args): return False
                def read(self): return json.dumps({"model_path": str(model)}).encode()

            with patch("app.gguf_runtime.urlopen", return_value=FakeResponse()):
                self.assertTrue(runtime.loaded)

    def test_generation_uses_no_thinking_and_json_response_mode(self):
        runtime = GgufRuntime(Path("model.gguf"), binary=Path("llama-server.exe"), port=18765)
        response = {"choices": [{"message": {"content": "{\"scene\":\"x\"}"}}]}

        class FakeResponse:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(response).encode()

        captured = {}
        def fake_urlopen(request, timeout=0):
            if hasattr(request, "full_url"):
                captured.update(json.loads(request.data.decode()))
            return FakeResponse()

        with patch.object(runtime, "ensure_started"), patch("app.gguf_runtime.urlopen", fake_urlopen):
            result = runtime.generate("source", "system", temperature=0.01, top_p=0.1, stop_on_json=True)
        self.assertEqual('{"scene":"x"}', result)
        self.assertEqual({"enable_thinking": False}, captured["chat_template_kwargs"])
        self.assertEqual({"type": "json_object"}, captured["response_format"])

    def test_stop_terminates_a_running_server(self):
        runtime = GgufRuntime(Path("model.gguf"))
        class Process:
            def __init__(self): self.terminated = False; self.returncode = None
            def poll(self): return self.returncode
            def terminate(self): self.terminated = True; self.returncode = 0
            def wait(self, timeout=None): return 0
        process = Process()
        runtime.process = process
        runtime.stop()
        self.assertTrue(process.terminated)
        self.assertIsNone(runtime.process)

    def test_start_ignores_a_probe_timeout_before_launching_server(self):
        with tempfile.TemporaryDirectory() as directory:
            binary = Path(directory) / "llama-server.exe"
            binary.write_bytes(b"placeholder")
            model = Path(directory) / "model.gguf"
            model.write_bytes(b"placeholder")
            runtime = GgufRuntime(model, binary=binary)
            with patch("app.gguf_runtime.urlopen", side_effect=TimeoutError("probe timeout")):
                with patch.object(runtime, "_healthy", side_effect=[False, True]), patch("app.gguf_runtime.subprocess.Popen") as popen:
                    popen.return_value.poll.return_value = None
                    runtime.ensure_started()


if __name__ == "__main__":
    unittest.main()
