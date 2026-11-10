from __future__ import annotations

from typing import Any


def _check(check_id: str, status: str, message: str, details: Any = None) -> dict[str, Any]:
    return {"check_id": check_id, "status": status, "message": message, "details": details}


def validate_continuity(
    analysis: dict[str, Any],
    style_bible: dict[str, Any],
    generations: list[dict[str, Any]],
    source_script_sha256: str,
) -> dict[str, Any]:
    """Run deterministic continuity checks over the analysis and generation metadata.

    Visual identity between images is not asserted here: it is reported as
    NOT_CHECKED because no validated vision comparison model is available.
    """
    checks: list[dict[str, Any]] = []

    shot_ids: list[str] = []
    scenes: list[dict[str, Any]] = []
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            scenes.append(scene)
            for shot in scene["shots"]:
                shot_ids.append(shot["shot_id"])

    duplicates = sorted({shot_id for shot_id in shot_ids if shot_ids.count(shot_id) > 1})
    checks.append(
        _check(
            "shot_ids_unique",
            "FAIL" if duplicates else "PASS",
            "Every shot identifier is unique." if not duplicates else f"Duplicate shot ids: {duplicates}",
            {"duplicates": duplicates, "shot_count": len(shot_ids)},
        )
    )

    missing_reference = [
        scene["scene_id"]
        for scene in scenes
        for shot in scene["shots"]
        if not shot.get("source_spans")
    ]
    checks.append(
        _check(
            "shot_script_reference",
            "FAIL" if missing_reference else "PASS",
            "Every shot traces back to a screenplay passage."
            if not missing_reference
            else f"Shots without a source reference: {missing_reference}",
            {"missing": missing_reference},
        )
    )

    unknown_characters: dict[str, list[str]] = {}
    known = {entry["name"] for entry in analysis.get("characters", [])}
    for scene in scenes:
        for shot in scene["shots"]:
            for name in shot.get("characters", []):
                if name not in known:
                    unknown_characters.setdefault(name, []).append(shot["shot_id"])
    checks.append(
        _check(
            "character_identity_known",
            "FAIL" if unknown_characters else "PASS",
            "All shot characters are described in the script."
            if not unknown_characters
            else "Characters used in shots but not described in the script.",
            {"unknown": unknown_characters},
        )
    )

    scene_location_changes = []
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            if scene.get("implicit"):
                scene_location_changes.append(
                    {
                        "scene_id": scene["scene_id"],
                        "issue": "Scene heading missing in source; location and time unknown.",
                    }
                )
    checks.append(
        _check(
            "scene_location_continuity",
            "REVIEW" if scene_location_changes else "PASS",
            "All scenes declare a location."
            if not scene_location_changes
            else "Scenes without an explicit location need a human decision.",
            {"scenes": scene_location_changes},
        )
    )

    stale = []
    for generation in generations:
        if generation.get("source_script_sha256") not in (None, source_script_sha256):
            stale.append(
                {
                    "generation_id": generation.get("generation_id"),
                    "reason": "source script changed",
                }
            )
    checks.append(
        _check(
            "source_hash_current",
            "FAIL" if stale else "PASS",
            "Every generated image was produced from the current screenplay."
            if not stale
            else "Generated images were produced from a different screenplay revision.",
            {"stale": stale},
        )
    )

    style_hash = style_bible.get("style_bible_sha256")
    stale_style = []
    for generation in generations:
        recorded = generation.get("style_bible_sha256")
        if recorded and style_hash and recorded != style_hash:
            stale_style.append(
                {
                    "generation_id": generation.get("generation_id"),
                    "reason": "style bible version changed",
                }
            )
    checks.append(
        _check(
            "style_version_current",
            "FAIL" if stale_style else "PASS",
            "Every generated image matches the current Style Bible version."
            if not stale_style
            else "Generated images were produced under a different Style Bible version.",
            {"stale": stale_style},
        )
    )

    missing_metadata = [
        generation.get("generation_id")
        for generation in generations
        if not generation.get("prompt")
        or generation.get("seed") is None
        or not generation.get("model")
        or not generation.get("workflow_id")
    ]
    checks.append(
        _check(
            "generation_metadata_complete",
            "FAIL" if missing_metadata else "PASS",
            "Every generated image records prompt, model, seed and workflow."
            if not missing_metadata
            else "Generated images are missing reproducibility metadata.",
            {"missing": missing_metadata},
        )
    )

    checks.append(
        _check(
            "visual_identity_between_images",
            "NOT_CHECKED",
            "Visual identity, clothing and palette consistency between images require human "
            "comparison; no validated vision comparison model is configured.",
            None,
        )
    )

    failed = [check for check in checks if check["status"] == "FAIL"]
    review = [check for check in checks if check["status"] == "REVIEW"]
    return {
        "status": "FAIL" if failed else ("REVIEW" if review else "PASS"),
        "checks": checks,
        "passed": sum(1 for check in checks if check["status"] == "PASS"),
        "failed": len(failed),
        "needs_review": len(review),
        "not_checked": sum(1 for check in checks if check["status"] == "NOT_CHECKED"),
    }
