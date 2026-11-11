"""Command line entry point for the Visual Development and Storyboard module."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .analyzer import parse_script
from .approved_script import ApprovedScriptError, load_approved_script, load_script_file
from .art_direction import build_candidates, select_candidate
from .breakdown import build_breakdown
from .common import new_id, sha256_bytes, utc_now
from .continuity import validate_continuity
from .generation import blocking_png_path, generate_image, write_blocking_layout
from .handoff import build_handoff, render_handoff_markdown
from .production import pipeline_status
from .prompt_builder import build_candidate_prompt, build_shot_prompt
from .prompt_overrides import (
    build_override,
    clear_override,
    effective_prompt,
    effective_settings,
    get_override,
    load_overrides,
    save_override,
)
from .style_bible import build_style_bible, style_bible_hash
from .storage import ProjectStore
from .workflows import validate_user_workflow, validate_workflow

DEFAULT_DB = "animation_forge.db"
DEFAULT_COMFY = "http://127.0.0.1:8188"


def _print(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, default=str))


def _load_store(project_dir: Path) -> ProjectStore:
    return ProjectStore(project_dir)


def _latest(store: ProjectStore, directory: str, prefix: str) -> Path | None:
    folder = store.path(directory)
    if not folder.exists():
        return None
    files = sorted(folder.glob(f"{prefix}_v*.json"))
    return files[-1] if files else None


def _analysis(store: ProjectStore) -> dict[str, Any]:
    path = _latest(store, "analysis", "analysis")
    if path is None:
        raise SystemExit("No analysis found. Run the 'analyze' command first.")
    return store.read(path.relative_to(store.root).as_posix())


def _candidate_set(store: ProjectStore) -> dict[str, Any]:
    path = _latest(store, "art_direction", "candidates")
    if path is None:
        raise SystemExit("No art-direction candidate set found. Run 'art-direction' first.")
    return store.read(path.relative_to(store.root).as_posix())


def _style_bible(store: ProjectStore) -> dict[str, Any]:
    path = _latest(store, "style_bibles", "style_bible")
    if path is None:
        raise SystemExit("No Style Bible found. Run 'style-bible' first.")
    return store.read(path.relative_to(store.root).as_posix())


def _character_index(analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["name"]: entry for entry in analysis.get("characters", [])}


def _user_workflow_for(store: ProjectStore, override: dict[str, Any] | None) -> dict[str, Any] | None:
    """Load the workflow a user attached to an override, if there is one."""
    if not override or not override.get("workflow_id"):
        return None
    relative = f"PROMPTS/workflows/{override['workflow_id']}.json"
    path = store.path(relative)
    if not path.is_file():
        raise SystemExit(f"The attached workflow {relative} is missing from the project.")
    return store.read(relative)


def _iter_shots(analysis: dict[str, Any]):
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            for shot in scene["shots"]:
                yield sequence, scene, shot


# --------------------------------------------------------------------- commands


def _set_stage(store: ProjectStore, stage: str) -> None:
    """Record how far the pipeline has progressed on the project manifest.

    The stage is working state, so it is updated in place. Without this the
    manifest kept reporting SOURCE_IMPORTED long after the pipeline had run.
    The stage never moves backwards: re-running an earlier command must not
    un-finish a later one.
    """
    from .production import stage_rank

    project = store.read("project.json")
    current = project.get("stage", "")
    if current == stage:
        return
    if current and stage_rank(stage) <= stage_rank(current):
        return
    project["stage"] = stage
    store.update_json("project.json", project, "project.schema.json")


def cmd_init(args: argparse.Namespace) -> int:
    script = load_approved_script(args.database, args.script_id)
    store = ProjectStore.create(args.project_dir, script)
    _print(
        {
            "status": "PASS",
            "project_dir": str(store.root),
            "project_id": store.read("project.json")["project_id"],
            "script_id": script["script_id"],
            "approval_status": script["approval_status"],
            "source_sha256": script["sha256"],
            "message": "Approved screenplay imported. No images generated and nothing approved.",
        }
    )
    return 0


def cmd_init_file(args: argparse.Namespace) -> int:
    script = load_script_file(
        args.script_file, args.script_id, args.project_id, args.episode_id, args.version
    )
    store = ProjectStore.create(args.project_dir, script)
    _print(
        {
            "status": "PASS",
            "project_dir": str(store.root),
            "project_id": store.read("project.json")["project_id"],
            "script_id": script["script_id"],
            "approval_status": script["approval_status"],
            "source_sha256": script["sha256"],
            "warning": (
                "This source was imported from a plain file and was NOT approved through "
                "the Animation Forge governance process. Use it for exploration and art "
                "direction only. It must not be presented as a production-ready package."
            ),
            "message": "Script file imported. No images generated and nothing approved.",
        }
    )
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    store = _load_store(args.project_dir)
    text, manifest = store.source()
    analysis = parse_script(text, store.read("project.json")["project_id"], manifest["sha256"])
    version = store.latest_number("analysis", "analysis")
    path = store.write_json(
        f"analysis/analysis_v{version:03d}.json", analysis, "analysis.schema.json"
    )
    _set_stage(store, "ANALYZED")
    shots = sum(len(scene["shots"]) for sequence in analysis["sequences"] for scene in sequence["scenes"])
    _print(
        {
            "status": "PASS",
            "analysis_path": path.relative_to(store.root).as_posix(),
            "analysis_id": analysis["analysis_id"],
            "sequences": len(analysis["sequences"]),
            "scenes": sum(len(sequence["scenes"]) for sequence in analysis["sequences"]),
            "shots": shots,
            "characters": [entry["name"] for entry in analysis.get("characters", [])],
            "open_questions": analysis["open_questions"],
        }
    )
    return 0


def cmd_art_direction(args: argparse.Namespace) -> int:
    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    candidate_set = build_candidates(
        analysis,
        store.read("project.json")["project_id"],
        args.comparison_scene,
    )
    version = store.latest_number("art_direction", "candidates")
    path = store.write_json(
        f"art_direction/candidates_v{version:03d}.json",
        candidate_set,
        "candidate.schema.json",
    )
    _set_stage(store, "ART_DIRECTION_READY")
    _print(
        {
            "status": "PASS",
            "candidate_set_path": path.relative_to(store.root).as_posix(),
            "candidate_set_id": candidate_set["candidate_set_id"],
            "comparison_scene_id": candidate_set["comparison_scene_id"],
            "comparison_seed": candidate_set["comparison_seed"],
            "candidates": [
                {"candidate_id": entry["candidate_id"], "style_name": entry["style_name"]}
                for entry in candidate_set["candidates"]
            ],
            "message": "Candidates are drafts. A human must select one.",
        }
    )
    return 0


def cmd_generate_candidates(args: argparse.Namespace) -> int:
    from .comfyui_client import ComfyUIClient

    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    candidate_set = _candidate_set(store)
    character_index = _character_index(analysis)
    comparison_scene = None
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            if scene["scene_id"] == candidate_set["comparison_scene_id"]:
                comparison_scene = scene
    if comparison_scene is None:
        raise SystemExit("The comparison scene is missing from the current analysis.")

    client = ComfyUIClient(args.comfy_url)
    results = []
    for candidate in candidate_set["candidates"]:
        if args.only and candidate["candidate_id"] not in args.only:
            continue
        built = build_candidate_prompt(
            candidate["style_prompt"], comparison_scene, character_index
        )
        override = get_override(store, candidate["candidate_id"])
        merged = effective_prompt(built, override)
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
            "seed": candidate_set["comparison_seed"],
        }
        settings = effective_settings(base_settings, override)["settings"]
        result = generate_image(
            client,
            store,
            artifact_type="ART_DIRECTION",
            relative_dir=f"art_direction/candidate_{candidate['candidate_id']}",
            prompt=merged["prompt"],
            negative_prompt=merged["negative_prompt"]
            or "extra characters, inconsistent character design, watermark, text, blurry, low resolution",
            settings=settings,
            workflow_id=(override or {}).get("workflow_id") or "txt2img_v1",
            scene_id=comparison_scene["scene_id"],
            sequence_id=next(
                sequence["sequence_id"]
                for sequence in analysis["sequences"]
                if comparison_scene in sequence["scenes"]
            ),
            source_script_sha256=analysis["source_script_sha256"],
            filename_prefix=f"ARTDIR_{candidate['candidate_id']}",
            user_workflow=_user_workflow_for(store, override),
            override_applied=merged["applied_overrides"],
        )
        candidate["generation_manifest"] = {
            "generation_id": result["generation_id"],
            "image_path": result["image_path"],
            "prompt": merged["prompt"],
            "prompt_id": result["prompt_id"],
        }
        results.append({"candidate_id": candidate["candidate_id"], **result})

    version = store.latest_number("art_direction", "candidates") - 1
    store.update_json(
        f"art_direction/candidates_v{version:03d}.json", candidate_set, "candidate.schema.json"
    )
    _set_stage(store, "ART_DIRECTION_GENERATED")
    _print({"status": "PASS", "generated": len(results), "results": results})
    return 0


def cmd_select(args: argparse.Namespace) -> int:
    from .common import new_id

    store = _load_store(args.project_dir)
    candidate_set = _candidate_set(store)
    select_candidate(candidate_set, args.candidate_id)
    path = _latest(store, "art_direction", "candidates")
    store.update_json(
        path.relative_to(store.root).as_posix(), candidate_set, "candidate.schema.json"
    )
    store.append_event(
        {
            "event_id": new_id("EVT"),
            "timestamp": utc_now(),
            "actor": args.actor,
            "action": "SELECT",
            "target_type": "ART_DIRECTION_CANDIDATE",
            "target_id": args.candidate_id,
            "note": args.note or "",
            "metadata": {},
        }
    )
    _set_stage(store, "DIRECTION_SELECTED")
    _print(
        {
            "status": "PASS",
            "selected": args.candidate_id,
            "message": "Selection recorded. A Style Bible can now be created.",
        }
    )
    return 0


def cmd_style_bible(args: argparse.Namespace) -> int:
    store = _load_store(args.project_dir)
    candidate_set = _candidate_set(store)
    project_id = store.read("project.json")["project_id"]
    style_bible = build_style_bible(candidate_set, args.candidate_id, project_id)
    version = store.latest_number("style_bibles", "style_bible")
    path = store.write_json(
        f"style_bibles/style_bible_v{version:03d}.json", style_bible, "style_bible.schema.json"
    )
    _set_stage(store, "STYLE_BIBLE_CREATED")
    _print(
        {
            "status": "PASS",
            "style_bible_path": path.relative_to(store.root).as_posix(),
            "style_bible_id": style_bible["style_bible_id"],
            "version": style_bible["version"],
            "style_identity": style_bible["style_identity"],
            "status_field": style_bible["status"],
            "message": "Style Bible created as a draft; a human must approve it.",
        }
    )
    return 0


def cmd_storyboard(args: argparse.Namespace) -> int:
    from .comfyui_client import ComfyUIClient
    from .presets import preset_settings

    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    style_bible = _style_bible(store)
    character_index = _character_index(analysis)
    client = ComfyUIClient(args.comfy_url)
    base_settings = dict(style_bible["global_rules"]["generation_settings"])
    if getattr(args, "preset", ""):
        base_settings.update(preset_settings(args.preset))
    settings = base_settings
    results = []
    for sequence, scene, shot in _iter_shots(analysis):
        if args.shot and shot["shot_id"] not in args.shot:
            continue
        if args.limit and len(results) >= args.limit:
            break
        built = build_shot_prompt(style_bible, shot, scene, character_index, mode="storyboard")
        override = get_override(store, shot["shot_id"])
        merged = effective_prompt(built, override)
        shot_settings = effective_settings(
            {**settings, "seed": _seed_for(shot, settings)},
            override,
        )["settings"]
        relative_dir = (
            f"storyboard/{sequence['sequence_id']}/{scene['scene_id']}/{shot['shot_id']}"
        )
        result = generate_image(
            client,
            store,
            artifact_type="STORYBOARD",
            relative_dir=relative_dir,
            prompt=merged["prompt"],
            negative_prompt=merged["negative_prompt"],
            settings=shot_settings,
            workflow_id=(override or {}).get("workflow_id") or "txt2img_v1",
            shot_id=shot["shot_id"],
            sequence_id=sequence["sequence_id"],
            scene_id=scene["scene_id"],
            style_bible_sha256=style_bible_hash(style_bible),
            source_script_sha256=analysis["source_script_sha256"],
            filename_prefix=f"SB_{shot['shot_id']}",
            user_workflow=_user_workflow_for(store, override),
            override_applied=merged["applied_overrides"],
        )
        results.append({"shot_id": shot["shot_id"], **result})
    _set_stage(store, "STORYBOARD_GENERATED")
    _print({"status": "PASS", "generated": len(results), "results": results})
    return 0


def cmd_blocking(args: argparse.Namespace) -> int:
    from .comfyui_client import ComfyUIClient
    from .presets import preset_settings

    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    style_bible = _style_bible(store)
    character_index = _character_index(analysis)
    client = ComfyUIClient(args.comfy_url)
    base_settings = dict(style_bible["global_rules"]["generation_settings"])
    if getattr(args, "preset", ""):
        base_settings.update(preset_settings(args.preset))
    settings = base_settings
    results = []
    for sequence, scene, shot in _iter_shots(analysis):
        if args.shot and shot["shot_id"] not in args.shot:
            continue
        if args.limit and len(results) >= args.limit:
            break
        relative_dir = f"blocking/{sequence['sequence_id']}/{scene['scene_id']}/{shot['shot_id']}"
        layout_result = write_blocking_layout(store, shot, scene, sequence, relative_dir)
        png_path = layout_result["png_path"]
        built = build_shot_prompt(style_bible, shot, scene, character_index, mode="blocking")
        entry: dict[str, Any] = {
            "shot_id": shot["shot_id"],
            "layout_path": layout_result["layout_path"],
            "svg_path": layout_result["svg_path"],
            "png_path": png_path,
        }
        if args.generate_images:
            result = generate_image(
                client,
                store,
                artifact_type="BLOCKING",
                relative_dir=relative_dir,
                prompt=built["prompt"],
                negative_prompt=built["negative_prompt"],
                settings={**settings, "seed": _seed_for(shot, settings)},
                workflow_id="txt2img_canny_v1",
                shot_id=shot["shot_id"],
                sequence_id=sequence["sequence_id"],
                scene_id=scene["scene_id"],
                style_bible_sha256=style_bible_hash(style_bible),
                source_script_sha256=analysis["source_script_sha256"],
                control_image_path=store.path(png_path),
                filename_prefix=f"BL_{shot['shot_id']}",
            )
            entry.update(result)
        results.append(entry)
    _set_stage(store, "BLOCKING_GENERATED")
    _print({"status": "PASS", "processed": len(results), "results": results})
    return 0


def _seed_for(shot: dict[str, Any], settings: dict[str, Any]) -> int:
    """Deterministic per-shot seed derived from the shot id and the base seed."""
    base = int(settings.get("seed", 536354036775427))
    offset = sum(ord(character) for character in shot["shot_id"])
    return (base + offset * 7919) % (2**53)


def cmd_check(args: argparse.Namespace) -> int:
    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    style_bible = _style_bible(store)
    generations = _collect_generations(store)
    report = validate_continuity(
        analysis,
        style_bible,
        generations,
        analysis["source_script_sha256"],
    )
    version = store.latest_number("reports", "continuity")
    store.write_json(f"reports/continuity_v{version:03d}.json", report)
    _set_stage(store, "CONTINUITY_CHECKED")
    _print({"status": report["status"], "report": report})
    return 0 if report["status"] in {"PASS", "REVIEW"} else 1


def _collect_generations(store: ProjectStore) -> list[dict[str, Any]]:
    generations: list[dict[str, Any]] = []
    for path in sorted(store.root.rglob("*.json")):
        relative = path.relative_to(store.root).as_posix()
        if relative.startswith("source/") or relative in {"project.json"}:
            continue
        if relative.startswith("analysis/") or relative.startswith("reports/"):
            continue
        if relative.startswith("art_direction/candidates"):
            continue
        if relative.startswith("style_bibles/") or relative.startswith("handoff/"):
            continue
        try:
            value = store.read(relative)
        except (ValueError, json.JSONDecodeError):
            continue
        if isinstance(value, dict) and value.get("generation_id"):
            generations.append(value)
    return generations


def cmd_handoff(args: argparse.Namespace) -> int:
    from .production import derive_shot_status

    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    style_bible = _style_bible(store)
    generations = _collect_generations(store)
    events = store.events()
    report_path = _latest(store, "reports", "continuity")
    continuity = store.read(report_path.relative_to(store.root).as_posix()) if report_path else None

    breakdown_path = _latest(store, "breakdown", "breakdown")
    breakdown = (
        store.read(breakdown_path.relative_to(store.root).as_posix()) if breakdown_path else None
    )
    overrides = load_overrides(store)
    animatic_path = _latest(store, "animatic", "animatic")
    animatic = (
        store.read(animatic_path.relative_to(store.root).as_posix()) if animatic_path else None
    )
    shot_statuses = {
        shot["shot_id"]: derive_shot_status(store, shot["shot_id"])
        for sequence in analysis.get("sequences", [])
        for scene in sequence.get("scenes", [])
        for shot in scene.get("shots", [])
    }

    package = build_handoff(
        analysis,
        style_bible,
        generations,
        events,
        store.read("source/script_manifest.json"),
        continuity,
        breakdown=breakdown,
        prompt_overrides=overrides,
        animatic=animatic,
        shot_statuses=shot_statuses,
    )
    version = store.latest_number("handoff", "handoff")
    store.write_json(f"handoff/handoff_v{version:03d}.json", package)
    store.write_bytes(
        f"handoff/handoff_v{version:03d}.md",
        render_handoff_markdown(package).encode("utf-8"),
    )
    _set_stage(store, "HANDOFF_EXPORTED")
    _print(
        {
            "status": "PASS",
            "handoff_json": f"handoff/handoff_v{version:03d}.json",
            "handoff_markdown": f"handoff/handoff_v{version:03d}.md",
            "approved_storyboard_images": len(package["approved_storyboard_images"]),
            "approved_blocking_images": len(package["approved_blocking_images"]),
            "unresolved_issues": len(package["unresolved_issues"]),
        }
    )
    return 0


def cmd_breakdown(args: argparse.Namespace) -> int:
    """Break the script down into the elements each department needs."""
    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    project_id = store.read("project.json")["project_id"]
    breakdown = build_breakdown(analysis, project_id)
    version = store.latest_number("breakdown", "breakdown")
    path = store.write_json(f"breakdown/breakdown_v{version:03d}.json", breakdown)
    _set_stage(store, "BREAKDOWN_COMPLETE")
    _print(
        {
            "status": "PASS",
            "breakdown_path": path.relative_to(store.root).as_posix(),
            "breakdown_id": breakdown["breakdown_id"],
            "scene_count": breakdown["summary"]["scene_count"],
            "element_count": breakdown["summary"]["element_count"],
            "by_category": breakdown["summary"]["by_category"],
            "by_department": breakdown["summary"]["by_department"],
            "needs_reference": breakdown["summary"]["needs_reference"],
        }
    )
    return 0


def cmd_production(args: argparse.Namespace) -> int:
    """Report the whole production spine for one project."""
    store = _load_store(args.project_dir)
    _print(pipeline_status(store))
    return 0


def cmd_set_prompt(args: argparse.Namespace) -> int:
    """Attach the user's own prompt and settings to a shot or a candidate."""
    store = _load_store(args.project_dir)
    override = build_override(
        args.target_id,
        args.kind,
        prompt_extra=args.prompt_extra or "",
        prompt_replace=args.prompt_replace,
        negative_extra=args.negative_extra or "",
        exclude_modules=args.exclude_module or [],
        settings_override=_parse_settings(args.setting or []),
        workflow_id=args.workflow_id,
        note=args.note or "",
        actor=args.actor,
    )
    save_override(store, override)
    _print(
        {
            "status": "PASS",
            "target_id": override["target_id"],
            "kind": override["kind"],
            "override_id": override["override_id"],
            "settings_override": override["settings_override"],
            "excluded_modules": override["exclude_modules"],
        }
    )
    return 0


