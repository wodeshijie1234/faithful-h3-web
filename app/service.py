import re
import time
from collections import Counter

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


def _has_repeated_enrichment_content(source: str, candidate: str) -> bool:
    """Reject a model result that loops the complete source or its own full body."""
    compact_source = re.sub(r"\s+", "", str(source or ""))
    compact_candidate = re.sub(r"\s+", "", str(candidate or ""))
    if compact_source and compact_candidate.count(compact_source) > 1:
        return True
    length = len(compact_candidate)
    if length >= 80 and len(set(compact_candidate)) >= 8:
        midpoint = length // 2
        left = compact_candidate[:midpoint]
        right = compact_candidate[midpoint:]
        if left == right or (length % 2 and left == right[:-1]):
            return True
    return False


def _quoted_fragments(value: str) -> list[str]:
    """Extract explicit quoted utterances without treating ordinary punctuation as speech."""
    text = str(value or "")
    pattern = re.compile(r"[“「『]([^”」』]{1,200})[”」』]|\"([^\"\r\n]{1,200})\"")
    sound_effect = re.compile(r"^(?:砰|嘭|啪|咚|轰|咔嚓|咔哒|吱呀|叮|嗡|噼啪|扑通|哐|当|唰|沙沙|滋滋)[—~～….!！?？]*$")
    fragments: list[str] = []
    for match in pattern.finditer(text):
        fragment = next(part for part in match.groups() if part).strip()
        if sound_effect.fullmatch(fragment):
            continue
        fragments.append(fragment)
    return fragments


def _has_utterance_contract_violation(source: str, candidate: str) -> bool:
    """Require every explicit quoted utterance verbatim once and reject extras."""
    normalize = lambda value: re.sub(r"\s+", "", str(value or ""))
    source_utterances = Counter(normalize(item) for item in _quoted_fragments(source))
    candidate_utterances = Counter(normalize(item) for item in _quoted_fragments(candidate))
    return source_utterances != candidate_utterances


def _clean_extra_utterance_clauses(source: str, candidate: str) -> str:
    """Remove the smallest clause containing a generated utterance, preserving source speech and SFX."""
    allowed = Counter(re.sub(r"\s+", "", item) for item in _quoted_fragments(source))
    used: Counter[str] = Counter()
    clauses = re.findall(r".*?(?:[，,；;。！？!?]|$)", str(candidate or ""), flags=re.S)
    kept: list[str] = []
    for clause in clauses:
        fragments = _quoted_fragments(clause)
        extra = False
        for fragment in fragments:
            normalized = re.sub(r"\s+", "", fragment)
            used[normalized] += 1
            if used[normalized] > allowed[normalized]:
                extra = True
        if not extra:
            kept.append(clause)
    return "".join(kept).strip()


def _enrichment_source_payload(source: str) -> str:
    """Make exact utterance preservation salient without changing source facts."""
    utterances = _quoted_fragments(source)
    if not utterances:
        return source
    anchors = "\n".join(f"- {utterance}" for utterance in utterances)
    return f"{source}\n\nMANDATORY VERBATIM UTTERANCES (each exactly once, no others):\n{anchors}"


