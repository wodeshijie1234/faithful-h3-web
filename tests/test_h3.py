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

                expected = case["timestamps"]
                if case["mode"] == "ref2va" and expected and expected[0] == "00:00.000":
                    expected = expected[1:]
                self.assertEqual(expected, timestamps)
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
        self.assertIn("summary: [reference generation]", output)
        self.assertIn(f"detailed_description: {source}", output)
        self.assertTrue(h3.audit(output, "ref2va")["valid"])

    def test_ref2va_wrap_preserves_picture_identity_and_start_reference(self):
        source = "\\u56fe1\\u662f\\u7537\\u751f\\uff0c\\u56fe2\\u662f\\u5973\\u751f\\uff0c\\u89c6\\u9891\\u4ece\\u56fe2\\u5f00\\u59cb\u3002"
        source = "图1是男生，图2是女生，视频从图2开始。"
        output = h3.strict_wrap("<Picture 2> is the starting reference.", "ref2va", source_text=source)
        self.assertIn("<Subject 1> is the male subject from <Picture 1>", output)
        self.assertIn("<Subject 2> is the female subject from <Picture 2>", output)
        self.assertIn("summary: [reference generation] The target video begins with <Picture 2>.", output)

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
        self.assertIn("[Shot 1] The man suddenly appears behind the woman", output)
        self.assertNotIn("[Shot 1] <Picture 1> is a man", output)
        self.assertNotIn("<Picture 2> is a woman. [Shot", output)
        self.assertIn("[Shot 1]", output)
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

    def test_english_seconds_later_becomes_a_new_timed_shot(self):
        translation = (
            "The umbrella is blown away. Four seconds later, the girl looks down and searches."
        )

        output = h3.fl2va_timeline_wrap(translation, "女孩的雨伞被吹走。4秒后，她低头寻找。")

        self.assertIn("[Shot 1] At 00:00.000, The umbrella is blown away.", output)
        self.assertIn("[Shot 2] At 00:04.000, the girl looks down and searches.", output)
        self.assertNotIn("Four seconds later", output)

    def test_at_seconds_prefix_remains_supported(self):
        translation = "The person waits. At 4 seconds, the person turns."

        output = h3.fl2va_timeline_wrap(translation, "一个人等待。4秒时，他转身。")

        self.assertIn("[Shot 2] At 00:04.000, the person turns.", output)
        self.assertNotIn("At 4 seconds", output)

    def test_ref2va_explicit_shot_time_ranges_override_inferred_timing(self):
        source = "图1是男生，视频从图1开始。镜头1（0-4秒）：男生走入画面。镜头2（4-7秒）：他停下。"
        translation = "<Picture 1> is a man. The video begins with <Picture 1>. Shot 1: The man walks into frame. Shot 2: He stops."

        output = h3.ref2va_timeline_wrap(translation, source)

        self.assertIn("[Shot 1] The man walks into frame.", output)
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
        self.assertIn("[Shot 1] Suddenly", output)
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

    def test_unsupported_vocalization_cleanup_preserves_same_sentence_chinese_dialogue(self):
        source = '她持续发出娇喘声，并不断用中文说道：“好爽，啊，爸爸，快干死我”。'
        candidate = 'She continues to moan softly and repeatedly says in Chinese: "So good, ah, Dad, fuck me to death."'

        cleaned = h3.remove_unsupported_vocalizations(source, candidate)

        self.assertIn('<d>[Chinese] 好爽，啊，爸爸，快干死我</d>', cleaned)
        self.assertIn('moan', cleaned.lower())

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

    def test_high_strength_enrichment_allows_supporting_creative_development(self):
        prompt = h3.enrichment_system(100, 2000)
        review = h3.enrichment_review_system(100, 2000)

        self.assertIn("1800", prompt)
        self.assertIn("2200", prompt)
        self.assertIn("may introduce", prompt.lower())
        self.assertIn("setting", prompt.lower())
        self.assertIn("minor events", prompt.lower())
        self.assertIn("do not change the nature", prompt.lower())
        self.assertIn("violence", prompt.lower())
        self.assertIn("biography", prompt.lower())
        self.assertIn("creative additions are expected", review.lower())
        self.assertIn("genre or emotional tone", review.lower())
        self.assertIn("100/100", review)

        continuation = h3.enrichment_continuation_system(100, 700).lower()
        self.assertIn("write no direct speech", continuation)
        self.assertIn("visible staging", continuation)

    def test_decompose_uses_explicit_or_semantic_shot_count_without_padding(self):
        prompt = h3.decompose_system("fl2va").lower()
        self.assertIn("exactly that many", prompt)
        self.assertIn("do not pad", prompt)
        self.assertIn("semantic", prompt)

    def test_ref2va_supports_chinese_numeral_picture_identity_and_start(self):
        source = "图一为男生参考图，图二为女生参考图，视频场景开始于图二。女生站在房间里。"
        output = h3.ref2va_timeline_wrap("The girl stands in the room.", source)
        self.assertIn("<Subject 1> is the male subject from <Picture 1>", output)
        self.assertIn("<Subject 2> is the female subject from <Picture 2>", output)
        self.assertIn("summary: [reference generation] The target video begins with <Picture 2>.", output)

    def test_ref2va_official_subject_lines_and_shot_one_format(self):
        source = (
            "<Subject 1> is the violinist from <Picture 1>, preserving her identity and dark braided hair.\n"
            "<Video 1> is the reference camera rhythm.\n"
            "<Audio 1> is the voice reference for <Subject 1> (S1).\n"
            "The target video uses <Subject 1> with <Picture 1> as a character reference."
        )
        translation = (
            "The target video is a rooftop performance. [Shot 1] <Subject 1> raises the violin. "
            "[Shot 2] At 00:03.500, the camera follows <Video 1>."
        )
        output = h3.ref2va_timeline_wrap(translation, source)
        self.assertIn("<Subject 1> is the violinist from <Picture 1>, preserving her identity and dark braided hair.", output)
        self.assertIn("<Video 1> is the reference camera rhythm.", output)
        self.assertIn("<Audio 1> is the voice reference for <Subject 1> (S1).", output)
        self.assertIn("summary: [reference generation + audio reference]", output)
        detailed = output.split("detailed_description:", 1)[1].split("\noverall_soundscape:", 1)[0]
        self.assertIn("[Shot 1]", detailed)
        self.assertNotIn("[Shot 1] At ", detailed)
        self.assertIn("[Shot 2] At 00:03.500,", detailed)
        self.assertNotIn("\n\n", output)

    def test_ref2va_chinese_bracketed_shots_keep_picture_start_and_dialogue(self):
        source = (
            "图片1是男生参考图。图片2是女生参考图。[镜头1]:0秒实景拍摄、逼真写实、正常速度(无慢动作亦无静止状态)。"
            "视频第一帧画面由女生的所在图2场景开始，镜头由女生脸部特写后推画面缩小，慢慢展现出她全身。"
            "[镜头2]：3秒，镜头切换，女生坐着双腿张开高高抬起，脸部不遮挡，五官清晰可见。"
            "[镜头3]：5秒，镜头切换，男生从画面侧边走进画面内，双腿张开跪下在女生的正前方，他一下子用手掐住女生的脖子，力气很大，女生呼吸困难翻白眼。"
            "女生不断用中文说道：“啊，爸爸”"
        )
        output = h3.ref2va_timeline_wrap(source, source)
        self.assertIn("<Subject 1> is the male subject from <Picture 1>", output)
        self.assertIn("<Subject 2> is the female subject from <Picture 2>", output)
        self.assertIn("<Picture 2> is the first frame of [Shot 1]", output)
        self.assertIn("summary: [reference generation + keyframe completion]", output)
        detailed = output.split("detailed_description:", 1)[1].split("\noverall_soundscape:", 1)[0]
        self.assertIn("[Shot 1]", detailed)
        self.assertNotIn("[Shot 1] At ", detailed)
        self.assertIn("[Shot 2] At 00:03.000,", detailed)
        self.assertIn("[Shot 3] At 00:05.000,", detailed)
        self.assertNotIn("[镜头", detailed)
        self.assertNotIn("reference image. reference image.", detailed.lower())
        self.assertNotRegex(detailed, r"\[Shot 1\][^\[]*\b0 seconds\b")
        self.assertNotRegex(detailed, r"\[Shot 2\][^\[]*\b3 seconds\b")
        self.assertNotRegex(detailed, r"\[Shot 3\][^\[]*\b5 seconds\b")
        self.assertIn("<d>[Chinese] 啊，爸爸</d>", output)
        self.assertIn("<Subject 1> (appears in [Shot 3]): fully_preserved", output)
        self.assertIn(
            "<Subject 2> (appears in [Shot 1], [Shot 2], and [Shot 3]): fully_preserved",
            output,
        )
        retention = output.split("retention_analysis:", 1)[1].split("\ndetailed_description:", 1)[0]
        self.assertEqual(2, len([line for line in retention.splitlines() if line.strip()]))

    def test_ref2va_model_numbered_shots_remove_scaffolding_and_duplicate_times(self):
        source = "图片1是男生参考图。图片2是女生参考图。[镜头1]:0秒开始。[镜头2]：3秒切换。"
        translation = (
            "[Shot 1] At 00:00.000, reference image. reference image. 0 seconds, real-life filming. "
            "[Shot 2] At 00:03.000, 3 seconds, camera cuts to the female."
        )

        output = h3.ref2va_timeline_wrap(translation, source)
        detailed = output.split("detailed_description:", 1)[1].split("\noverall_soundscape:", 1)[0]

        self.assertIn("[Shot 1] real-life filming.", detailed)
        self.assertIn("[Shot 2] At 00:03.000, camera cuts to the female.", detailed)
        self.assertNotIn("reference image. reference image.", detailed.lower())
        self.assertNotIn("0 seconds", detailed)
        self.assertNotIn("3 seconds", detailed)

    def test_ref2va_final_output_cleanup_is_limited_to_shot_body_prefixes(self):
        output = (
            "subject_definitions: <Subject 1> is sourced from a reference image.\n"
            "summary: [reference generation]\n"
            "retention_analysis: N/A\n"
            "detailed_description: <Picture 1> is the first frame of [Shot 1]. "
            "[Shot 1] reference image. reference image. 0 seconds, real-life filming. "
            "[Shot 2] At 00:03.000, 3 seconds, camera cuts.\n"
            "overall_soundscape: N/A\n"
            "non_diegetic_music: N/A"
        )

        cleaned = h3._clean_built_ref2va_shot_prefixes(output)

        self.assertIn("<Subject 1> is sourced from a reference image.", cleaned)
        self.assertIn("<Picture 1> is the first frame of [Shot 1]. [Shot 1] real-life filming.", cleaned)
        self.assertIn("[Shot 1] real-life filming.", cleaned)
        self.assertIn("[Shot 2] At 00:03.000, camera cuts.", cleaned)
        self.assertNotIn("reference image. reference image.", cleaned)
        self.assertNotIn("0 seconds", cleaned)
        self.assertNotIn("3 seconds", cleaned)


if __name__ == "__main__":
    unittest.main()
