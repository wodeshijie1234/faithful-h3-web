import re
import json
import time

from . import h3


class PromptService:
    def __init__(self, runtime):
        self.runtime = runtime

    def enrich(self, text: str, strength: int) -> str:
        strength = max(0, min(100, int(strength)))
        temperature = round(0.15 + 0.75 * strength / 100, 3)
        top_p = round(0.35 + 0.60 * strength / 100, 3)
        return self.runtime.generate(text, h3.enrichment_system(strength), temperature=temperature, top_p=top_p)

    def convert(self, text: str, mode: str) -> dict:
        stages = []
        translation = self._timed_generate(stages, "translate",
            text, h3.conversion_system(mode), temperature=0.01, top_p=0.05, max_new_tokens=700
        )
        review = self._timed_generate(stages, "visual_review",
            f"ORIGINAL SOURCE:\n{text}\n\nPROPOSED ENGLISH TRANSLATION:\n{translation}",
            h3.visual_review_system(mode),
            temperature=0.01,
            top_p=0.1,
            max_new_tokens=8,
        ).strip().upper()
        if review != "PASS":
            raise RuntimeError("The visual translation failed the strict no-invention review; no H3 output was returned.")
        soundscape, music = h3.parse_audio_output(
            self._timed_generate(stages, "audio", text, h3.audio_system(), temperature=0.01, top_p=0.1,
                                 max_new_tokens=160)
        )
        output = h3.strict_wrap(translation, mode, soundscape, music)
        check = h3.audit(output, mode)
        chinese = self._timed_generate(stages, "chinese_preview",
            output, h3.chinese_preview_system(mode), temperature=0.01, top_p=0.1, max_new_tokens=900
        )
        return {"output": output, "chinese": chinese, "audit": check, "_stages": stages}

    def _timed_generate(self, stages: list[dict], name: str, text: str, system: str, **settings) -> str:
        started = time.monotonic()
        try:
            return self.runtime.generate(text, system, **settings)
        finally:
            stages.append({"name": name, "elapsed_seconds": round(time.monotonic() - started, 3)})

    def decompose(self, text: str, mode: str) -> dict:
        output = self.runtime.generate(
            text, h3.decompose_system(mode), temperature=0.01, top_p=0.05, max_new_tokens=384, stop_on_json=True
        )
        return {"modules": h3.parse_modules_json(output, mode)}

    def convert_modules(self, modules: dict, mode: str) -> dict:
        source_modules = h3.normalize_modules(modules, mode)
        translated_raw = self.runtime.generate(
            json.dumps(source_modules, ensure_ascii=False),
            h3.translate_modules_system(mode),
            temperature=0.01,
            top_p=0.05,
            max_new_tokens=1200,
            stop_on_json=True,
        )
        translated = h3.parse_modules_json(translated_raw, mode)
        original_visual = h3.module_source_text(source_modules, mode)
        translated_visual = h3.module_source_text(translated, mode)
        review = self.runtime.generate(
            f"ORIGINAL SOURCE:\n{original_visual}\n\nPROPOSED ENGLISH TRANSLATION:\n{translated_visual}",
            h3.visual_review_system(mode),
            temperature=0.01,
            top_p=0.1,
            max_new_tokens=8,
        ).strip().upper()
        if review != "PASS":
            raise RuntimeError("The visual translation failed the strict no-invention review; no H3 output was returned.")
        if not translated["overall_soundscape"] and not translated["non_diegetic_music"]:
            soundscape, music = h3.parse_audio_output(
                self.runtime.generate(
                    original_visual, h3.audio_system(), temperature=0.01, top_p=0.1, max_new_tokens=160
                )
            )
            translated["overall_soundscape"] = soundscape
            translated["non_diegetic_music"] = music
        output = h3.build_h3(translated, mode)
        check = h3.audit(output, mode)
        chinese = h3.build_h3(source_modules, mode)
        return {"output": output, "chinese": chinese, "audit": check, "modules": translated}

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