def _parse_settings(pairs: list[str]) -> dict[str, Any]:
    """Parse ``key=value`` settings arguments into typed values."""
    values: dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise SystemExit(f"Settings must be given as key=value, got {pair!r}")
        key, _, raw = pair.partition("=")
        if raw.lower() in {"true", "false"}:
            value: Any = raw.lower() == "true"
        else:
            try:
                value = int(raw)
            except ValueError:
                try:
                    value = float(raw)
                except ValueError:
                    value = raw
        values[key.strip()] = value
    return values


def cmd_show_prompt(args: argparse.Namespace) -> int:
    """Show the effective prompt for a shot or a candidate, and where it came from."""
    store = _load_store(args.project_dir)
    override = get_override(store, args.target_id)
    if args.target_id.startswith("SHT_"):
        analysis = _analysis(store)
        style_bible = _style_bible(store)
        character_index = _character_index(analysis)
        shot = None
        scene = None
        for sequence in analysis["sequences"]:
            for candidate_scene in sequence["scenes"]:
                for candidate_shot in candidate_scene["shots"]:
                    if candidate_shot["shot_id"] == args.target_id:
                        shot = candidate_shot
                        scene = candidate_scene
        if shot is None:
            raise SystemExit(f"Unknown shot: {args.target_id}")
        built = build_shot_prompt(
            style_bible, shot, scene, character_index, mode="storyboard"
        )
        settings = dict(style_bible["global_rules"]["generation_settings"])
    else:
        analysis = _analysis(store)
        candidate_set = _candidate_set(store)
        candidate = next(
            (
                entry
                for entry in candidate_set["candidates"]
                if entry["candidate_id"] == args.target_id
            ),
            None,
        )
        if candidate is None:
            raise SystemExit(f"Unknown candidate: {args.target_id}")
        comparison_scene = None
        for sequence in analysis["sequences"]:
            for candidate_scene in sequence["scenes"]:
                if candidate_scene["scene_id"] == candidate_set["comparison_scene_id"]:
                    comparison_scene = candidate_scene
        built = build_candidate_prompt(
            candidate["style_prompt"], comparison_scene, _character_index(analysis)
        )
        settings = {"seed": candidate_set["comparison_seed"], "model": "dreamshaper_8.safetensors"}

    merged = effective_prompt(built, override)
    resolved = effective_settings(settings, override)
    _print(
        {
            "target_id": args.target_id,
            "generated_prompt": merged["generated_prompt"],
            "effective_prompt": merged["prompt"],
            "generated_negative_prompt": merged["generated_negative_prompt"],
            "effective_negative_prompt": merged["negative_prompt"],
            "modules": merged["modules"],
            "excluded_modules": merged["excluded_modules"],
            "applied_overrides": merged["applied_overrides"],
            "changed": merged["changed"],
            "settings": resolved["settings"],
            "settings_overrides_applied": resolved["applied_overrides"],
            "has_override": override is not None,
        }
    )
    return 0


