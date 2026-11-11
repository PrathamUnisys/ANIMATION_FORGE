from __future__ import annotations

import re
from typing import Any

from .common import new_id, utc_now

TITLE_RE = re.compile(r"^#\s+(.+?)\s*$")
METADATA_RE = re.compile(r"^-\s+\*\*([^*]+)\*\*:\s*(.+?)\s*$")
METADATA_SEGMENT_RE = re.compile(r"^\*\*([^*]+)\*\*:\s*(.+?)\s*$")
ACT_RE = re.compile(
    r"^##\s+ACT\s+([IVX]+)\s*[—–-]\s*(.+?)(?:\s*\(([^)]*)\))?\s*$", re.IGNORECASE
)
SCENE_RE = re.compile(r"^\*\*(INT\.|EXT\.|INT\./EXT\.|I/E\.)\s*(.*?)\*\*\s*$", re.IGNORECASE)
CHAR_RE = re.compile(r"^\*\*([A-Z][A-Z0-9 .'-]{1,40})\*\*\s*$")
PAREN_RE = re.compile(r"^\*\((.*?)\)\*\s*$")
ACTOR_RE = re.compile(
    r"\b(SIR PIP|GLOOP|STONE GOLEM BAILIFF|STONE GOLEM|KING GLOOP)\b", re.IGNORECASE
)
PROP_RE = re.compile(
    r"\b(crown|turnip cloth|monocle|clipboard|pauldrons|drawbridge|foreclosure notice|"
    r"rune|stone clipboard|turnips?)\b",
    re.IGNORECASE,
)
CHARACTER_DESCRIPTION_RE = re.compile(
    r"\b(SIR PIP|GLOOP|STONE GOLEM BAILIFF|STONE GOLEM|KING GLOOP)\s*\(([^)]*)\)", re.IGNORECASE
)

# Narrator / documentary-explainer format: "### 00:00 - Title" sections holding
# **[NARRATION]**, **[VISUAL]**, **[ON-SCREEN TEXT]**, **[SOUND]** and
# **[EDITOR NOTE]** blocks.
NARRATOR_SECTION_RE = re.compile(r"^###\s+(\d+):(\d+)\s*[—–-]\s*(.+?)\s*$", re.MULTILINE)
NARRATOR_TAG_RE = re.compile(r"^\*\*\[([A-Z][A-Z ]*)\]\*\*\s*(.*)$", re.MULTILINE)
NARRATOR_FIELD_RE = re.compile(r"^\*\*([^*]+)\*\*:?\s*(.+?)\s*$", re.MULTILINE)
NARRATOR_SCRIPT_HEADING_RE = re.compile(r"^##\s+Script\s*$", re.IGNORECASE | re.MULTILINE)

# Visual-beat separators used to split a single VISUAL direction into shot beats.
NARRATOR_BEAT_SPLIT_RE = re.compile(
    r"(?<=[.;])\s+(?:then|after that|followed by|next|finally)\s+", re.IGNORECASE
)

CHARACTER_CANON = {
    "SIR PIP": "Sir Pip",
    "GLOOP": "Gloop",
    "STONE GOLEM": "Stone Golem",
    "STONE GOLEM BAILIFF": "Stone Golem",
    "KING GLOOP": "King Gloop",
}


def normalize_character(name: str) -> str:
    return CHARACTER_CANON.get(name.upper(), name.title())


def _span(text: str, start: int, end: int) -> dict[str, Any]:
    return {"start": start, "end": end, "text": text[start:end]}


def _line_offsets(text: str) -> list[int]:
    offsets = []
    position = 0
    for line in text.splitlines():
        offsets.append(position)
        position += len(line) + 1
    return offsets


def _find_offset(text: str, needle: str, start: int = 0) -> int:
    index = text.find(needle, start)
    if index < 0:
        raise ValueError(f"Could not locate source excerpt: {needle!r}")
    return index


