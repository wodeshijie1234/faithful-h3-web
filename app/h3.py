import re
import json


FIELDS = {
    "fl2va": ["integrated_multimodal_description:", "overall_soundscape:", "non_diegetic_music:"],
    "ref2va": ["subject_definitions:", "summary:", "retention_analysis:", "detailed_description:", "overall_soundscape:", "non_diegetic_music:"],
}

FL2VA_HEADER = "For the target video, at 0.00 seconds into the target video, <Picture 1> (from [Shot 1]) is fully referenced."
MODULE_KEYS = ["scene", "shots", "overall_soundscape", "non_diegetic_music"]
REF_MODULE_KEYS = ["subject_definitions", "summary", "retention_analysis"] + MODULE_KEYS


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


def strict_wrap(text: str, mode: str, soundscape: str = "N/A", music: str = "N/A") -> str:
    """Place a translated prompt in the H3 template without generating visual facts."""
    value = str(text or "").strip()
    value = re.sub(r"(?im)(?<!\[)\bshot\s+(\d+)\s*:\s*", r"[Shot \1] ", value)
    if not value:
        raise ValueError("Source prompt cannot be empty.")
    mode = normalize_mode(mode)
    soundscape = str(soundscape or "N/A").strip() or "N/A"
    music = str(music or "N/A").strip() or "N/A"
    if mode == "fl2va":
        return (
            f"{FL2VA_HEADER}\n\n"
            f"integrated_multimodal_description: {value}\n"
            f"overall_soundscape: {soundscape}\n"
            f"non_diegetic_music: {music}"
        )
    return (
        "subject_definitions: N/A\n"
        "summary: N/A\n"
        "retention_analysis: N/A\n"
        f"detailed_description: {value}\n"
        f"overall_soundscape: {soundscape}\n"
        f"non_diegetic_music: {music}"
    )


def empty_modules(mode: str, shot_count: int = 3) -> dict:
    mode = normalize_mode(mode)
    modules = {
        "scene": "",
        "shots": [
            {"duration_seconds": 3.0, "action": "", "camera": ""}
            for index in range(max(1, shot_count))
        ],
        "overall_soundscape": "",
        "non_diegetic_music": "",
    }
    if mode == "ref2va":
        modules = {
            "subject_definitions": "",
            "summary": "",
            "retention_analysis": "",
            **modules,
        }
    return modules


def normalize_modules(raw: dict, mode: str) -> dict:
    if not isinstance(raw, dict):
        raise ValueError("H3 modules must be an object.")
    mode = normalize_mode(mode)
    modules = empty_modules(mode, 1)
    for key in MODULE_KEYS:
        if key != "shots":
            modules[key] = str(raw.get(key, "") or "").strip()
    if mode == "ref2va":
        for key in ("subject_definitions", "summary", "retention_analysis"):
            modules[key] = str(raw.get(key, "") or "").strip()
    shots = raw.get("shots", [])
    if not isinstance(shots, list):
        raise ValueError("shots must be a list.")
    modules["shots"] = []
    for item in shots[:20]:
        if not isinstance(item, dict):
            continue
        duration = float(item.get("duration_seconds", 3.0) or 3.0)
        duration = round(max(0.5, min(30.0, duration)) * 2) / 2
        modules["shots"].append({
            "duration_seconds": duration,
            "action": str(item.get("action", "") or "").strip(),
            "camera": str(item.get("camera", "") or "").strip(),
        })
    if not modules["shots"]:
        modules["shots"] = empty_modules(mode, 1)["shots"]
    return modules


def parse_modules_json(text: str, mode: str) -> dict:
    value = str(text or "").strip()
    value = re.sub(r"```(?:json)?", "", value, flags=re.I).replace("```", "").strip()
    start, end = value.find("{"), value.rfind("}")
    if start >= 0 and end >= start:
        value = value[start:end + 1]
    value = re.sub(r",\s*([}\]])", r"\1", value)
    return normalize_modules(json.loads(value), mode)