def cmd_reset_prompt(args: argparse.Namespace) -> int:
    """Remove the override on a shot or a candidate."""
    store = _load_store(args.project_dir)
    removed = clear_override(store, args.target_id)
    _print(
        {
            "status": "PASS" if removed else "NOTHING_TO_RESET",
            "target_id": args.target_id,
            "removed": removed,
        }
    )
    return 0


def cmd_import_workflow(args: argparse.Namespace) -> int:
    """Store a user supplied ComfyUI API-format workflow in the project."""
    store = _load_store(args.project_dir)
    source = Path(args.file) if args.file else None
    if source is None or not source.is_file():
        raise SystemExit("Provide a readable --file with the workflow JSON.")
    try:
        workflow = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"The workflow file is not valid JSON: {exc}") from exc
    if not isinstance(workflow, dict) or not workflow:
        raise SystemExit("The workflow must be a non-empty JSON object of nodes.")
    workflow_id = args.workflow_id or new_id("WF")
    store.write_json(f"PROMPTS/workflows/{workflow_id}.json", workflow)
    _print(
        {
            "status": "PASS",
            "workflow_id": workflow_id,
            "path": f"PROMPTS/workflows/{workflow_id}.json",
            "node_count": len(workflow),
        }
    )
    return 0


def cmd_validate_workflow(args: argparse.Namespace) -> int:
    """Check a user supplied workflow against the live ComfyUI server."""
    from .comfyui_client import ComfyUIClient

    store = _load_store(args.project_dir)
    workflow = store.read(f"PROMPTS/workflows/{args.workflow_id}.json")
    client = ComfyUIClient(args.comfy_url)
    report = validate_user_workflow(client, workflow)
    _print({"workflow_id": args.workflow_id, **report})
    return 0 if report["status"] == "PASS" else 1


