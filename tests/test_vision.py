import base64
import unittest
from pathlib import Path
from unittest.mock import Mock


class VisionModelContractTests(unittest.TestCase):
    def test_accurate_storyboard_model_uses_verified_qwen3_vl_pair(self):
        from app.vision import VISION_MODELS

        accurate = VISION_MODELS["accurate"]
        self.assertEqual("Qwen3-VL-8B Abliterated Caption-it", accurate.label)
        self.assertEqual(
            "mradermacher/Qwen3-VL-8B-Abliterated-Caption-it-GGUF",
            accurate.repo,
        )
        self.assertEqual(5_027_785_888, accurate.model_size)
        self.assertEqual(752_290_336, accurate.mmproj_size)
        self.assertEqual(
            "3ffdeb8d9765fb9d415df7b134a713a930b5144fad0fe6370054fa7cc4bdd588",
            accurate.model_sha256,
        )
        self.assertEqual(
            "c0e36e3ffa229f67f95a662c7c680c07bcfb58f6b95854b22ef04d9f1f0e36cc",
            accurate.mmproj_sha256,
        )

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

    def test_caption_removes_repeated_sentences_and_their_truncated_tail(self):
        from app.vision import VisionCaptionRuntime

        runtime = VisionCaptionRuntime(Path("missing"))
        repeated = "角色手持金色弓箭。角色表情严肃。" + "角色表情严肃。" * 8 + "角色表情严"
        runtime._runtime = Mock(generate_with_image=Mock(return_value=repeated))
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.caption(png, "", "zh-CN")

        self.assertEqual("角色手持金色弓箭。角色表情严肃。", result)

    def test_caption_retries_when_chinese_output_is_not_in_requested_language(self):
        from app.vision import VisionCaptionRuntime

        runtime = VisionCaptionRuntime(Path("missing"))
        runtime._runtime = Mock(generate_with_image=Mock(side_effect=["A character stands in a room.", "角色站在房间里。"]))
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.caption(png, "", "zh-CN")

        self.assertEqual("角色站在房间里。", result)
        self.assertEqual(2, runtime._runtime.generate_with_image.call_count)
        self.assertIn("只用简体中文", runtime._runtime.generate_with_image.call_args.args[1])

    def test_caption_converts_simplified_model_output_to_traditional_chinese(self):
        from app.vision import VisionCaptionRuntime

        runtime = VisionCaptionRuntime(Path("missing"))
        runtime._runtime = Mock(generate_with_image=Mock(return_value="这张图片里有蓝色头发。"))
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.caption(png, "", "zh-TW")

        self.assertEqual("這張圖片裡有藍色頭髮。", result)

    def test_storyboard_returns_an_editable_cumulative_timeline(self):
        import json
        from app.vision import VisionCaptionRuntime, VISION_MODELS

        runtime = VisionCaptionRuntime(Path("missing"), spec=VISION_MODELS["accurate"])
        raw_storyboard = json.dumps({
            "title": "Night encounter",
            "synopsis": "A stranger arrives.",
            "characters": ["Woman", "Stranger"],
            "shots": [
                {"panel_index": 1, "duration_seconds": 2, "shot_size": "Wide shot", "camera_movement": "Static", "visual_action": "A woman waits.", "dialogue": "", "sound": "Night ambience", "transition": "Cut"},
                {"panel_index": 2, "duration_seconds": 3.5, "shot_size": "Close-up", "camera_movement": "Push in", "visual_action": "A stranger appears.", "dialogue": "Who are you?", "sound": "Footsteps", "transition": "Cut"},
            ],
            "sound_design": "Wind and footsteps",
            "viral_hook": "A stranger appears without warning.",
            "ending": "Cut before the reveal.",
        }, ensure_ascii=False)
        runtime._runtime = Mock(
            generate_with_image=Mock(return_value="A woman waits while a stranger approaches."),
            generate=Mock(return_value=raw_storyboard),
        )
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.storyboard(
            png,
            task_type="comic_panels",
            goal="Keep the original reading order.",
            language="en",
            panel_boxes=[{"x": 0.0, "y": 0.0, "width": 1.0, "height": 0.5}],
        )

        self.assertEqual(0.0, result["shots"][0]["start_seconds"])
        self.assertEqual(2.0, result["shots"][1]["start_seconds"])
        self.assertEqual(5.5, result["total_duration_seconds"])
        self.assertEqual(1, runtime._runtime.generate_with_image.call_count)
        call = runtime._runtime.generate.call_args
        self.assertIn("Panel candidates", call.args[0])
        self.assertIn("A woman waits", call.args[0])
        self.assertTrue(call.kwargs["stop_on_json"])

    def test_storyboard_rejects_an_empty_schema_instead_of_returning_fake_defaults(self):
        import json
        from app.vision import VisionCaptionRuntime, VISION_MODELS

        runtime = VisionCaptionRuntime(Path("missing"), spec=VISION_MODELS["accurate"])
        runtime._runtime = Mock(
            generate_with_image=Mock(return_value="A visible character."),
            generate=Mock(return_value=json.dumps({
                "title": "", "synopsis": "", "characters": [],
                "shots": [{"duration_seconds": 2.5, "visual_action": ""}],
                "sound_design": "", "viral_hook": "", "ending": "",
            })),
        )
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        with self.assertRaisesRegex(RuntimeError, "incomplete"):
            runtime.storyboard(png, task_type="viral_video", goal="", language="en")

    def test_storyboard_repairs_invalid_json_once_without_reanalyzing_the_image(self):
        import json
        from app.vision import VisionCaptionRuntime, VISION_MODELS

        valid = json.dumps({
            "title": "Visible subject", "synopsis": "A visible subject moves.",
            "characters": ["Subject"],
            "shots": [{
                "panel_index": 1, "duration_seconds": 2.5, "shot_size": "Medium shot",
                "camera_movement": "Static", "visual_action": "The subject turns.",
                "dialogue": "", "sound": "Room tone", "transition": "Cut",
            }],
            "sound_design": "Room tone", "viral_hook": "A sudden turn", "ending": "Cut to black",
        })
        runtime = VisionCaptionRuntime(Path("missing"), spec=VISION_MODELS["accurate"])
        runtime._runtime = Mock(
            generate_with_image=Mock(return_value="A visible subject."),
            generate=Mock(side_effect=['{"title":"Broken" "shots":[]}', valid]),
        )
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.storyboard(png, task_type="viral_video", goal="", language="en")

        self.assertEqual("Visible subject", result["title"])
        self.assertEqual(2, runtime._runtime.generate.call_count)
        self.assertEqual(1, runtime._runtime.generate_with_image.call_count)

    def test_storyboard_drops_panel_references_when_no_candidates_exist(self):
        import json
        from app.vision import VisionCaptionRuntime, VISION_MODELS

        runtime = VisionCaptionRuntime(Path("missing"), spec=VISION_MODELS["accurate"])
        runtime._runtime = Mock(
            generate_with_image=Mock(return_value="A visible subject."),
            generate=Mock(return_value=json.dumps({
                "title": "Subject", "synopsis": "The subject moves.", "characters": ["Subject"],
                "shots": [{
                    "panel_index": 3, "duration_seconds": 2.5, "shot_size": "Medium shot",
                    "camera_movement": "Static", "visual_action": "The subject turns.",
                    "dialogue": "", "sound": "Room tone", "transition": "Cut",
                }],
                "sound_design": "Room tone", "viral_hook": "A turn", "ending": "Cut to black",
            })),
        )
        png = "data:image/png;base64," + base64.b64encode(b"\x89PNG\r\n\x1a\nminimal").decode()

        result = runtime.storyboard(png, task_type="viral_video", goal="", language="en", panel_boxes=[])

        self.assertIsNone(result["shots"][0]["panel_index"])


if __name__ == "__main__":
    unittest.main()
