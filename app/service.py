import re
import time

from . import h3


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", str(text or "")))


def _is_within_enrichment_target(source: str, candidate: str, target_length: int | None) -> bool:
    """Honor the requested result length without ever shortening a longer source."""
    if target_length is None:
        return True
    compact_length = lambda value: len(re.sub(r"\s+", "", str(value or "")))
    lower_bound = round(target_length * 0.9)
    upper_bound = round(target_length * 1.1)
    if compact_length(source) > upper_bound:
        return True
    length = compact_length(candidate)
    return lower_bound <= length <= upper_bound


def _compact_length(value: str) -> int:
    return len(re.sub(r"\s+", "", str(value or "")))


def _enrichment_length_status(source: str, candidate: str, target_length: int | None) -> int:
    """Return -1 below target, 0 within target, or 1 above target."""
    if target_length is None:
        return 0
    lower_bound = round(target_length * 0.9)
    upper_bound = round(target_length * 1.1)
    if _compact_length(source) > upper_bound:
        return 0
    length = _compact_length(candidate)
    return -1 if length < lower_bound else 1 if length > upper_bound else 0


def _append_with_compact_limit(existing: str, addition: str, upper_bound: int) -> str:
    """Append creative prose without cutting the final result beyond its length ceiling."""
    available = max(0, upper_bound - _compact_length(existing))
    if available <= 0:
        return existing
    value = str(addition or "").strip()
    if _compact_length(value) <= available:
        return f"{existing.rstrip()} {value}".strip()

    consumed = 0
    cut_index = 0
    for index, character in enumerate(value):
        if not character.isspace():
            consumed += 1
        if consumed > available:
            break
        cut_index = index + 1
    prefix = value[:cut_index].rstrip()
    sentence_ends = [match.end() for match in re.finditer(r"[。！？.!?]", prefix)]
    if sentence_ends:
        viable = [end for end in sentence_ends if _compact_length(prefix[:end]) >= max(40, round(available * 0.6))]
        if viable:
            prefix = prefix[:viable[-1]].rstrip()
    return f"{existing.rstrip()} {prefix}".strip() if prefix else existing


def _ensure_source_opening(source: str, candidate: str) -> str:
    """Anchor an enrichment to the user's exact premise before creative detail."""
    source = str(source or "").strip()
    candidate = str(candidate or "").strip()
    if not source or not candidate:
        return candidate or source

    sentence_end = "。" if _contains_cjk(source) else "."
    anchored_source = source if re.search(r"[。！？.!?]$", source) else source + sentence_end
    if candidate.startswith(anchored_source):
        return candidate
    if candidate.startswith(source):
        remainder = candidate[len(source):].lstrip(" ，,。.!！？?；;：:\t\r\n")
        return anchored_source if not remainder else f"{anchored_source}{'' if _contains_cjk(source) else ' '}{remainder}"
    return f"{anchored_source}{'' if _contains_cjk(source) else ' '}{candidate}"


def _fit_enrichment_upper_bound(source: str, candidate: str, target_length: int | None) -> str:
    """Keep the exact source anchor while fitting a model result to the requested ceiling."""
    if target_length is None:
        return candidate
    upper_bound = round(target_length * 1.1)
    if _compact_length(source) > upper_bound or _compact_length(candidate) <= upper_bound:
        return candidate
    sentence_end = "。" if _contains_cjk(source) else "."
    anchored_source = source if re.search(r"[。！？.!?]$", source) else source + sentence_end
    remainder = candidate[len(anchored_source):].lstrip() if candidate.startswith(anchored_source) else candidate
    return _append_with_compact_limit(anchored_source, remainder, upper_bound)


_ENRICHMENT_DRIFT_PATTERNS = {
    "violence/coercion": (
        r"强迫|强行|胁迫|绑架|施暴|殴打|掐住|窒息|侵犯|强奸|威胁|按住|束缚|昏厥|昏迷|迷晕|下药|"
        r"伤害|伤口|伤痕|红肿|破皮|划破|流血|鲜血|沾血|血痕|血污|尸体|刺杀|人口贩卖|审讯|"
        r"铁笼|牢笼|锁孔|绑住|绑在|扣住|按向|砸向|踢(?:她|他|人)|咬进|牙印|挣扎|失去抵抗|"
        r"(?:force|coerc|kidnap|assault|rape|strangl|chok|threat|restrain|unconscious|drugged|"
        r"human trafficking|stab|corpse|blood|bleed|bruise|wound|cage|bind|tied|bite mark)\w*"
    ),
    "sexual content": (
        r"性爱|性交|性行为|阴道|阴蒂|肛门|乳房|乳头|精液|高潮|性侵|插入|侵入|抽插|淫语|"
        r"性器官|勃起|呻吟|舔(?:她|他|掉|过)|双腿之间|大腿内侧|"
        r"(?:sex|sexual|vagina|clitoris|anus|anal|breast|nipple|semen|orgasm|penetrat|genital|"
        r"erect|thrust|moan|lick)\w*"
    ),
    "crime": r"犯罪|卖淫|妓院|勒索|谋杀|(?:crime|criminal|brothel|prostitut|blackmail|murder)\w*",
    "disease/injury": (
        r"疾病|病史|患有|诊断|受伤|伤口|骨折|营养不良|(?:disease|diagnos|injur|wound|fracture|"
        r"malnutrition|medical condition)\w*"
    ),
}

