import re


FIELDS = {
    "fl2va": ["integrated_multimodal_description:", "overall_soundscape:", "non_diegetic_music:"],
    "ref2va": ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"],
}

FL2VA_HEADER = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."


def normalize_mode(mode: str) -> str:
    value = str(mode or "").lower().strip()
    if value not in FIELDS:
        raise ValueError("Mode must be FL2VA or Ref2VA.")
    return value


def required_fields(mode: str) -> list[str]:
    return FIELDS[normalize_mode(mode)]


def has_complete_structure(text: str, mode: str) -> bool:
    value = str(text or "")
    positions = [value.find(field) for field in required_fields(mode)]
    return all(pos >= 0 for pos in positions) and positions == sorted(positions)


def has_untranslated_chinese(text: str) -> bool:
    value = re.sub(r"<d>.*?</d>", "", str(text or ""), flags=re.I | re.S)
    return bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff]", value))


def structure_signature(text: str, mode: str) -> list[str]:
    fields = required_fields(mode)
    pattern = r"(?:" + "|".join(re.escape(field) for field in fields) + r"|<Picture \d+>|<Subject \d+>|\[Shot \d+\]|<d>|</d>|N/A|\b\d{2}:\d{2}\.\d{3}\b)"
    return re.findall(pattern, str(text or ""))


def contract_matches(original: str, candidate: str, mode: str) -> bool:
    return has_complete_structure(candidate, mode) and structure_signature(original, mode) == structure_signature(candidate, mode)


def normalize_output(text: str, mode: str) -> str:
    value = str(text or "").strip()
    if normalize_mode(mode) != "fl2va":
        return value
    value = re.sub(r"^For the target video,.*?fully referenced\.\s*", "", value, count=1, flags=re.I | re.S).lstrip()
    return f"{FL2VA_HEADER}\n\n{value}"


def audit(text: str, mode: str) -> dict:
    missing = [field for field in required_fields(mode) if field not in str(text or "")]
    return {"valid": not missing and has_complete_structure(text, mode), "missing": missing}


def conversion_system(mode: str) -> str:
    mode = normalize_mode(mode)
    if mode == "fl2va":
        return f"""You are a deterministic MiniMax H3 FL2VA formatter. Translate only explicit user facts into English. Output exactly this first line:\n{FL2VA_HEADER}\nThen output exactly these fields in order: integrated_multimodal_description, overall_soundscape, non_diegetic_music. Preserve shot order, positions, actions, camera angles, continuity, and exact dialogue. Keep dialogue in its original language inside <d>[Language] ...</d>. Never infer image content. Never add, remove, embellish, intensify, explain, or continue content. Use N/A when sound or music is not supplied. Output only the H3 prompt."""
    return """You are a deterministic MiniMax H3 Ref2VA formatter. Translate only explicit user facts into English. Output exactly these fields in order: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Use stable <Subject N> and <Picture N> labels. Preserve shot order, positions, actions, camera angles, continuity, and exact dialogue. Keep dialogue in its original language inside <d>[Language] ...</d>. Never infer reference content. Never add, remove, embellish, intensify, explain, or continue content. Use N/A when sound or music is not supplied. Output only the H3 prompt."""


def enrichment_system(strength: int) -> str:
    strength = max(0, min(100, int(strength)))
    return f"""Enrich a short video prompt while preserving its core intent and every explicit fact. Return only the enriched prompt in exactly the same language as the input. Creative strength is {strength}/100. At low strength add only essential visible continuity; at high strength add filmable visual, motion, camera, lighting, atmosphere, and sound detail. Never contradict identities, counts, positions, actions, order, dialogue, or boundaries."""


def chinese_preview_system(mode: str) -> str:
    fields = " -> ".join(required_fields(mode))
    return f"Translate only descriptive English values into Chinese for editing. Keep field names, exact structure and order ({fields}), tags, references, timestamps, dialogue, and N/A unchanged. Do not add, remove, summarize, or rewrite anything. Return only the complete H3 prompt."


def micro_edit_system(mode: str, original_h3: str = "") -> str:
    fields = " -> ".join(required_fields(mode))
    reference = f"\nOriginal English H3 for unchanged-content reference:\n{original_h3}" if original_h3.strip() else ""
    return f"Translate every Chinese descriptive value into English. Keep Chinese only inside explicit <d>[Chinese] ...</d> dialogue. Preserve exact structure and order ({fields}), tags, references, timestamps, facts, and N/A. Do not add, remove, summarize, embellish, or change unrelated content.{reference}\nReturn only the complete English H3 prompt."

