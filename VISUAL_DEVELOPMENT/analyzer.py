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


def parse_script(
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