def _camera_for(block: str, is_establishing: bool) -> tuple[str, str, str]:
    lowered = block.lower()
    if is_establishing:
        return "wide", "eye-level", "establishing shot"
    if any(word in lowered for word in ("close", "glimpse", "detail", "monocle", "crown", "rune")):
        return "close-up", "eye-level", "detail or reaction close-up"
    if any(word in lowered for word in ("nervous", "reaction", "expression", "face", "freezes")):
        return "medium close-up", "eye-level", "reaction medium close-up"
    if any(word in lowered for word in ("awakes", "awakens", "behind the throne", "rises", "enters")):
        return "wide", "low angle", "revealing wide shot"
    return "medium", "eye-level", "medium shot"


def _new_shot(scene: dict[str, Any], block_type: str, is_establishing: bool = False) -> dict[str, Any]:
    return {
        "shot_id": f"SHT_{scene['scene_id']}_{len(scene['shots']) + 1:03d}",
        "purpose": "Action beat" if block_type == "action" else "Dialogue",
        "visual_description": "",
        "environment": scene["location"],
        "characters": [],
        "character_positions": "",
        "character_actions": "",
        "props": [],
        "camera_shot_type": "",
        "camera_angle": "",
        "camera_perspective": "",
        "camera_movement": "",
        "composition": "",
        "foreground": "",
        "middle_ground": "",
        "background": "",
        "lighting": "",
        "weather": "",
        "continuity_refs": [],
        "estimated_duration_sec": 0.0,
        "production_complexity": "LOW",
        "engine_notes": "",
        "source_spans": [],
        "explicit_facts": [],
        "inferred_staging": ["Shot boundaries inferred from screenplay structure."],
        "is_establishing": is_establishing,
        "block_type": block_type,
    }


def _parse_timecode(value: str) -> tuple[float, float] | None:
    """Parse a '0:00 - 0:15' style range into seconds."""
    if not value:
        return None
    numbers = re.findall(r"(\d+):(\d+)", value)
    if len(numbers) < 2:
        return None
    (start_min, start_sec), (end_min, end_sec) = numbers[0], numbers[1]
    start = int(start_min) * 60 + int(start_sec)
    end = int(end_min) * 60 + int(end_sec)
    if end <= start:
        return None
    return float(start), float(end)


def _distribute_durations(sequence: dict[str, Any]) -> None:
    """Spread the sequence timecode across its shots by source-excerpt length."""
    parsed = _parse_timecode(sequence.get("timecode", ""))
    shots = [shot for scene in sequence["scenes"] for shot in scene["shots"]]
    if not shots:
        return
    if parsed is None:
        even = 5.0
        for shot in shots:
            shot["estimated_duration_sec"] = even
            shot["duration_basis"] = "Default planning estimate; sequence timecode unavailable."
        return
    start, end = parsed
    total = end - start
    weights = []
    for shot in shots:
        spans = shot.get("source_spans") or []
        length = sum(span["end"] - span["start"] for span in spans)
        weights.append(max(length, 1))
    weight_sum = sum(weights)
    remaining = total
    for index, shot in enumerate(shots):
        if index == len(shots) - 1:
            value = remaining
        else:
            value = round(total * weights[index] / weight_sum, 2)
            remaining = round(remaining - value, 2)
        shot["estimated_duration_sec"] = value
        shot["duration_basis"] = (
            f"Proportional split of sequence timecode {sequence['timecode']} by source excerpt length."
        )


def detect_format(text: str) -> str:
    """Return 'NARRATOR' for a narrated explainer script, 'SCREENPLAY' otherwise."""
    if NARRATOR_SECTION_RE.search(text) or NARRATOR_TAG_RE.search(text):
        return "NARRATOR"
    return "SCREENPLAY"


NARRATOR_ENVIRONMENT_HINTS: list[tuple[str, str]] = [
    ("streetlamp", "London street at street level"),
    ("street", "London street at street level"),
    ("hospital", "hospital interior and window"),
    ("timeline", "editorial timeline graphic"),
    ("diagram", "explanatory diagram"),
    ("chart", "plain data chart"),
    ("map", "map graphic"),
    ("chimney", "rooftop skyline with chimneys"),
    ("factory", "industrial cityscape"),
    ("bus", "London street with traffic"),
    ("neighbourhood", "London residential street"),
    ("sky", "open sky above the city"),
    ("water droplets", "macro view of fog droplets and smoke particles"),
    ("coal", "coal fire and chimney smoke"),
]