def module_source_text(modules: dict, mode: str, include_audio: bool = False) -> str:
    modules = normalize_modules(modules, mode)
    parts = []
    if normalize_mode(mode) == "ref2va":
        parts.extend(modules[key] for key in ("subject_definitions", "summary", "retention_analysis") if modules[key])
    if modules["scene"]:
        parts.append(modules["scene"])
    for shot in modules["shots"]:
        parts.extend(value for value in (shot["action"], shot["camera"]) if value)
    if include_audio:
        parts.extend(value for value in (modules["overall_soundscape"], modules["non_diegetic_music"]) if value)
    return "\n".join(parts).strip()


def build_h3(modules: dict, mode: str) -> str:
    mode = normalize_mode(mode)
    modules = normalize_modules(modules, mode)
    shot_parts = []
    elapsed = 0.0
    for index, shot in enumerate(modules["shots"], start=1):
        content = " ".join(value for value in (shot["action"], shot["camera"]) if value).strip()
        if not content:
            elapsed += shot["duration_seconds"]
            continue
        marker = f"[Shot {index}]"
        if index > 1:
            marker += f" At {format_timestamp(elapsed)},"
        shot_parts.append(f"{marker} {content}")
        elapsed += shot["duration_seconds"]
    detailed = " ".join(value for value in (modules["scene"], " ".join(shot_parts)) if value).strip() or "N/A"
    sound = modules["overall_soundscape"] or "N/A"
    music = modules["non_diegetic_music"] or "N/A"
    if mode == "fl2va":
        return (
            f"{FL2VA_HEADER}\n\n"
            f"integrated_multimodal_description: {detailed}\n"
            f"overall_soundscape: {sound}\n"
            f"non_diegetic_music: {music}"
        )
    return (
        f"subject_definitions: {modules['subject_definitions'] or 'N/A'}\n"
        f"summary: {modules['summary'] or 'N/A'}\n"
        f"retention_analysis: {modules['retention_analysis'] or 'N/A'}\n"
        f"detailed_description: {detailed}\n"
        f"overall_soundscape: {sound}\n"
        f"non_diegetic_music: {music}"
    )