def _enrichment_action_segments(source: str, maximum: int = 5) -> list[str]:
    """Split a long Chinese action chain on top-level punctuation, never inside quotes."""
    text = str(source or "").strip()
    if not text:
        return []
    clauses: list[str] = []
    start = 0
    closing = ""
    pairs = {"“": "”", "「": "」", "『": "』", '"': '"'}
    for index, character in enumerate(text):
        if closing:
            if character == closing:
                closing = ""
            continue
        if character in pairs:
            closing = pairs[character]
            continue
        if character in "，,；;。！？!?":
            clause = text[start:index + 1].strip()
            if clause:
                clauses.append(clause)
            start = index + 1
    tail = text[start:].strip()
    if tail:
        clauses.append(tail)
    if len(clauses) <= 1:
        return clauses

    final_index = next(
        (index for index, clause in enumerate(clauses) if re.search(r"(?:最后|最终|finally|at last)", clause, flags=re.I)),
        len(clauses),
    )
    prefix = clauses[:final_index]
    final_group = "".join(clauses[final_index:]).strip() if final_index < len(clauses) else ""

    setup_pattern = re.compile(
        r"(?:参考图|reference (?:image|picture)|视频从|视频以|场景出发|场景开始|第一帧|"
        r"保持(?:第一帧|姿势|动作|不变)|^\s*(?:图|图片|picture)\s*\d+\s*(?:是|为|is))",
        flags=re.I,
    )
    first_action_end = 0
    while first_action_end < len(prefix) and setup_pattern.search(prefix[first_action_end]):
        first_action_end += 1
    if first_action_end < len(prefix):
        first_action_end += 1

    groups: list[str] = []
    if first_action_end:
        groups.append("".join(prefix[:first_action_end]).strip())
    for clause in prefix[first_action_end:]:
        value = clause.strip()
        if (groups and re.match(
                r"^(?:同时|并且|并|随后)?\s*(?:用[^，,；;。]*?(?:发出|说道|说：|说:)|"
                r"(?:声音|叫声|笑声|vocalization|sound)\b)", value, flags=re.I)):
            groups[-1] += value
        else:
            groups.append(value)
    if final_group:
        groups.append(final_group)

    while len(groups) > maximum:
        merge_index = min(range(len(groups) - 1), key=lambda index: _compact_length(groups[index]) + _compact_length(groups[index + 1]))
        groups[merge_index:merge_index + 2] = [groups[merge_index] + groups[merge_index + 1]]
    return [group for group in groups if group]


def _has_post_terminal_continuation(source: str, candidate: str) -> bool:
    """Reject a new story appended after the source's explicit final utterance.

    Quoted dialogue is a stable terminal anchor because enrichment must preserve
    its exact text. Camera or staging detail belongs before that anchor, beside
    the action it develops; prose after it is an appended continuation.
    """
    source_quotes = _quoted_fragments(source)
    if not source_quotes:
        return False
    terminal = re.sub(r"\s+", "", source_quotes[-1])
    compact_candidate = re.sub(r"\s+", "", str(candidate or ""))
    end = compact_candidate.rfind(terminal)
    if end < 0:
        return False
    tail = compact_candidate[end + len(terminal):]
    tail = re.sub(r"^[”」』\"'。，、；：！？,.!?;:—…·（）()\[\]【】]+", "", tail)
    return bool(tail)


def _truncate_after_terminal_utterance(source: str, candidate: str) -> str:
    """Cut deterministic aftermath after a source-ending quoted utterance."""
    source = str(source or "").strip()
    candidate = str(candidate or "").strip()
    source_matches = list(re.finditer(r"[“「『]([^”」』]{1,200})[”」』]|\"([^\"\r\n]{1,200})\"", source))
    if not source_matches:
        return candidate
    source_tail = source[source_matches[-1].end():]
    if re.sub(r"[\s。！？.!?；;：:，,—…]+", "", source_tail):
        return candidate
    terminal = next(part for part in source_matches[-1].groups() if part).strip()
    candidate_matches = list(re.finditer(r"[“「『]([^”」』]{1,200})[”」』]|\"([^\"\r\n]{1,200})\"", candidate))
    matching = [
        match for match in candidate_matches
        if next(part for part in match.groups() if part).strip() == terminal
    ]
    if not matching:
        return candidate
    if matching[-1].start() < round(len(candidate) * 0.5):
        return candidate
    end = matching[-1].end()
    punctuation = re.match(r"[。！？.!?；;：:，,—…]+", candidate[end:])
    if punctuation:
        end += punctuation.end()
    return candidate[:end].rstrip()