_BIOGRAPHY_PATTERN = re.compile(
    r"(?:\b\d{1,3}\s*(?:岁|周岁|years? old|year-old|kg|公斤|千克|cm|厘米)\b|"
    r"[零一二三四五六七八九十百两]{1,4}(?:岁|米)|身高|体重|名叫|姓名(?:是|为)|职业(?:是|为)|曾任|前(?:模特|演员|教师|学生)|"
    r"(?:named|called|works? as|occupation|formerly|weighs?|kilograms?|medical history)\b)",
    flags=re.I,
)

_DIALOGUE_PATTERN = re.compile(
    r"[“”‘’「」『』\"!?！？]|(?:说道|说着|说话|说|问道|问|喊道|喊|回答|提议|欢呼|解释|低语|命令道|催促|"
    r"哽咽着说|(?:^|[^他她它])你们?|(?:^|[^他她它])我们?|"
    r"\b(?:says?|speaks?|dialogue|whispers?|orders?|asks?|replies?)\b)",
    flags=re.I,
)


def _enrichment_drift_categories(source: str, candidate: str) -> list[str]:
    """Detect high-risk story categories invented by an enrichment.

    This is deliberately relative to the source. It never removes or rejects a
    category the user supplied; it only catches a category that first appears in
    model-generated prose after a neutral premise.
    """
    source = str(source or "")
    candidate = str(candidate or "")
    categories = [
        name
        for name, pattern in _ENRICHMENT_DRIFT_PATTERNS.items()
        if re.search(pattern, candidate, flags=re.I) and not re.search(pattern, source, flags=re.I)
    ]
    if _BIOGRAPHY_PATTERN.search(candidate) and not _BIOGRAPHY_PATTERN.search(source):
        categories.append("biography")
    if _DIALOGUE_PATTERN.search(candidate) and not _DIALOGUE_PATTERN.search(source):
        categories.append("dialogue")
    return categories


def _remove_new_drift_sentences(source: str, candidate: str) -> str:
    """Drop only generated sentences that introduce a prohibited new category."""
    source = str(source or "").strip()
    candidate = _ensure_source_opening(source, candidate)
    sentence_end = "。" if _contains_cjk(source) else "."
    anchored_source = source if re.search(r"[。！？.!?]$", source) else source + sentence_end
    remainder = candidate[len(anchored_source):].lstrip() if candidate.startswith(anchored_source) else candidate
    sentences = re.findall(r".*?(?:[。！？.!?](?=\s|$)|[。！？]|$)", remainder, flags=re.S)
    kept: list[str] = []
    for sentence in sentences:
        value = sentence.strip().lstrip("”’」』\"").strip()
        if not value:
            continue
        categories = _enrichment_drift_categories(source, value)
        if categories:
            if "dialogue" in categories and kept and re.search(r"[！？!?]$", kept[-1]):
                kept.pop()
            continue
        kept.append(value)
    separator = "" if _contains_cjk(source) else " "
    return anchored_source if not kept else anchored_source + separator + separator.join(kept)


def _clean_enrichment_addition(source: str, addition: str) -> str:
    """Clean one new continuation without re-segmenting previously accepted prose."""
    source = str(source or "").strip()
    sentence_end = "。" if _contains_cjk(source) else "."
    anchored_source = source if re.search(r"[。！？.!?]$", source) else source + sentence_end
    cleaned = _remove_new_drift_sentences(source, addition)
    return cleaned[len(anchored_source):].lstrip() if cleaned.startswith(anchored_source) else cleaned


def _is_pass_verdict(text: str) -> bool:
    value = str(text or "").strip()
    value = re.sub(r"^```(?:text)?\s*|\s*```$", "", value, flags=re.I).strip()
    value = value.strip("`*_\"'")
    return re.fullmatch(r"PASS[.!:]?", value, flags=re.I) is not None


