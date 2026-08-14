import unittest

from app.service import PromptService


class FakeRuntime:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def generate(self, text, system, **settings):
        self.calls.append((text, system, settings))
        return next(self.outputs)


class PromptServiceTests(unittest.TestCase):
    def test_decompose_returns_editable_modules(self):
        runtime = FakeRuntime([
            '{"scene":"原场景","shots":[{"duration_seconds":3,"action":"动作1","camera":""},{"duration_seconds":3,"action":"动作2","camera":""},{"duration_seconds":3,"action":"动作3","camera":""}],"overall_soundscape":"","non_diegetic_music":""}'
        ])
        result = PromptService(runtime).decompose("原始提示词", "fl2va")
        self.assertEqual(3, len(result["modules"]["shots"]))
        self.assertEqual("动作1", result["modules"]["shots"][0]["action"])
        self.assertEqual(384, runtime.calls[0][2]["max_new_tokens"])

    def test_convert_modules_builds_h3_without_model_formatting(self):
        source = {
            "scene": "女生在左边，男生在右边。",
            "shots": [
                {"duration_seconds": 3.5, "action": "女生抬腿。", "camera": ""},
                {"duration_seconds": 2.5, "action": "男生蹲下。", "camera": "中景。"},
            ],
            "overall_soundscape": "",
            "non_diegetic_music": "",
        }
        translated = {
            "scene": "The woman is on the left and the man is on the right.",
            "shots": [
                {"duration_seconds": 3.5, "action": "The woman raises one leg.", "camera": ""},
                {"duration_seconds": 2.5, "action": "The man crouches.", "camera": "Medium shot."},
            ],
            "overall_soundscape": "",
            "non_diegetic_music": "",
        }
        import json
        runtime = FakeRuntime([
            json.dumps(translated),
            "PASS",
            "overall_soundscape: breathing and fabric movement\nnon_diegetic_music: N/A",
        ])
        result = PromptService(runtime).convert_modules(source, "fl2va")
        self.assertIn("The woman is on the left", result["output"])
        self.assertIn("[Shot 2] At 00:03.500", result["output"])
        self.assertIn("breathing and fabric movement", result["output"])

    def test_conversion_translates_visuals_and_separately_infers_audio(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs.",
            "PASS",
            "overall_soundscape: running footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: running footsteps\nnon_diegetic_music: N/A",
        ])
        result = PromptService(runtime).convert("一个人奔跑", "fl2va")
        self.assertIn("A person runs", result["output"])
        self.assertIn("overall_soundscape: running footsteps", result["output"])
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("一个人奔跑", result["chinese"])
        self.assertEqual(700, runtime.calls[0][2]["max_new_tokens"])
        self.assertEqual(8, runtime.calls[1][2]["max_new_tokens"])
        self.assertEqual(160, runtime.calls[2][2]["max_new_tokens"])
        self.assertEqual(
            ["translate", "visual_review", "audio", "chinese_preview"],
            [stage["name"] for stage in result["_stages"]],
        )
        self.assertTrue(all(stage["elapsed_seconds"] >= 0 for stage in result["_stages"]))

    def test_conversion_rejects_visual_invention(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
        ])
        with self.assertRaisesRegex(RuntimeError, "no-invention review"):
            PromptService(runtime).convert("一个人奔跑", "fl2va")

    def test_conversion_falls_back_to_the_chinese_source_when_gguf_preview_is_corrupted(self):
        source = "\u4e00\u4e2a\u4eba\u5954\u8dd1"
        runtime = FakeRuntime([
            "[Shot 1] A person runs.",
            "PASS",
            "overall_soundscape: running footsteps\nnon_diegetic_music: N/A",
            "????????????????",
        ])

        result = PromptService(runtime).convert(source, "fl2va")

        self.assertIn(source, result["chinese"])
        self.assertNotIn("?", result["chinese"])
        self.assertTrue(result["audit"]["valid"])

    def test_micro_edit_rejects_chinese_after_retry(self):
        runtime = FakeRuntime([
            "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])
        with self.assertRaisesRegex(RuntimeError, "untranslated Chinese"):
            PromptService(runtime).micro_edit("integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A", "fl2va")

    def test_plain_micro_input_can_be_used_standalone(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs.",
            "PASS",
            "overall_soundscape: running footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: running footsteps\nnon_diegetic_music: N/A",
        ])
        result = PromptService(runtime).micro_edit("一个人奔跑", "fl2va")
        self.assertIn("A person runs", result["output"])


if __name__ == "__main__":
    unittest.main()
