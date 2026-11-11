from __future__ import annotations

from typing import Any

from .common import new_id, utc_now

NOMINAL_FOCAL_LENGTH_MM = {
    "wide": 24.0,
    "medium wide": 35.0,
    "medium": 40.0,
    "medium close-up": 50.0,
    "close-up": 85.0,
    "extreme close-up": 100.0,
}

GENERATION_RESOLUTION = "768x768"
GENERATION_FPS = 24


def _focal_length(shot_size: str) -> float:
    return NOMINAL_FOCAL_LENGTH_MM.get((shot_size or "medium").lower(), 40.0)


def _scene_projection(scene: dict[str, Any], sequence: dict[str, Any]) -> dict[str, Any]:
    shots = scene["shots"]
    duration = round(sum(shot.get("estimated_duration_sec", 0.0) for shot in shots), 2)
    return {
        "scene_id": scene["scene_id"],
        "project_id": sequence.get("project_id", ""),
        "title": scene.get("heading") or scene["scene_id"],
        "location_id": scene.get("location") or "UNSPECIFIED",
        "characters": scene.get("characters", []),
        "required_assets": scene.get("props", []),
        "duration_sec": duration,
        "animation_method": "3D",
        "required_shots": [shot["shot_id"] for shot in shots],
        "camera_requirements": scene.get("camera_requirements", ""),
        "audio_dependencies": [],
        "lighting": style_lighting(scene),
        "vfx": [],
        "production_dependencies": [],
        "notes": scene.get("inferred_staging", []),
    }


def style_lighting(scene: dict[str, Any]) -> str:
    if scene.get("time"):
        return f"Time of day: {scene['time']}"
    return "Time of day unspecified in source; requires a human decision."


