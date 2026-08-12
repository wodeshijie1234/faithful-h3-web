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
    def test_conversion_returns_english_h3_and_chinese_editor_copy(self):
        runtime = FakeRuntime([
            "integrated_multimodal_description: [Shot 1] A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])
        result = PromptService(runtime).convert("一个人奔跑", "fl2va")
        self.assertIn("A person runs", result["output"])
        self.assertIn("一个人奔跑", result["chinese"])

    def test_micro_edit_rejects_chinese_after_retry(self):
        runtime = FakeRuntime([
            "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])
        with self.assertRaisesRegex(RuntimeError, "untranslated Chinese"):
            PromptService(runtime).micro_edit("integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A", "fl2va")

    def test_plain_micro_input_can_be_used_standalone(self):
        runtime = FakeRuntime([
            "integrated_multimodal_description: [Shot 1] A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])
        result = PromptService(runtime).micro_edit("一个人奔跑", "fl2va")
        self.assertIn("A person runs", result["output"])


if __name__ == "__main__":
    unittest.main()
