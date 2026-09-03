import unittest

from app.service import (
    _build_deterministic_integrated_enrichment,
    PromptService,
    _clean_extra_utterance_clauses,
    _enrichment_drift_categories,
    _has_utterance_contract_violation,
    _remove_new_drift_sentences,
    _truncate_after_terminal_utterance,
    _enrichment_action_segments,
)


class FakeRuntime:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.calls = []

    def generate(self, text, system, **settings):
        self.calls.append((text, system, settings))
        return next(self.outputs)


class PromptServiceTests(unittest.TestCase):
    def test_enrichment_drift_guard_detects_only_new_sensitive_story_elements(self):
        neutral = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        drifted = neutral + "。女孩约十六岁，被强行按住并遭到性侵犯。她说道：“不要。”"

        categories = _enrichment_drift_categories(neutral, drifted)

        self.assertIn("violence/coercion", categories)
        self.assertIn("sexual content", categories)
        self.assertIn("biography", categories)
        self.assertIn("dialogue", categories)

        explicit = "一个成年人遭到强迫并说道：“不要。”"
        self.assertNotIn("violence/coercion", _enrichment_drift_categories(explicit, explicit + "镜头保持不动。"))
        self.assertNotIn("dialogue", _enrichment_drift_categories(explicit, explicit + "镜头保持不动。"))

    def test_enrichment_drift_cleaner_keeps_neutral_sentences_and_exact_source(self):
        source = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        candidate = (
            source + "。阳光落在草地上。女孩约十六岁，名叫美咲。"
            "他们把彩球传来传去。她说道：“再来一次。”镜头缓慢拉远。"
        )

        cleaned = _remove_new_drift_sentences(source, candidate)

        self.assertTrue(cleaned.startswith(source + "。"))
        self.assertIn("阳光落在草地上", cleaned)
        self.assertIn("把彩球传来传去", cleaned)
        self.assertIn("镜头缓慢拉远", cleaned)
        self.assertNotIn("十六岁", cleaned)
        self.assertNotIn("美咲", cleaned)
        self.assertNotIn("再来一次", cleaned)

    def test_enrichment_drift_guard_detects_unquoted_dialogue_and_body_measurements(self):
        source = "女孩和小矮人玩耍"
        candidate = source + "。小矮人身高约一米。你们要玩什么？她问。"

        categories = _enrichment_drift_categories(source, candidate)

        self.assertIn("biography", categories)
        self.assertIn("dialogue", categories)

    def test_enrichment_drift_cleaner_removes_speech_before_an_attribution(self):
        source = "女孩和小矮人玩耍"
        candidate = source + "。阳光落在草地上。太酷了！女孩笑着说。镜头缓慢拉远。"

        cleaned = _remove_new_drift_sentences(source, candidate)

        self.assertIn("阳光落在草地上", cleaned)
        self.assertIn("镜头缓慢拉远", cleaned)
        self.assertNotIn("太酷了", cleaned)
        self.assertNotIn("笑着说", cleaned)

    def test_enrichment_drift_cleaner_removes_real_model_harm_and_sexual_drift(self):
        source = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        candidate = (
            source + "。室内光线柔和。看啊！男孩用脚踢她的膝盖。"
            "玻璃瓶划破她的脸颊，血顺着下巴滴落。镜头缓慢拉远。"
            "他把她推进铁笼并绑住手腕。手指揉弄她的阴蒂。地板反射着微光。"
        )

        cleaned = _remove_new_drift_sentences(source, candidate)

        self.assertTrue(cleaned.startswith(source + "。"))
        self.assertIn("室内光线柔和", cleaned)
        self.assertIn("镜头缓慢拉远", cleaned)
        self.assertIn("地板反射着微光", cleaned)
        for forbidden in ("看啊", "踢她", "划破", "血顺着", "铁笼", "绑住", "阴蒂"):
            self.assertNotIn(forbidden, cleaned)

    def test_enrichment_repairs_a_drifted_candidate_even_when_model_review_passes(self):
        source = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        drifted = source + "。她被强行按住，并说道：“不要。”"
        repaired = source + "。阳光落在草地上，他们围着彩色木球做轻松的传接游戏。" + "景" * 1800
        runtime = FakeRuntime([drifted, repaired, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertTrue(result.startswith(source + "。"))
        self.assertNotIn("强行", result)
        self.assertEqual(3, len(runtime.calls))
        self.assertIn("DETERMINISTIC DRIFT FLAGS", runtime.calls[1][0])
        self.assertLessEqual(runtime.calls[1][2]["temperature"], 0.35)

    def test_enrichment_retries_drift_repair_from_the_source_before_failing(self):
        source = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        drifted = source + "。她被强行按住。"
        still_drifted = source + "。场景变成性侵。"
        repaired = source + "。他们在草地上传接彩球。" + "景" * 1800
        runtime = FakeRuntime([drifted, still_drifted, repaired, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertTrue(result.startswith(source + "。"))
        self.assertNotIn("性侵", result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("previous automatic attempt", runtime.calls[2][0])

    def test_complete_english_h3_input_is_not_translated_again(self):
        source = (
            "subject_definitions: <Subject 1> (<Picture 1>) is male.\n"
            "summary: [reference generation] The target video begins with <Picture 1>.\n"
            "retention_analysis: N/A\n"
            "detailed_description: [Shot 1] At 00:00.000, A man walks forward.\n"
            "overall_soundscape: footsteps\nnon_diegetic_music: N/A"
        )
        runtime = FakeRuntime([source])

        result = PromptService(runtime).convert(source, "ref2va")

        self.assertEqual(source, result["output"])
        self.assertEqual(1, len(runtime.calls))

    def test_complete_chinese_ref2va_input_uses_fieldwise_micro_edit(self):
        source = (
            "subject_definitions: <Subject 1> (<Picture 1>) 是男性。\n"
            "summary: 目标视频以 <Picture 1> 开始。\n"
            "retention_analysis: N/A\n"
            "detailed_description: [Shot 1] At 00:00.000, 男人向前走。\n"
            "overall_soundscape: 脚步声\nnon_diegetic_music: N/A"
        )
        translated = (
            "subject_definitions: <Subject 1> (<Picture 1>) is male.\n"
            "summary: The target video begins with <Picture 1>.\n"
            "retention_analysis: N/A\n"
            "detailed_description: [Shot 1] At 00:00.000, A man walks forward.\n"
            "overall_soundscape: footsteps\nnon_diegetic_music: N/A"
        )
        runtime = FakeRuntime([translated])

        result = PromptService(runtime).convert(source, "ref2va")

        self.assertEqual(translated, result["output"])
        self.assertEqual(1, len(runtime.calls))

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
            [(0.27, 0.5), (0.35, 0.6), (0.47, 0.75), (0.55, 0.85)],
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

    def test_enrichment_integrates_the_full_ref_prompt_without_prepending_the_source(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景出发，女生保持第一帧动作不变，"
            "男生从侧边进入画面，他举起手不断摇摆向女生打招呼，她看着男生不断打招呼感到滑稽"
            "用手捂住嘴巴偷笑，女生用中文不断发出“啊，啊”的声音，最后女生高高抬起一条腿，"
            "另一条腿站立，旋转身体一脚踢到男生脸上，男生应声倒地。女生用中文说：“你发神经，该打”"
        )
        integrated = (
            "图1是男生参考图，图2是女生参考图，视频从女生所在场景展开；女生保持第一帧姿态稳定，"
            "镜头以中景记录男生从画面侧边进入，他举起手连续左右摇摆向她打招呼；她注视男生反复"
            "挥手的滑稽动作，抬手捂住嘴偷笑，同时持续用中文发出“啊，啊”的声音。动作推进到结尾，"
            "女生以另一条腿稳稳支撑，高高抬起一条腿并旋转身体，一脚踢中男生脸部，男生随即倒地；"
            "她最后用中文说：“你发神经，该打”。"
        )
        runtime = FakeRuntime([integrated, "PASS"])

        result = PromptService(runtime).enrich(source, strength=80)

        self.assertEqual(integrated, result)
        self.assertNotIn(source, result)
        self.assertEqual(1, result.count("男生从画面侧边进入"))
        self.assertEqual(1, result.count("你发神经，该打"))

    def test_enrichment_repairs_a_repeated_full_source_even_when_review_passes(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景出发，女生保持第一帧动作不变，"
            "男生从侧边进入画面，他举起手不断摇摆向女生打招呼，她用手捂住嘴巴偷笑，"
            "最后女生旋转身体一脚踢到男生脸上，男生应声倒地。"
        )
        repeated = source + source
        integrated = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景展开，女生保持第一帧动作不变；"
            "男生从侧边进入画面，镜头跟随他举起并不断摇摆的手，她看着这滑稽动作，用手捂住嘴巴偷笑；"
            "最后女生以单腿支撑旋转身体，一脚踢到男生脸上，男生应声倒地。"
        )
        runtime = FakeRuntime([repeated, "PASS", integrated, "PASS"])

        result = PromptService(runtime).enrich(source, strength=80)

        self.assertEqual(integrated, result)
        self.assertEqual(1, result.count("图1是男生参考图"))
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("repeated", runtime.calls[2][0].lower())

    def test_enrichment_repairs_story_continued_after_the_source_ending_even_when_review_passes(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景出发，女生保持第一帧动作不变，"
            "男生从侧边进入画面，他举起手不断摇摆向女生打招呼，她看着男生不断打招呼感到滑稽"
            "用手捂住嘴巴偷笑，女生用中文不断发出“啊，啊”的声音，最后女生高高抬起一条腿，"
            "另一条腿站立，旋转身体一脚踢到男生脸上，男生应声倒地。女生用中文说：“你发神经，该打”"
        )
        continued_story = (
            source
            + "。男生躺在地上揉着脸，女生走到门口，她又说：“再敢来就不只是脸了。”"
            + "两人随后走进电梯，前往一场灯火辉煌的宴会。"
        )
        integrated = (
            "图1是男生参考图，图2是女生参考图。镜头从女生所在场景平稳展开，女生保持第一帧动作不变；"
            "男生从侧边进入画面，他举起手连续摇摆向她打招呼，她看着这组滑稽动作，抬手捂住嘴巴偷笑，"
            "同时不断用中文发出“啊，啊”的声音。最后，女生以一条腿稳稳站立，高高抬起另一条腿，"
            "旋转身体一脚踢到男生脸上，男生应声倒地；女生用中文说：“你发神经，该打”。"
        )
        runtime = FakeRuntime([continued_story, "PASS", integrated, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100)

        self.assertEqual(integrated, result)
        self.assertNotIn("电梯", result)
        self.assertNotIn("再敢来", result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("post-terminal", runtime.calls[2][0])

    def test_enrichment_retries_a_post_terminal_story_repair_before_failing(self):
        source = "人物挥手，最后用中文说：“到此为止”"
        continued_story = source + "。随后人物走进电梯。"
        still_continued = source + "。接着人物前往宴会厅。"
        integrated = "人物在柔和侧光下连续挥手，最后面向镜头用中文说：“到此为止”。"
        runtime = FakeRuntime([
            continued_story, "PASS",
            still_continued,
            integrated, "PASS",
        ])

        result = PromptService(runtime).enrich(source, strength=100)

        self.assertEqual(integrated, result)
        self.assertEqual(5, len(runtime.calls))
        self.assertIn("previous automatic attempt", runtime.calls[3][0])

    def test_utterance_contract_rejects_missing_source_speech_and_invented_speech(self):
        source = "女生不断发出“啊，啊”的声音，最后说：“你发神经，该打”"

        self.assertTrue(_has_utterance_contract_violation(source, "女生说：“干嘛？”然后离开。"))
        self.assertTrue(_has_utterance_contract_violation(source, "女生发出“啊，啊”的声音。"))
        self.assertTrue(
            _has_utterance_contract_violation(
                source,
                "女生发出“啊，啊”的声音，最后说：“你发神经，该打”，又说：“再见”。",
            )
        )
        self.assertFalse(
            _has_utterance_contract_violation(
                source,
                "女生持续发出“啊，啊”的声音，最后清晰地说：“你发神经，该打”。",
            )
        )

    def test_utterance_contract_ignores_quoted_non_vocal_sound_effects(self):
        source = "女生说：“到此为止”"
        candidate = "碰撞时发出沉闷的“砰”声，女生最后说：“到此为止”。"

        self.assertFalse(_has_utterance_contract_violation(source, candidate))

    def test_enrichment_truncates_only_the_story_after_an_explicit_terminal_utterance(self):
        source = "人物挥手，最后说：“到此为止”"
        candidate = "人物在侧光下连续挥手，最后清晰地说：“到此为止”。说完后走进电梯。"

        result = _truncate_after_terminal_utterance(source, candidate)

        self.assertEqual("人物在侧光下连续挥手，最后清晰地说：“到此为止”。", result)
        self.assertNotIn("电梯", result)

    def test_terminal_utterance_in_the_middle_is_not_used_to_truncate_source_actions(self):
        source = "人物抬腿踢击并倒地，最后说：“到此为止”"
        candidate = "人物先说：“到此为止”，随后抬腿踢击并倒地。"

        self.assertEqual(candidate, _truncate_after_terminal_utterance(source, candidate))

    def test_enrichment_removes_only_extra_utterance_clauses_and_keeps_source_actions(self):
        source = "男生进入并挥手，女生发出“啊，啊”的声音，最后说：“到此为止”"
        candidate = (
            "男生从侧边进入并连续挥手，嘴里喊着“喂喂喂”；女生捂嘴偷笑并发出“啊，啊”的声音，"
            "碰撞发出“砰”声，男生发出“哎哟”的痛呼，最后女生说：“到此为止”。"
        )

        cleaned = _clean_extra_utterance_clauses(source, candidate)

        self.assertIn("男生从侧边进入并连续挥手", cleaned)
        self.assertIn("“啊，啊”", cleaned)
        self.assertIn("“砰”声", cleaned)
        self.assertIn("“到此为止”", cleaned)
        self.assertNotIn("喂喂喂", cleaned)
        self.assertNotIn("哎哟", cleaned)

    def test_enrichment_repairs_utterance_contract_even_when_model_review_passes(self):
        source = "人物挥手并不断发出“啊，啊”的声音，最后说：“到此为止”"
        wrong = "人物挥手后说：“喂，你看我。”随后走进电梯。"
        integrated = "人物在侧光下连续挥手，同时不断发出“啊，啊”的声音，最后清晰地说：“到此为止”。"
        runtime = FakeRuntime([wrong, "PASS", integrated, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100)

        self.assertEqual(integrated, result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("utterance contract violation", runtime.calls[2][0])

    def test_enrichment_passes_explicit_verbatim_utterance_anchors_to_the_model(self):
        source = "人物不断发出“啊，啊”的声音，最后说：“到此为止”"
        integrated = "人物在稳定镜头中不断发出“啊，啊”的声音，最后清晰地说：“到此为止”。"
        runtime = FakeRuntime([integrated, "PASS"])

        PromptService(runtime).enrich(source, strength=100)

        self.assertIn("MANDATORY VERBATIM UTTERANCES", runtime.calls[0][0])
        self.assertIn("- 啊，啊", runtime.calls[0][0])
        self.assertIn("- 到此为止", runtime.calls[0][0])

    def test_enrichment_discards_a_structurally_invalid_story_before_repair(self):
        source = "人物挥手，最后说：“到此为止”"
        drifted = source + "。随后走进电梯参加宴会。"
        repaired = "人物在侧光下连续挥手，最后清晰地说：“到此为止”。"
        runtime = FakeRuntime([drifted, "PASS", repaired, "PASS"])

        PromptService(runtime).enrich(source, strength=100)

        self.assertNotIn("电梯参加宴会", runtime.calls[2][0])
        self.assertIn("regenerate from ORIGINAL SOURCE only", runtime.calls[2][0])

    def test_enrichment_sampling_remains_instruction_controlled_at_max_strength(self):
        runtime = FakeRuntime(["完整融合提示词。", "PASS"])

        PromptService(runtime).enrich("原始提示词。", strength=100)

        self.assertLessEqual(runtime.calls[0][2]["temperature"], 0.55)
        self.assertLessEqual(runtime.calls[0][2]["top_p"], 0.85)

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

    def test_high_strength_review_receives_strength_and_length_contract(self):
        runtime = FakeRuntime(["中" * 1900, "PASS"])

        result = PromptService(runtime).enrich("一个简短场景。", strength=100, target_length=2000)

        self.assertGreaterEqual(len(result), 1900)
        self.assertIn("Creative strength is 100/100", runtime.calls[1][1])
        self.assertIn("Target output length is 2000 characters", runtime.calls[1][1])

    def test_enrichment_reports_contract_failure_instead_of_silent_source_fallback(self):
        source = "一个简短场景。"
        runtime = FakeRuntime([
            "稍有扩展。", "PASS",
            "", "", "", "", "", "",
        ])

        with self.assertRaisesRegex(RuntimeError, "target length"):
            PromptService(runtime).enrich(source, strength=100, target_length=2000)

    def test_enrichment_uses_a_full_integrated_rewrite_to_reach_a_long_target(self):
        source = "一个简短场景。"
        initial = "中" * 600
        rewritten = "景" * 1900
        runtime = FakeRuntime([initial, "PASS", rewritten, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertGreaterEqual(len(result), 1800)
        self.assertLessEqual(len(result), 2200)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("Rewrite the entire", runtime.calls[2][1])

    def test_enrichment_rewrites_the_whole_short_draft_instead_of_appending_after_terminal_dialogue(self):
        source = "人物挥手，最后说：“到此为止”"
        short = "人物在侧光下挥手，最后说：“到此为止”。"
        expanded = "人物在柔和侧光与稳定中景里连续挥手，镜头记录手臂运动细节。" + "光" * 1800 + "最后说：“到此为止”。"
        runtime = FakeRuntime([short, "PASS", expanded, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertEqual(expanded, result)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("Rewrite the entire", runtime.calls[2][1])
        self.assertNotIn(short + expanded, result)

    def test_enrichment_falls_back_to_ordered_in_place_action_segments_for_a_long_source(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景开始，女生保持姿势，"
            "男生从侧边进入并挥手，女生捂嘴偷笑并发出“啊，啊”的声音，"
            "最后女生抬腿旋转踢中男生，男生倒地，女生说：“到此为止”"
        )
        short = "图1和图2作为参考，动作依次发生，女生发出“啊，啊”，最后说：“到此为止”。"
        segment_outputs = [
            "参考图与起始构图中，女生保持姿势，男生进入并挥手。" + "甲" * 610,
            "女生捂嘴偷笑并发出“啊，啊”的声音。" + "乙" * 610,
            "女生抬腿旋转踢中男生，男生倒地。" + "丙" * 600 + "最后说：“到此为止”。",
        ]
        runtime = FakeRuntime([short, "PASS", "", "", "", *segment_outputs, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertGreaterEqual(len(result.replace(" ", "")), 1800)
        self.assertLessEqual(len(result.replace(" ", "")), 2200)
        self.assertEqual(1, result.count("啊，啊"))
        self.assertEqual(1, result.count("到此为止"))
        self.assertLess(result.index("男生进入并挥手"), result.index("女生捂嘴偷笑"))
        self.assertIn("Enrich only SOURCE ACTION SEGMENT", runtime.calls[5][1])

    def test_enrichment_action_segments_do_not_isolate_reference_setup_or_terminal_dialogue(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景出发，女生保持第一帧动作不变，"
            "男生从侧边进入画面，他举手不断摇摆打招呼，女生捂住嘴巴偷笑并发出“啊，啊”的声音，"
            "最后女生抬腿旋转踢中男生，男生倒地。女生说：“到此为止”"
        )

        segments = _enrichment_action_segments(source)

        self.assertGreaterEqual(len(segments), 3)
        self.assertIn("男生从侧边进入", segments[0])
        self.assertTrue(any("捂住嘴巴偷笑" in segment and "啊，啊" in segment for segment in segments))
        self.assertIn("抬腿旋转", segments[-1])
        self.assertIn("到此为止", segments[-1])

    def test_segment_fallback_retries_a_drifted_action_segment(self):
        source = "人物进入画面并挥手，最后说：“到此为止”"
        short = "人物进入并挥手，最后说：“到此为止”。"
        bad_segment = "人物进入画面并说：“跟我走。”"
        good_first = "人物进入画面并连续挥手。" + "甲" * 920
        good_final = "人物保持动作连续。" + "乙" * 880 + "最后说：“到此为止”。"
        runtime = FakeRuntime([
            short, "PASS", "", "", "",
            bad_segment, good_first, good_final, "PASS",
        ])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertNotIn("跟我走", result)
        self.assertEqual(1, result.count("到此为止"))
        self.assertNotIn("FULL SOURCE CONTEXT", runtime.calls[5][0])
        self.assertNotIn("到此为止", runtime.calls[5][0])
        self.assertIn("retry this segment", runtime.calls[6][0])

    def test_segment_fallback_adds_non_repeating_details_inside_each_short_action_segment(self):
        source = (
            "图1是男生参考图，视频从女生场景开始，男生进入并挥手，"
            "女生捂嘴偷笑并发出“啊，啊”的声音，"
            "最后女生旋转踢中男生，女生说：“到此为止”"
        )
        short = "男生进入挥手，女生发出“啊，啊”，最后说：“到此为止”。"
        bases = [
            "图1作为参考，视频从女生场景开始，男生进入并挥手。" + "甲" * 150,
            "女生捂嘴偷笑并发出“啊，啊”的声音。" + "乙" * 150,
            "最后女生旋转踢中男生。" + "丙" * 150 + "女生说：“到此为止”。",
        ]
        details = ["镜" * 450, "光" * 450, "声" * 450]
        runtime = FakeRuntime([
            short, "PASS", "", "", "",
            bases[0], details[0], bases[1], details[1], bases[2], details[2], "PASS",
        ])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertGreaterEqual(len(result.replace(" ", "")), 1800)
        self.assertEqual(1, result.count("男生进入并挥手"))
        self.assertEqual(1, result.count("啊，啊"))
        self.assertEqual(1, result.count("到此为止"))
        self.assertIn("supplemental", runtime.calls[6][1])

    def test_deterministic_integrated_fallback_meets_length_without_repeating_actions_or_dialogue(self):
        source = (
            "图1是男生参考图，图2是女生参考图。视频从女生场景开始，男生进入并挥手，"
            "女生捂嘴偷笑并发出“啊，啊”的声音，"
            "最后女生旋转踢中男生，男生倒地，女生说：“到此为止”"
        )

        result = _build_deterministic_integrated_enrichment(source, 2000)

        compact = "".join(result.split())
        self.assertGreaterEqual(len(compact), 1800)
        self.assertLessEqual(len(compact), 2200)
        self.assertEqual(1, result.count("男生进入并挥手"))
        self.assertEqual(1, result.count("女生捂嘴偷笑"))
        self.assertEqual(1, result.count("女生旋转踢中男生"))
        self.assertEqual(1, result.count("啊，啊"))
        self.assertEqual(1, result.count("到此为止"))
        self.assertTrue(result.rstrip().endswith("“到此为止”"))

    def test_enrichment_retries_a_drifted_full_length_rewrite(self):
        source = "一个简短场景。"
        initial = "景" * 600
        drifted = "你们继续吧！她说道。"
        safe = "光" * 1900
        runtime = FakeRuntime([initial, "PASS", drifted, safe, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertGreaterEqual(len(result), 1800)
        self.assertNotIn("你们继续", result)
        self.assertEqual(5, len(runtime.calls))

    def test_enrichment_retries_a_repeated_full_length_rewrite(self):
        source = "一个人物走入画面。"
        initial = "人物走入画面，镜头跟随脚步。" + "景" * 580
        repeated = "人物走入画面，镜头跟随脚步。" * 100
        safe = "人物走入画面，镜头跟随脚步。" + "光" * 1850
        runtime = FakeRuntime([initial, "PASS", repeated, safe, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertGreaterEqual(len(result), 1800)
        self.assertEqual(1, result.count("人物走入画面，镜头跟随脚步"))
        self.assertIn("光" * 100, result)
        self.assertEqual(5, len(runtime.calls))

    def test_enrichment_does_not_prepend_the_source_to_a_long_integrated_result(self):
        source = "一群小矮人和一个瘦弱日本女孩玩耍的场景"
        expanded = "公园里，一群小矮人围绕瘦弱日本女孩继续玩耍。" + "景" * 1900
        runtime = FakeRuntime([expanded, "PASS"])

        result = PromptService(runtime).enrich(source, strength=100, target_length=2000)

        self.assertEqual(expanded, result)
        self.assertNotIn(source, result)

    def test_enrichment_repairs_an_output_that_exceeds_the_target_length_tolerance(self):
        source = "A woman opens a blue umbrella."
        too_long = "A " * 200
        repaired = "A woman slowly opens a blue umbrella in light rain, keeping the camera focused on her hands and the unfolding fabric on a quiet street."
        runtime = FakeRuntime([too_long, "PASS", repaired, "PASS"])

        result = PromptService(runtime).enrich(source, strength=30, target_length=120)

        self.assertEqual(repaired, result)
        self.assertGreaterEqual(len(result.replace(" ", "")), 108)
        self.assertLessEqual(len(result.replace(" ", "")), 132)
        self.assertEqual(4, len(runtime.calls))
        self.assertIn("Target output length is 120 characters", runtime.calls[2][1])

    def test_enrichment_repairs_when_chinese_input_is_returned_in_english(self):
        runtime = FakeRuntime([
            "The person presses the remote.",
            "人物按下遥控器时，镜头聚焦于手指和按键的连续动作。",
            "PASS",
        ])

        result = PromptService(runtime).enrich("人物按下遥控器。", 100)

        self.assertIn("人物按下遥控器", result)
        self.assertNotEqual("人物按下遥控器。", result)
        self.assertEqual(3, len(runtime.calls))

    def test_enrichment_repairs_a_new_plot_before_returning_it(self):
        runtime = FakeRuntime([
            "人物按下遥控器，陌生人进入房间并开始说话。",
            "FAIL",
            "人物按下遥控器，镜头短暂聚焦于按键动作。",
            "PASS",
        ])

        result = PromptService(runtime).enrich("人物按下遥控器。", 80)

        self.assertEqual("人物按下遥控器，镜头短暂聚焦于按键动作。", result)
        self.assertIn("镜头短暂聚焦于按键动作", result)
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
        self.assertIn("镜头短暂聚焦于按键动作", result)
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
        self.assertNotIn(source, result)
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

        result = PromptService(runtime).convert("source " * 60, "fl2va")

        self.assertIn("A person runs.", result["output"])
        self.assertNotIn("red coat", result["output"])
        self.assertEqual(6, len(runtime.calls))
        self.assertEqual(
            ["translate", "visual_review", "translation_retry", "visual_review_retry", "audio", "chinese_preview"],
            [stage["name"] for stage in result["_stages"]],
        )

    def test_conversion_allows_multiple_repairs_for_long_translation(self):
        runtime = FakeRuntime([
            "bad", "FAIL", "still bad", "FAIL", "complete", "PASS",
            "overall_soundscape: N/A\nnon_diegetic_music: N/A", "preview",
        ])
        result = PromptService(runtime).convert("source " * 60, "fl2va")
        self.assertIn("complete", result["output"])

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
