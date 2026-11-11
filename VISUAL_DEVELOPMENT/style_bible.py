from __future__ import annotations

from typing import Any

from .common import new_id, sha256_text, utc_now

DEFAULT_GENERATION_SETTINGS: dict[str, Any] = {
    "model": "dreamshaper_8.safetensors",
    "lora": "arcane_offset.safetensors",
    "lora_strength": 0.65,
    "width": 768,
    "height": 768,
    "steps": 25,
    "cfg": 8.0,
    "sampler": "euler",
    "scheduler": "simple",
    "seed": 536354036775427,
}


def build_style_bible(
    candidate_set: dict[str, Any],
    candidate_id: str,
    project_id: str,
    version: int = 1,
) -> dict[str, Any]:
    """Create a versioned Style Bible from a human-selected candidate."""
    candidate = None
    for entry in candidate_set["candidates"]:
        if entry["candidate_id"] == candidate_id:
            candidate = entry
            break
    if candidate is None:
        raise ValueError(f"Unknown candidate_id: {candidate_id!r}")
    if not candidate.get("selected"):
        raise ValueError(
            f"Candidate {candidate_id!r} is not selected; a human must select it first."
        )

    global_rules = {
        "visual_principles": [
            candidate["description"],
            candidate["storytelling"],
        ],
        "color_palette": candidate["palette"],
        "materials": candidate["materials"],
        "geometry": candidate["geometry"],
        "character_design": candidate["character_design"],
        "environment_design": candidate["environment"],
        "lighting": candidate["lighting"],
        "camera_language": candidate["camera"],
        # Composition and atmosphere must carry their own direction. Copying the
        # camera and lighting text into them produced a Style Bible where two
        # rules repeated two others and carried no information.
        "composition": candidate.get("composition")
        or "Framing follows the camera language above; keep the subject readable and the beat legible.",
        "atmosphere": candidate.get("atmosphere")
        or "Mood follows the lighting direction above; keep it consistent across shots.",
        "accuracy_requirements": (
            "Preserve script-specified character identity, clothing, props and location. "
            "Do not invent story facts."
        ),
        "restrictions": [
            "Do not change character identity, clothing or proportions between shots.",
            "Do not introduce locations, props or characters absent from the script.",
            "Do not present inferred staging as explicit script fact.",
        ],
        "positive_prompt": [
            candidate["style_prompt"],
            "consistent character identity",
            "coherent environment design",
            "clear composition",
        ],
        "negative_prompt": [
            "extra characters",
            "inconsistent character design",
            "changing outfit",
            "unreadable composition",
            "watermark",
            "text",
            "logo",
            "low resolution",
            "blurry",
            "poor anatomy",
            "extra limbs",
            "missing hands",
            "cropped subject",
        ],
        "generation_settings": dict(DEFAULT_GENERATION_SETTINGS),
    }

    return {
        "schema_version": "1.0.0",
        "style_bible_id": new_id("STYLE"),
        "project_id": project_id,
        "candidate_id": candidate_id,
        "version": version,
        "status": "DRAFT",
        "created_at": utc_now(),
        "style_identity": candidate["style_name"],
        "global_rules": global_rules,
        "scene_variables": {
            "location": "per scene",
            "time": "per scene",
            "weather": "per scene",
            "action": "per shot",
            "lighting_conditions": "per scene",
            "camera_angle": "per shot",
        },
        "reference_images": [],
    }


def style_bible_hash(style_bible: dict[str, Any]) -> str:
    """Stable hash of the immutable global rules and identity."""
    payload = {
        "style_identity": style_bible["style_identity"],
        "global_rules": style_bible["global_rules"],
        "version": style_bible["version"],
    }
    return sha256_text(repr(payload))


def revise_style_bible(
    style_bible: dict[str, Any],
    global_rule_changes: dict[str, Any],
    scene_variable_changes: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new version; the previous version remains immutable."""
    new_version = style_bible["version"] + 1
    new_rules = dict(style_bible["global_rules"])
    for key, value in global_rule_changes.items():
        if key not in new_rules:
            raise ValueError(f"Unknown global rule: {key!r}")
        new_rules[key] = value
    new_variables = dict(style_bible["scene_variables"])
    if scene_variable_changes:
        new_variables.update(scene_variable_changes)
    return {
        **style_bible,
        "style_bible_id": new_id("STYLE"),
        "version": new_version,
        "status": "DRAFT",
        "created_at": utc_now(),
        "global_rules": new_rules,
        "scene_variables": new_variables,
    }