def _truncate_integrated_terminal_aftermath(source: str, candidate: str) -> str:
    """Use terminal truncation only when meaningful enrichment precedes it."""
    truncated = _truncate_after_terminal_utterance(source, candidate)
    if truncated == str(candidate or "").strip():
        return truncated
    if _compact_length(truncated) <= _compact_length(source) + 20:
        return str(candidate or "").strip()
    return truncated


def _insert_before_terminal_utterance(source_segment: str, enriched_segment: str, detail: str) -> str:
    """Insert supplemental detail before a source-ending utterance, otherwise append in-segment."""
    detail = str(detail or "").strip()
    value = str(enriched_segment or "").strip()
    source_quotes = _quoted_fragments(source_segment)
    if not detail:
        return value
    if not source_quotes:
        return f"{value}{detail}" if _contains_cjk(value) else f"{value} {detail}"
    terminal = source_quotes[-1]
    matches = [match for match in re.finditer(re.escape(terminal), value)]
    if not matches:
        return value
    quote_start = matches[-1].start()
    sentence_start = max(value.rfind("。", 0, quote_start), value.rfind("！", 0, quote_start), value.rfind("？", 0, quote_start)) + 1
    return f"{value[:sentence_start]}{detail}{value[sentence_start:]}"


_CHINESE_FILMABLE_DETAIL_BANK = (
    "镜头以稳定中景建立人物之间的空间关系，画面轴线保持一致，避免方位无故跳变。",
    "构图在动作方向预留充足空间，主体始终落在安全画幅内，面部与手部不被遮挡。",
    "焦点随当前动作的重心平滑转移，景深连续变化，不出现突兀虚焦或无意义抖动。",
    "柔和主光勾勒人物轮廓，辅光保留眼神、表情与关键肢体部位的清晰层次。",
    "摄影机的起步、跟随与停稳均保留自然缓冲，动作全程以正常速度连贯完成。",
    "背景只承担空间参照，纹理、反射和阴影随人物位置变化，不抢夺主体注意力。",
    "动作按准备、发力、经过与收势连续呈现，身体重心和关节变化符合真实惯性。",
    "衣料摩擦、脚步与室内混响保持逐帧同步，不加入任何额外人声或新台词。",
    "关键手势处景别适度收紧但不切断肢体，随后平稳恢复到能看清完整关系的范围。",
    "色彩与曝光前后一致，高光不过曝、暗部保留纹理，参考身份特征不发生漂移。",
    "人物视线、站位距离与左右关系持续稳定，不因镜头运动产生无理由的位置变化。",
    "所有细微反应都限定在当前原动作持续期间，不提前触发下一阶段或新的结果。",
    "自然运动模糊只强化速度方向，主体轮廓与关键动作瞬间仍保持明确可辨。",
    "镜头节奏完全由当前动作驱动，不插入无关转场，停顿只用于交代动作过程。",
    "现场声的远近变化与人物距离一致，音量不过度夸张，也不覆盖既有中文发声。",
    "服装、发型、姿态起点与画面内物件位置保持连续，不出现凭空增减的元素。",
    "摄影方向服务于原始动作链，新增内容仅描述同一时刻可见的制作细节。",
    "画面严格停留在本段既有动作范围内，不追加离场、交谈或事后叙事。",
    "镜头高度贴合人物重心，透视关系自然，近景与中景之间的变化有明确动机。",
    "主体边缘与背景形成清楚分离，光影过渡柔和，快速动作中也不丢失五官信息。",
    "相机沿既定轴线小幅调整，让动作方向清晰，同时保持空间比例和人物尺度稳定。",
    "画面中的空气感与环境反射维持统一，细节丰富但不改变原场景的核心性质。",
    "每次姿态变化都有可见的重心传递，脚下支撑与上身转动保持同步和连贯。",
    "镜头不使用慢动作、定格或突然加速，时间流速从动作开始到完成保持一致。",
    "声音层次以动作现场为主，保留轻微呼吸和环境底噪，但绝不新增发声内容。",
    "取景持续照顾动作完整性，既能看清表情反应，也能确认手脚位置与相互距离。",
    "对焦与曝光变化采用平滑过渡，避免亮度闪烁、边缘重影和不必要的视觉跳切。",
    "动作方向、速度与力度在相邻画面中连续，接点清楚，不以新动作替代原动作。",
    "环境细节保持克制，只补充材质、光泽与空间纵深，不赋予人物新的经历或目的。",
    "本段完成点与源文本完全一致，镜头在既有动作结束处收束，不向后续故事延伸。",
)


