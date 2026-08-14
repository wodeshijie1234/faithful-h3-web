import json
import re
import unittest
from pathlib import Path

from app import h3


class H3ContractTests(unittest.TestCase):
    def test_chinese_timeline_sample_set_uses_standard_h3_timestamps(self):
        cases = json.loads((Path(__file__).with_name("timeline_cn_cases.json")).read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(cases), 10)

        for case in cases:
            with self.subTest(case=case["id"]):
                wrapper = h3.ref2va_timeline_wrap if case["mode"] == "ref2va" else h3.fl2va_timeline_wrap
                output = wrapper(case["translation"], case["source"])
                description = output.split("detailed_description:", 1)[-1] if case["mode"] == "ref2va" else output.split("integrated_multimodal_description:", 1)[-1]
                description = description.split("\noverall_soundscape:", 1)[0]
                timestamps = re.findall(r"\[Shot\s+\d+\]\s+At\s+(\d{2}:\d{2}\.\d{3}),", description)

                self.assertEqual(case["timestamps"], timestamps)
                self.assertIsNone(re.search(
                    r"\bAt\s+(?:the\s+)?\d+(?:\.\d+)?(?:\s*-\s*|\s+)(?:seconds?|secs?|s)\b",
                    description,
                    flags=re.I,
                ))

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

    def test_strict_wrap_normalizes_plain_shot_labels(self):
        output = h3.strict_wrap("Shot 1: A person runs.\nShot 2: The person stops.", "fl2va")
        self.assertIn("[Shot 1] A person runs.", output)
        self.assertIn("[Shot 2] The person stops.", output)
        self.assertNotIn("clothing", output.lower())
        self.assertEqual([], h3.audit(output, "fl2va")["missing"])

    def test_ref2va_strict_wrap_preserves_source_verbatim(self):
        source = "参考图中的人物站在门边，镜头向前推进。"
        output = h3.strict_wrap(source, "ref2va")
        self.assertIn("summary: N/A", output)
        self.assertIn(f"detailed_description: {source}", output)
        self.assertTrue(h3.audit(output, "ref2va")["valid"])

    def test_ref2va_wrap_preserves_picture_identity_and_start_reference(self):
        source = "\\u56fe1\\u662f\\u7537\\u751f\\uff0c\\u56fe2\\u662f\\u5973\\u751f\\uff0c\\u89c6\\u9891\\u4ece\\u56fe2\\u5f00\\u59cb\u3002"
        source = "图1是男生，图2是女生，视频从图2开始。"
        output = h3.strict_wrap("<Picture 2> is the starting reference.", "ref2va", source_text=source)
        self.assertIn("<Subject 1> (<Picture 1>) is male.", output)
        self.assertIn("<Subject 2> (<Picture 2>) is female.", output)
        self.assertIn("summary: The video begins with <Picture 2>.", output)

    def test_ref2va_timeline_wrap_splits_explicit_camera_cuts(self):
        source = "图1是男生，图2是女生，视频场景开始于图2。"
        translation = (
            "<Picture 1> is a man, <Picture 2> is a woman. The video begins with <Picture 2>. "
            "The man suddenly appears behind the woman, holding a remote control. "
            "Close-up on him pressing the remote. Cut to medium shot. "
            "The woman freezes with vacant eyes and a slightly open mouth. He taps her shoulder from behind and runs his fingers through her hair. "
            "Cut to an extremely low-angle shot as he crouches in front of her, hugging her thighs and rubbing his face against her thigh."
        )

        output = h3.ref2va_timeline_wrap(translation, source)

        self.assertIn("summary: [reference generation] The target video begins with <Picture 2>.", output)
        self.assertIn("retention_analysis: <Subject 1> (appears in [Shot 1]): fully_preserved", output)
        self.assertIn("[Shot 1] At 00:00.000, The man suddenly appears behind the woman", output)
        self.assertNotIn("[Shot 1] <Picture 1> is a man", output)
        self.assertNotIn("<Picture 2> is a woman. [Shot", output)
        self.assertIn("[Shot 1] At 00:00.000", output)
        self.assertIn("[Shot 2] At 00:02.500, Close-up on him pressing the remote.", output)
        self.assertIn("[Shot 3] At 00:04.500, Cut to medium shot.", output)
        self.assertIn("[Shot 4] At 00:07.500, Cut to an extremely low-angle shot", output)
        self.assertTrue(h3.audit(output, "ref2va")["valid"])

    def test_fl2va_numbered_shots_keep_their_boundaries_and_infer_timing(self):
        source = "镜头1：一个人走入画面。镜头2：他停下。"
        translation = "Shot 1: A person walks into frame. Shot 2: He stops."

        output = h3.fl2va_timeline_wrap(translation, source)

        self.assertIn("[Shot 1] At 00:00.000, A person walks into frame.", output)
        self.assertIn("[Shot 2] At 00:02.000, He stops.", output)
        self.assertEqual(2, output.count("[Shot "))

    def test_fl2va_explicit_shot_time_ranges_override_inferred_timing(self):
        source = "镜头1（0-4秒）：一个人走入画面。镜头2（4-7秒）：他停下。"
        translation = "Shot 1: A person walks into frame. Shot 2: He stops."

        output = h3.fl2va_timeline_wrap(translation, source)

        self.assertIn("[Shot 1] At 00:00.000, A person walks into frame.", output)
        self.assertIn("[Shot 2] At 00:04.000, He stops.", output)

    def test_ref2va_explicit_shot_time_ranges_override_inferred_timing(self):
        source = "图1是男生，视频从图1开始。镜头1（0-4秒）：男生走入画面。镜头2（4-7秒）：他停下。"
        translation = "<Picture 1> is a man. The video begins with <Picture 1>. Shot 1: The man walks into frame. Shot 2: He stops."

        output = h3.ref2va_timeline_wrap(translation, source)

        self.assertIn("[Shot 1] At 00:00.000, The man walks into frame.", output)
        self.assertIn("[Shot 2] At 00:04.000, He stops.", output)

    def test_ref2va_unnumbered_explicit_times_create_standard_timed_shots(self):
        source = (
            "图1是男生，图2是女生，视频场景是开始于图2，视频开场于图2的场景。"
            "突然，男生从画面外悄无声息地出现在她身后，手里攥着一个黑色遥控器，"
            "镜头缓慢推进他的侧脸，他嘴角噙着一丝玩味的笑。"
            "2秒的时候，他按下遥控器，画面瞬间切换为中景，女生像被按下了暂停键。"
            "3秒，男生从她身后绕到正面。"
        )
        translation = (
            "<Picture 1> is male. <Picture 2> is female. The target video begins with <Picture 2>. "
            "Suddenly, the man appears silently behind her from off-screen, clutching a black remote control. "
            "The camera slowly pushes in on his profile as a smile plays on his lips. "
            "At 2 seconds, he presses the remote and the scene instantly cuts to a medium shot. "
            "The woman freezes in place. At 3 seconds, he moves around her to the front."
        )

        output = h3.ref2va_timeline_wrap(translation, source)

        detailed = output.split("detailed_description:", 1)[1].split("\noverall_soundscape:", 1)[0]
        self.assertEqual(3, detailed.count("[Shot "))
        self.assertIn("[Shot 1] At 00:00.000, Suddenly", output)
        self.assertIn("[Shot 2] At 00:02.000, he presses the remote", output)
        self.assertIn("[Shot 3] At 00:03.000, he moves around her to the front.", output)
        self.assertNotIn("At 2 seconds", output)
        self.assertNotIn("At 3 seconds", output)

    def test_unmentioned_vocalizations_are_detected(self):
        self.assertTrue(h3.has_unsupported_vocalization("A person remains still.", "The person moans."))
        self.assertFalse(h3.has_unsupported_vocalization("The person moans.", "The person moans."))

    def test_unmentioned_vocalization_sentence_is_removed_before_visual_review(self):
        source = "The person remains still."
        candidate = "The person remains still. She moans softly, eyes unfocused."

        cleaned = h3.remove_unsupported_vocalizations(source, candidate)

        self.assertEqual("The person remains still. Eyes unfocused.", cleaned)

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
        self.assertIn("[Shot 1] At 00:00.000, The woman raises one leg.", output)
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

    def test_decompose_parser_accepts_fenced_json_with_a_trailing_comma(self):
        raw = '''The extracted modules are:
```json
{"scene":"source","shots":[{"duration_seconds":3,"action":"run","camera":""}],"overall_soundscape":"","non_diegetic_music":"",}
```
'''
        modules = h3.parse_modules_json(raw, "fl2va")
        self.assertEqual("source", modules["scene"])
        self.assertEqual("run", modules["shots"][0]["action"])

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
