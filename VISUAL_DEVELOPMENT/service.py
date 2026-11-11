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


# ------------------------------------------------------------ generation plan


def resolve_plan(store: ProjectStore, target_id: str, kind: str = "") -> dict[str, Any]:
    """What would be sent to the image service for one target.

    This is the single answer to that question. The command line, the
    application and the review page all ask it here, so a user cannot get a
    different picture from the same override depending on where they clicked.

    The plan carries the effective prompt, the effective negative prompt, the
    effective settings, the workflow the user attached, what was applied, and
    anything that could not be applied.
    """
    from .prompt_builder import build_candidate_prompt, build_shot_prompt
    from .prompt_overrides import (
        effective_prompt,
        effective_settings,
        get_override,
    )
    from .production import seed_for_shot

    analysis = _latest_json(store, "analysis", "analysis")
    style_bible = _latest_json(store, "style_bibles", "style_bible")
    candidate_set = _latest_json(store, "art_direction", "candidates")
    characters = {entry["name"]: entry for entry in analysis.get("characters", [])}

    shot = None
    scene = None
    sequence = None
    for candidate_sequence in analysis.get("sequences", []):
        for candidate_scene in candidate_sequence.get("scenes", []):
            for candidate_shot in candidate_scene.get("shots", []):
                if candidate_shot.get("shot_id") == target_id:
                    shot = candidate_shot
                    scene = candidate_scene
                    sequence = candidate_sequence

    if shot is not None:
        built = build_shot_prompt(style_bible, shot, scene, characters, mode="storyboard")
        base_settings = dict(style_bible.get("global_rules", {}).get("generation_settings", {}))
        base_settings["seed"] = seed_for_shot(shot, base_settings)
        resolved_kind = "SHOT"
        context = {
            "sequence_id": sequence.get("sequence_id", ""),
            "scene_id": scene.get("scene_id", ""),
            "shot": shot,
            "scene": scene,
        }
    else:
        candidate = next(
            (
                entry
                for entry in candidate_set.get("candidates", [])
                if entry.get("candidate_id") == target_id
            ),
            None,
        )
        if candidate is None:
            raise KeyError(f"Unknown target: {target_id}")
        comparison_scene = None
        for candidate_sequence in analysis.get("sequences", []):
            for candidate_scene in candidate_sequence.get("scenes", []):
                if (
                    candidate_scene.get("scene_id")
                    == candidate_set.get("comparison_scene_id")
                ):
                    comparison_scene = candidate_scene
        built = build_candidate_prompt(
            candidate.get("style_prompt", ""), comparison_scene, characters
        )
        base_settings = {
            "model": "dreamshaper_8.safetensors",
            "lora": "arcane_offset.safetensors",
            "lora_strength": 0.65,
            "width": 768,
            "height": 768,
            "steps": 25,
            "cfg": 8.0,
            "sampler": "euler",
            "scheduler": "simple",
            "seed": candidate_set.get("comparison_seed", 536354036775427),
        }
        resolved_kind = "ART_DIRECTION_CANDIDATE"
        context = {
            "sequence_id": "",
            "scene_id": comparison_scene.get("scene_id", "") if comparison_scene else "",
            "shot": None,
            "scene": comparison_scene,
            "candidate": candidate,
        }

    override = get_override(store, target_id)
    merged = effective_prompt(built, override)
    resolved = effective_settings(base_settings, override)
    settings = resolved["settings"]

    # The settings the user set by hand, as opposed to the ones that came
    # from the Style Bible. Only these are written into a workflow of the
    # user's own: a graph the user built keeps its own values unless the
    # user changed them.
    explicit_settings = dict((override or {}).get("settings_override") or {})
    if explicit_settings.get("preset"):
        from .presets import preset_settings

        explicit_settings = {
            **preset_settings(explicit_settings["preset"]),
            **explicit_settings,
        }
    explicit_settings.pop("preset", None)
    explicit_settings.pop("workflow_template", None)

    warnings: list[str] = []

    user_workflow = None
    workflow_id = (override or {}).get("workflow_id")
    if workflow_id:
        relative = f"PROMPTS/workflows/{workflow_id}.json"
        if store.path(relative).is_file():
            user_workflow = store.read(relative)
        else:
            warnings.append(f"The attached workflow {relative} is missing from the project.")

    if user_workflow is not None:
        # A user graph is the user's own. The preset cannot be forced onto it,
        # but the settings that the graph does have are still applied.
        if settings.get("preset"):
            warnings.append(
                "The generation preset sets the model, the sampler and the size, "
                "but a workflow of your own keeps its own nodes. The preset is not "
                "applied to it."
            )
        if "vae" in settings and settings.get("vae"):
            warnings.append(
                "A workflow of your own loads its own VAE; the preset's VAE is not forced onto it."
            )

    return {
        "target_id": target_id,
        "kind": resolved_kind,
        "prompt": merged["prompt"],
        "negative_prompt": merged["negative_prompt"],
        "generated_prompt": merged["generated_prompt"],
        "modules": merged["modules"],
        "excluded_modules": merged["excluded_modules"],
        "applied_overrides": merged["applied_overrides"]
        + resolved["applied_overrides"],
        "settings": settings,
        "explicit_settings": explicit_settings,
        "user_workflow": user_workflow,
        "workflow_id": workflow_id or "",
        "has_override": override is not None,
        "warnings": warnings,
        **context,
    }