def cmd_animatic(args: argparse.Namespace) -> int:
    """Cut the boards to an animatic: a timed cut with the voice on it."""
    from .animatic import (
        animatic_manifest,
        build_animatic,
        mix_voice_track,
        render_animatic,
        synthesize_voice,
    )

    store = _load_store(args.project_dir)
    analysis = _analysis(store)
    generations = _collect_generations(store)
    timeline = build_animatic(analysis, generations)

    audio_dir = store.path("animatic/audio")
    clips: list[tuple[Path, float]] = []
    voice_results = []
    for index, line in enumerate(timeline["voice_lines"]):
        if args.no_voice:
            voice_results.append({**line, "status": "SKIPPED"})
            continue
        target = audio_dir / f"{line['line_id']}.wav"
        result = synthesize_voice(line["text"], target, voice=args.voice)
        voice_results.append({**line, **{k: v for k, v in result.items() if k != "path"}})
        if result["status"] == "PASS":
            clips.append((Path(result["path"]), line["start_sec"]))

    audio_path: Path | None = None
    if clips:
        mixed = mix_voice_track(
            clips,
            store.path("animatic/voice.wav"),
            timeline["summary"]["total_duration_sec"],
        )
        audio_path = Path(mixed["path"]) if mixed["status"] == "PASS" else None

    version = store.latest_number("animatic", "animatic")
    video = render_animatic(
        timeline,
        store.path(f"animatic/animatic_v{version:03d}.mp4"),
        project_root=store.root,
        audio_path=audio_path,
        fps=args.fps,
    )
    manifest = animatic_manifest(timeline, video)
    manifest["voice_lines"] = voice_results
    store.write_json(f"animatic/animatic_v{version:03d}.json", manifest)

    _set_stage(store, "ANIMATIC_EXPORTED")
    _print(
        {
            "status": video["status"],
            "animatic_id": timeline["animatic_id"],
            "manifest_path": f"animatic/animatic_v{version:03d}.json",
            "video_path": video.get("path", ""),
            "video_error": video.get("error", ""),
            "shots": timeline["summary"]["shot_count"],
            "pictures": timeline["summary"]["picture_count"],
            "missing_pictures": timeline["summary"]["missing_pictures"],
            "voice_lines": len(timeline["voice_lines"]),
            "voice_clips": len(clips),
            "total_duration_sec": timeline["summary"]["total_duration_sec"],
        }
    )
    return 0 if video["status"] == "PASS" else 1