def format_timestamp(seconds: float) -> str:
    total_ms = round(float(seconds) * 1000)
    minutes, remainder = divmod(total_ms, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def decompose_system(mode: str) -> str:
    keys = REF_MODULE_KEYS if normalize_mode(mode) == "ref2va" else MODULE_KEYS
    return f"""Split the source prompt into this JSON module schema: {json.dumps(keys)}. shots is an array of objects with duration_seconds (number), action, and camera. Copy source-language facts into the most relevant module without translating, rewriting, summarizing, or adding anything. Preserve every explicit fact. Determine shot count from the source: when it explicitly numbers or states a shot count, return exactly that many shot objects; otherwise use semantic action stages and explicit cuts or camera changes to create only the shots supported by the text. Do not pad the result to three shots and do not invent extra shots. Use explicit shot timing to derive durations when supplied; otherwise use 3.0 seconds per shot. Put ambience, physical sounds, and non-verbal human sounds in overall_soundscape; put audience-only score in non_diegetic_music. For Ref2VA, use subject_definitions, summary, and retention_analysis only when the source explicitly supplies those concepts; otherwise use empty strings. Return JSON only."""


def translate_modules_system(mode: str) -> str:
    keys = REF_MODULE_KEYS if normalize_mode(mode) == "ref2va" else MODULE_KEYS
    return f"""Translate every non-empty string value in the supplied JSON into faithful English. Preserve the exact JSON schema and key order {json.dumps(keys)}, shot count, duration_seconds values, labels, tags, reference IDs, explicit facts, positions, actions, camera directions, and dialogue. This is literal translation only. Never add appearance, clothing, setting, props, lighting, mood, motion, camera, or any other fact. Keep dialogue text in its original language inside existing <d> tags. Return JSON only."""


def translate_modules_repair_system(mode: str) -> str:
    keys = REF_MODULE_KEYS if normalize_mode(mode) == "ref2va" else MODULE_KEYS
    return f"""Use ORIGINAL MODULE JSON as the sole source of facts. Return corrected, valid JSON with the exact schema and key order {json.dumps(keys)}. Translate every non-empty original value faithfully into English. The proposed JSON may contain inventions: delete every unsupported appearance, clothing, setting, prop, lighting, mood, motion, camera, relationship, intention, or other visual fact. Preserve original shot count, duration_seconds, labels, tags, reference IDs, positions, actions, camera directions, dialogue, and every supported fact. Do not add, remove, summarize, or embellish. Return JSON only."""


def audit(text: str, mode: str) -> dict:
    missing = [field for field in required_fields(mode) if field not in str(text or "")]
    return {"valid": not missing and has_complete_structure(text, mode), "missing": missing}


def audio_system() -> str:
    return """You are the audio-only assistant for a strict H3 formatter. Infer only audible details directly supported by explicit actions, objects, environment, or dialogue in the source. Return exactly two lines: overall_soundscape: <brief sound description or N/A> and non_diegetic_music: <music description or N/A>. Do not describe or infer appearance, clothing, location, lighting, camera, choreography, or any visual detail. Do not invent specific sounds when the source gives no reasonable audio cue. Never output any other field, explanation, or markdown."""


def parse_audio_output(text: str) -> tuple[str, str]:
    values = {"overall_soundscape": "N/A", "non_diegetic_music": "N/A"}
    for line in str(text or "").splitlines():
        key, separator, value = line.partition(":")
        key = key.strip().lower()
        if key in values and separator:
            cleaned = value.strip()
            if cleaned and len(cleaned) <= 500:
                values[key] = cleaned
    return values["overall_soundscape"], values["non_diegetic_music"]


def visual_review_system(mode: str) -> str:
    normalize_mode(mode)
    return """You are a strict visual-translation faithfulness reviewer. Compare the original source with the proposed English translation sentence by sentence. Return exactly PASS only when the translation preserves every explicit person, count, left/right position, action, shot, camera direction, continuity fact, and dialogue, and contains no visual proposition unsupported by the source. Return exactly FAIL for any omission, reinterpretation, or added appearance, age, ethnicity, clothing, color, indoor/outdoor setting, room, location, prop, lighting, mood, pose, camera movement, body detail, relationship, intention, or other visual fact. Generic filler such as 'indoor setting', 'young', 'wearing', 'dim light', and 'cinematic' is an addition unless explicitly present. Audio is out of scope. When uncertain, return FAIL. Return only PASS or FAIL."""


def conversion_system(mode: str) -> str:
    mode = normalize_mode(mode)
    if mode == "fl2va":
        return """Translate the source prompt faithfully into English. This is literal translation only, not prompt writing and not H3 formatting. Translate each source clause exactly once and in the original order. Preserve every explicit person, count, left/right position, action, shot number, camera direction, continuity fact, and dialogue. Keep dialogue text in its original language inside <d>[Language] ...</d>. Do not add, remove, summarize, embellish, intensify, explain, resolve ambiguity, or continue anything. Never infer appearance, age, ethnicity, clothing, color, indoor/outdoor setting, room, location, props, lighting, mood, camera movement, body details, relationships, intentions, or transitions. If the source does not specify a fact, omit it. Return only the English translation."""
    return """Translate the Ref2VA source prompt faithfully into English. This is literal translation only, not prompt writing and not H3 formatting. Preserve every explicit subject, picture reference, count, left/right position, action, shot number, camera direction, continuity fact, and dialogue in the original order. Keep <Subject N>, <Picture N>, [Shot N], timestamps, and dialogue tags unchanged. Do not add, remove, summarize, embellish, intensify, explain, or continue anything. Never invent appearance, age, ethnicity, clothing, color, setting, props, lighting, mood, camera movement, body details, or other visual facts. Return only the English translation."""


def translation_repair_system(mode: str) -> str:
    normalize_mode(mode)
    return """Rewrite the proposed English translation to be a literal translation of the ORIGINAL SOURCE. Delete every visual clause that is not explicitly supported by the source. Preserve all supported people, counts, positions, actions, shot numbers, camera directions, continuity facts, and dialogue in their original order. Do not add, remove, summarize, embellish, explain, resolve ambiguity, or introduce appearance, clothing, setting, props, lighting, mood, relationships, intentions, transitions, or camera movement. Return only the corrected English translation, not H3 formatting or commentary."""


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