def regenerate(
    store: ProjectStore,
    client: Any,
    target_id: str,
    *,
    artifact_type: str = "STORYBOARD",
    actor: str = "frontend",
    mode: str = "storyboard",
) -> dict[str, Any]:
    """Generate one image for a target, using the plan.

    The plan is what the user configured. An approved image is never
    overwritten: the module always writes a new revision next to it.
    """
    from .generation import generate_image
    from .style_bible import style_bible_hash

    plan = resolve_plan(store, target_id)
    style_bible = _latest_json(store, "style_bibles", "style_bible")
    analysis = _latest_json(store, "analysis", "analysis")
    shot = plan.get("shot") or {}
    scene = plan.get("scene") or {}

    if artifact_type == "ART_DIRECTION":
        candidate = plan.get("candidate") or {}
        relative_dir = f"art_direction/candidate_{target_id}"
        filename_prefix = f"ARTDIR_{target_id}"
    else:
        relative_dir = (
            f"storyboard/{plan.get('sequence_id', '')}/{plan.get('scene_id', '')}/{target_id}"
        )
        filename_prefix = f"SB_{target_id}"

    result = generate_image(
        client,
        store,
        artifact_type=artifact_type,
        relative_dir=relative_dir,
        prompt=plan["prompt"],
        negative_prompt=plan["negative_prompt"],
        settings=plan["settings"],
        workflow_id=plan["workflow_id"] or "txt2img_v1",
        shot_id=target_id if artifact_type != "ART_DIRECTION" else "",
        sequence_id=plan.get("sequence_id", ""),
        scene_id=plan.get("scene_id", ""),
        style_bible_sha256=style_bible_hash(style_bible) if style_bible else "",
        source_script_sha256=analysis.get("source_script_sha256", ""),
        filename_prefix=filename_prefix,
        actor=actor,
        user_workflow=plan["user_workflow"],
        user_settings=plan["explicit_settings"],
        override_applied=plan["applied_overrides"],
    )
    result["plan"] = {
        "applied_overrides": list(
            dict.fromkeys(list(plan["applied_overrides"]) + list(result.get("applied_overrides", [])))
        ),
        "warnings": plan["warnings"],
        "has_override": plan["has_override"],
        "settings": plan["settings"],
        "workflow_source": result.get("workflow_source", "BUILT_IN"),
    }
    return result


def validate_workflow_report(workflow: dict[str, Any]) -> dict[str, Any]:
    """Check a user supplied workflow against the live ComfyUI server.

    A workflow that the server accepts, but whose text nodes cannot be
    resolved, is refused: it would put the prompt into the wrong node.
    """
    from .comfyui_client import ComfyUIClient
    from .workflows import validate_user_workflow

    try:
        return validate_user_workflow(ComfyUIClient(), workflow)
    except Exception as exc:  # noqa: BLE001 - the report has to explain the failure
        return {
            "status": "FAIL",
            "missing_nodes": [],
            "missing_inputs": [],
            "unknown_inputs": [],
            "can_take_prompt": False,
            "errors": [str(exc)[:300]],
        }


def style_bible_status(store: ProjectStore) -> dict[str, Any]:
    """The Style Bible and whether a human has approved it.

    The Style Bible is an immutable artifact, so an approval is recorded as an
    event rather than by rewriting the file. The status that is reported is
    the approval when there is one, and the file's own draft status otherwise.
    """
    style_bible = _latest_json(store, "style_bibles", "style_bible")
    if not style_bible:
        return {"status": "NOT_FOUND", "style_bible": {}, "approved": False}
    bible_id = style_bible.get("style_bible_id", "")
    approved = any(
        event.get("action") == "APPROVE"
        and event.get("target_type") == "STYLE_BIBLE"
        and event.get("target_id") == bible_id
        for event in store.events()
    )
    return {
        "status": "APPROVED" if approved else style_bible.get("status", "DRAFT"),
        "style_bible": style_bible,
        "approved": approved,
        "style_bible_id": bible_id,
    }


def record_decision(
    store: ProjectStore,
    action: str,
    target_type: str,
    target_id: str,
    *,
    actor: str = "operator",
    note: str = "",
) -> dict[str, Any]:
    """Record a human decision in the append-only event log.

    The decision applies to the revision that is on screen, so approving one
    revision does not silently approve the next one that is generated.
    """
    from .common import new_id, utc_now

    event = {
        "event_id": new_id("EVT"),
        "timestamp": utc_now(),
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "note": note,
        "metadata": {},
    }
    store.append_event(event)
    return event
