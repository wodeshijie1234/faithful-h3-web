import unittest

from app import h3


class H3ContractTests(unittest.TestCase):
    def test_mode_names_are_only_fl2va_and_ref2va(self):
        self.assertEqual("fl2va", h3.normalize_mode("FL2VA"))
        self.assertEqual("ref2va", h3.normalize_mode("Ref2VA"))

    def test_fl2va_contract_and_header(self):
        text = "integrated_multimodal_description: [Shot 1] A.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        output = h3.normalize_output(text, "fl2va")
        self.assertTrue(output.startswith(h3.FL2VA_HEADER))
        self.assertTrue(h3.audit(output, "fl2va")["valid"])

    def test_strict_wrap_preserves_source_verbatim(self):
        source = "图片是男生女生合照。女生在左边，男生在右边。镜头1：女生抬腿。"
        output = h3.strict_wrap(source, "fl2va")
        self.assertIn(f"integrated_multimodal_description: {source}", output)
        self.assertNotIn("clothing", output.lower())
        self.assertEqual([], h3.audit(output, "fl2va")["missing"])

    def test_ref2va_strict_wrap_preserves_source_verbatim(self):
        source = "参考图中的人物站在门边，镜头向前推进。"
        output = h3.strict_wrap(source, "ref2va")
        self.assertIn("summary: N/A", output)
        self.assertIn(f"detailed_description: {source}", output)
        self.assertTrue(h3.audit(output, "ref2va")["valid"])

    def test_audio_parser_only_accepts_two_audio_fields(self):
        soundscape, music = h3.parse_audio_output(
            "overall_soundscape: footsteps and fabric movement\n"
            "non_diegetic_music: N/A\n"
            "integrated_multimodal_description: invented visual detail"
        )
        self.assertEqual("footsteps and fabric movement", soundscape)
        self.assertEqual("N/A", music)

    def test_visual_review_is_strict_and_audio_is_out_of_scope(self):
        prompt = h3.visual_review_system("fl2va")
        self.assertIn("Return exactly PASS", prompt)
        self.assertIn("clothing", prompt)
        self.assertIn("Audio is out of scope", prompt)

    def test_empty_modules_start_with_three_shots(self):
        modules = h3.empty_modules("fl2va")
        self.assertEqual(3, len(modules["shots"]))
        self.assertTrue(all(shot["duration_seconds"] == 3.0 for shot in modules["shots"]))

    def test_build_fl2va_from_modules(self):
        modules = h3.empty_modules("fl2va")
        modules["scene"] = "The woman is on the left and the man is on the right."
        modules["shots"][0]["action"] = "The woman raises one leg."
        modules["shots"][0]["duration_seconds"] = 3.5
        modules["shots"][1].update(duration_seconds=2.5, action="The man crouches.", camera="Medium shot.")
        modules["overall_soundscape"] = "Breathing and fabric movement."
        output = h3.build_h3(modules, "fl2va")
        self.assertIn("[Shot 1] The woman raises one leg.", output)
        self.assertIn("[Shot 2] At 00:03.500, The man crouches. Medium shot.", output)
        self.assertIn("overall_soundscape: Breathing and fabric movement.", output)

    def test_shot_durations_are_clamped_and_quantized_to_half_seconds(self):
        modules = h3.normalize_modules(
            {
                "shots": [
                    {"duration_seconds": 0.1},
                    {"duration_seconds": 4.24},
                    {"duration_seconds": 35},
                ]
            },
            "fl2va",
        )
        self.assertEqual([0.5, 4.0, 30.0], [shot["duration_seconds"] for shot in modules["shots"]])

    def test_build_h3_uses_cumulative_shot_durations(self):
        modules = h3.empty_modules("fl2va")
        modules["shots"][0].update(duration_seconds=2.5, action="First action.")
        modules["shots"][1].update(duration_seconds=4.0, action="Second action.")
        modules["shots"][2].update(duration_seconds=1.5, action="Third action.")
        output = h3.build_h3(modules, "fl2va")
        self.assertIn("[Shot 2] At 00:02.500, Second action.", output)
        self.assertIn("[Shot 3] At 00:06.500, Third action.", output)

    def test_decompose_parser_preserves_module_shape(self):
        raw = '{"scene":"原场景","shots":[{"duration_seconds":3.5,"action":"动作1","camera":""}],"overall_soundscape":"","non_diegetic_music":""}'
        modules = h3.parse_modules_json(raw, "fl2va")
        self.assertEqual("原场景", modules["scene"])
        self.assertEqual("动作1", modules["shots"][0]["action"])
        self.assertEqual(3.5, modules["shots"][0]["duration_seconds"])

    def test_ref2va_requires_all_six_fields(self):
        text = "subject_definitions: x\nsummary: x\nretention_analysis: x\ndetailed_description: x\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        self.assertTrue(h3.audit(text, "ref2va")["valid"])

    def test_micro_edit_language_and_structure_guards(self):
        source = "integrated_multimodal_description: [Shot 1] 人物奔跑。\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        good = "integrated_multimodal_description: [Shot 1] A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        bad = "integrated_multimodal_description: A person runs.\noverall_soundscape: N/A\nnon_diegetic_music: N/A"
        self.assertTrue(h3.has_untranslated_chinese(source))
        self.assertFalse(h3.has_untranslated_chinese(good))
        self.assertTrue(h3.contract_matches(source, good, "fl2va"))
        self.assertFalse(h3.contract_matches(source, bad, "fl2va"))

    def test_prompts_are_non_creative_where_required(self):
        self.assertIn("do not add", h3.conversion_system("fl2va").lower())
        self.assertIn("Do not add, remove", h3.micro_edit_system("ref2va"))

    def test_decompose_uses_explicit_or_semantic_shot_count_without_padding(self):
        prompt = h3.decompose_system("fl2va").lower()
        self.assertIn("exactly that many", prompt)
        self.assertIn("do not pad", prompt)
        self.assertIn("semantic", prompt)


if __name__ == "__main__":
    unittest.main()
