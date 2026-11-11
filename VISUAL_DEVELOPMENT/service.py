"""The project service: one implementation of "what does this package contain".

There used to be two answers to that question. The standalone review server
built its own state, and the application bridge built its own, and they could
drift apart. The review page once served a blank shell while the application
showed the same data correctly, and the fix had to be made twice.

There is now one. Both surfaces call :func:`project_state`, and each one
presents it in its own shape. A defect in the answer is fixed once.
"""

from __future__ import annotations

from typing import Any

from .storage import ProjectStore


def _latest_json(store: ProjectStore, directory: str, prefix: str) -> dict[str, Any]:
    """The newest JSON artifact in a directory, or an empty dict."""
    from .cli import _latest

    path = _latest(store, directory, prefix)
    if path is None:
        return {}
    return store.read(path.relative_to(store.root).as_posix())


def _generations(store: ProjectStore) -> list[dict[str, Any]]:
    from .cli import _collect_generations

    return _collect_generations(store)


def comfyui_status() -> dict[str, Any]:
    """The state of the local image service, or why it is not reachable."""
    try:
        from .comfyui_client import ComfyUIClient

        client = ComfyUIClient()
        stats = client.system_stats()
        return {
            "status": "CONNECTED",
            "comfyui_version": stats["system"]["comfyui_version"],
            "devices": [
                {"name": device["name"], "vram_free": device["vram_free"]}
                for device in stats.get("devices", [])
            ],
        }
    except Exception as exc:  # noqa: BLE001 - the UI must still load when ComfyUI is down
        return {"status": "UNAVAILABLE", "error": str(exc)}


def project_state(store: ProjectStore) -> dict[str, Any]:
    """Everything one package holds, in one dict.

    The shape is stable and shared. The review server renders it as a page,
    the application bridge maps it into its API payload, and both therefore
    report the same thing.
    """
    from .production import derive_shot_status
    from .prompt_overrides import load_overrides

    project = store.read("project.json")
    analysis = _latest_json(store, "analysis", "analysis")
    candidate_set = _latest_json(store, "art_direction", "candidates")
    style_bible = _latest_json(store, "style_bibles", "style_bible")
    breakdown = _latest_json(store, "breakdown", "breakdown")
    animatic = _latest_json(store, "animatic", "animatic")
    continuity = _latest_json(store, "reports", "continuity")
    generations = _generations(store)

    by_shot: dict[tuple[str, str], dict[str, Any]] = {}
    for generation in generations:
        by_shot[(generation.get("artifact_type", ""), generation.get("shot_id", ""))] = generation

    shots = []
    for sequence in analysis.get("sequences", []):
        for scene in sequence.get("scenes", []):
            for shot in scene.get("shots", []):
                shot_id = shot["shot_id"]
                storyboard = by_shot.get(("STORYBOARD", shot_id))
                blocking = by_shot.get(("BLOCKING", shot_id))
                shots.append(
                    {
                        "shot_id": shot_id,
                        "sequence_id": sequence.get("sequence_id", ""),
                        "scene_id": scene.get("scene_id", ""),
                        "scene_heading": scene.get("heading", ""),
                        "shot_size": shot.get("camera_shot_type", ""),
                        "purpose": shot.get("purpose", ""),
                        "description": shot.get("visual_description", ""),
                        "duration_sec": shot.get("estimated_duration_sec", 0.0),
                        "production_complexity": shot.get("production_complexity", ""),
                        "board_image_path": (storyboard or {}).get("image_path", ""),
                        "board_review_status": (storyboard or {}).get(
                            "review_status", "NOT_GENERATED"
                        ),
                        "blocking_image_path": (blocking or {}).get("image_path", ""),
                        "blocking_review_status": (blocking or {}).get(
                            "review_status", "NOT_GENERATED"
                        ),
                        "status": derive_shot_status(store, shot_id),
                    }
                )

    candidate_list = []
    for candidate in candidate_set.get("candidates", []):
        manifest = candidate.get("generation_manifest", {})
        candidate_list.append(
            {
                "candidate_id": candidate.get("candidate_id", ""),
                "style_name": candidate.get("style_name", ""),
                "description": candidate.get("description", ""),
                "palette": candidate.get("palette", ""),
                "lighting": candidate.get("lighting", ""),
                "camera": candidate.get("camera", ""),
                "storytelling": candidate.get("storytelling", ""),
                "feasibility": candidate.get("feasibility", ""),
                "strengths": candidate.get("strengths", []),
                "limitations": candidate.get("limitations", []),
                "selected": candidate.get("selected", False),
                "status": candidate.get("status", ""),
                "image_path": manifest.get("image_path", ""),
                "prompt_id": manifest.get("prompt_id", ""),
            }
        )

    return {
        "project": project,
        "episode": analysis.get("episode", {}),
        "open_questions": analysis.get("open_questions", []),
        "analysis": analysis,
        "candidates": {
            "comparison_scene_id": candidate_set.get("comparison_scene_id", ""),
            "comparison_seed": candidate_set.get("comparison_seed"),
            "candidates": candidate_list,
        },
        "style_bible": style_bible,
        "shots": shots,
        "generations": generations,
        "events": store.events(),
        "comfyui": comfyui_status(),
        "continuity": continuity,
        "breakdown": breakdown,
        "animatic": animatic,
        "overrides": load_overrides(store),
    }
