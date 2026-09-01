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


def canonicalize_picture_references(text: str) -> str:
    value = str(text or "")
    # Users commonly write Chinese numerals (图一/图片二); normalize them before
    # extracting identities and start references so Ref2VA keeps the anchors.
    chinese_numerals = {
        "一": "1", "二": "2", "三": "3", "四": "4", "五": "5",
        "六": "6", "七": "7", "八": "8", "九": "9", "十": "10",
    }
    numeral_pattern = "|".join(chinese_numerals)
    value = re.sub(
        rf"(?<!<)(?:图片|图)\s*({numeral_pattern})(?![一二三四五六七八九十])",
        lambda match: f"<Picture {chinese_numerals[match.group(1)]}>",
        value,
    )
    value = re.sub(r"(?<!<)(?:\u56fe\u7247|\u56fe)\s*(\d+)", r"<Picture \1>", value)
    return re.sub(r"(?<!<)\b(?:picture|image)\s*(\d+)\b", r"<Picture \1>", value, flags=re.I)


def has_unsupported_vocalization(source: str, candidate: str) -> bool:
    vocalization = r"\b(?:moan|groan|whimper|gasp|scream|cry|laugh)(?:s|ed|ing)?\b"
    if not re.search(vocalization, str(candidate or ""), flags=re.I):
        return False
    source_vocalization = r"(?:\u547b\u541f|\u5a07\u5598|\u547c\u558a|\u5c16\u53eb|\u54ed\u558a|\u54ed\u6ce3|\u7b11\u58f0|\u53d1\u51fa.*?\u58f0\u97f3|" + vocalization + r")"
    return not re.search(source_vocalization, str(source or ""), flags=re.I)


def restore_explicit_dialogue(source: str, candidate: str) -> str:
    """Keep quoted source dialogue verbatim inside the H3 dialogue tag."""
    value = str(candidate or "").strip()
    # Capture Chinese/curly quoted utterances, including punctuation inside them.
    quoted = re.findall(r"[\u201c\u2018\u300c\u300e\"']([^\u201d\u2019\u300d\u300f\"']*[\u3400-\u9fff][^\u201d\u2019\u300d\u300f\"']*)[\u201d\u2019\u300d\u300f\"']", str(source or ""))
    if not quoted:
        return value
    for dialogue in quoted:
        tag = f"<d>[Chinese] {dialogue}</d>"
        if tag in value:
            continue
        # Remove a translated quoted utterance when present, then preserve the
        # original Chinese verbatim. This also handles a model omitting dialogue.
        value = re.sub(r"(?:\"[^\"\n]*\"|‘[^’\n]*’|“[^”\n]*”)", "", value, count=1)
        value = value.rstrip()
        value = f"{value} {tag}".strip()
    return value


def remove_unsupported_vocalizations(source: str, candidate: str) -> str:
    """Drop complete invented vocalization sentences before the visual-fact review."""
    value = str(candidate or "").strip()
    value = restore_explicit_dialogue(source, value)
    if not has_unsupported_vocalization(source, value):
        return value
    vocalization = re.compile(r"\b(?:moan|groan|whimper|gasp|scream|cry|laugh)(?:s|ed|ing)?\b", re.I)
    sentences = re.split(r"(?<=[.!?])\s+", value)
    cleaned_sentences = []
    vocal_clause = re.compile(
        r"\b(?:he|she|they|the\s+[\w-]+)\s+"
        r"(?:moan|groan|whimper|gasp|scream|cry|laugh)(?:s|ed|ing)?"
        r"(?:\s+(?:softly|loudly|quietly|gently|weakly))?\s*,\s*",
        re.I,
    )
    vocal_leading_clause = re.compile(
        r"\b(?:he|she|they|the\s+[\w-]+)\s+"
        r"(?:continues\s+to\s+)?(?:moan|groan|whimper|gasp|scream|cry|laugh)(?:s|ed|ing)?"
        r"(?:\s+(?:softly|loudly|quietly|gently|weakly|in\s+pleasure))?\s*(?:and\s+)?",
        re.I,
    )
    for sentence in sentences:
        if not vocalization.search(sentence):
            cleaned_sentences.append(sentence)
            continue
        original_sentence = sentence.strip()
        remainder = vocal_clause.sub("", sentence).strip()
        if remainder == original_sentence:
            remainder = vocal_leading_clause.sub("", sentence).strip()
        if remainder == original_sentence:
            continue
        if remainder:
            cleaned_sentences.append(remainder[0].upper() + remainder[1:])
    return " ".join(cleaned_sentences).strip()


def structure_signature(text: str, mode: str) -> list[str]:
    fields = required_fields(mode)
    pattern = r"(?:" + "|".join(re.escape(field) for field in fields) + r"|<Picture \d+>|<Subject \d+>|<Video \d+>|<Audio \d+>|\[Shot \d+\]|<d>|</d>|<scenetrans>|</scenetrans>|<cutoff>|N/A|\b\d{2}:\d{2}\.\d{3}\b)"
    return re.findall(pattern, str(text or ""))


def contract_matches(original: str, candidate: str, mode: str) -> bool:
    return has_complete_structure(candidate, mode) and structure_signature(original, mode) == structure_signature(candidate, mode)


def normalize_output(text: str, mode: str) -> str:
    value = str(text or "").strip()
    if normalize_mode(mode) != "fl2va":
        return value
    value = re.sub(r"^For the target video,.*?fully referenced\.\s*", "", value, count=1, flags=re.I | re.S).lstrip()
    return f"{FL2VA_HEADER}\n\n{value}"


def strict_wrap(text: str, mode: str, soundscape: str = "N/A", music: str = "N/A", source_text: str = "") -> str:
    """Place a translated prompt in the H3 template without generating visual facts."""
    value = canonicalize_picture_references(text).strip()
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
    reference_source = canonicalize_picture_references(source_text or text)
    subject_definitions = "\n".join(_ref2va_subject_definition_lines(reference_source)) or "N/A"
    _, start_reference = _ref2va_reference_metadata(reference_source)
    summary = _ref2va_summary(reference_source, start_reference)
    return (
        f"subject_definitions: {subject_definitions}\n"
        f"summary: {summary}\n"
        "retention_analysis: N/A\n"
        f"detailed_description: {value}\n"
        f"overall_soundscape: {soundscape}\n"
        f"non_diegetic_music: {music}"
    )


