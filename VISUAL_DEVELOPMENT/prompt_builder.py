from __future__ import annotations

from typing import Any

from .art_direction import COMPARISON_NEGATIVE_PROMPT

SHOT_NEGATIVES = [
    "duplicate character",
    "crowd",
    "floating objects",
    "inconsistent lighting direction",
]

BLOCKING_NEGATIVES = [
    "text overlay",
    "annotation labels",
    "photorealistic skin",
    "busy background",
]


def _join(parts: list[str]) -> str:
    return ", ".join(part.strip().rstrip(",") for part in parts if part and part.strip())


def _character_descriptions(
    shot: dict[str, Any], character_index: dict[str, dict[str, Any]]
) -> list[str]:
    descriptions = []
    for name in shot.get("characters", []):
        entry = character_index.get(name)
        if entry and entry.get("description"):
            descriptions.append(f"{name} ({entry['description']})")
        else:
            descriptions.append(name)
    return descriptions


def build_shot_prompt(
    style_bible: dict[str, Any],
    shot: dict[str, Any],
    scene: dict[str, Any],
    character_index: dict[str, dict[str, Any]] | None = None,
    mode: str = "storyboard",
) -> dict[str, Any]:
    """Compose a modular prompt from the Style Bible and the structured shot spec.

    The structured shot specification is preserved separately in the returned
    ``shot_spec`` so a reviewer can always read what the image was asked to show.
    """
    character_index = character_index or {}
    rules = style_bible["global_rules"]

    style = list(rules.get("positive_prompt", []))
    if mode == "blocking":
        style = [
            "production blocking reference render",
            "previs staging view",
            "clean readable staging",
            *style,
        ]

    scene_context = [
        scene.get("heading") or f"scene {scene.get('scene_id', '')}",
        scene.get("time") or "",
    ]
    environment = [
        scene.get("location") or "",
        "mossy gothic throne room with arched stone windows" if not scene.get("location") else "",
    ]
    characters = _character_descriptions(shot, character_index)
    action = [shot.get("visual_description", ""), shot.get("character_actions", "")]
    objects = [", ".join(shot.get("props", []))]
    camera = [
        shot.get("camera_shot_type", ""),
        shot.get("camera_angle", ""),
        shot.get("camera_perspective", ""),
        shot.get("camera_movement", ""),
    ]
    composition = [
        shot.get("composition", ""),
        f"foreground: {shot['foreground']}" if shot.get("foreground") else "",
        f"middle ground: {shot['middle_ground']}" if shot.get("middle_ground") else "",
        f"background: {shot['background']}" if shot.get("background") else "",
    ]
    lighting = [rules.get("lighting", ""), shot.get("lighting", ""), shot.get("weather", "")]
    atmosphere = [rules.get("atmosphere", ""), rules.get("materials", "")]

    modules = {
        "style": _join(style),
        "scene_context": _join(scene_context),
        "environment": _join(environment),
        "characters": _join(characters),
        "action": _join(action),
        "objects": _join(objects),
        "camera": _join(camera),
        "composition": _join(composition),
        "lighting": _join(lighting),
        "atmosphere": _join(atmosphere),
        "emphasis": shot.get("purpose", ""),
    }

    negative_base = list(rules.get("negative_prompt", []))
    negative = _join(negative_base + (BLOCKING_NEGATIVES if mode == "blocking" else SHOT_NEGATIVES))

    return {
        "prompt": _join([value for value in modules.values() if value]),
        "negative_prompt": negative,
        "modules": modules,
        "mode": mode,
        "shot_spec": shot,
    }


def build_candidate_prompt(
    style_prompt: str,
    comparison_scene: dict[str, Any],
    character_index: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build the shared comparison prompt used for every art-direction candidate.

    The prompt deliberately describes a single concrete frame rather than the whole
    scene action. A multi-sentence direction makes the model produce a split-panel
    layout, which would make the candidates differ by composition instead of by
    direction and would waste the image resolution.
    """
    from .art_direction import SINGLE_FRAME_CONSTRAINT, comparison_subject

    character_index = character_index or {}
    characters = [
        f"{name} ({entry['description']})" if entry.get("description") else name
        for name, entry in character_index.items()
        if name in comparison_scene.get("characters", [])
    ]
    modules = {
        "style": style_prompt,
        "scene_context": comparison_scene.get("heading", ""),
        "environment": comparison_scene.get("location", ""),
        "characters": _join(characters),
        "action": comparison_subject(comparison_scene),
        "objects": ", ".join(comparison_scene.get("props", [])),
        "camera": "wide establishing composition",
        "composition": "readable foreground, middle ground and background separation",
        "lighting": "motivated cinematic key light",
        "atmosphere": "storybook production concept art",
        "emphasis": SINGLE_FRAME_CONSTRAINT,
    }
    return {
        "prompt": _join([value for value in modules.values() if value]),
        "negative_prompt": COMPARISON_NEGATIVE_PROMPT,
        "modules": modules,
    }