def cmd_status(args: argparse.Namespace) -> int:
    store = _load_store(args.project_dir)
    project = store.read("project.json")
    generations = _collect_generations(store)
    events = store.events()
    by_type: dict[str, int] = {}
    for generation in generations:
        key = generation.get("artifact_type", "UNKNOWN")
        by_type[key] = by_type.get(key, 0) + 1
    review_counts: dict[str, int] = {}
    for generation in generations:
        key = generation.get("review_status", "UNKNOWN")
        review_counts[key] = review_counts.get(key, 0) + 1
    _print(
        {
            "project_id": project["project_id"],
            "stage": project["stage"],
            "source_script": project["source_script"]["script_id"],
            "approval_status": project["source_script"]["approval_status"],
            "analysis": _latest(store, "analysis", "analysis") is not None,
            "candidate_sets": len(list(store.path("art_direction").glob("candidates_v*.json")))
            if store.path("art_direction").exists()
            else 0,
            "style_bibles": len(list(store.path("style_bibles").glob("style_bible_v*.json")))
            if store.path("style_bibles").exists()
            else 0,
            "generations_by_type": by_type,
            "generations_by_review_status": review_counts,
            "review_events": len(events),
        }
    )
    return 0


def cmd_comfy_check(args: argparse.Namespace) -> int:
    from .comfyui_client import ComfyUIClient

    client = ComfyUIClient(args.comfy_url)
    stats = client.system_stats()
    _print(
        {
            "status": "PASS",
            "comfyui_version": stats["system"]["comfyui_version"],
            "python_version": stats["system"]["python_version"],
            "pytorch_version": stats["system"]["pytorch_version"],
            "devices": [
                {
                    "name": device["name"],
                    "vram_total": device["vram_total"],
                    "vram_free": device["vram_free"],
                }
                for device in stats.get("devices", [])
            ],
            "checkpoints": client.list_models("checkpoints"),
            "loras": client.list_models("loras"),
            "controlnets": client.list_models("controlnet"),
        }
    )
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    from .review_server import serve

    serve(Path(args.project_dir), host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="visual-development",
        description="Approved script to art direction, Style Bible, storyboard and blocking.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Import an APPROVED screenplay into a new project.")
    init.add_argument("--database", type=Path, default=DEFAULT_DB)
    init.add_argument("--script-id", required=True)
    init.add_argument("--project-dir", type=Path, required=True)

    init_file = commands.add_parser(
        "init-file",
        help="Import a plain script file for exploration only (not an approved screenplay).",
    )
    init_file.add_argument("--script-file", type=Path, required=True)
    init_file.add_argument("--script-id", required=True)
    init_file.add_argument("--project-id", required=True)
    init_file.add_argument("--episode-id")
    init_file.add_argument("--version", type=int, default=1)
    init_file.add_argument("--project-dir", type=Path, required=True)

    analyze = commands.add_parser("analyze", help="Parse the approved screenplay into a visual breakdown.")
    analyze.add_argument("--project-dir", type=Path, required=True)

    art = commands.add_parser("art-direction", help="Build art-direction candidates on one shared scene.")
    art.add_argument("--project-dir", type=Path, required=True)
    art.add_argument("--comparison-scene")

    gen_candidates = commands.add_parser(
        "generate-candidates", help="Generate the comparison image for each candidate."
    )
    gen_candidates.add_argument("--project-dir", type=Path, required=True)
    gen_candidates.add_argument("--comfy-url", default=DEFAULT_COMFY)
    gen_candidates.add_argument("--only", nargs="*")

    select = commands.add_parser("select", help="Record the human selection of an art direction.")
    select.add_argument("--project-dir", type=Path, required=True)
    select.add_argument("--candidate-id", required=True)
    select.add_argument("--actor", default="operator")
    select.add_argument("--note", default="")

    bible = commands.add_parser("style-bible", help="Create a versioned Style Bible from a selected candidate.")
    bible.add_argument("--project-dir", type=Path, required=True)
    bible.add_argument("--candidate-id", required=True)

    storyboard = commands.add_parser("storyboard", help="Generate storyboard images.")
    storyboard.add_argument("--project-dir", type=Path, required=True)
    storyboard.add_argument("--comfy-url", default=DEFAULT_COMFY)
    storyboard.add_argument("--shot", nargs="*")
    storyboard.add_argument("--limit", type=int, default=0)
    storyboard.add_argument(
        "--preset",
        default="",
        help="Generation preset to use, e.g. sdxl_lightning_4step.",
    )

    blocking = commands.add_parser("blocking", help="Generate blocking layouts and images.")
    blocking.add_argument("--project-dir", type=Path, required=True)
    blocking.add_argument("--comfy-url", default=DEFAULT_COMFY)
    blocking.add_argument("--shot", nargs="*")
    blocking.add_argument("--limit", type=int, default=0)
    blocking.add_argument("--generate-images", action="store_true")
    blocking.add_argument(
        "--preset",
        default="",
        help="Generation preset to use, e.g. sdxl_lightning_4step.",
    )

    check = commands.add_parser("check", help="Run deterministic continuity checks.")
    check.add_argument("--project-dir", type=Path, required=True)

    handoff = commands.add_parser("handoff", help="Export the production handoff package.")
    handoff.add_argument("--project-dir", type=Path, required=True)

    status = commands.add_parser("status", help="Show project status.")
    status.add_argument("--project-dir", type=Path, required=True)

    production = commands.add_parser(
        "production", help="Report the whole production spine for a project."
    )
    production.add_argument("--project-dir", type=Path, required=True)

    breakdown = commands.add_parser(
        "breakdown", help="Break the script down into the elements each department needs."
    )
    breakdown.add_argument("--project-dir", type=Path, required=True)

    set_prompt = commands.add_parser(
        "set-prompt", help="Attach your own prompt and settings to a shot or a candidate."
    )
    set_prompt.add_argument("--project-dir", type=Path, required=True)
    set_prompt.add_argument("--target-id", required=True)
    set_prompt.add_argument(
        "--kind", required=True, choices=["SHOT", "ART_DIRECTION_CANDIDATE"]
    )
    set_prompt.add_argument("--prompt-extra", default="")
    set_prompt.add_argument("--prompt-replace", default=None)
    set_prompt.add_argument("--negative-extra", default="")
    set_prompt.add_argument("--exclude-module", action="append", default=[])
    set_prompt.add_argument(
        "--setting",
        action="append",
        default=[],
        help="Override a generation setting, as key=value. Repeatable.",
    )
    set_prompt.add_argument("--workflow-id", default=None)
    set_prompt.add_argument("--note", default="")
    set_prompt.add_argument("--actor", default="operator")

    show_prompt = commands.add_parser(
        "show-prompt", help="Show the effective prompt for a shot or a candidate."
    )
    show_prompt.add_argument("--project-dir", type=Path, required=True)
    show_prompt.add_argument("--target-id", required=True)

    reset_prompt = commands.add_parser(
        "reset-prompt", help="Remove the override on a shot or a candidate."
    )
    reset_prompt.add_argument("--project-dir", type=Path, required=True)
    reset_prompt.add_argument("--target-id", required=True)

    import_workflow = commands.add_parser(
        "import-workflow", help="Store a ComfyUI API-format workflow in the project."
    )
    import_workflow.add_argument("--project-dir", type=Path, required=True)
    import_workflow.add_argument("--file", default=None)
    import_workflow.add_argument("--workflow-id", default=None)

    validate_wf = commands.add_parser(
        "validate-workflow", help="Check a stored workflow against the live ComfyUI server."
    )
    validate_wf.add_argument("--project-dir", type=Path, required=True)
    validate_wf.add_argument("--workflow-id", required=True)
    validate_wf.add_argument("--comfy-url", default=DEFAULT_COMFY)

    animatic = commands.add_parser(
        "animatic", help="Cut the boards to a timed animatic with the voice on it."
    )
    animatic.add_argument("--project-dir", type=Path, required=True)
    animatic.add_argument("--voice", default="af_heart")
    animatic.add_argument("--no-voice", action="store_true")
    animatic.add_argument("--fps", type=int, default=24)

    comfy = commands.add_parser("comfy-check", help="Report live ComfyUI status and models.")
    comfy.add_argument("--comfy-url", default=DEFAULT_COMFY)

    review = commands.add_parser("review", help="Serve the local review UI on loopback.")
    review.add_argument("--project-dir", type=Path, required=True)
    review.add_argument("--host", default="127.0.0.1")
    review.add_argument("--port", type=int, default=8790)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "init": cmd_init,
        "init-file": cmd_init_file,
        "analyze": cmd_analyze,
        "art-direction": cmd_art_direction,
        "generate-candidates": cmd_generate_candidates,
        "select": cmd_select,
        "style-bible": cmd_style_bible,
        "storyboard": cmd_storyboard,
        "blocking": cmd_blocking,
        "check": cmd_check,
        "handoff": cmd_handoff,
        "breakdown": cmd_breakdown,
        "production": cmd_production,
        "set-prompt": cmd_set_prompt,
        "show-prompt": cmd_show_prompt,
        "reset-prompt": cmd_reset_prompt,
        "import-workflow": cmd_import_workflow,
        "validate-workflow": cmd_validate_workflow,
        "animatic": cmd_animatic,
        "status": cmd_status,
        "comfy-check": cmd_comfy_check,
        "review": cmd_review,
    }
    try:
        return handlers[args.command](args)
    except ApprovedScriptError as exc:
        _print({"status": "FAIL", "error": str(exc)})
        return 2
    except (FileNotFoundError, FileExistsError, ValueError, SystemExit) as exc:
        _print({"status": "FAIL", "error": str(exc)})
        return 2


if __name__ == "__main__":
    sys.exit(main())