def _ref2va_reference_metadata(source_text: str) -> tuple[list[tuple[str, str]], str | None]:
    """Extract explicit reusable subjects and the concrete starting picture.

    The descriptor is deliberately copied from the source (then lightly normalized)
    so the wrapper can emit an official ``<Subject N> ... from <Picture N>`` line
    without inventing appearance details.
    """
    source = canonicalize_picture_references(source_text)
    subjects: list[tuple[str, str]] = []
    seen_ids = set()

    # Already structured Ref2VA input: preserve the declared subject wording and
    # its picture provenance instead of reducing it to a gender label.
    for subject_id, definition in re.findall(
        r"<Subject\s+(\d+)>\s*(?:is|=)\s*(.+?)(?=(?:\n|<Subject\s+\d+>|<Picture\s+\d+>|<Video\s+\d+>|<Audio\s+\d+>|$))",
        source,
        flags=re.I | re.S,
    ):
        definition = " ".join(definition.split()).strip(" .")
        if definition and subject_id not in seen_ids:
            subjects.append((subject_id, definition))
            seen_ids.add(subject_id)

    def add_picture(picture_id: str, descriptor: str) -> None:
        if picture_id in seen_ids:
            return
        descriptor = " ".join(descriptor.split()).strip(" .，,")
        descriptor = re.sub(r"(?:参考图|reference\s+(?:image|picture))$", "", descriptor, flags=re.I).strip(" ,")
        if not descriptor:
            return
        # Normalize bare gender facts; the final Subject definition still uses
        # the official source-reference sentence instead of a bare label.
        gender = re.fullmatch(r"(?:a\s+)?(?:man|male|boy|woman|female|girl)|(?:男生|男人|男性|女生|女人|女性)", descriptor, flags=re.I)
        subjects.append((picture_id, "male" if gender and descriptor.lower().lstrip("a ").startswith(("man", "male", "boy")) or descriptor.startswith(("男",)) else "female" if gender else descriptor))
        seen_ids.add(picture_id)

    for picture_id, descriptor in re.findall(
        r"<Picture\s+(\d+)>\s*(?:\u662f|\u4e3a)\s*(?:\u4e00\u540d|\u4e00\u4e2a)?\s*([^，,。！？.!?\n<]+)",
        source,
    ):
        add_picture(picture_id, descriptor)
    for picture_id, descriptor in re.findall(
        r"<Picture\s+(\d+)>\s+is\s+([^,，.!?\n<]+)", source, flags=re.I
    ):
        add_picture(picture_id, descriptor)

    start_patterns = (
        r"(?:\u5f00\u59cb\u4e8e|\u4ece)\s*<Picture\s+(\d+)>",
        r"(?:\u7b2c\s*一\s*帧|\u9996\u5e27|\u7b2c\s*1\s*\u5e27)[^。.!?\n]{0,40}?<Picture\s+(\d+)>|(?:\u7b2c\s*一\s*帧|\u9996\u5e27)[^图\n]{0,20}?图\s*(\d+)",
        r"(?:the\s+)?(?:target\s+)?video(?:\s+scene)?\s+(?:begins|starts)\s+(?:with|from)\s+<Picture\s+(\d+)>",
        r"(?:first\s+frame|opening\s+frame)[^\n.]{0,60}?<Picture\s+(\d+)>",
    )
    for pattern in start_patterns:
        match = re.search(pattern, source, flags=re.I)
        if match:
            groups = [value for value in match.groups() if value]
            if groups:
                return subjects, groups[-1]
    return subjects, None


def _ref2va_subject_definition_lines(source_text: str) -> list[str]:
    """Build official subject/video/audio definition lines from explicit source facts."""
    source = canonicalize_picture_references(source_text)
    structured = re.findall(
        r"<(Subject|Video|Audio)\s+(\d+)>\s*(?:is|=)\s*([^\n]+)",
        source,
        flags=re.I | re.S,
    )
    if structured:
        lines = []
        for label, number, definition in structured:
            text = " ".join(definition.split()).strip(" .")
            if text:
                lines.append(f"<{label.title()} {number}> is {text}.")
        if lines:
            return lines
    subjects, _ = _ref2va_reference_metadata(source)
    lines: list[str] = []
    for subject_index, (picture_id, descriptor) in enumerate(subjects, start=1):
        if descriptor in {"male", "female"}:
            lines.append(
                f"<Subject {subject_index}> is the {descriptor} subject from <Picture {picture_id}>, "
                "preserving the identity and visible appearance shown in the reference image."
            )
        elif re.search(r"<Picture\s+" + re.escape(picture_id) + r">", descriptor, flags=re.I):
            lines.append(f"<Subject {subject_index}> is {descriptor}.")
        else:
            lines.append(f"<Subject {subject_index}> is {descriptor} from <Picture {picture_id}>.")
    # Structured reference assets may be declared independently of pictures.
    return lines


def _ref2va_summary(source_text: str, start_picture: str | None = None) -> str:
    """Infer only explicit Ref2VA task roles for the required summary prefix."""
    source = str(source_text or "")
    roles: list[str] = []
    lower = source.lower()
    if re.search(r"\b(?:edit|edited|editing|modify|修改|编辑)\b", lower):
        roles.append("video editing")
    if re.search(r"\b(?:continue|continuation|续接|延续|接续)\b", lower):
        roles.append("video continuation")
    if re.search(r"(?:首帧|第一帧|最后一帧|关键帧|first\s+frame|keyframe|last\s+frame)", source, flags=re.I):
        roles.append("keyframe completion")
    if re.search(r"\b(?:reuse|reused|copy|copied|复用|复制|原声)\b", lower):
        roles.append("audio reuse")
    elif re.search(r"\b(?:audio|voice|timbre|音频|声音|音色|配音)\b", lower):
        roles.append("audio reference")
    if not roles and not start_picture and not re.search(r"<Picture\s+\d+>|<Video\s+\d+>|<Audio\s+\d+>|参考图|参考视频|参考音频|reference", source, flags=re.I):
        return "N/A"
    if not roles:
        roles.append("reference generation")
    elif "reference generation" not in roles and re.search(r"(?:<Picture\s+\d+>|<Video\s+\d+>|参考图|参考视频|reference\s+(?:image|video)|借鉴|参考)", source, flags=re.I):
        roles.insert(0, "reference generation")
    prefix = "[" + " + ".join(dict.fromkeys(roles)) + "]"
    if start_picture:
        return f"{prefix} The target video begins with <Picture {start_picture}>."
    return prefix