def _shot_projection(shot: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    return {
        "shot_id": shot["shot_id"],
        "scene_id": scene["scene_id"],
        "camera_angle": shot.get("camera_angle", ""),
        "shot_size": shot.get("camera_shot_type", "medium"),
        "camera_position": shot.get("character_positions", ""),
        "camera_movement": shot.get("camera_movement", ""),
        "focal_length_mm": _focal_length(shot.get("camera_shot_type", "medium")),
        "character_placement": shot.get("character_positions", ""),
        "character_movement": shot.get("character_actions", ""),
        "facial_expression": "",
        "lighting": shot.get("lighting", ""),
        "audio_cues": [],
        "duration_sec": shot.get("estimated_duration_sec", 0.0),
        "fps": GENERATION_FPS,
        "resolution": GENERATION_RESOLUTION,
        "required_assets": shot.get("props", []),
        "engine_notes": shot.get("engine_notes", ""),
        "focal_length_note": (
            "Nominal planning equivalent of the shot size, not a measured lens value."
        ),
        "source_spans": shot.get("source_spans", []),
        "purpose": shot.get("purpose", ""),
        "visual_description": shot.get("visual_description", ""),
        "production_complexity": shot.get("production_complexity", "LOW"),
    }


def build_handoff(
    analysis: dict[str, Any],
    style_bible: dict[str, Any],
    generations: list[dict[str, Any]],
    review_events: list[dict[str, Any]],
    source_script_ref: dict[str, Any],
    continuity_report: dict[str, Any] | None = None,
    breakdown: dict[str, Any] | None = None,
    prompt_overrides: dict[str, Any] | None = None,
    animatic: dict[str, Any] | None = None,
    shot_statuses: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build the structured production handoff package.

    The package answers three questions for whoever receives it: what was
    asked for (the breakdown and the shot list), what was decided (the
    selected direction and the prompt overrides), and what came out (the
    approved images with their provenance and the status of every shot).
    """
    approved_generations = [
        generation
        for generation in generations
        if generation.get("review_status") == "APPROVED"
    ]
    storyboard_images = [
        generation for generation in approved_generations if generation.get("artifact_type") == "STORYBOARD"
    ]
    blocking_images = [
        generation for generation in approved_generations if generation.get("artifact_type") == "BLOCKING"
    ]

    unresolved: list[str] = list(analysis.get("open_questions", []))
    source_approved = source_script_ref.get("approval_status") == "APPROVED"
    if not source_approved:
        unresolved.insert(
            0,
            "Source script approval status is "
            f"{source_script_ref.get('approval_status')!r}, not 'APPROVED'. This package is "
            "an exploration artifact and is not production-ready.",
        )
    if continuity_report:
        for check in continuity_report.get("checks", []):
            if check["status"] in {"FAIL", "REVIEW"}:
                unresolved.append(f"{check['check_id']}: {check['message']}")

    sequences_out = []
    for sequence in analysis["sequences"]:
        scenes_out = []
        for scene in sequence["scenes"]:
            shots_out = [_shot_projection(shot, scene) for shot in scene["shots"]]
            scenes_out.append(
                {
                    "sequence_id": sequence["sequence_id"],
                    "sequence_title": sequence["title"],
                    "sequence_purpose": sequence.get("purpose", ""),
                    "scene_id": scene["scene_id"],
                    "heading": scene.get("heading", ""),
                    "location": scene.get("location", ""),
                    "time": scene.get("time", ""),
                    "characters": scene.get("characters", []),
                    "props": scene.get("props", []),
                    "explicit_facts": scene.get("explicit_facts", []),
                    "inferred_staging": scene.get("inferred_staging", []),
                    "source_spans": scene.get("source_spans", []),
                    "shots": shots_out,
                    "scene_projection": _scene_projection(scene, sequence),
                    "blocking_layouts": [
                        generation.get("blocking_layout")
                        for generation in blocking_images
                        if generation.get("shot_id") == (scene["shots"][0]["shot_id"] if scene["shots"] else "")
                    ],
                }
            )
        sequences_out.append(
            {
                "sequence_id": sequence["sequence_id"],
                "act_label": sequence.get("act_label", ""),
                "title": sequence["title"],
                "timecode": sequence.get("timecode", ""),
                "scenes": scenes_out,
            }
        )

    return {
        "schema_version": "1.0.0",
        "package_id": new_id("HANDOFF"),
        "created_at": utc_now(),
        "project_id": analysis["project_id"],
        "episode": analysis["episode"],
        "source_script": source_script_ref,
        "style_bible": {
            "style_bible_id": style_bible["style_bible_id"],
            "version": style_bible["version"],
            "status": style_bible["status"],
            "style_identity": style_bible["style_identity"],
            "global_rules": style_bible["global_rules"],
            "scene_variables": style_bible["scene_variables"],
            "reference_images": style_bible.get("reference_images", []),
        },
        "characters": analysis.get("characters", []),
        "sequences": sequences_out,
        "approved_storyboard_images": storyboard_images,
        "approved_blocking_images": blocking_images,
        "character_reference_sheets": [],
        "environment_reference_sheets": [],
        "prop_references": sorted(
            {prop for sequence in analysis["sequences"] for scene in sequence["scenes"] for prop in scene.get("props", [])}
        ),
        "camera_notes": [
            "Camera intent only. No validated 3D camera transform is produced by this module."
        ],
        "lighting_notes": [
            style_bible["global_rules"].get("lighting", ""),
            style_bible["global_rules"].get("atmosphere", ""),
        ],
        "animation_requirements": [
            "Rig and animation are produced in the 3D stage; this package supplies shot intent only."
        ],
        "environment_construction_requirements": [
            "Environment geometry, scale and layout are constructed manually from the storyboard "
            "and the normalized blocking layout.",
        ],
        "production_complexity": [
            {
                "shot_id": shot["shot_id"],
                "complexity": shot.get("production_complexity", "LOW"),
            }
            for sequence in analysis["sequences"]
            for scene in sequence["scenes"]
            for shot in scene["shots"]
        ],
        "unresolved_issues": unresolved,
        "review_events": review_events,
        "continuity_report": continuity_report,
        "breakdown": breakdown or {},
        "prompt_overrides": prompt_overrides or {},
        "shot_statuses": shot_statuses or {},
        "animatic": animatic or {},
        "engine_notes": {
            "coordinate_space": "NONE",
            "world_coordinates": False,
            "scale": "UNSPECIFIED",
            "source_script_approved": source_approved,
            "statement": (
                "This package contains shot intent, references and normalized staging only. "
                "It contains no Blender or Unreal scene, no measured coordinates and no scale."
            ),
        },
    }


def render_handoff_markdown(handoff: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# Production Handoff - {handoff['episode'].get('title', handoff['project_id'])}")
    lines.append("")
    lines.append(f"- **Package ID:** `{handoff['package_id']}`")
    lines.append(f"- **Project:** `{handoff['project_id']}`")
    lines.append(
        f"- **Style:** {handoff['style_bible']['style_identity']} "
        f"(Style Bible v{handoff['style_bible']['version']}, {handoff['style_bible']['status']})"
    )
    lines.append(f"- **Created:** {handoff['created_at']}")
    lines.append("")
    lines.append("> This package is shot intent and references. It is not a 3D scene and contains "
                 "no measured coordinates or scale.")
    lines.append("")
    lines.append("## Source script")
    lines.append("")
    source = handoff["source_script"]
    lines.append(f"- Script ID: `{source.get('script_id')}`")
    lines.append(f"- Approval status: `{source.get('approval_status')}`")
    lines.append(f"- SHA-256: `{source.get('sha256')}`")
    lines.append("")
    lines.append("## Sequence, scene and shot breakdown")
    lines.append("")
    for sequence in handoff["sequences"]:
        lines.append(f"### {sequence['sequence_id']} - {sequence['title']} ({sequence['timecode']})")
        lines.append("")
        for scene in sequence["scenes"]:
            lines.append(f"#### {scene['scene_id']} - {scene['heading'] or 'location unspecified'}")
            lines.append("")
            lines.append(f"- Characters: {', '.join(scene['characters']) or 'none identified'}")
            lines.append(f"- Props: {', '.join(scene['props']) or 'none identified'}")
            if scene.get("inferred_staging"):
                lines.append(f"- Inferred staging: {'; '.join(scene['inferred_staging'])}")
            lines.append("")
            lines.append("| Shot | Size | Purpose | Duration | Description |")
            lines.append("|---|---|---|---|---|")
            for shot in scene["shots"]:
                description = shot["visual_description"].replace("|", "/")
                lines.append(
                    f"| {shot['shot_id']} | {shot['shot_size']} | {shot['purpose']} | "
                    f"{shot['duration_sec']}s | {description} |"
                )
            lines.append("")
    lines.append("## Approved images")
    lines.append("")
    for generation in handoff["approved_storyboard_images"]:
        lines.append(f"- Storyboard {generation.get('shot_id')}: `{generation.get('image_path')}`")
    for generation in handoff["approved_blocking_images"]:
        lines.append(f"- Blocking {generation.get('shot_id')}: `{generation.get('image_path')}`")
    if not handoff["approved_storyboard_images"] and not handoff["approved_blocking_images"]:
        lines.append("- No images are approved yet. Every generated image is a draft until a human decides.")
    lines.append("")

    breakdown = handoff.get("breakdown") or {}
    if breakdown.get("scenes"):
        lines.append("## Script breakdown")
        lines.append("")
        summary = breakdown.get("summary", {})
        lines.append(
            f"{summary.get('scene_count', 0)} scenes, {summary.get('element_count', 0)} elements, "
            f"{summary.get('total_page_eighths', 0)} eighths of a page."
        )
        lines.append("")
        for scene in breakdown["scenes"]:
            lines.append(f"### {scene['scene_id']} - {scene['heading']}")
            lines.append("")
            if scene["elements"]:
                lines.append("| Category | Element | Qty | Status | Source |")
                lines.append("|---|---|---|---|---|")
                for element in scene["elements"]:
                    lines.append(
                        f"| {element['category']} | {element['name']} | {element['quantity']} | "
                        f"{element['status']} | {element['source']} |"
                    )
                lines.append("")
            else:
                lines.append("- No elements tagged in this scene.")
                lines.append("")

    overrides = handoff.get("prompt_overrides") or {}
    if overrides:
        lines.append("## Prompt overrides")
        lines.append("")
        lines.append("These targets were generated from a prompt the user wrote, not from the "
                     "generated one alone.")
        lines.append("")
        for target_id, override in sorted(overrides.items()):
            lines.append(f"### {target_id} ({override.get('kind', '')})")
            lines.append("")
            if override.get("prompt_extra"):
                lines.append(f"- Added text: {override['prompt_extra']}")
            if override.get("prompt_replace"):
                lines.append(f"- Replaced the prompt with: {override['prompt_replace']}")
            if override.get("negative_extra"):
                lines.append(f"- Added negative text: {override['negative_extra']}")
            if override.get("exclude_modules"):
                lines.append(f"- Dropped modules: {', '.join(override['exclude_modules'])}")
            if override.get("settings_override"):
                lines.append(
                    f"- Settings: "
                    + ", ".join(f"{k}={v}" for k, v in override["settings_override"].items())
                )
            if override.get("workflow_id"):
                lines.append(f"- ComfyUI workflow: `{override['workflow_id']}`")
            lines.append(f"- By {override.get('actor', 'unknown')} on {override.get('updated_at', '')}")
            lines.append("")

    statuses = handoff.get("shot_statuses") or {}
    if statuses:
        lines.append("## Shot status")
        lines.append("")
        lines.append("| Shot | Status |")
        lines.append("|---|---|")
        for shot_id, status in sorted(statuses.items()):
            lines.append(f"| {shot_id} | {status} |")
        lines.append("")

    animatic = handoff.get("animatic") or {}
    if animatic:
        lines.append("## Animatic")
        lines.append("")
        summary = animatic.get("summary", {})
        lines.append(f"- Video: `{animatic.get('video_path') or 'not rendered'}`")
        lines.append(f"- Shots: {summary.get('shot_count', 0)}")
        lines.append(f"- Duration: {summary.get('total_duration_sec', 0)}s")
        lines.append(f"- Voice lines: {summary.get('voice_line_count', 0)}")
        lines.append("")

    lines.append("## Unresolved issues")
    lines.append("")
    if handoff["unresolved_issues"]:
        for issue in handoff["unresolved_issues"]:
            lines.append(f"- {issue}")
    else:
        lines.append("- None recorded.")
    lines.append("")
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + "\n"
