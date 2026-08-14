import base64
import unittest


class VisionModelContractTests(unittest.TestCase):
    def test_caption_model_uses_verified_small_uncensored_gguf_pair(self):
        from app.vision import VISION_MODEL

        self.assertEqual("Qwen2-VL-2B Abliterated Caption-it", VISION_MODEL.label)
        self.assertEqual(
            "mradermacher/Qwen2-VL-2B-Abliterated-Caption-it-GGUF",
            VISION_MODEL.repo,
        )
        self.assertEqual(940_312_704, VISION_MODEL.model_size)
        self.assertEqual(712_895_168, VISION_MODEL.mmproj_size)
        self.assertEqual(
            "1fffe7ef7b2f44c6323e158aa10348991b15fd47d9b3982a9910bf75e616842f",
            VISION_MODEL.model_sha256,
        )
        self.assertEqual(
            "21356973f9f9d8ba131d83b21e2798df5b1bbcd125761a68ae8e14b5f41f4062",
            VISION_MODEL.mmproj_sha256,
        )

    def test_image_validation_rejects_a_spoofed_file_type(self):
        from app.vision import validate_image_data_url

        fake_jpeg = "data:image/jpeg;base64," + base64.b64encode(b"not-a-jpeg").decode()
        with self.assertRaisesRegex(ValueError, "does not match"):
            validate_image_data_url(fake_jpeg)

    def test_image_validation_accepts_a_png_signature(self):
        from app.vision import validate_image_data_url

        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()
        validate_image_data_url(png)


if __name__ == "__main__":
    unittest.main()
