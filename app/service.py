import re
import time

from . import h3


def _contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", str(text or "")))


def _is_pass_verdict(text: str) -> bool:
    value = str(text or "").strip()
    value = re.sub(r"^```(?:text)?\s*|\s*```$", "", value, flags=re.I).strip()
    value = value.strip("`*_\"'")
    return re.fullmatch(r"PASS[.!:]?", value, flags=re.I) is not None


class PromptService:
    def __init__(self, runtime):
        self.runtime = runtime

    def enrich(self, text: str, strength: int) -> str:
        strength = max(0, min(100, int(strength)))
        source = text.strip()
        if strength == 0:
            # Zero is the conservative preset: retain every supplied fact exactly.
            return source
        temperature = round(0.15 + 0.75 * strength / 100, 3)
        top_p = round(0.35 + 0.60 * strength / 100, 3)
        enriched = self.runtime.generate(
            source,
            h3.enrichment_system(strength),
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=h3.enrichment_token_limit(strength),
        ).strip()
        if not enriched or (_contains_cjk(source) and not _contains_cjk(enriched)):
            return source
        enriched = h3.restore_enrichment_protected_facts(source, enriched)
        review = self.runtime.generate(
            f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{enriched}",
            h3.enrichment_review_system(), temperature=0.01, top_p=0.1, max_new_tokens=8,
        ).strip().upper()
        needs_integration = enriched.startswith(source) and "\n\n" in enriched
        if _is_pass_verdict(review) and not needs_integration:
            return enriched

        repaired = self.runtime.generate(
            f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHMENT:\n{enriched}",
            h3.enrichment_repair_system(strength), temperature=temperature, top_p=top_p,
            max_new_tokens=h3.enrichment_token_limit(strength),
        ).strip()
        if not repaired or (_contains_cjk(source) and not _contains_cjk(repaired)):
            return source
        repaired = h3.restore_enrichment_protected_facts(source, repaired)
        review = self.runtime.generate(
            f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{repaired}",
            h3.enrichment_review_system(), temperature=0.01, top_p=0.1, max_new_tokens=8,
        ).strip().upper()
        if not _is_pass_verdict(review) or (repaired.startswith(source) and "\n\n" in repaired):
            return source
        return repaired

    def convert(self, text: str, mode: str) -> dict:
        source = h3.canonicalize_picture_references(text)
        stages = []
        translation = self._timed_generate(stages, "translate",
            source, h3.conversion_system(mode), temperature=0.01, top_p=0.05, max_new_tokens=700
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
            translation = self._timed_generate(
                stages, "translation_retry",
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                h3.translation_repair_system(mode), temperature=0.01, top_p=0.05, max_new_tokens=700,
            )
            translation = h3.remove_unsupported_vocalizations(source, translation)
            review = self._timed_generate(
                stages, "visual_review_retry",
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                h3.visual_review_system(mode), temperature=0.01, top_p=0.1, max_new_tokens=8,
            ).strip().upper()
            if not _is_pass_verdict(review):
                raise RuntimeError("The visual translation failed the strict no-invention review after automatic correction; no H3 output was returned.")
        if h3.has_unsupported_vocalization(source, translation):
            translation = self._timed_generate(
                stages, "vocalization_retry",
                f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
                h3.translation_repair_system(mode), temperature=0.01, top_p=0.05, max_new_tokens=700,
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