def _ref2va_retention_lines(source_text: str, subjects: list[tuple[str, str]]) -> str:
    """Emit one concrete retention statement per declared reference label."""
    source = canonicalize_picture_references(source_text)
    shot_marker = re.compile(
        r"(?:\[Shot\s*(\d+)\]|\[镜头\s*(\d+)\]|(?:Shot|镜头)\s*(\d+))\s*[:：]?",
        re.I,
    )
    matches = list(shot_marker.finditer(source))
    numbered_shots: list[tuple[int, str]] = []
    for position, match in enumerate(matches):
        end = matches[position + 1].start() if position + 1 < len(matches) else len(source)
        numbered_shots.append((
            int(match.group(1) or match.group(2) or match.group(3)),
            source[match.end():end],
        ))

    lines = []
    for index, (picture_id, descriptor) in enumerate(subjects, start=1):
        if descriptor == "male":
            subject_pattern = re.compile(r"(?:男生|男人|男性|男子|\b(?:man|male|boy)\b)", re.I)
        elif descriptor == "female":
            subject_pattern = re.compile(r"(?:女生|女人|女性|女子|\b(?:woman|female|girl)\b)", re.I)
        else:
            subject_pattern = None
        appearances = [
            number for number, body in numbered_shots
            if re.search(rf"<Picture\s+{re.escape(picture_id)}>", body, flags=re.I)
            or (subject_pattern is not None and subject_pattern.search(body))
        ]
        appearances = list(dict.fromkeys(appearances)) or [1]
        labels = [f"[Shot {number}]" for number in appearances]
        if len(labels) == 1:
            appearance_text = labels[0]
        elif len(labels) == 2:
            appearance_text = " and ".join(labels)
        else:
            appearance_text = ", ".join(labels[:-1]) + f", and {labels[-1]}"
        lines.append(
            f"<Subject {index}> (appears in {appearance_text}): fully_preserved - "
            f"the referenced subject from <Picture {picture_id}> is retained."
        )
    for label, number, definition in re.findall(
        r"<(Video|Audio)\s+(\d+)>\s*(?:is|=)\s*([^\n]+)",
        source, flags=re.I | re.S,
    ):
        marker = "reference" if label.lower() == "audio" else "weak_reference"
        lines.append(f"<{label.title()} {number}>: {marker} - the declared reference role is retained.")
    return "\n".join(lines) or "N/A"


_ENGLISH_TIME_WORDS = (
    "zero|one|two|three|four|five|six|seven|eight|nine|ten|"
    "eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|"
    "eighteen|nineteen|twenty|thirty|forty|fifty|sixty"
)
_EXPLICIT_TIME_PREFIX = re.compile(
    r"^(?:"
    r"At\s+(?:the\s+)?(?P<english>\d+(?:\.\d+)?)\s*(?:-\s*)?(?:seconds?|secs?|s)(?:\s+mark)?|"
    r"(?P<english_later>\d+(?:\.\d+)?|(?:" + _ENGLISH_TIME_WORDS + r"))\s*(?:seconds?|secs?|s)\s+later|"
    r"(?:\u7b2c\s*)?(?P<chinese>\d+(?:\.\d+)?)\s*\u79d2(?:\u4e4b?后|\u4ee5后|\u7684\u65f6\u5019|\u65f6|\u5904|(?=\s*[，,：:]))?)"
    r"\s*[，,：: -]?\s*",
    re.I,
)

_ENGLISH_NUMBER_VALUES = {
    "zero": 0.0, "one": 1.0, "two": 2.0, "three": 3.0,
    "four": 4.0, "five": 5.0, "six": 6.0, "seven": 7.0,
    "eight": 8.0, "nine": 9.0, "ten": 10.0, "eleven": 11.0,
    "twelve": 12.0, "thirteen": 13.0, "fourteen": 14.0,
    "fifteen": 15.0, "sixteen": 16.0, "seventeen": 17.0,
    "eighteen": 18.0, "nineteen": 19.0, "twenty": 20.0,
    "thirty": 30.0, "forty": 40.0, "fifty": 50.0, "sixty": 60.0,
}


def _explicit_time_value(match: re.Match) -> float:
    numeric = match.group("english") or match.group("chinese")
    if numeric is not None:
        return float(numeric)
    return _ENGLISH_NUMBER_VALUES[match.group("english_later").lower()]


def _unnumbered_timing_hints(text: str) -> dict[int, dict[str, float]]:
    value = str(text or "")
    sentence_starts = re.compile(
        r"(?:^|(?<=[!?\u3002\uff01\uff1f;\uff1b])|(?<=\.)(?!\d))\s*"
    )
    starts: list[float] = []
    for boundary in sentence_starts.finditer(value):
        match = _EXPLICIT_TIME_PREFIX.match(value[boundary.end():])
        if match:
            starts.append(_explicit_time_value(match))
    if not starts:
        return {}

    shot_number = 1 if starts[0] <= 0 else 2
    hints = {}
    for start in starts:
        hints[shot_number] = {"start": start}
        shot_number += 1
    return hints


def _clean_ref2va_action_prefix(text: str) -> str:
    """Remove translation scaffolding and duplicate time cues from a shot body."""
    value = str(text or "").strip()
    prefix_patterns = (
        r"^\s*At\s+\d{1,3}:\d{2}(?:\.\d{1,3})?\s*,?\s*",
        r"^\s*(?:(?:reference|source)\s+(?:image|picture)\s*[.;,]?\s*)+",
        r"^\s*\d+(?:\.\d+)?\s*秒\s*[，,：:]?\s*",
        r"^\s*(?:At\s+(?:the\s+)?)?\d+(?:\.\d+)?\s*(?:seconds?|secs?|s)(?:\s+mark)?\s*[，,：:.-]?\s*",
    )
    while True:
        previous = value
        for pattern in prefix_patterns:
            value = re.sub(pattern, "", value, flags=re.I)
        if value == previous:
            return value.strip()