def _translation_token_limit(source: str) -> int:
    """Reserve enough output for long source prompts without overrunning context."""
    # Chinese source text is close to one token per character, while the faithful
    # English translation is usually longer.  Keep the default fast for short
    # prompts, but scale up for long prompts that previously hit the 700-token cap.
    source_length = len(re.sub(r"\s+", "", str(source or "")))
    extra_length = max(0, source_length - 20)
    return min(1800, max(700, 700 + round(extra_length * 0.45)))


class PromptService:
    def __init__(self, runtime):
        self.runtime = runtime

    def enrich(self, text: str, strength: int, target_length: int | None = None) -> str:
        strength = max(0, min(100, int(strength)))
        requested_target_length = target_length
        target_length = max(100, min(2000, int(target_length or 500)))
        source = text.strip()
        if strength == 0:
            # Zero is the conservative preset: retain every supplied fact exactly.
            return source
        temperature = round(0.15 + 0.75 * strength / 100, 3)
        top_p = round(0.35 + 0.60 * strength / 100, 3)
        enriched = self.runtime.generate(
            source,
            h3.enrichment_system(strength, target_length),
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=h3.enrichment_token_limit(strength, target_length),
        ).strip()
        enriched_valid = bool(enriched) and not (_contains_cjk(source) and not _contains_cjk(enriched))
        candidate = ""
        candidate_reviewed = False
        deterministic_drift: list[str] = []
        if enriched_valid:
            enriched = h3.restore_enrichment_protected_facts(source, enriched)
            enriched = _ensure_source_opening(source, enriched)
            deterministic_drift = _enrichment_drift_categories(source, enriched)
            if deterministic_drift:
                enriched = _remove_new_drift_sentences(source, enriched)
            if not deterministic_drift:
                review = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{enriched}",
                    h3.enrichment_review_system(strength, target_length), temperature=0.01, top_p=0.1, max_new_tokens=8,
                ).strip().upper()
                needs_integration = enriched.startswith(source) and "\n\n" in enriched
                if _is_pass_verdict(review) and not needs_integration:
                    candidate = enriched
                    candidate_reviewed = True
                    if _is_within_enrichment_target(source, candidate, requested_target_length):
                        return candidate

        if not candidate_reviewed or _enrichment_length_status(source, candidate, requested_target_length) > 0:
            drift_note = ", ".join(deterministic_drift) if deterministic_drift else "none"
            proposed_enrichment = (
                "[discarded because it introduced new story categories; regenerate from ORIGINAL SOURCE only]"
                if deterministic_drift
                else enriched if enriched_valid else "[invalid or empty output]"
            )
            repair_attempts = 3 if deterministic_drift else 1
            repair_temperature = min(temperature, 0.35) if deterministic_drift else temperature
            repair_top_p = min(top_p, 0.6) if deterministic_drift else top_p
            repair_succeeded = False
            for attempt in range(repair_attempts):
                retry_note = "\nThe previous automatic attempt still drifted; regenerate again from ORIGINAL SOURCE only." if attempt else ""
                repaired = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nDETERMINISTIC DRIFT FLAGS: {drift_note}{retry_note}\n\n"
                    f"PROPOSED ENRICHMENT:\n{proposed_enrichment}",
                    h3.enrichment_repair_system(strength, target_length),
                    temperature=repair_temperature,
                    top_p=repair_top_p,
                    max_new_tokens=h3.enrichment_token_limit(strength, target_length),
                ).strip()
                if not repaired or (_contains_cjk(source) and not _contains_cjk(repaired)):
                    continue
                candidate = h3.restore_enrichment_protected_facts(source, repaired)
                candidate = _ensure_source_opening(source, candidate)
                raw_repaired_drift = _enrichment_drift_categories(source, candidate)
                candidate = _remove_new_drift_sentences(source, candidate)
                candidate = _fit_enrichment_upper_bound(source, candidate, requested_target_length)
                repaired_drift = _enrichment_drift_categories(source, candidate)
                if repaired_drift:
                    drift_note = ", ".join(repaired_drift)
                    proposed_enrichment = "[discarded because it introduced new story categories; regenerate from ORIGINAL SOURCE only]"
                    continue
                if raw_repaired_drift and _compact_length(candidate) <= _compact_length(source) + 40:
                    drift_note = ", ".join(raw_repaired_drift)
                    proposed_enrichment = "[discarded because cleaning left no usable enrichment; regenerate from ORIGINAL SOURCE only]"
                    continue
                review = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{candidate}",
                    h3.enrichment_review_system(strength, target_length), temperature=0.01, top_p=0.1, max_new_tokens=8,
                ).strip().upper()
                if _is_pass_verdict(review) and not (candidate.startswith(source) and "\n\n" in candidate):
                    repair_succeeded = True
                    break
            if not repair_succeeded:
                raise RuntimeError("Prompt enrichment could not satisfy the requested creative-strength contract after automatic correction.")

        if _enrichment_length_status(source, candidate, requested_target_length) < 0:
            lower_bound = round(target_length * 0.9)
            upper_bound = round(target_length * 1.1)
            for _ in range(16):
                remaining = max(100, min(700, target_length - _compact_length(candidate)))
                context_tail = candidate[-800:]
                addition = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nEND OF EXISTING ENRICHED PROMPT:\n{context_tail}",
                    h3.enrichment_continuation_system(strength, remaining),
                    temperature=temperature,
                    top_p=top_p,
                    max_new_tokens=min(900, max(256, round(remaining * 1.5))),
                ).strip()
                if not addition or (_contains_cjk(source) and not _contains_cjk(addition)):
                    break
                compact_addition = re.sub(r"\s+", "", addition)
                if not compact_addition or compact_addition in re.sub(r"\s+", "", candidate):
                    break
                safe_addition = _clean_enrichment_addition(source, addition)
                if not safe_addition:
                    continue
                proposed_candidate = _append_with_compact_limit(candidate, safe_addition, upper_bound)
                candidate = proposed_candidate
                if _compact_length(candidate) >= lower_bound:
                    break

            if not _is_within_enrichment_target(source, candidate, requested_target_length):
                raise RuntimeError("Prompt enrichment could not meet the requested target length after bounded continuation.")
            final_review = self.runtime.generate(
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{candidate}",
                h3.enrichment_review_system(strength, target_length), temperature=0.01, top_p=0.1, max_new_tokens=8,
            ).strip().upper()
            if not _is_pass_verdict(final_review) or _enrichment_drift_categories(source, candidate):
                raise RuntimeError("Prompt enrichment continuations violated the requested creative-strength contract.")

        if not _is_within_enrichment_target(source, candidate, requested_target_length):
            raise RuntimeError("Prompt enrichment could not meet the requested target length after automatic correction.")
        return candidate

    def convert(self, text: str, mode: str) -> dict:
        source = h3.canonicalize_picture_references(text)
        stages = []
        # The direct-convert button is also used with prompts copied from WanGP's
        # queue/gallery.  Such input is already a complete H3 document; feeding
        # the whole document back through literal translation nests its fields
        # inside detailed_description and can never be faithful.
        if h3.has_complete_structure(source, mode) and h3.normalize_mode(mode) == "ref2va" and h3.has_untranslated_chinese(source):
            # A complete Chinese/mixed-language H3 document needs field-wise
            # translation, not the plain-prompt visual review pipeline.
            return self.micro_edit(source, mode)
        if h3.has_complete_structure(source, mode) and not h3.has_untranslated_chinese(source):
            output = h3.normalize_output(source, mode)
            check = h3.audit(output, mode)
            if not check.get("valid"):
                raise RuntimeError("The supplied H3 prompt has an invalid structure or missing fields.")
            chinese = self._timed_generate(
                stages, "chinese_preview", output, h3.chinese_preview_system(mode),
                temperature=0.01, top_p=0.1, max_new_tokens=900,
            )
            if not chinese or "\ufffd" in chinese or chinese.count("?") > 3:
                chinese = output
            return {"output": output, "chinese": chinese, "audit": check, "_stages": stages}
        translation_token_limit = _translation_token_limit(source)
        translation = self._timed_generate(stages, "translate",
            source, h3.conversion_system(mode), temperature=0.01, top_p=0.05,
            max_new_tokens=translation_token_limit
        )
        translation = h3.remove_unsupported_vocalizations(source, translation)
        review = self._timed_generate(stages, "visual_review",
            f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
            h3.visual_review_system(mode),
            temperature=0.01,
            top_p=0.1,
            max_new_tokens=8,
        ).strip().upper()
        if not _is_pass_verdict(review):
            # Long prompts can need more than one deterministic repair pass: a
            # first pass may remove an invention while accidentally dropping a
            # later clause. Keep the guard strict, but give the model two further
            # opportunities to restore the complete source before failing closed.
            max_repairs = 2 if len(re.sub(r"\s+", "", source)) >= 300 else 1
            for attempt in range(1, max_repairs + 1):
                translation = self._timed_generate(
                    stages, "translation_retry" if attempt == 1 else f"translation_retry_{attempt}",
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                    h3.translation_repair_system(mode), temperature=0.01, top_p=0.05,
                    max_new_tokens=translation_token_limit,
                )
                translation = h3.remove_unsupported_vocalizations(source, translation)
                review = self._timed_generate(
                    stages, "visual_review_retry" if attempt == 1 else f"visual_review_retry_{attempt}",
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                    h3.visual_review_system(mode), temperature=0.01, top_p=0.1, max_new_tokens=8,
                ).strip().upper()
                if _is_pass_verdict(review):
                    break
            if not _is_pass_verdict(review):
                raise RuntimeError("The visual translation failed the strict no-invention review after automatic correction; no H3 output was returned.")
        if h3.has_unsupported_vocalization(source, translation):
            translation = self._timed_generate(
                stages, "vocalization_retry",
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                h3.translation_repair_system(mode), temperature=0.01, top_p=0.05,
                max_new_tokens=translation_token_limit,
            )
            review = self._timed_generate(
                stages, "visual_review_vocalization_retry",
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                h3.visual_review_system(mode), temperature=0.01, top_p=0.1, max_new_tokens=8,
            ).strip().upper()
            if not _is_pass_verdict(review) or h3.has_unsupported_vocalization(source, translation):
                raise RuntimeError("The visual translation contains an unsupported vocalization after automatic correction; no H3 output was returned.")
        soundscape, music = h3.parse_audio_output(
            self._timed_generate(stages, "audio", source, h3.audio_system(), temperature=0.01, top_p=0.1,
                                 max_new_tokens=160)
        )
        if soundscape == "N/A":
            soundscape = h3.infer_soundscape(source, translation)
        if h3.normalize_mode(mode) == "ref2va":
            output = h3.ref2va_timeline_wrap(translation, source, soundscape, music)
        else:
            output = h3.fl2va_timeline_wrap(translation, source, soundscape, music)
        check = h3.audit(output, mode)
        chinese = self._timed_generate(stages, "chinese_preview",
            output, h3.chinese_preview_system(mode), temperature=0.01, top_p=0.1, max_new_tokens=900
        )
        if _contains_cjk(source) and not _contains_cjk(chinese):
            # GGUF variants can occasionally emit literal question marks for Chinese.
            # Keep the source facts editable instead of returning corrupt text.
            if h3.normalize_mode(mode) == "ref2va":
                chinese = h3.ref2va_timeline_wrap(source, source)
            else:
                chinese = h3.fl2va_timeline_wrap(source, source)
        elif "\ufffd" in chinese or chinese.count("?") > 3:
            raise RuntimeError("The Chinese preview was unreadable; no corrupt preview was returned.")
        return {"output": output, "chinese": chinese, "audit": check, "_stages": stages}

    def _timed_generate(self, stages: list[dict], name: str, text: str, system: str, **settings) -> str:
        started = time.monotonic()
        try:
            return self.runtime.generate(text, system, **settings)
        finally:
            stages.append({"name": name, "elapsed_seconds": round(time.monotonic() - started, 3)})

    def micro_edit(self, edited: str, mode: str, original: str = "") -> dict:
        if not h3.has_complete_structure(edited, mode):
            return self.convert(edited, mode)
        baseline = original.strip() if original.strip() else edited
        system = h3.micro_edit_system(mode, original)
        output = self.runtime.generate(edited, system, temperature=0.01, top_p=0.1)
        output = h3.normalize_output(output, mode)
        if h3.has_untranslated_chinese(output):
            retry = "OUTPUT ENGLISH H3 ONLY. Translate every Chinese character outside <d> dialogue tags into English. Preserve every field, tag, reference, timestamp, fact, and line. Do not add or delete content."
            output = self.runtime.generate(output, retry, temperature=0.01, top_p=0.1)
            output = h3.normalize_output(output, mode)
        if h3.has_untranslated_chinese(output):
            raise RuntimeError("The output still contains untranslated Chinese outside dialogue tags.")
        if not h3.contract_matches(baseline, output, mode):
            raise RuntimeError("The output changed the H3 structure, shot markers, tags, or timestamps.")
        return {"output": output, "audit": h3.audit(output, mode)}


def _replace_audio_fields(output: str, soundscape: str, music: str) -> str:
    output = re.sub(r"(?m)^overall_soundscape:.*$", f"overall_soundscape: {soundscape}", output, count=1)
    output = re.sub(r"(?m)^non_diegetic_music:.*$", f"non_diegetic_music: {music}", output, count=1)
    return output
