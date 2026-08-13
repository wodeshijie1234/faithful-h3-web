import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from app.model_files import MODEL_SPECS
from scripts.self_check import run_self_check


class InstallerSelfCheckTests(unittest.TestCase):
    def test_self_check_verifies_model_generates_text_and_releases_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            model = Path(directory) / MODEL_SPECS["4b"].gguf_filename
            model.write_bytes(b"placeholder")
            runtime = Mock()
            runtime.generate.return_value = "OK"

            with patch("scripts.self_check.verify_gguf_file") as verify:
                result = run_self_check(model, MODEL_SPECS["4b"], Path("llama-server.exe"), runtime=runtime)

            verify.assert_called_once_with(model, MODEL_SPECS["4b"])
            runtime.ensure_started.assert_called_once_with()
            runtime.generate.assert_called_once()
            runtime.stop.assert_called_once_with()
            self.assertEqual("OK", result["output"])

    def test_self_check_rejects_empty_generation_and_releases_runtime(self):
        runtime = Mock()
        runtime.generate.return_value = "   "
        with patch("scripts.self_check.verify_gguf_file"):
            with self.assertRaisesRegex(RuntimeError, "readable text"):
                run_self_check(Path("model.gguf"), MODEL_SPECS["4b"], Path("llama-server.exe"), runtime=runtime)
        runtime.stop.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