def _ref2va_action_sentences(translation: str) -> list[str]:
    """Split only explicit cuts and camera cues; all other action clauses stay together."""
    value = canonicalize_picture_references(translation).strip()
    value = re.sub(r"(?im)(?<!\[)\bshot\s+\d+\s*:\s*", "", value)
    value = _clean_ref2va_action_prefix(value)
    value = re.sub(
        r"<Picture\s+\d+>\s+is\s+(?:a\s+)?(?:man|male|boy|woman|female|girl)\s*[,.;]?\s*",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(
        r"<Picture\s+\d+>\s*(?:\u662f|\u4e3a)\s*(?:\u4e00\u540d|\u4e00\u4e2a)?\s*"
        r"(?:\u7537\u751f|\u7537\u4eba|\u7537\u6027|\u5973\u751f|\u5973\u4eba|\u5973\u6027)(?:\u53c2\u8003\u56fe)?\s*[,\uff0c\u3002.]?\s*",
        "",
        value,
    )
    value = re.sub(r"<Picture\s+\d+>\s*(?:\u662f|\u4e3a)[^\n,.!?，。！？]*?\u53c2\u8003\u56fe\s*[,.!?，。！？]?\s*", "", value)
    value = re.sub(
        r"\bThe\s+(?:man|woman|male|female)\s+is\s+(?:a\s+)?"
        r"(?:man|woman|male|female)\s*[,.;]?\s*",
        "",
        value,
        flags=re.I,
    )
    value = re.sub(
        r"(?:\u89c6\u9891(?:\u573a\u666f)?(?:\u662f)?(?:\u5f00\u59cb\u4e8e|\u4ece)|\u89c6\u9891\u573a\u666f\u5f00\u59cb\u4e8e)\s*"
        r"<Picture\s+\d+>\s*[,\uff0c\u3002]?\s*",
        "",
        value,
    )
    value = re.sub(
        r"[,\uff0c]\s*(?=(?:\u7279\u5199|\u5207\u6362(?:\u4e3a|\u5230)?(?:\u4e2d|\u8fd1|\u8fdc|\u5168)\u666f|\u955c\u5934(?:\u5207\u6362|\u8f6c(?:\u4e3a|\u5230)?)))",
        ". ",
        value,
    )
    sentences = re.split(r"(?<=[.!?])\s+", value)
    intro_patterns = (
        r"^<Picture\s+\d+>\s+is\s+(?:a\s+)?(?:man|male|boy|woman|female|girl)\.?$",
        r"^(?:The\s+)?(?:target\s+)?video(?:\s+scene)?\s+(?:begins|starts)\s+(?:with|from)\s+<Picture\s+\d+>\.?$",
        r"^(?:The\s+)?(?:target\s+)?video(?:\s+scene)?\s+(?:begins|starts)\s+(?:with|from)\s+(?:the\s+)?(?:man|woman|male|female)\.?$",
        r"^(?:the\s+)?(?:target\s+)?video(?:\s+)?(?:first\s+frame|opening\s+frame).*$",
        r"^(?:\u89c6\u9891)?(?:\u7b2c\s*一\s*帧|\u9996\u5e27).*$",
    )
    boundary = re.compile(
        r"^(?:\[Shot\s+\d+\]\s*)?(?:"
        r"cut\s+to\b|(?:the\s+)?camera\s+(?:cuts|switches)\b|switch(?:es)?\s+to\b|"
        r"close[- ]up\b|(?:an?\s+)?(?:medium|wide|full|long|over[- ]the[- ]shoulder)\s+shot\b|"
        r"(?:an?\s+)?(?:extreme(?:ly)?\s+|very\s+)?(?:low|high)[- ]angle\b|"
        r"\u7279\u5199|\u5207\u6362(?:\u4e3a|\u5230)?(?:\u4e2d|\u8fd1|\u8fdc|\u5168)\u666f|\u955c\u5934(?:\u5207\u6362|\u8f6c(?:\u4e3a|\u5230)?))",
        flags=re.I,
    )

    shots: list[str] = []
    current: list[str] = []
    for sentence in sentences:
        item = sentence.strip()
        if not item or any(re.match(pattern, item, flags=re.I) for pattern in intro_patterns):
            continue
        item = re.sub(r"^\[Shot\s+\d+\]\s*", "", item, flags=re.I).strip()
        explicit_time = _EXPLICIT_TIME_PREFIX.match(item)
        if (boundary.match(item) or explicit_time) and current:
            shots.append(" ".join(current))
            current = []
        if explicit_time:
            item = item[explicit_time.end():].strip()
        if not item:
            continue
        if not current:
            current = [item]
        else:
            current.append(item)
    if current:
        shots.append(" ".join(current))
    return shots


def _numbered_shot_actions(translation: str) -> list[str]:
    """Preserve explicit Shot N boundaries before semantic camera splitting."""
    value = canonicalize_picture_references(translation).strip()
    marker = re.compile(r"(?:\[Shot\s*(\d+)\]|\[\u955c\u5934\s*(\d+)\]|(?:Shot|\u955c\u5934)\s*(\d+))\s*[:\uff1a]?", re.I)
    matches = list(marker.finditer(value))
    if not matches:
        return []

    prefix = value[:matches[0].start()].strip()
    actions = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        segment = value[match.end():end].strip()
        if index == 0 and prefix:
            segment = f"{prefix} {segment}".strip()
        cleaned = " ".join(_ref2va_action_sentences(segment))
        if cleaned:
            actions.append(cleaned)
    return actions


def _clean_built_ref2va_shot_prefixes(output: str) -> str:
    """Apply the Shot-body prefix contract to the final detailed_description."""
    start_marker = "detailed_description:"
    end_marker = "\noverall_soundscape:"
    start = output.find(start_marker)
    end = output.find(end_marker, start + len(start_marker))
    if start < 0 or end < 0:
        return output

    body_start = start + len(start_marker)
    detailed = output[body_start:end]
    shot_marker = re.compile(
        r"\[Shot\s+\d+\](?!\.)(?:\s+At\s+\d{1,3}:\d{2}(?:\.\d{1,3})?\s*,)?",
        re.I,
    )
    matches = list(shot_marker.finditer(detailed))
    if not matches:
        return output

    pieces = [detailed[:matches[0].start()]]
    for index, match in enumerate(matches):
        segment_end = matches[index + 1].start() if index + 1 < len(matches) else len(detailed)
        action = _clean_ref2va_action_prefix(detailed[match.end():segment_end])
        pieces.append(f"{match.group(0)}{' ' + action if action else ''}")
    normalized = " " + " ".join(piece.strip() for piece in pieces if piece.strip())
    return output[:body_start] + normalized + output[end:]


def _ref2va_semantic_duration(action: str) -> float:
    """Estimate a shot length from explicit action density without generating new content."""
    value = str(action or "")
    event_pattern = (
        r"\b(?:appear(?:s|ed|ing)?|enter(?:s|ed|ing)?|hold(?:s|ing)?|press(?:es|ed|ing)?|"
        r"freez(?:es|ing)?|tap(?:s|ped|ping)?|run(?:s|ning)?\s+(?:his|her|their)\s+fingers|"
        r"crouch(?:es|ed|ing)?|hug(?:s|ged|ging)?|rub(?:s|bed|bing)?|raise(?:s|d|ing)?|"
        r"walk(?:s|ed|ing)?|look(?:s|ed|ing)?|turn(?:s|ed|ing)?|move(?:s|d|ing)?)\b|"
        r"(?:\u51fa\u73b0|\u8fdb\u5165|\u62ff(?:\u8d77|\u7740)?|\u6309(?:\u4e0b)?|\u9759\u6b62|\u51dd\u56fa|\u62cd|\u6478|\u8e72|\u62b1|\u8e6d|\u62ac|\u8d70|\u8dd1|\u770b|\u8f6c\u8eab|\u79fb\u52a8)"
    )
    action_count = len(re.findall(event_pattern, value, flags=re.I))
    duration = 2.0 + 0.5 * min(6, max(0, action_count - 1))
    if re.search(r"\bclose[- ]up\b|\u7279\u5199", value, flags=re.I):
        duration = min(duration, 2.0)
    elif action_count == 0 and re.search(r"\b(?:cut|camera|shot|angle)\b|\u5207\u6362|\u955c\u5934|\u89c6\u89d2", value, flags=re.I):
        duration = 1.5
    return round(max(1.5, min(6.0, duration)) * 2) / 2


def _shot_timing_hints(text: str) -> dict[int, dict[str, float]]:
    """Extract explicit per-shot starts and durations from common Chinese or English notation."""
    value = str(text or "")
    marker = re.compile(r"(?:\[Shot\s*(\d+)\]|\[\u955c\u5934\s*(\d+)\]|(?:Shot|\u955c\u5934)\s*(\d+))", re.I)
    matches = list(marker.finditer(value))
    if not matches:
        return _unnumbered_timing_hints(value)
    hints: dict[int, dict[str, float]] = {}
    for index, match in enumerate(matches):
        shot_number = int(match.group(1) or match.group(2) or match.group(3))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(value)
        header = value[match.end():min(end, match.end() + 80)]
        hint: dict[str, float] = {}

        timestamp = re.search(r"\bAt\s+(\d{1,3}):(\d{2}(?:\.\d{1,3})?)", header, flags=re.I)
        if timestamp:
            hint["start"] = int(timestamp.group(1)) * 60 + float(timestamp.group(2))

        time_range = re.search(
            r"(?:\u7b2c)?\s*(\d+(?:\.\d+)?)\s*(?:\u79d2|s|seconds?)?\s*"
            r"(?:-|\u2013|\u2014|~|\u81f3|\u5230)\s*(?:\u7b2c)?\s*(\d+(?:\.\d+)?)\s*(?:\u79d2|s|seconds?)",
            header,
            flags=re.I,
        )
        if time_range:
            start, end_time = float(time_range.group(1)), float(time_range.group(2))
            hint.update(start=start, duration=max(0.0, end_time - start))

        duration = re.search(
            r"(?:\u6301\u7eed|\u65f6\u957f|duration(?:\s+of)?|lasts?)\s*[:\uff1a]?\s*"
            r"(\d+(?:\.\d+)?)\s*(?:\u79d2|s|seconds?)",
            header,
            flags=re.I,
        )
        if duration:
            hint["duration"] = float(duration.group(1))

        start_second = re.search(
            r"(?:\u4ece|\u7b2c|at)\s*(\d+(?:\.\d+)?)\s*(?:\u79d2|s|seconds?)(?:\u5f00\u59cb)?",
            header,
            flags=re.I,
        )
        if start_second and "start" not in hint:
            hint["start"] = float(start_second.group(1))
        plain_second = re.match(r"\s*[：:，,]?\s*(\d+(?:\.\d+)?)\s*\u79d2", header)
        if plain_second and "start" not in hint:
            hint["start"] = float(plain_second.group(1))
        if hint:
            hints[shot_number] = hint
    return hints


def _timeline_durations(actions: list[str], source_text: str, translation: str) -> list[float]:
    hints = _shot_timing_hints(source_text) or _shot_timing_hints(translation)
    durations = []
    elapsed = 0.0
    for index, action in enumerate(actions, start=1):
        current = hints.get(index, {})
        following = hints.get(index + 1, {})
        explicit_next = following.get("start")
        explicit_timing = False
        if explicit_next is not None and explicit_next > elapsed:
            duration = explicit_next - elapsed
            explicit_timing = True
        elif current.get("duration", 0) > 0:
            duration = current["duration"]
            explicit_timing = True
        else:
            duration = _ref2va_semantic_duration(action)
        duration = max(0.001 if explicit_timing else 0.5, min(30.0, duration))
        duration = round(duration, 3) if explicit_timing else round(duration * 2) / 2
        durations.append(duration)
        elapsed += duration
    return durations


def ref2va_timeline_wrap(
    translation: str,
    source_text: str,
    soundscape: str = "N/A",
    music: str = "N/A",
) -> str:
    """Apply the Ref2VA contract without adding visual facts to a reviewed translation."""
    value = canonicalize_picture_references(translation).strip()
    if not value:
        raise ValueError("Source prompt cannot be empty.")

    subjects, start_picture = _ref2va_reference_metadata(source_text or translation)
    subject_definitions = "\n".join(_ref2va_subject_definition_lines(source_text or translation)) or "N/A"
    summary = _ref2va_summary(source_text or translation, start_picture)
    retention_analysis = _ref2va_retention_lines(source_text or translation, subjects)

    shot_actions = _numbered_shot_actions(value) or _ref2va_action_sentences(value)
    # Preserve exact Chinese dialogue in the translated H3 body.
    value_with_dialogue = restore_explicit_dialogue(source_text or translation, value)
    if shot_actions and value_with_dialogue != value:
        tags = re.findall(r"<d>\[Chinese\].*?</d>", value_with_dialogue, flags=re.I | re.S)
        if tags and all(tag not in shot_actions[-1] for tag in tags):
            shot_actions[-1] = f"{shot_actions[-1]} {' '.join(tags)}"
    durations = _timeline_durations(shot_actions, source_text, translation)
    modules = {
        "subject_definitions": subject_definitions,
        "summary": summary,
        "retention_analysis": retention_analysis,
        "scene": (
            f"<Picture {start_picture}> is the first frame of [Shot 1]."
            if start_picture and re.search(r"(?:首帧|第一帧|first\s+frame|opening\s+frame)", source_text or translation, flags=re.I)
            else f"The target video begins with <Picture {start_picture}>."
            if start_picture else ""
        ),
        "shots": [
            {"duration_seconds": duration, "action": action, "camera": ""}
            for action, duration in zip(shot_actions, durations)
        ],
        "overall_soundscape": str(soundscape or "N/A").strip() or "N/A",
        "non_diegetic_music": str(music or "N/A").strip() or "N/A",
    }
    return _clean_built_ref2va_shot_prefixes(
        build_h3(modules, "ref2va", preserve_timing=True)
    )


def _fl2va_header(picture_id: str | None) -> str:
    if not picture_id or picture_id == "1":
        return FL2VA_HEADER
    return (
        "For the target video, at 0.00 seconds into the target video, "
        f"<Picture {picture_id}> (from [Shot 1]) is fully referenced."
    )


def fl2va_timeline_wrap(
    translation: str,
    source_text: str,
    soundscape: str = "N/A",
    music: str = "N/A",
) -> str:
    """Apply the first-frame FL2VA contract without adding visual facts."""
    value = canonicalize_picture_references(translation).strip()
    if not value:
        raise ValueError("Source prompt cannot be empty.")

    reference_source = canonicalize_picture_references(source_text)
    subjects, start_picture = _ref2va_reference_metadata(reference_source)
    explicit_pictures = re.findall(r"<Picture\s+(\d+)>", reference_source, flags=re.I)
    reference_picture = start_picture or (explicit_pictures[0] if explicit_pictures else None)
    shot_actions = _numbered_shot_actions(value) or _ref2va_action_sentences(value) or [value]
    subject_facts = " ".join(
        f"<Picture {picture_id}> is {gender}." for picture_id, gender in subjects
    )
    first_action = " ".join(
        item for item in (
            f"Continue directly from <Picture {reference_picture}>." if reference_picture else "",
            subject_facts,
            shot_actions[0],
        ) if item
    )
    durations = _timeline_durations(shot_actions, source_text, translation)

    shot_parts = []
    elapsed = 0.0
    for index, action in enumerate([first_action, *shot_actions[1:]], start=1):
        marker = f"[Shot {index}] At {format_timestamp(elapsed)},"
        shot_parts.append(f"{marker} {action}")
        elapsed += durations[index - 1]

    sound = str(soundscape or "N/A").strip() or "N/A"
    score = str(music or "N/A").strip() or "N/A"
    header = f"{_fl2va_header(reference_picture)}\n\n" if reference_picture else ""
    return (
        header +
        f"integrated_multimodal_description: {' '.join(shot_parts)}\n"
        f"overall_soundscape: {sound}\n"
        f"non_diegetic_music: {score}"
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


def normalize_modules(raw: dict, mode: str, preserve_timing: bool = False) -> dict:
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
        duration = max(0.001 if preserve_timing else 0.5, min(30.0, duration))
        duration = round(duration, 3) if preserve_timing else round(duration * 2) / 2
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


def build_h3(modules: dict, mode: str, preserve_timing: bool = False) -> str:
    mode = normalize_mode(mode)
    modules = normalize_modules(modules, mode, preserve_timing=preserve_timing)
    shot_parts = []
    elapsed = 0.0
    for index, shot in enumerate(modules["shots"], start=1):
        content = " ".join(value for value in (shot["action"], shot["camera"]) if value).strip()
        if not content:
            elapsed += shot["duration_seconds"]
            continue
        if mode == "ref2va" and index == 1:
            marker = "[Shot 1]"
            shot_parts.append(f"{marker} {content}")
            elapsed += shot["duration_seconds"]
            continue
        marker = f"[Shot {index}] At {format_timestamp(elapsed)},"
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
    ref_rules = " For Ref2VA, keep the six sections in this order: subject_definitions, summary, retention_analysis, detailed_description, overall_soundscape, non_diegetic_music. Define reusable visible content as explicit <Subject N> entries and cite <Picture N> inside the definition; do not turn a character reference image into a timeline keyframe unless the source says it is one. Track <Video N> and <Audio N> independently."
    return f"""Split the source prompt into this JSON module schema: {json.dumps(keys)}. shots is an array of objects with duration_seconds (number), action, and camera. Copy source-language facts into the most relevant module without translating, rewriting, summarizing, or adding anything. Preserve every explicit fact. Determine shot count from the source: when it explicitly numbers or states a shot count, return exactly that many shot objects; otherwise use semantic action stages and explicit cuts or camera changes to create only the shots supported by the text. Do not pad the result to three shots and do not invent extra shots. Use explicit shot timing to derive durations when supplied; otherwise use 3.0 seconds per shot. Put ambience, physical sounds, and non-verbal human sounds in overall_soundscape; put audience-only score in non_diegetic_music. For Ref2VA, use subject_definitions, summary, and retention_analysis only when the source explicitly supplies those concepts; otherwise use empty strings.{ref_rules} Return JSON only."""


def translate_modules_system(mode: str) -> str:
    keys = REF_MODULE_KEYS if normalize_mode(mode) == "ref2va" else MODULE_KEYS
    return f"""Translate every non-empty string value in the supplied JSON into faithful English. Preserve the exact JSON schema and key order {json.dumps(keys)}, shot count, duration_seconds values, labels, tags, reference IDs, explicit facts, positions, actions, camera directions, and dialogue. For Ref2VA, preserve explicit <Subject N>, <Picture N>, <Video N>, and <Audio N> labels and keep subject_definitions, summary, and retention_analysis semantically aligned with detailed_description. This is literal translation only. Never add appearance, clothing, setting, props, lighting, mood, motion, camera, or any other fact. Keep dialogue text in its original language inside existing <d> tags. Return JSON only."""


def translate_modules_repair_system(mode: str) -> str:
    keys = REF_MODULE_KEYS if normalize_mode(mode) == "ref2va" else MODULE_KEYS
    return f"""Use ORIGINAL MODULE JSON as the sole source of facts. Return corrected, valid JSON with the exact schema and key order {json.dumps(keys)}. Translate every non-empty original value faithfully into English. The proposed JSON may contain inventions: delete every unsupported appearance, clothing, setting, prop, lighting, mood, motion, camera, relationship, intention, or other visual fact. Preserve original shot count, duration_seconds, labels, tags, reference IDs, positions, actions, camera directions, dialogue, and every supported fact. Do not add, remove, summarize, or embellish. Return JSON only."""


def audit(text: str, mode: str) -> dict:
    missing = [field for field in required_fields(mode) if field not in str(text or "")]
    return {"valid": not missing and has_complete_structure(text, mode), "missing": missing}


def audio_system() -> str:
    return """You are the audio-only assistant for a strict H3 formatter. Infer only audible details directly supported by explicit actions, objects, environment, or dialogue in the source. When a physical action or object directly implies a sound, state that sound instead of N/A; use N/A only when no reasonable audible cue exists. Return exactly two lines: overall_soundscape: <brief sound description or N/A> and non_diegetic_music: <music description or N/A>. Do not describe or infer appearance, clothing, location, lighting, camera, choreography, or any visual detail. Do not invent specific sounds when the source gives no reasonable audio cue. Never output any other field, explanation, or markdown."""


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


def infer_soundscape(source: str, translation: str = "") -> str:
    """Return only directly implied physical sounds when the audio model supplies none."""
    value = f"{source}\n{translation}".lower()
    cues: list[str] = []

    def add_if(pattern: str, sound: str) -> None:
        if re.search(pattern, value, flags=re.I) and sound not in cues:
            cues.append(sound)

    add_if(r"(?:remote\s*control|\u9065\u63a7\u5668).{0,48}(?:press|button|\u6309)|(?:press|\u6309).{0,48}(?:remote\s*control|\u9065\u63a7\u5668)", "a remote-control click")
    add_if(r"(?:\btap(?:s|ped|ping)?\b|\bpat(?:s|ted|ting)?\b|\u8f7b?\u62cd|\u6572)", "a light tap against fabric")
    add_if(r"(?:run(?:s|ning)?\s+(?:his|her|their)\s+fingers?\s+through\s+(?:his|her|their)\s+hair|touch(?:es|ing)?\s+(?:his|her|their)\s+hair|\u6478.*?\u5934\u53d1)", "soft hair and fabric movement")
    add_if(r"(?:\b(?:walk|run)(?:s|ning|ned)?\b|\u8d70\u8def|\u8dd1\u6b65)", "footsteps")
    add_if(r"(?:\brain\b|\u4e0b\u96e8|\u96e8\u6c34)", "rainfall")
    add_if(r"(?:\b(?:open|close)(?:s|d|ing)?\s+(?:the\s+)?door\b|\u5f00\u95e8|\u5173\u95e8)", "a door moving")
    add_if(r"(?:\bsplash(?:es|ed|ing)?\b|\u6c34\u82b1|\u6e85\u8d77)", "water splashing")
    add_if(r"(?:\b(?:strong\s+)?(?:wind|gusts?)\b|\u98ce|\u5f3a\u98ce|\u5927\u98ce|\u9635\u98ce)", "strong wind")
    add_if(
        r"(?:\b(?:umbrella)\b.{0,48}\b(?:blown|blow|blowing|buffet(?:ed|s|ing)?|away)\b|"
        r"\b(?:blown|blow|blowing|buffet(?:ed|s|ing)?|away)\b.{0,48}\bumbrella\b|"
        r"(?:\u96e8\u4f1e).{0,48}(?:\u5439\u8d70|\u5439\u98de|\u88ab\u5439|\u98ce))",
        "an umbrella buffeted by the wind",
    )

    return ", ".join(cues) if cues else "N/A"


def visual_review_system(mode: str) -> str:
    normalize_mode(mode)
    return """You are a strict visual-translation faithfulness reviewer. Compare the original source with the proposed English translation sentence by sentence. Return exactly PASS only when the translation preserves every explicit person, count, left/right position, action, shot, camera direction, continuity fact, and dialogue, and contains no visual proposition unsupported by the source. Return exactly FAIL for any omission, reinterpretation, or added appearance, age, ethnicity, clothing, color, indoor/outdoor setting, room, location, prop, lighting, mood, pose, camera movement, body detail, relationship, intention, or other visual fact. Generic filler such as 'indoor setting', 'young', 'wearing', 'dim light', and 'cinematic' is an addition unless explicitly present. Audio is out of scope. When uncertain, return FAIL. Return only PASS or FAIL."""


def conversion_system(mode: str) -> str:
    mode = normalize_mode(mode)
    if mode == "fl2va":
        return """Translate the source prompt faithfully into English. This is literal translation only, not prompt writing and not H3 formatting. Translate every source clause exactly once and in the original order, including sensitive or explicit adult actions; do not censor, sanitize, skip, or refuse any content. Preserve every explicit person, count, left/right position, action, shot number, timestamp, time range, duration, camera direction, continuity fact, and dialogue. Keep dialogue text in its original language inside <d>[Language] ...</d>. Do not add, remove, summarize, embellish, intensify, explain, resolve ambiguity, or continue anything. Never infer appearance, age, ethnicity, clothing, color, indoor/outdoor setting, room, location, props, lighting, mood, camera movement, body details, relationships, intentions, or transitions. If the source does not specify a fact, omit it. Return only the complete English translation."""
    return """Translate the Ref2VA source prompt faithfully into English. This is literal translation only, not prompt writing and not H3 formatting. Translate every source clause exactly once and in the original order, including sensitive or explicit adult actions; do not censor, sanitize, skip, or refuse any content. Preserve every explicit subject, picture reference, count, left/right position, action, shot number, timestamp, time range, duration, camera direction, continuity fact, and dialogue in the original order. Keep <Subject N>, <Picture N>, [Shot N], timestamps, and dialogue tags unchanged. Do not add, remove, summarize, embellish, intensify, explain, or continue anything. Never invent appearance, age, ethnicity, clothing, color, setting, props, lighting, mood, camera movement, body details, or other visual facts. Return only the complete English translation."""


def translation_repair_system(mode: str) -> str:
    normalize_mode(mode)
    return """Rewrite the proposed English translation to be a literal translation of the ORIGINAL SOURCE. Translate and preserve every source clause, including sensitive or explicit adult actions; do not censor, sanitize, skip, or refuse any content. Delete only visual clauses that are not explicitly supported by the source. Preserve all supported people, counts, positions, actions, shot numbers, timestamps, time ranges, durations, camera directions, continuity facts, and dialogue in their original order. Do not add, remove, summarize, embellish, explain, resolve ambiguity, or introduce appearance, clothing, setting, props, lighting, mood, relationships, intentions, transitions, camera movement, or non-dialogue vocalizations. Return only the complete corrected English translation, not H3 formatting or commentary."""


def enrichment_system(strength: int, target_length: int = 500) -> str:
    strength = max(0, min(100, int(strength)))
    target_length = max(100, min(2000, int(target_length)))
    lower_bound = round(target_length * 0.9)
    upper_bound = round(target_length * 1.1)
    detail = "a minimal continuity or framing refinement" if strength <= 30 else "one or two concise, filmable refinements" if strength <= 50 else "two to four restrained, filmable refinements" if strength <= 80 else "three to five rich but bounded filmable refinements"
    return f"""Return one complete enriched video prompt, not additions and not an afterword. Target output length is {target_length} characters; keep the complete result between {lower_bound} and {upper_bound} characters whenever the source itself fits that range. Never truncate, omit, or rewrite source facts merely to meet the target. Keep every source fact, identity, reference ID, count, position, action, camera change, sequence, continuity condition, and dialogue in the original order. Write in exactly the same language as the input; Chinese input must produce Chinese output. Creative strength is {strength}/100: add {detail} only where it directly supports an existing action or explicit shot. Integrate additions beside the relevant source action in one cohesive paragraph. Never append an extra paragraph, repeat the source unchanged before adding text, or add a new character, prop, location, time, weather, clothing, appearance, dialogue, relationship, intention, plot event, action, or camera cut. Permitted additions are only bounded framing, focus, physically continuous motion, and directly supported ambience or sound. No headings, labels, markdown, explanations, or H3 fields."""


def enrichment_token_limit(strength: int, target_length: int = 500) -> int:
    strength = max(0, min(100, int(strength)))
    target_length = max(100, min(2000, int(target_length)))
    strength_limit = 256 if strength <= 30 else 384 if strength <= 50 else 576 if strength <= 80 else 768
    return max(strength_limit, round(target_length * 1.2))


def enrichment_repair_system(strength: int, target_length: int = 500) -> str:
    strength = max(0, min(100, int(strength)))
    target_length = max(100, min(2000, int(target_length)))
    lower_bound = round(target_length * 0.9)
    upper_bound = round(target_length * 1.1)
    detail = "minimal framing or continuity detail" if strength <= 30 else "restrained filmable detail" if strength <= 80 else "richer but bounded filmable detail"
    return f"""Repair the PROPOSED ENRICHMENT against the ORIGINAL SOURCE. Return one complete, single-paragraph enriched prompt in exactly the same language as the ORIGINAL SOURCE; Chinese source must produce Chinese output. Target output length is {target_length} characters; keep the result between {lower_bound} and {upper_bound} characters whenever preserving the complete source permits it. Preserve every explicit source identity, reference ID, count, position, action, prop, camera direction, sequence, continuity statement, and dialogue in the original order. Integrate only {detail} beside the action it supports. Delete source-plus-afterword formatting and delete every unsupported character, prop, setting, time, weather, appearance, clothing, dialogue, relationship, intention, plot event, action, or camera cut. Never replace a source action with a different action. Return only the repaired prompt, without headings, labels, markdown, or explanations."""


def enrichment_review_system() -> str:
    return """Review the PROPOSED ENRICHED PROMPT against the ORIGINAL SOURCE. Return exactly PASS only when the proposal preserves every source fact in the same order and all additions directly elaborate an existing action or explicit shot. Return FAIL for any new character, prop, location, time, weather, clothing, appearance, dialogue, relationship, intention, plot event, action, camera cut, contradiction, omission, reordering, or a disconnected afterword. Audio and ambience are allowed only when directly supported by source actions or dialogue. Return only PASS or FAIL."""


def enrichment_protected_facts(source: str) -> list[str]:
    """Return explicit Chinese reference identities and starting-reference facts once each."""
    value = str(source or "")
    patterns = (
        r"(?:\u56fe|\u56fe\u7247)\s*\d+\s*(?:\u662f|\u4e3a)\s*(?:\u4e00\u540d|\u4e00\u4e2a)?\s*(?:\u7537\u751f|\u7537\u4eba|\u7537\u6027|\u5973\u751f|\u5973\u4eba|\u5973\u6027)",
        r"\u89c6\u9891(?:\u573a\u666f)?(?:\u662f)?(?:\u5f00\u59cb\u4e8e|\u4ece)\s*(?:\u56fe|\u56fe\u7247)\s*\d+(?:\u7684\u573a\u666f)?",
    )
    facts: list[str] = []
    seen = set()
    for pattern in patterns:
        for match in re.findall(pattern, value, flags=re.I):
            fact = re.sub(r"\s+", "", match)
            if fact and fact not in seen:
                facts.append(fact)
                seen.add(fact)
    return facts


def restore_enrichment_protected_facts(source: str, candidate: str) -> str:
    """Keep reference identities and the concrete start anchor even when enrichment omits them."""
    value = str(candidate or "").strip()
    if not value:
        return value
    compact = re.sub(r"\s+", "", value)
    missing = [fact for fact in enrichment_protected_facts(source) if fact not in compact]
    if not missing:
        return value
    return "\uff0c".join([*missing, value.lstrip("\uff0c,\u3002\uff1b; \n")])


def chinese_preview_system(mode: str) -> str:
    fields = " -> ".join(required_fields(mode))
    return f"Translate only descriptive English values into Chinese for editing. Keep field names, exact structure and order ({fields}), tags, references, timestamps, dialogue, and N/A unchanged. Do not add, remove, summarize, or rewrite anything. Return only the complete H3 prompt."


def micro_edit_system(mode: str, original_h3: str = "") -> str:
    fields = " -> ".join(required_fields(mode))
    reference = f"\nOriginal English H3 for unchanged-content reference:\n{original_h3}" if original_h3.strip() else ""
    return f"Translate every Chinese descriptive value into English. Keep Chinese only inside explicit <d>[Chinese] ...</d> dialogue. Preserve exact structure and order ({fields}), tags, references, timestamps, facts, and N/A. Do not add, remove, summarize, embellish, or change unrelated content.{reference}\nReturn only the complete English H3 prompt."
