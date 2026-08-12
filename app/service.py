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
        output = self.runtime.generate(text, h3.conversion_system(mode), temperature=0.01, top_p=0.1)
        output = h3.normalize_output(output, mode)
        check = h3.audit(output, mode)
        if not check["valid"]:
            raise RuntimeError(f"The model returned an invalid H3 structure. Missing: {', '.join(check['missing'])}")
        chinese = self.runtime.generate(output, h3.chinese_preview_system(mode), temperature=0.01, top_p=0.1)
        return {"output": output, "chinese": chinese, "audit": check}

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