def _narrator_environment(text: str) -> str:
    lowered = text.lower()
    for keyword, label in NARRATOR_ENVIRONMENT_HINTS:
        if keyword in lowered:
            return label
    return ""


def _narrator_camera(text: str) -> tuple[str, str, str]:
    lowered = text.lower()
    if any(word in lowered for word in ("side view", "cross-section", "cutaway")):
        return "wide", "orthographic side view", "explanatory side view"
    if any(word in lowered for word in ("timeline", "chart", "diagram", "map", "graphic")):
        return "wide", "straight-on", "explanatory graphic frame"
    if any(word in lowered for word in ("close", "detail", "macro")):
        return "close-up", "eye-level", "detail close-up"
    if any(word in lowered for word in ("wide", "city", "skyline", "street")):
        return "wide", "eye-level", "wide establishing shot"
    return "medium", "eye-level", "medium shot"


def _narrator_beats(text: str) -> list[str]:
    """Split one visual direction into individual shot beats."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    parts = [part.strip(" .;") for part in NARRATOR_BEAT_SPLIT_RE.split(cleaned)]
    beats = [part for part in parts if len(part) > 12]
    return beats or [cleaned.strip(" .;")]


def parse_narrator_script(
    text: str,
    project_id: str,
    source_sha256: str,
    analysis_id: str | None = None,
) -> dict[str, Any]:
    """Parse a narrated documentary/explainer script into the visual hierarchy.

    Each ``### MM:SS - Title`` section becomes a sequence with one scene. The
    section's ``[VISUAL]`` direction is split into shot beats; ``[ON-SCREEN TEXT]``
    becomes a graphic shot. Narration, sound and editor notes are recorded as
    explicit facts, never as shots.
    """
    lines = text.splitlines()
    offsets = _line_offsets(text)

    title = ""
    metadata: dict[str, str] = {}
    body_start = 0
    body_end = len(text)

    for index, raw in enumerate(lines):
        line = raw.strip()
        if not line:
            continue
        if not title and TITLE_RE.match(line):
            title = TITLE_RE.match(line).group(1)
            continue
        if NARRATOR_SCRIPT_HEADING_RE.match(line):
            body_start = offsets[index] + len(raw)
            for later in range(index + 1, len(lines)):
                if lines[later].strip().startswith("## "):
                    body_end = offsets[later]
                    break
            break
        field = NARRATOR_FIELD_RE.match(line)
        if field:
            key = field.group(1).strip().rstrip(":").strip()
            metadata[key] = field.group(2).strip()

    body = text[body_start:body_end]

    open_questions: list[str] = []
    sequences: list[dict[str, Any]] = []

    section_matches = list(NARRATOR_SECTION_RE.finditer(body))
    if not section_matches:
        raise ValueError("No '### MM:SS - Title' sections found in the narrator script body.")

    target_seconds = _narrator_runtime_seconds(metadata)

    for section_index, section_match in enumerate(section_matches):
        start_seconds = int(section_match.group(1)) * 60 + int(section_match.group(2))
        section_title = section_match.group(3).strip()
        section_body_start = body_start + section_match.end()
        section_body_end = (
            body_start + section_matches[section_index + 1].start()
            if section_index + 1 < len(section_matches)
            else body_end
        )
        section_body = text[section_body_start:section_body_end]

        narration_paragraphs: list[str] = []
        visual_blocks: list[str] = []
        on_screen_texts: list[str] = []
        sound_notes: list[str] = []
        editor_notes: list[str] = []

        current_tag: str | None = None
        current_lines: list[str] = []
        current_start = 0

        def flush_narrator_block() -> None:
            nonlocal current_tag, current_lines
            if current_tag is None:
                current_lines = []
                return
            body_text = " ".join(current_lines).strip()
            if current_tag == "NARRATION":
                for paragraph in re.split(r"\n\s*\n", body_text):
                    cleaned = " ".join(paragraph.split())
                    if cleaned:
                        narration_paragraphs.append(cleaned)
            elif current_tag == "VISUAL":
                if body_text:
                    visual_blocks.append({"text": body_text, "start": current_start})
            elif current_tag == "ON-SCREEN TEXT":
                if body_text:
                    on_screen_texts.append({"text": body_text, "start": current_start})
            elif current_tag == "SOUND":
                if body_text:
                    sound_notes.append(body_text)
            elif current_tag == "EDITOR NOTE":
                if body_text:
                    editor_notes.append(body_text)
            current_tag = None
            current_lines = []

        section_lines = section_body.splitlines()
        section_line_offsets = _line_offsets(section_body)
        for line_index, raw_line in enumerate(section_lines):
            stripped = raw_line.strip()
            tag_match = NARRATOR_TAG_RE.match(stripped)
            if tag_match:
                flush_narrator_block()
                current_tag = tag_match.group(1).strip().upper()
                inline = tag_match.group(2).strip()
                current_lines = [inline] if inline else []
                current_start = section_body_start + section_line_offsets[line_index]
                continue
            if not stripped:
                continue
            if current_tag is not None:
                current_lines.append(stripped)
        flush_narrator_block()

        beats: list[tuple[str, str, int]] = []
        for block in visual_blocks:
            for beat in _narrator_beats(block["text"]):
                beats.append(("VISUAL", beat, block["start"]))
        for overlay in on_screen_texts:
            beats.append(("ON-SCREEN TEXT", " ".join(overlay["text"].split()), overlay["start"]))
        if not beats:
            for paragraph in narration_paragraphs:
                beats.append(("NARRATION", paragraph, section_body_start))

        sequence_id = f"SEQ_{section_index + 1:02d}"
        scene_id = f"SCN_{section_index + 1:02d}_01"
        shots: list[dict[str, Any]] = []

        for beat_index, (beat_kind, beat_text, beat_offset) in enumerate(beats):
            shot_type, angle, composition = (
                _narrator_camera(beat_text)
                if beat_kind == "VISUAL"
                else ("wide", "straight-on", "graphic overlay frame")
            )
            environment = _narrator_environment(beat_text)
            shot_id = f"SHT_{scene_id}_{beat_index + 1:03d}"
            span_start = text.find(beat_text, beat_offset)
            span_end = span_start + len(beat_text)
            if span_start < 0:
                probe = beat_text[:60]
                span_start = text.find(probe, beat_offset)
                span_end = (span_start + len(probe)) if span_start >= 0 else beat_offset
            if span_start < 0:
                span_start = beat_offset
                span_end = min(beat_offset + len(beat_text), len(text))
            shots.append(
                {
                    "shot_id": shot_id,
                    "purpose": f"{section_title} - {beat_kind.lower()} beat",
                    "visual_description": beat_text,
                    "environment": environment,
                    "characters": [],
                    "character_positions": "",
                    "character_actions": "",
                    "props": [],
                    "camera_shot_type": shot_type,
                    "camera_angle": angle,
                    "camera_perspective": "",
                    "camera_movement": "",
                    "composition": composition,
                    "foreground": "",
                    "middle_ground": "",
                    "background": "",
                    "lighting": "",
                    "weather": "",
                    "continuity_refs": [],
                    "estimated_duration_sec": 0.0,
                    "production_complexity": "MEDIUM" if beat_kind == "VISUAL" else "LOW",
                    "engine_notes": "",
                    "source_spans": [_span(text, span_start, min(span_end, len(text)))],
                    "explicit_facts": [f"{beat_kind}: {beat_text}"],
                    "inferred_staging": [
                        f"Camera and composition inferred from the {beat_kind.lower()} direction: {composition}."
                    ],
                    "beat_kind": beat_kind,
                }
            )

        if not environment:
            open_questions.append(
                f"{scene_id} visual direction does not name a location; location is unknown."
            )

        sequences.append(
            {
                "sequence_id": sequence_id,
                "act_label": "",
                "title": section_title,
                "timecode": f"{section_match.group(1)}:{section_match.group(2)}",
                "start_seconds": start_seconds,
                "purpose": f"Narrated segment beginning at {section_match.group(1)}:{section_match.group(2)}.",
                "scenes": [
                    {
                        "scene_id": scene_id,
                        "heading": f"{section_match.group(1)}:{section_match.group(2)} - {section_title}",
                        "int_ext": "NARRATED",
                        "location": environment,
                        "time": "NARRATED SEGMENT",
                        "action": " ".join(beat[1] for beat in beats),
                        "characters": [],
                        "props": [],
                        "source_spans": [
                            _span(
                                text,
                                section_body_start,
                                min(section_body_end, len(text)),
                            )
                        ],
                        "explicit_facts": [
                            f"Narration: {paragraph}" for paragraph in narration_paragraphs
                        ]
                        + [f"Visual: {block}" for block in visual_blocks]
                        + [f"On-screen text: {overlay}" for overlay in on_screen_texts]
                        + [f"Sound: {note}" for note in sound_notes]
                        + [f"Editor note: {note}" for note in editor_notes],
                        "inferred_staging": [],
                        "shots": shots,
                        "start_offset": section_body_start,
                        "implicit": False,
                    }
                ],
                "start_offset": section_body_start,
            }
        )

    # Section end times come from the next section start; the last one runs to the
    # stated target runtime.
    for index, sequence in enumerate(sequences):
        if index + 1 < len(sequences):
            end_seconds = sequences[index + 1]["start_seconds"]
        else:
            end_seconds = target_seconds or (sequence["start_seconds"] + 30)
        end_seconds = int(end_seconds)
        sequence["end_seconds"] = end_seconds
        sequence["timecode"] = (
            f"{sequence['start_seconds'] // 60}:{sequence['start_seconds'] % 60:02d}"
            f"-{end_seconds // 60}:{end_seconds % 60:02d}"
        )
        shots = sequence["scenes"][0]["shots"]
        total = max(end_seconds - sequence["start_seconds"], 1)
        weights = [max(len(shot["visual_description"]), 1) for shot in shots]
        weight_sum = sum(weights) or 1
        remaining = float(total)
        for shot_index, shot in enumerate(shots):
            if shot_index == len(shots) - 1:
                value = remaining
            else:
                value = round(total * weights[shot_index] / weight_sum, 2)
                remaining = round(remaining - value, 2)
            shot["estimated_duration_sec"] = value
            shot["duration_basis"] = (
                f"Proportional split of segment {sequence['timecode']} by direction length."
            )

    target_runtime = 0.0
    for key, value in metadata.items():
        if "duration" in key.lower() or "runtime" in key.lower():
            numbers = re.findall(r"(\d+):(\d+)", value)
            if numbers:
                minutes, seconds = numbers[-1]
                target_runtime = int(minutes) * 60 + int(seconds)

    return {
        "schema_version": "1.0.0",
        "analysis_id": analysis_id or new_id("ANALYSIS"),
        "project_id": project_id,
        "source_script_sha256": source_sha256,
        "created_at": utc_now(),
        "source_format": "NARRATOR",
        "episode": {
            "episode_id": f"EP_{project_id}",
            "title": title,
            "genre": metadata.get("Format", "Narrated documentary"),
            "target_runtime_sec": target_runtime,
            "logline": metadata.get("Opening promise", ""),
        },
        "sequences": sequences,
        "characters": [],
        "open_questions": open_questions,
    }


def _narrator_runtime_seconds(metadata: dict[str, str]) -> float:
    """Best-effort end time for the final narrated segment."""
    for key, value in metadata.items():
        if "runtime" in key.lower() or "duration" in key.lower():
            numbers = re.findall(r"(\d+):(\d+)", value)
            if numbers:
                minutes, seconds = numbers[-1]
                return float(int(minutes) * 60 + int(seconds))
    return 0.0


def parse_script(
    text: str,
    project_id: str,
    source_sha256: str,
    analysis_id: str | None = None,
) -> dict[str, Any]:
    """Parse a script of either supported format into the visual hierarchy.

    Format is detected from the source text: a narrated explainer uses
    ``### MM:SS - Title`` sections with ``[NARRATION]`` / ``[VISUAL]`` blocks; a
    screenplay uses act and scene headings.
    """
    if detect_format(text) == "NARRATOR":
        return parse_narrator_script(text, project_id, source_sha256, analysis_id)
    return parse_screenplay_script(text, project_id, source_sha256, analysis_id)


def parse_screenplay_script(
    text: str,
    project_id: str,
    source_sha256: str,
    analysis_id: str | None = None,
) -> dict[str, Any]:
    """Parse a screenplay into episode -> sequence -> scene -> shot records.

    The parser is deterministic and rule-based. Camera and staging choices are
    recorded as inferred staging, never as explicit script facts. Missing scene
    headings produce an implicit scene plus an open question rather than an
    invented location.
    """
    lines = text.splitlines()
    offsets = _line_offsets(text)

    title = ""
    metadata: dict[str, str] = {}
    acts: list[dict[str, Any]] = []
    open_questions: list[str] = []
    character_registry: dict[str, dict[str, Any]] = {}

    for description_match in CHARACTER_DESCRIPTION_RE.finditer(text):
        name = normalize_character(description_match.group(1))
        if name not in character_registry:
            character_registry[name] = {
                "name": name,
                "description": description_match.group(2).strip(),
                "source_spans": [
                    _span(text, description_match.start(), description_match.end())
                ],
            }

    current_act: dict[str, Any] | None = None
    current_scene: dict[str, Any] | None = None
    current_block: dict[str, Any] | None = None
    block_lines: list[str] = []
    block_start = 0

    def flush_block() -> None:
        nonlocal current_block, block_lines
        if current_block is None or not block_lines:
            current_block = None
            block_lines = []
            return
        content = " ".join(block_lines).strip()
        current_block["visual_description"] = content.strip("* ")
        start = block_start
        end = _find_offset(text, block_lines[0], start) + sum(
            len(line) + 1 for line in block_lines
        )
        current_block["source_spans"] = [_span(text, start, min(end, len(text)))]
        if current_scene is not None:
            shot_type, angle, composition = _camera_for(
                content, current_block.get("is_establishing", False)
            )
            current_block["camera_shot_type"] = shot_type
            current_block["camera_angle"] = angle
            current_block["composition"] = composition
            current_block["inferred_staging"].append(
                f"Camera/staging inferred from content: {composition}."
            )
            current_scene["shots"].append(current_block)
        current_block = None
        block_lines = []

    for index, raw in enumerate(lines):
        line = raw.strip()
        offset = offsets[index]

        if not line:
            continue

        title_match = TITLE_RE.match(line)
        if title_match and not title:
            title = title_match.group(1)
            continue

        metadata_match = METADATA_RE.match(line)
        if metadata_match and not acts:
            key = metadata_match.group(1).strip()
            value = metadata_match.group(2).strip()
            segments = [segment.strip() for segment in value.split("|")]
            metadata[key] = segments[0]
            for segment in segments[1:]:
                segment_match = METADATA_SEGMENT_RE.match(segment)
                if segment_match:
                    metadata[segment_match.group(1).strip()] = segment_match.group(2).strip()
            continue

        act_match = ACT_RE.match(line)
        if act_match:
            flush_block()
            current_scene = None
            current_act = {
                "sequence_id": f"SEQ_{len(acts) + 1:02d}",
                "act_label": act_match.group(1).upper(),
                "title": act_match.group(2).strip(),
                "timecode": (act_match.group(3) or "").strip(),
                "purpose": "",
                "scenes": [],
                "start_offset": offset,
            }
            acts.append(current_act)
            continue

        scene_match = SCENE_RE.match(line)
        if scene_match and current_act is not None:
            flush_block()
            current_scene = {
                "scene_id": f"SCN_{current_act['sequence_id'].split('_')[-1]}_{len(current_act['scenes']) + 1:02d}",
                "heading": line.strip("* ").strip(),
                "int_ext": scene_match.group(1).upper(),
                "location": scene_match.group(2).strip(),
                "time": "",
                "action": "",
                "characters": [],
                "props": [],
                "source_spans": [],
                "explicit_facts": [],
                "inferred_staging": [],
                "shots": [],
                "start_offset": offset,
                "implicit": False,
            }
            parts = [part.strip() for part in current_scene["location"].split("-")]
            if len(parts) > 1:
                current_scene["location"] = parts[0].strip()
                current_scene["time"] = "-".join(parts[1:]).strip()
            current_act["scenes"].append(current_scene)
            current_scene["source_spans"] = [_span(text, offset, offset + len(raw))]
            continue

        if current_act is None:
            continue

        if current_scene is None:
            current_scene = {
                "scene_id": f"SCN_{current_act['sequence_id'].split('_')[-1]}_{len(current_act['scenes']) + 1:02d}",
                "heading": "",
                "int_ext": "INT.",
                "location": "",
                "time": "",
                "action": "",
                "characters": [],
                "props": [],
                "source_spans": [],
                "explicit_facts": [],
                "inferred_staging": ["No scene heading in source; scene inferred from act context."],
                "shots": [],
                "start_offset": offset,
                "implicit": True,
            }
            current_act["scenes"].append(current_scene)
            open_questions.append(
                f"{current_act['sequence_id']} has no scene heading; location and time are unknown."
            )

        char_match = CHAR_RE.match(line)
        if char_match:
            flush_block()
            name = normalize_character(char_match.group(1).strip())
            if name not in current_scene["characters"]:
                current_scene["characters"].append(name)
            current_block = _new_shot(current_scene, "dialogue")
            current_block["purpose"] = f"Dialogue: {name}"
            current_block["characters"] = [name]
            current_block["explicit_facts"] = [f"Character speaks: {name}"]
            block_lines = []
            block_start = offset
            continue

        if PAREN_RE.match(line):
            continue

        if current_block is None:
            current_block = _new_shot(
                current_scene, "action", is_establishing=len(current_scene["shots"]) == 0
            )
            block_lines = []
            block_start = offset

        block_lines.append(line)
        content = " ".join(block_lines).strip("* ")
        # Only action blocks establish who is present; dialogue mentions are not
        # automatically treated as characters on screen.
        if current_block["block_type"] == "action":
            found_chars = [normalize_character(match.group(1)) for match in ACTOR_RE.finditer(content)]
            for name in found_chars:
                if name not in current_block["characters"]:
                    current_block["characters"].append(name)
                if name not in current_scene["characters"]:
                    current_scene["characters"].append(name)
            found_props = [match.group(1).lower() for match in PROP_RE.finditer(content)]
            for prop in found_props:
                if prop not in current_block["props"]:
                    current_block["props"].append(prop)
                if prop not in current_scene["props"]:
                    current_scene["props"].append(prop)
        if current_block["block_type"] == "dialogue":
            # A dialogue block is a line somebody says, not action. Keeping the
            # speaker and the words separately is what lets an animatic put
            # the right voice on the right board.
            current_block["dialogue"] = content
            current_block["explicit_facts"] = [
                fact
                for fact in current_block["explicit_facts"]
                if fact.startswith("Character speaks")
            ] + [f"Dialogue: {content}"]
        else:
            current_block["explicit_facts"] = ["Action text: " + content]

    flush_block()

    for act in acts:
        _distribute_durations(act)
        for scene in act["scenes"]:
            scene["action"] = " ".join(
                shot["visual_description"] for shot in scene["shots"]
            ).strip()
            scene["explicit_facts"].extend(
                fact for shot in scene["shots"] for fact in shot["explicit_facts"]
            )
            scene["explicit_facts"] = list(dict.fromkeys(scene["explicit_facts"]))
            scene["inferred_staging"] = list(
                dict.fromkeys(
                    note for shot in scene["shots"] for note in shot["inferred_staging"]
                )
            )
            for shot in scene["shots"]:
                shot.pop("block_type", None)
                shot.pop("is_establishing", None)

    target_runtime = 0.0
    for key, value in metadata.items():
        if "runtime" in key.lower():
            match = re.search(r"(\d+)", value)
            if match:
                target_runtime = float(match.group(1))

    genre = metadata.get("Genre", "")
    if "|" in genre:
        genre = genre.split("|")[0].strip()

    return {
        "schema_version": "1.0.0",
        "analysis_id": analysis_id or new_id("ANALYSIS"),
        "project_id": project_id,
        "source_script_sha256": source_sha256,
        "created_at": utc_now(),
        "source_format": "SCREENPLAY",
        "episode": {
            "episode_id": f"EP_{project_id}",
            "title": title,
            "genre": genre,
            "target_runtime_sec": target_runtime,
            "logline": metadata.get("Tone", ""),
        },
        "sequences": acts,
        "characters": list(character_registry.values()),
        "open_questions": open_questions,
    }
