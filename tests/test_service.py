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
    def test_enrichment_maps_all_requested_strength_levels(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，特写他按下遥控器，切换中景，女生静止不动，镜头切换，极低视角仰拍。"
        runtime = FakeRuntime([
            "昏暗的室内空间以克制暖光勾勒背景层次。",
            "雨夜街道的霓虹反光、潮湿空气与深邃阴影共同构成背景氛围。",
        ])
        service = PromptService(runtime)

        outputs = [service.enrich(source, strength) for strength in (0, 30, 50, 80, 100)]

        self.assertEqual(source, outputs[0])
        self.assertIn("焦点稳定落在按键和手部动作上", outputs[1])
        self.assertIn("人物相对位置与前后动作保持连续", outputs[2])
        self.assertIn("静止姿态与空洞目光在镜头切换后保持一致", outputs[3])
        self.assertIn("按键动作的节奏与后续镜头切换保持连贯", outputs[4])
        self.assertIn("昏暗的室内空间", outputs[3])
        self.assertIn("雨夜街道的霓虹反光", outputs[4])
        self.assertTrue(all("图1是男生" in output and "图2是女生" in output for output in outputs))
        self.assertEqual(2, len(runtime.calls))

    def test_enrichment_returns_one_integrated_prompt_instead_of_an_appended_afterword(self):
        runtime = FakeRuntime([])

        result = PromptService(runtime).enrich("特写人物按下遥控器，切换中景。", 50)

        self.assertNotIn("\n\n", result)
        self.assertIn("焦点稳定落在按键和手部动作上", result)
        self.assertIn("人物相对位置与前后动作保持连续", result)
        self.assertEqual([], runtime.calls)

    def test_high_strength_rejects_scene_text_with_people_or_actions(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，特写他按下遥控器。"
        runtime = FakeRuntime(["陌生人走进房间并开始说话。"])

        result = PromptService(runtime).enrich(source, 80)

        self.assertIn("图1是男生", result)
        self.assertIn("图2是女生", result)
        self.assertIn("场景氛围：雨夜的空旷街道覆盖着潮湿反光与深邃阴影", result)
        self.assertNotIn("陌生人", result)
        self.assertNotIn("说话", result)

    def test_zero_strength_enrichment_returns_the_source_without_inventing_details(self):
        runtime = FakeRuntime([])
        source = "A person enters from behind and presses a remote."

        result = PromptService(runtime).enrich(source, 0)

        self.assertEqual(source, result)
        self.assertEqual([], runtime.calls)

    def test_high_strength_accepts_a_chinese_scene_clause_and_keeps_protected_facts(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        runtime = FakeRuntime(["雨夜的街道映出需虹反光，潮湿空气与深遂阴影营造出紧张氛围。"])

        result = PromptService(runtime).enrich(source, 100)

        self.assertIn("雨夜的街道", result)
        self.assertTrue(all(anchor in result for anchor in ("图1是男生", "图2是女生", "视频场景是开始于图2")))
        self.assertIn("男生按下遥控器", result)
        self.assertNotIn("\n\n", result)

    def test_strength_60_is_the_first_level_that_allows_a_new_scene_clause(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        runtime = FakeRuntime(["黄昏的废弃车站笼罩在薄雾与冷色光影中。"])

        result = PromptService(runtime).enrich(source, 60)

        self.assertIn("黄昏的废弃车站", result)
        self.assertTrue(all(anchor in result for anchor in ("图1是男生", "图2是女生", "视频场景是开始于图2")))

    def test_high_strength_rejects_english_scene_for_chinese_source(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        runtime = FakeRuntime(["A dim room with warm light and soft shadows."])

        result = PromptService(runtime).enrich(source, 80)

        self.assertIn("雨夜的空旷街道覆盖着潮湿反光与深邃阴影", result)
        self.assertNotIn("A dim room", result)

    def test_high_strength_rejects_scene_text_with_people_actions_dialogue_or_camera(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        unsafe_scenes = [
            "陌生人走进雨夜的街道。",
            "远处传来“别动”的说话声。",
            "镜头缓慢推近空旷的走廊。",
        ]

        for unsafe_scene in unsafe_scenes:
            with self.subTest(scene=unsafe_scene):
                result = PromptService(FakeRuntime([unsafe_scene])).enrich(source, 80)
                self.assertIn("雨夜的空旷街道覆盖着潮湿反光与深邃阴影", result)
                self.assertNotIn(unsafe_scene, result)

    def test_high_strength_rejects_a_new_prop_in_scene_text(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        runtime = FakeRuntime(["是暧的室内空间中，电视屏幕和冰箱嗡鸣在远处延续。"])

        result = PromptService(runtime).enrich(source, 60)

        self.assertIn("昏暗的室内场景笼罩在冷色月光与寂静空气中", result)
        self.assertNotIn("电视", result)
        self.assertNotIn("冰箱", result)

    def test_high_strength_rejects_a_new_lamp_in_scene_text(self):
        source = "图1是男生，图2是女生，视频场景是开始于图2，男生按下遥控器。"
        runtime = FakeRuntime(["是暧的客厅里，冷色调的台灯在背景中投下微弱的光晕。"])

        result = PromptService(runtime).enrich(source, 60)

        self.assertIn("昏暗的室内场景笼罩在冷色月光与寂静空气中", result)
        self.assertNotIn("台灯", result)

    def test_decompose_returns_editable_modules(self):
        runtime = FakeRuntime([
            '{"scene":"原场景","shots":[{"duration_seconds":3,"action":"动作1","camera":""},{"duration_seconds":3,"action":"动作2","camera":""},{"duration_seconds":3,"action":"动作3","camera":""}],"overall_soundscape":"","non_diegetic_music":""}'
        ])
        result = PromptService(runtime).decompose("原始提示词", "fl2va")
        self.assertEqual(3, len(result["modules"]["shots"]))
        self.assertEqual("动作1", result["modules"]["shots"][0]["action"])
        self.assertEqual(384, runtime.calls[0][2]["max_new_tokens"])

    def test_decompose_retries_once_when_the_model_returns_unterminated_json(self):
        runtime = FakeRuntime([
            '{"scene":"unterminated',
            '{"scene":"source","shots":[{"duration_seconds":3,"action":"run","camera":""}],"overall_soundscape":"","non_diegetic_music":""}',
        ])

        result = PromptService(runtime).decompose("source", "fl2va")

        self.assertEqual("source", result["modules"]["scene"])
        self.assertEqual(2, len(runtime.calls))
        self.assertTrue(runtime.calls[1][2]["stop_on_json"])

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

    def test_convert_modules_retries_a_failed_visual_review_without_relaxing_the_guard(self):
        source = {
            "scene": "a person runs",
            "shots": [{"duration_seconds": 3, "action": "", "camera": ""}],
            "overall_soundscape": "",
            "non_diegetic_music": "",
        }
        runtime = FakeRuntime([
            '{"scene":"A person runs in a red coat.","shots":[{"duration_seconds":3,"action":"","camera":""}],"overall_soundscape":"","non_diegetic_music":""}',
            "FAIL",
            '{"scene":"A person runs.","shots":[{"duration_seconds":3,"action":"","camera":""}],"overall_soundscape":"","non_diegetic_music":""}',
            "PASS",
            "overall_soundscape: footsteps\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert_modules(source, "fl2va")

        self.assertIn("A person runs.", result["output"])
        self.assertNotIn("red coat", result["output"])
        self.assertEqual(5, len(runtime.calls))

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

    def test_ref2va_conversion_emits_timeline_after_faithful_review(self):
        source = (
            "\u56fe1\u662f\u7537\u751f\uff0c\u56fe2\u662f\u5973\u751f\uff0c\u89c6\u9891\u5f00\u59cb\u4e8e\u56fe2\u3002"
            "\u7537\u751f\u7a81\u7136\u51fa\u73b0\u5728\u5973\u751f\u8eab\u540e\uff0c\u4ed6\u62ff\u7740\u9065\u63a7\u5668\uff0c\u7279\u5199\u4ed6\u6309\u4e0b\u9065\u63a7\u5668\uff0c\u5207\u6362\u4e2d\u666f\uff0c"
            "\u5973\u751f\u7a81\u7136\u9759\u6b62\u4e0d\u52a8\uff0c\u773c\u795e\u7a7a\u6d1e\uff0c\u5634\u5df4\u5fae\u5f20\uff0c\u7537\u751f\u4ece\u540e\u9762\u62cd\u5979\u7684\u80a9\u8180\uff0c"
            "\u955c\u5934\u5207\u6362\uff0c\u6781\u4f4e\u89c6\u89d2\u4ef0\u62cd\uff0c\u4ed6\u9762\u5bf9\u5973\u751f\u8e72\u4e0b\u3002"
        )
        translation = (
            "<Picture 1> is a man. <Picture 2> is a woman. The video begins with <Picture 2>. "
            "The man suddenly appears behind the woman, holding a remote control. "
            "Close-up on him pressing the remote. Cut to medium shot. "
            "The woman freezes with vacant eyes and a slightly open mouth. He taps her shoulder from behind and runs his fingers through her hair. "
            "Cut to an extremely low-angle shot as he crouches in front of her."
        )
        runtime = FakeRuntime([
            translation,
            "PASS",
            "overall_soundscape: a remote-control click and light movement\nnon_diegetic_music: N/A",
            "????????",
        ])

        result = PromptService(runtime).convert(source, "ref2va")

        self.assertIn("summary: [reference generation] The target video begins with <Picture 2>.", result["output"])
        self.assertIn("[Shot 2] At 00:02.500, Close-up on him pressing the remote.", result["output"])
        self.assertIn("[Shot 4] At 00:07.500, Cut to an extremely low-angle shot", result["output"])
        self.assertIn("[Shot 1]", result["chinese"])
        self.assertIn("[Shot 2] At 00:02.500", result["chinese"])

    def test_conversion_rejects_visual_invention(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
        ])
        with self.assertRaisesRegex(RuntimeError, "no-invention review"):
            PromptService(runtime).convert("一个人奔跑", "fl2va")

    def test_conversion_retries_a_failed_visual_review_without_relaxing_the_guard(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
            "[Shot 1] A person runs.",
            "PASS",
            "overall_soundscape: running footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] source\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert("source", "fl2va")

        self.assertIn("A person runs.", result["output"])
        self.assertNotIn("red coat", result["output"])
        self.assertEqual(6, len(runtime.calls))
        self.assertEqual(
            ["translate", "visual_review", "translation_retry", "visual_review_retry", "audio", "chinese_preview"],
            [stage["name"] for stage in result["_stages"]],
        )

    def test_conversion_removes_an_unmentioned_vocalization_before_visual_review(self):
        runtime = FakeRuntime([
            "[Shot 1] The person remains still. The person moans.",
            "PASS",
            "overall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: source\noverall_soundscape: N/A\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert("source", "fl2va")

        self.assertNotIn("moans", result["output"])
        self.assertEqual(
            ["translate", "visual_review", "audio", "chinese_preview"],
            [stage["name"] for stage in result["_stages"]],
        )

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
