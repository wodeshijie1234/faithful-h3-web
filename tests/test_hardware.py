import unittest

from app.hardware import acceleration_plan, recommend_model_from_vram
from scripts.install_runtime import detect_backend, verify_asset, ASSET_SHA256
import tempfile
from pathlib import Path
from unittest.mock import patch


class HardwarePlanTests(unittest.TestCase):
    def test_modern_gpu_prefers_accelerated_backend_after_self_test(self):
        plan = acceleration_plan(platform="Windows", python=(3, 11), capability=(8, 9), vram_gib=12)
        self.assertEqual("accelerated", plan.tier)
        self.assertTrue(plan.requires_self_test)
        self.assertEqual("4b", plan.recommended_model)

    def test_python_310_uses_stable_backend_on_windows(self):
        plan = acceleration_plan(platform="Windows", python=(3, 10), capability=(8, 9), vram_gib=12)
        self.assertEqual("stable", plan.tier)
        self.assertEqual("4b", plan.recommended_model)

    def test_older_cuda_gpu_falls_back_safely(self):
        plan = acceleration_plan(platform="Windows", python=(3, 11), capability=(7, 5), vram_gib=8)
        self.assertEqual("compatible", plan.tier)
        self.assertFalse(plan.install_triton)
        self.assertEqual("4b", plan.recommended_model)

    def test_runtime_installer_prefers_cuda_when_nvidia_smi_works(self):
        with patch("scripts.install_runtime.subprocess.check_output", return_value="NVIDIA RTX, 12282\n"):
            backend, detail = detect_backend()
        self.assertEqual("cuda", backend)
        self.assertIn("NVIDIA RTX", detail)

    def test_runtime_installer_falls_back_to_vulkan(self):
        with patch("scripts.install_runtime.subprocess.check_output", side_effect=FileNotFoundError):
            backend, _ = detect_backend()
        self.assertEqual("vulkan", backend)

    def test_runtime_installer_rejects_unverified_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / next(iter(ASSET_SHA256))
            path.write_bytes(b"not an official runtime")
            with self.assertRaisesRegex(RuntimeError, "SHA256"):
                verify_asset(path)

    def test_model_recommendation_handles_empty_spaced_and_multi_gpu_values(self):
        self.assertEqual("4b", recommend_model_from_vram(""))
        self.assertEqual("4b", recommend_model_from_vram(" 12282 "))
        self.assertEqual("9b", recommend_model_from_vram("8192\n 24576 \n"))


if __name__ == "__main__":
    unittest.main()