def _deterministic_segment_detail(index: int, total: int, needed: int) -> str:
    """Supply unique neutral production detail when the local model cannot obey a segment."""
    needed = max(0, int(needed))
    if needed <= 0:
        return ""
    bank = _CHINESE_FILMABLE_DETAIL_BANK
    phase_prefixes = (
        "在当前空间关系建立时，",
        "在当前动作开始衔接时，",
        "在当前动作稳定推进时，",
        "在当前姿态持续变化时，",
        "在当前动作接近收束时，",
    )
    prefix = phase_prefixes[index % len(phase_prefixes)]
    stride = max(1, len(bank) // max(1, total))
    start = (index * stride) % len(bank)
    ordered = [bank[(start + offset) % len(bank)] for offset in range(len(bank))]
    chunks: list[str] = []
    for sentence in ordered:
        if sentence in chunks:
            continue
        chunks.append(prefix + sentence)
        if _compact_length("".join(chunks)) >= needed:
            break
    return "".join(chunks)


def _build_deterministic_integrated_enrichment(source: str, target_length: int) -> str:
    """Build a faithful long prompt when the local model cannot obey length/structure together."""
    segments = _enrichment_action_segments(source)
    if not segments:
        return str(source or "").strip()
    lower_bound = round(max(100, min(2000, int(target_length))) * 0.9)
    per_segment = max(0, -(-lower_bound // len(segments)))
    enriched: list[str] = []
    for index, segment in enumerate(segments):
        needed = max(0, per_segment - _compact_length(segment))
        detail = _deterministic_segment_detail(index, len(segments), needed)
        enriched.append(_insert_before_terminal_utterance(segment, segment, detail))
    result = "".join(enriched) if _contains_cjk(source) else " ".join(enriched)
    return _fit_enrichment_upper_bound(source, result, target_length)


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
    """Fit an integrated model result to the requested ceiling without prepending source."""
    if target_length is None:
        return candidate
    upper_bound = round(target_length * 1.1)
    if _compact_length(source) > upper_bound or _compact_length(candidate) <= upper_bound:
        return candidate
    return _append_with_compact_limit("", candidate, upper_bound)


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
    candidate = str(candidate or "").strip()
    sentences = re.findall(r".*?(?:[。！？.!?](?=\s|$)|[。！？]|$)", candidate, flags=re.S)
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
    return separator.join(kept)


def _clean_enrichment_addition(source: str, addition: str) -> str:
    """Clean one new continuation without re-segmenting previously accepted prose."""
    source = str(source or "").strip()
    return _remove_new_drift_sentences(source, addition)


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
        temperature = round(0.15 + 0.40 * strength / 100, 3)
        top_p = round(0.35 + 0.50 * strength / 100, 3)
        source_payload = _enrichment_source_payload(source)
        enriched = self.runtime.generate(
            source_payload,
            h3.enrichment_system(strength, target_length),
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=h3.enrichment_token_limit(strength, target_length),
        ).strip()
        enriched_valid = bool(enriched) and not (_contains_cjk(source) and not _contains_cjk(enriched))
        candidate = ""
        candidate_reviewed = False
        deterministic_drift: list[str] = []
        repeated_content = False
        post_terminal_continuation = False
        utterance_contract_violation = False
        if enriched_valid:
            enriched = h3.restore_enrichment_protected_facts(source, enriched)
            enriched = _clean_extra_utterance_clauses(source, enriched)
            enriched = _truncate_integrated_terminal_aftermath(source, enriched)
            repeated_content = _has_repeated_enrichment_content(source, enriched)
            post_terminal_continuation = _has_post_terminal_continuation(source, enriched)
            utterance_contract_violation = _has_utterance_contract_violation(source, enriched)
            deterministic_drift = _enrichment_drift_categories(source, enriched)
            if deterministic_drift:
                enriched = _remove_new_drift_sentences(source, enriched)
            if not deterministic_drift:
                review = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{enriched}",
                    h3.enrichment_review_system(strength, target_length), temperature=0.01, top_p=0.1, max_new_tokens=8,
                ).strip().upper()
                needs_integration = enriched.startswith(source) and "\n\n" in enriched
                if (_is_pass_verdict(review) and not needs_integration and not repeated_content
                        and not post_terminal_continuation and not utterance_contract_violation):
                    candidate = enriched
                    candidate_reviewed = True
                    if _is_within_enrichment_target(source, candidate, requested_target_length):
                        return candidate

        if not candidate_reviewed or _enrichment_length_status(source, candidate, requested_target_length) > 0:
            drift_note = ", ".join(deterministic_drift) if deterministic_drift else "none"
            structure_flags = []
            if repeated_content:
                structure_flags.append("repeated full source/body")
            if post_terminal_continuation:
                structure_flags.append("post-terminal story continuation")
            if utterance_contract_violation:
                structure_flags.append("utterance contract violation")
            structure_note = ", ".join(structure_flags) or "none"
            deterministic_structure_failure = (
                repeated_content or post_terminal_continuation or utterance_contract_violation
            )
            proposed_enrichment = (
                "[discarded because it violated content or structure; regenerate from ORIGINAL SOURCE only]"
                if deterministic_drift or deterministic_structure_failure
                else enriched if enriched_valid else "[invalid or empty output]"
            )
            repair_attempts = 3 if deterministic_drift or deterministic_structure_failure else 1
            repair_temperature = min(temperature, 0.35) if deterministic_drift or deterministic_structure_failure else temperature
            repair_top_p = min(top_p, 0.6) if deterministic_drift or deterministic_structure_failure else top_p
            repair_succeeded = False
            for attempt in range(repair_attempts):
                retry_note = "\nThe previous automatic attempt still drifted; regenerate again from ORIGINAL SOURCE only." if attempt else ""
                repaired = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source_payload}\n\nDETERMINISTIC DRIFT FLAGS: {drift_note}\n"
                    f"STRUCTURE FLAGS: {structure_note}{retry_note}\n\n"
                    f"PROPOSED ENRICHMENT:\n{proposed_enrichment}",
                    h3.enrichment_repair_system(strength, target_length),
                    temperature=repair_temperature,
                    top_p=repair_top_p,
                    max_new_tokens=h3.enrichment_token_limit(strength, target_length),
                ).strip()
                if not repaired or (_contains_cjk(source) and not _contains_cjk(repaired)):
                    continue
                candidate = h3.restore_enrichment_protected_facts(source, repaired)
                candidate = _clean_extra_utterance_clauses(source, candidate)
                candidate = _truncate_integrated_terminal_aftermath(source, candidate)
                raw_repaired_drift = _enrichment_drift_categories(source, candidate)
                if raw_repaired_drift:
                    candidate = _remove_new_drift_sentences(source, candidate)
                candidate = _fit_enrichment_upper_bound(source, candidate, requested_target_length)
                repaired_drift = _enrichment_drift_categories(source, candidate)
                repaired_repetition = _has_repeated_enrichment_content(source, candidate)
                repaired_post_terminal = _has_post_terminal_continuation(source, candidate)
                repaired_utterance_violation = _has_utterance_contract_violation(source, candidate)
                if (repaired_drift or repaired_repetition or repaired_post_terminal
                        or repaired_utterance_violation):
                    drift_note = ", ".join(repaired_drift)
                    structure_flags = []
                    if repaired_repetition:
                        structure_flags.append("repeated full source/body")
                    if repaired_post_terminal:
                        structure_flags.append("post-terminal story continuation")
                    if repaired_utterance_violation:
                        structure_flags.append("utterance contract violation")
                    structure_note = ", ".join(structure_flags) or "none"
                    proposed_enrichment = "[discarded because it violated content or structure; regenerate from ORIGINAL SOURCE only]"
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
            short_draft = candidate
            length_repair_succeeded = False
            for attempt in range(3):
                retry_note = "\nThe previous full rewrite still failed the contract; rewrite from the ORIGINAL SOURCE again." if attempt else ""
                rewritten = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source_payload}\n\nSHORT ENRICHED DRAFT:\n{short_draft}{retry_note}",
                    h3.enrichment_length_repair_system(strength, target_length),
                    temperature=min(temperature, 0.45),
                    top_p=min(top_p, 0.7),
                    max_new_tokens=h3.enrichment_token_limit(strength, target_length),
                ).strip()
                if not rewritten or (_contains_cjk(source) and not _contains_cjk(rewritten)):
                    continue
                proposed_candidate = h3.restore_enrichment_protected_facts(source, rewritten)
                proposed_candidate = _clean_extra_utterance_clauses(source, proposed_candidate)
                proposed_candidate = _truncate_integrated_terminal_aftermath(source, proposed_candidate)
                proposed_candidate = _fit_enrichment_upper_bound(source, proposed_candidate, requested_target_length)
                if (not _is_within_enrichment_target(source, proposed_candidate, requested_target_length)
                        or _enrichment_drift_categories(source, proposed_candidate)
                        or _has_repeated_enrichment_content(source, proposed_candidate)
                        or _has_post_terminal_continuation(source, proposed_candidate)
                        or _has_utterance_contract_violation(source, proposed_candidate)):
                    short_draft = proposed_candidate
                    continue
                final_review = self.runtime.generate(
                    f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{proposed_candidate}",
                    h3.enrichment_review_system(strength, target_length),
                    temperature=0.01,
                    top_p=0.1,
                    max_new_tokens=8,
                ).strip().upper()
                if not _is_pass_verdict(final_review):
                    short_draft = proposed_candidate
                    continue
                candidate = proposed_candidate
                length_repair_succeeded = True
                break
            if not length_repair_succeeded:
                source_segments = _enrichment_action_segments(source)
                enriched_segments: list[str] = []
                segment_target = max(160, min(600, round(target_length / max(1, len(source_segments)))))
                segment_minimum = max(120, -(-round(target_length * 0.9) // max(1, len(source_segments))))
                for segment_index, segment in enumerate(source_segments):
                    segment_payload = _enrichment_source_payload(segment)
                    accepted_segment = ""
                    for segment_attempt in range(3):
                        retry_note = (
                            "\nThe previous attempt violated this segment; retry this segment from its source only."
                            if segment_attempt else ""
                        )
                        expanded_segment = self.runtime.generate(
                            f"SOURCE ACTION SEGMENT:\n{segment_payload}{retry_note}",
                            h3.enrichment_segment_system(strength, segment_target),
                            temperature=min(temperature, 0.35),
                            top_p=min(top_p, 0.6),
                            max_new_tokens=max(320, round(segment_target * 1.8)),
                        ).strip()
                        expanded_segment = _clean_extra_utterance_clauses(segment, expanded_segment)
                        if (not expanded_segment or (_contains_cjk(segment) and not _contains_cjk(expanded_segment))
                                or _has_utterance_contract_violation(segment, expanded_segment)
                                or _enrichment_drift_categories(source, expanded_segment)
                                or _has_repeated_enrichment_content(segment, expanded_segment)):
                            continue
                        accepted_segment = expanded_segment
                        break
                    accepted_from_model = bool(accepted_segment)
                    if not accepted_segment:
                        accepted_segment = segment
                    facets = (
                        "camera, framing, spatial depth, and focus transitions",
                        "physical motion continuity, timing, balance, and gesture",
                        "lighting, material texture, environmental response, and supported non-vocal sound",
                    )
                    for facet in facets[:1] if accepted_from_model else ():
                        if _compact_length(accepted_segment) >= segment_minimum:
                            break
                        missing = segment_minimum - _compact_length(accepted_segment)
                        detail = self.runtime.generate(
                            f"SOURCE ACTION SEGMENT:\n{segment}\n\n"
                            f"CURRENT ENRICHED ACTION SEGMENT:\n{accepted_segment}",
                            h3.enrichment_segment_detail_system(facet, min(500, max(100, missing))),
                            temperature=min(temperature, 0.35),
                            top_p=min(top_p, 0.6),
                            max_new_tokens=max(220, round(min(500, max(100, missing)) * 1.8)),
                        ).strip()
                        detail = _clean_extra_utterance_clauses("", detail)
                        if (not detail or (_contains_cjk(segment) and not _contains_cjk(detail))
                                or _enrichment_drift_categories(source, detail)
                                or _has_repeated_enrichment_content(segment, detail)):
                            continue
                        accepted_segment = _insert_before_terminal_utterance(
                            segment, accepted_segment, detail
                        )
                    if _compact_length(accepted_segment) < segment_minimum:
                        deterministic_detail = _deterministic_segment_detail(
                            segment_index,
                            len(source_segments),
                            segment_minimum - _compact_length(accepted_segment),
                        )
                        accepted_segment = _insert_before_terminal_utterance(
                            segment, accepted_segment, deterministic_detail
                        )
                    enriched_segments.append(accepted_segment)
                if enriched_segments:
                    assembled = "".join(enriched_segments) if _contains_cjk(source) else " ".join(enriched_segments)
                    assembled = h3.restore_enrichment_protected_facts(source, assembled)
                    assembled = _truncate_integrated_terminal_aftermath(source, assembled)
                    assembled = _fit_enrichment_upper_bound(source, assembled, requested_target_length)
                    if (_is_within_enrichment_target(source, assembled, requested_target_length)
                            and not _enrichment_drift_categories(source, assembled)
                            and not _has_repeated_enrichment_content(source, assembled)
                            and not _has_post_terminal_continuation(source, assembled)
                            and not _has_utterance_contract_violation(source, assembled)):
                        segment_review = self.runtime.generate(
                            f"ORIGINAL SOURCE:\n{source}\n\nPROPOSED ENRICHED PROMPT:\n{assembled}",
                            h3.enrichment_review_system(strength, target_length),
                            temperature=0.01,
                            top_p=0.1,
                            max_new_tokens=8,
                        ).strip().upper()
                        if _is_pass_verdict(segment_review):
                            candidate = assembled
                            length_repair_succeeded = True
                if not length_repair_succeeded:
                    deterministic_candidate = _build_deterministic_integrated_enrichment(source, target_length)
                    if (_is_within_enrichment_target(source, deterministic_candidate, requested_target_length)
                            and not _has_repeated_enrichment_content(source, deterministic_candidate)
                            and not _has_post_terminal_continuation(source, deterministic_candidate)
                            and not _has_utterance_contract_violation(source, deterministic_candidate)):
                        candidate = deterministic_candidate
                        length_repair_succeeded = True
                if not length_repair_succeeded:
                    raise RuntimeError("Prompt enrichment could not meet the requested target length as one integrated rewrite.")

        if not _is_within_enrichment_target(source, candidate, requested_target_length):
            raise RuntimeError("Prompt enrichment could not meet the requested target length after automatic correction.")
        if _has_utterance_contract_violation(source, candidate):
            raise RuntimeError("Prompt enrichment violated the source utterance contract after automatic correction.")
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
