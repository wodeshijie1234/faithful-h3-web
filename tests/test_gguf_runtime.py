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

    def test_multimodal_generation_sends_an_image_data_url(self):
        runtime = GgufRuntime(
            Path("vision.gguf"),
            binary=Path("llama-server.exe"),
            port=18766,
            mmproj_path=Path("vision-mmproj.gguf"),
            context_size=8192,
        )
        response = {"choices": [{"message": {"content": "A factual caption."}}]}

        class FakeResponse:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return json.dumps(response).encode()

        captured = {}
        def fake_urlopen(request, timeout=0):
            captured.update(json.loads(request.data.decode()))
            return FakeResponse()

        with patch.object(runtime, "ensure_started"), patch("app.gguf_runtime.urlopen", fake_urlopen):
            result = runtime.generate_with_image(
                "data:image/png;base64,iVBORw0KGgo=",
                "Describe only visible facts.",
                "Return one caption.",
                max_new_tokens=512,
            )

        self.assertEqual("A factual caption.", result)
        content = captured["messages"][1]["content"]
        self.assertEqual("image_url", content[0]["type"])
        self.assertEqual("data:image/png;base64,iVBORw0KGgo=", content[0]["image_url"]["url"])
        self.assertEqual("text", content[1]["type"])

    def test_multimodal_server_starts_with_the_vision_projector(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binary = root / "llama-server.exe"
            model = root / "vision.gguf"
            mmproj = root / "vision-mmproj.gguf"
            for path in (binary, model, mmproj):
                path.write_bytes(b"placeholder")
            runtime = GgufRuntime(model, binary=binary, port=18766, mmproj_path=mmproj)

            with patch("app.gguf_runtime.urlopen", side_effect=TimeoutError("probe timeout")):
                with patch.object(runtime, "_healthy", side_effect=[False, True]), patch("app.gguf_runtime.subprocess.Popen") as popen:
                    popen.return_value.poll.return_value = None
                    runtime.ensure_started()

            command = popen.call_args.args[0]
            self.assertIn("--mmproj", command)
            self.assertEqual(str(mmproj), command[command.index("--mmproj") + 1])
            self.assertIn("--image-min-tokens", command)

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
