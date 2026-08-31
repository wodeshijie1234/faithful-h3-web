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
    def test_long_conversion_scales_translation_budget(self):
        source = "一个人观察周围环境并缓慢向前走。" * 80
        runtime = FakeRuntime([
            "A person observes the surroundings and slowly walks forward.",
            "PASS",
            "overall_soundscape: footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: source\noverall_soundscape: footsteps\nnon_diegetic_music: N/A",
        ])

        PromptService(runtime).convert(source, "fl2va")

        self.assertGreater(runtime.calls[0][2]["max_new_tokens"], 700)
        self.assertLessEqual(runtime.calls[0][2]["max_new_tokens"], 1800)

    def test_enrichment_maps_all_requested_strength_levels(self):
        runtime = FakeRuntime([
            "integrated30", "PASS",
            "integrated50", "PASS",
            "integrated80", "PASS",
            "integrated100", "PASS",
        ])
        service = PromptService(runtime)

        outputs = [service.enrich("source", strength) for strength in (0, 30, 50, 80, 100)]

        self.assertEqual(
            ["source", "integrated30", "integrated50", "integrated80", "integrated100"],
            outputs,
        )
        self.assertEqual(
            [(0.375, 0.53), (0.525, 0.65), (0.75, 0.83), (0.9, 0.95)],
            [(call[2]["temperature"], call[2]["top_p"]) for call in runtime.calls[::2]],
        )

    def test_enrichment_returns_one_integrated_prompt_instead_of_an_appended_afterword(self):
        runtime = FakeRuntime(["Source facts with integrated camera detail.", "PASS"])

        result = PromptService(runtime).enrich("source facts", 50)

        self.assertEqual("Source facts with integrated camera detail.", result)
        self.assertNotIn("\n\n", result)
        self.assertEqual(2, len(runtime.calls))
        self.assertIn("not additions", runtime.calls[0][1])
        self.assertIn("Return exactly PASS", runtime.calls[1][1])

    def test_zero_strength_enrichment_returns_the_source_without_inventing_details_or_length_rewrite(self):
        runtime = FakeRuntime([])
        source = "A person enters from behind and presses a remote."

        result = PromptService(runtime).enrich(source, 0, target_length=2000)

        self.assertEqual(source, result)
        self.assertEqual([], runtime.calls)

    def test_enrichment_uses_the_requested_target_length(self):
        runtime = FakeRuntime(["A" * 1100, "PASS"])

        PromptService(runtime).enrich("A concise prompt.", strength=50, target_length=1200)

        self.assertIn("1200 characters", runtime.calls[0][1])
        self.assertEqual(1440, runtime.calls[0][2]["max_new_tokens"])

    def test_enrichment_repairs_an_output_that_exceeds_the_target_length_tolerance(self):
        source = "A woman opens a blue umbrella."
        too_long = "A " * 200
        repaired = "A woman slowly opens a blue umbrella in light rain, keeping the camera focused on her hands and the unfolding fabric on a quiet street."
        runtime = FakeRuntime([too_long, "PASS", repaired, "PASS"])

        result = PromptService(runtime).enrich(source, strength=30, target_length=120)

        self.assertEqual(repaired, result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("Target output length is 120 characters", runtime.calls[2][1])

    def test_enrichment_retries_when_chinese_input_is_returned_in_english(self):
        runtime = FakeRuntime(["The person presses the remote."])

        result = PromptService(runtime).enrich("人物按下遥控器。", 100)

        self.assertEqual("人物按下遥控器。", result)
        self.assertEqual(1, len(runtime.calls))

    def test_enrichment_repairs_a_new_plot_before_returning_it(self):
        runtime = FakeRuntime([
            "人物按下遥控器，陌生人进入房间并开始说话。",
            "FAIL",
            "人物按下遥控器，镜头短暂聚焦于按键动作。",
            "PASS",
        ])

        result = PromptService(runtime).enrich("人物按下遥控器。", 80)

        self.assertEqual("人物按下遥控器，镜头短暂聚焦于按键动作。", result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("new character", runtime.calls[1][1])
        self.assertIn("ORIGINAL SOURCE", runtime.calls[2][0])

    def test_enrichment_repairs_a_source_plus_afterword_even_when_the_content_review_passes(self):
        source = "人物按下遥控器。"
        runtime = FakeRuntime([
            f"{source}\n\n镜头短暂聚焦于按键动作。",
            "PASS",
            "人物按下遥控器时，镜头短暂聚焦于按键动作。",
            "PASS",
        ])

        result = PromptService(runtime).enrich(source, 50)

        self.assertEqual("人物按下遥控器时，镜头短暂聚焦于按键动作。", result)
        self.assertNotIn("\n\n", result)
        self.assertEqual(4, len(runtime.calls))

    def test_enrichment_restores_missing_picture_identity_and_starting_reference(self):
        source = (
            "图1是男生，图2是女生，视频场景是开始于图2。"
            "男生突然出现在女生后面，他拿着遥控器。"
        )
        runtime = FakeRuntime([
            "男生突然出现在女生后面，镜头跟随他手中的遥控器。",
            "PASS",
        ])

        result = PromptService(runtime).enrich(source, 50)

        self.assertTrue(result.startswith("图1是男生，图2是女生，视频场景是开始于图2，"))
        self.assertIn("男生突然出现在女生后面", result)
        self.assertNotIn("\n\n", result)

    def test_enrichment_restores_image_spelled_identity_and_start_scene_anchor(self):
        source = "图片1是男人，图片2是女人，视频开始于图片2的场景，男人出现在女人的画面中。"
        runtime = FakeRuntime([
            "画面始于女人的背影，男人从身后出现。",
            "PASS",
        ])

        result = PromptService(runtime).enrich(source, 100)

        self.assertTrue(result.startswith("图片1是男人，图片2是女人，视频开始于图片2的场景，"))

    @unittest.skip("H3 module editor removed")
    def test_decompose_returns_editable_modules(self):
        runtime = FakeRuntime([
            '{"scene":"原场景","shots":[{"duration_seconds":3,"action":"动作1","camera":""},{"duration_seconds":3,"action":"动作2","camera":""},{"duration_seconds":3,"action":"动作3","camera":""}],"overall_soundscape":"","non_diegetic_music":""}'
        ])
        result = PromptService(runtime).decompose("原始提示词", "fl2va")
        self.assertEqual(3, len(result["modules"]["shots"]))
        self.assertEqual("动作1", result["modules"]["shots"][0]["action"])
        self.assertEqual(384, runtime.calls[0][2]["max_new_tokens"])

    @unittest.skip("H3 module editor removed")
    def test_decompose_retries_once_when_the_model_returns_unterminated_json(self):
        runtime = FakeRuntime([
            '{"scene":"unterminated',
            '{"scene":"source","shots":[{"duration_seconds":3,"action":"run","camera":""}],"overall_soundscape":"","non_diegetic_music":""}',
        ])

        result = PromptService(runtime).decompose("source", "fl2va")

        self.assertEqual("source", result["modules"]["scene"])
        self.assertEqual(2, len(runtime.calls))
        self.assertTrue(runtime.calls[1][2]["stop_on_json"])

    @unittest.skip("H3 module editor removed")
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

    @unittest.skip("H3 module editor removed")
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
            "The man is male, the woman is female. The video scene begins with the woman. "
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
        self.assertNotIn("The man is male, the woman is female.", result["output"])
        self.assertNotIn("The video scene begins with the woman.", result["output"])
        self.assertIn("[Shot 1]", result["chinese"])
        self.assertIn("[Shot 2] At 00:02.500", result["chinese"])

    def test_fl2va_conversion_preserves_the_start_reference_and_emits_a_timed_shot_sequence(self):
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
            "\u4e2d\u6587\u9884\u89c8",
        ])

        result = PromptService(runtime).convert(source, "fl2va")

        self.assertTrue(result["output"].startswith(
            "For the target video, at 0.00 seconds into the target video, <Picture 2> (from [Shot 1]) is fully referenced."
        ))
        self.assertIn("integrated_multimodal_description: [Shot 1] At 00:00.000, Continue directly from <Picture 2>", result["output"])
        self.assertIn("[Shot 2] At 00:02.500, Close-up on him pressing the remote.", result["output"])
        self.assertIn("[Shot 4] At 00:07.500, Cut to an extremely low-angle shot", result["output"])
        self.assertIn("overall_soundscape: a remote-control click and light movement", result["output"])
        self.assertTrue(result["audit"]["valid"])

    def test_fl2va_conversion_does_not_invent_a_picture_reference(self):
        runtime = FakeRuntime([
            "A person runs.",
            "PASS",
            "overall_soundscape: footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: footsteps\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert("一个人奔跑。", "fl2va")

        self.assertNotIn("<Picture", result["output"])
        self.assertNotIn("fully referenced", result["output"])
        self.assertIn("integrated_multimodal_description: [Shot 1] At 00:00.000, A person runs.", result["output"])
        self.assertTrue(result["audit"]["valid"])

    def test_fl2va_conversion_preserves_explicit_chinese_dialogue_untranslated(self):
        runtime = FakeRuntime([
            "The woman says <d>[Chinese] 不要动。</d>",
            "PASS",
            "overall_soundscape: the woman speaking\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 女人说 <d>[Chinese] 不要动。</d>\noverall_soundscape: 女人说话\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert("女人说：“不要动。”", "fl2va")

        self.assertIn("The woman says <d>[Chinese] 不要动。</d>", result["output"])
        self.assertNotIn("do not move", result["output"].lower())
        self.assertFalse(result["audit"]["missing"])

    def test_fl2va_and_ref2va_infer_soundscape_when_audio_model_returns_na(self):
        source = "A man presses a remote control and taps the woman's shoulder."
        translation = "A man presses a remote control and taps the woman's shoulder."
        for mode in ("fl2va", "ref2va"):
            runtime = FakeRuntime([
                translation,
                "PASS",
                "overall_soundscape: N/A\nnon_diegetic_music: N/A",
                "translated preview",
            ])

            result = PromptService(runtime).convert(source, mode)

            self.assertNotEqual("overall_soundscape: N/A", result["output"].splitlines()[-2])
            self.assertIn("remote-control click", result["output"])

    def test_fl2va_maps_seconds_later_and_infers_wind_and_umbrella_sounds(self):
        source = "女孩被一阵强风吹得头发飞扬，手里的雨伞被吹走。4秒后，女孩低头发现雨伞不见了，迅速四处查看。"
        translation = (
            "The girl's hair flies in a strong gust of wind and the umbrella in her hand is blown away. "
            "Four seconds later, the girl looks down, realizes the umbrella is gone, and quickly looks around."
        )
        runtime = FakeRuntime([
            translation,
            "PASS",
            "overall_soundscape: N/A\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: 中文预览\noverall_soundscape: 强风和雨伞拍打声\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert(source, "fl2va")

        self.assertIn("[Shot 1] At 00:00.000", result["output"])
        self.assertIn("[Shot 2] At 00:04.000, the girl looks down", result["output"])
        self.assertNotIn("Four seconds later", result["output"])
        self.assertIn("overall_soundscape: strong wind", result["output"])
        self.assertIn("an umbrella buffeted by the wind", result["output"])

    def test_conversion_rejects_visual_invention(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
        ])
        with self.assertRaisesRegex(RuntimeError, "no-invention review"):
            PromptService(runtime).convert("一个人奔跑", "fl2va")

    def test_conversion_accepts_a_punctuated_pass_verdict(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs.",
            "PASS.",
            "overall_soundscape: running footsteps\nnon_diegetic_music: N/A",
            "integrated_multimodal_description: [Shot 1] 一个人奔跑。\noverall_soundscape: running footsteps\nnon_diegetic_music: N/A",
        ])

        result = PromptService(runtime).convert("一个人奔跑。", "fl2va")

        self.assertIn("A person runs.", result["output"])
        self.assertEqual(
            ["translate", "visual_review", "audio", "chinese_preview"],
            [stage["name"] for stage in result["_stages"]],
        )

    def test_conversion_rejects_an_ambiguous_pass_explanation(self):
        runtime = FakeRuntime([
            "[Shot 1] A person runs in a red coat.",
            "PASS because most details match.",
            "[Shot 1] A person runs in a red coat.",
            "FAIL",
        ])

        with self.assertRaisesRegex(RuntimeError, "no-invention review"):
            PromptService(runtime).convert("一个人奔跑。", "fl2va")

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
