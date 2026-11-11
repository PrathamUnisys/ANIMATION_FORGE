"""Read-mostly bridge from the Animation Forge API to the isolated Visual
Development module.

This adapter does not reimplement any Visual Development logic. It locates the
module's project packages on disk and exposes them through the local API so the
existing frontend can display the real generated files.

It never writes to the Animation Forge database and never touches the module's
immutable generation artifacts. Decisions (select / approve / reject) are
appended to the module's own append-only review event log.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from VISUAL_DEVELOPMENT.storage import ProjectStore

VISUAL_DEVELOPMENT_PREFIX = "VDEV_"


class VisualDevelopmentError(ValueError):
    """Raised when a visual development project or file cannot be resolved."""


def _ensure_module_importable(root_dir: str | Path) -> None:
    root = Path(root_dir).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _latest_json(folder: Path, prefix: str) -> Path | None:
    if not folder.is_dir():
        return None
    files = sorted(folder.glob(f"{prefix}_v*.json"))
    return files[-1] if files else None


def _count_files(folder: Path, suffix: str) -> int:
    if not folder.is_dir():
        return 0
    return sum(1 for _ in folder.rglob(f"*{suffix}"))


class VisualDevelopmentBridge:
    """Locates and reads Visual Development project packages."""

    def __init__(self, root_dir: str | Path):
        self.root = Path(root_dir).resolve()
        self.projects_dir = self.root / "PROJECTS"
        _ensure_module_importable(self.root)

    # ------------------------------------------------------------- discovery

    def project_ids(self) -> list[str]:
        if not self.projects_dir.is_dir():
            return []
        return sorted(
            entry.name
            for entry in self.projects_dir.iterdir()
            if entry.is_dir()
            and entry.name.startswith(VISUAL_DEVELOPMENT_PREFIX)
            and (entry / "project.json").is_file()
        )

    def project_dir(self, project_id: str) -> Path:
        if not project_id.startswith(VISUAL_DEVELOPMENT_PREFIX) or "/" in project_id or "\\" in project_id:
            raise VisualDevelopmentError(f"Invalid visual development project id: {project_id!r}")
        candidate = (self.projects_dir / project_id).resolve()
        if not candidate.is_relative_to(self.projects_dir.resolve()):
            raise VisualDevelopmentError("Project path escapes the projects directory.")
        if not (candidate / "project.json").is_file():
            raise VisualDevelopmentError(f"Unknown visual development project: {project_id}")
        return candidate

    # ------------------------------------------------------------- summaries

    def list_projects(self) -> list[dict[str, Any]]:
        summaries = []
        for project_id in self.project_ids():
            try:
                summaries.append(self.summarize(project_id))
            except (VisualDevelopmentError, OSError, json.JSONDecodeError):
                continue
        return summaries

    def summarize(self, project_id: str) -> dict[str, Any]:
        project_dir = self.project_dir(project_id)
        manifest = _read_json(project_dir / "project.json")
        source = manifest.get("source_script", {})
        analysis_path = _latest_json(project_dir / "analysis", "analysis")
        candidates_path = _latest_json(project_dir / "art_direction", "candidates")
        style_bible_path = _latest_json(project_dir / "style_bibles", "style_bible")
        continuity_path = _latest_json(project_dir / "reports", "continuity")

        analysis = _read_json(analysis_path) if analysis_path else {}
        continuity = _read_json(continuity_path) if continuity_path else {}
        candidates = _read_json(candidates_path) if candidates_path else {}

        return {
            "project_id": project_id,
            "title": manifest.get("title", project_id),
            "stage": manifest.get("stage", ""),
            "status": manifest.get("status", ""),
            "created_at": manifest.get("created_at", ""),
            "source_script": {
                "script_id": source.get("script_id", ""),
                "approval_status": source.get("approval_status", "UNKNOWN"),
                "sha256": source.get("sha256", ""),
                "source_type": source.get("source_type", "DATABASE"),
            },
            "source_format": analysis.get("source_format", ""),
            "episode": analysis.get("episode", {}),
            "counts": {
                "sequences": len(analysis.get("sequences", [])),
                "shots": sum(
                    len(scene.get("shots", []))
                    for sequence in analysis.get("sequences", [])
                    for scene in sequence.get("scenes", [])
                ),
                # Candidates and images are different numbers once a direction
                # has been regenerated: the artifact store keeps every image.
                "art_direction_candidates": len(candidates.get("candidates", [])),
                "art_direction_images": _count_files(project_dir / "art_direction", ".png"),
                "storyboard_images": _count_files(project_dir / "storyboard", ".png"),
                "blocking_images": _count_files(project_dir / "blocking", ".png"),
            },
            "has_style_bible": style_bible_path is not None,
            "style_identity": (
                _read_json(style_bible_path).get("style_identity", "") if style_bible_path else ""
            ),
            "continuity_status": continuity.get("status", "NOT_RUN"),
            "open_questions": analysis.get("open_questions", []),
        }

    def detail(self, project_id: str) -> dict[str, Any]:
        """One package, in the shape the application consumes.

        The facts come from the shared project service, which is the same
        implementation the standalone review page uses, so the two can never
        disagree about what a package holds.
        """
        from VISUAL_DEVELOPMENT.service import project_state
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        project_dir = self.project_dir(project_id)
        store = ProjectStore(project_dir)
        state = project_state(store)
        summary = self.summarize(project_id)

        return {
            **summary,
            "comparison_scene_id": state["candidates"].get("comparison_scene_id", ""),
            "comparison_seed": state["candidates"].get("comparison_seed"),
            "candidates": state["candidates"]["candidates"],
            "shots": state["shots"],
            "style_bible": state["style_bible"],
            "generations": self._generations(project_dir),
            "review_events": state["events"],
            "breakdown": state["breakdown"],
            "animatic": state["animatic"],
        }

    def _generations(self, project_dir: Path) -> list[dict[str, Any]]:
        generations = []
        for manifest_path in sorted(project_dir.rglob("GEN_*.json")):
            try:
                manifest = _read_json(manifest_path)
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(manifest, dict) or not manifest.get("generation_id"):
                continue
            generations.append(
                {
                    "generation_id": manifest.get("generation_id", ""),
                    "artifact_type": manifest.get("artifact_type", ""),
                    "shot_id": manifest.get("shot_id", ""),
                    "image_path": manifest.get("image_path", ""),
                    "review_status": manifest.get("review_status", "PENDING"),
                    "model": manifest.get("model", ""),
                    "seed": manifest.get("seed"),
                    "prompt_id": manifest.get("comfyui_prompt_id", ""),
                }
            )
        return generations

    def _events(self, project_dir: Path) -> list[dict[str, Any]]:
        path = project_dir / "reviews" / "review_events.jsonl"
        if not path.is_file():
            return []
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return events

    # ------------------------------------------------------------- production

    def pipeline(self, project_id: str) -> dict[str, Any]:
        """The whole production spine for one project."""
        from VISUAL_DEVELOPMENT.production import pipeline_status
        from VISUAL_DEVELOPMENT.service import project_state
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        store = ProjectStore(self.project_dir(project_id))
        status = pipeline_status(store)
        state = project_state(store)
        # The rollup counts the shots per status; the list is the shots.
        counts = status.pop("shots", {})
        status["shot_total"] = counts.get("total", 0)
        status["shot_statuses"] = counts.get("statuses", {})
        status["candidates"] = state["candidates"]["candidates"]
        status["shots"] = state["shots"]
        status["overrides"] = self._overrides(project_id)
        return status

    def _overrides(self, project_id: str) -> list[dict[str, Any]]:
        path = self.project_dir(project_id) / "PROMPTS" / "prompt_overrides_v001.json"
        if not path.is_file():
            return []
        value = _read_json(path)
        overrides = value.get("overrides", {}) if isinstance(value, dict) else {}
        return [
            {
                "target_id": target_id,
                "kind": override.get("kind", ""),
                "prompt_extra": override.get("prompt_extra", ""),
                "prompt_replace": override.get("prompt_replace"),
                "negative_extra": override.get("negative_extra", ""),
                "exclude_modules": override.get("exclude_modules", []),
                "settings_override": override.get("settings_override", {}),
                "workflow_id": override.get("workflow_id"),
                "updated_at": override.get("updated_at", ""),
                "actor": override.get("actor", ""),
                "note": override.get("note", ""),
            }
            for target_id, override in sorted(overrides.items())
        ]

    def breakdown(self, project_id: str) -> dict[str, Any]:
        """The script breakdown for one project."""
        path = _latest_json(self.project_dir(project_id) / "breakdown", "breakdown")
        if path is None:
            return {"status": "NOT_RUN", "scenes": [], "summary": {}, "taxonomy": []}
        return _read_json(path)

    def effective_prompt(self, project_id: str, target_id: str) -> dict[str, Any]:
        """The generated prompt, the user's override and the merged result."""
        from VISUAL_DEVELOPMENT.prompt_builder import build_candidate_prompt, build_shot_prompt
        from VISUAL_DEVELOPMENT.prompt_overrides import (
            effective_prompt as merge_prompt,
            effective_settings,
            get_override,
        )
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        project_dir = self.project_dir(project_id)
        store = ProjectStore(project_dir)
        detail = self.detail(project_id)
        analysis_path = _latest_json(project_dir / "analysis", "analysis")
        style_bible_path = _latest_json(project_dir / "style_bibles", "style_bible")
        candidates_path = _latest_json(project_dir / "art_direction", "candidates")
        analysis = _read_json(analysis_path) if analysis_path else {}
        style_bible = _read_json(style_bible_path) if style_bible_path else {}
        candidate_set = _read_json(candidates_path) if candidates_path else {}
        override = get_override(store, target_id)

        characters = {entry["name"]: entry for entry in analysis.get("characters", [])}
        shot = None
        scene = None
        for sequence in analysis.get("sequences", []):
            for candidate_scene in sequence.get("scenes", []):
                for candidate_shot in candidate_scene.get("shots", []):
                    if candidate_shot.get("shot_id") == target_id:
                        shot = candidate_shot
                        scene = candidate_scene

        if shot is not None:
            built = build_shot_prompt(style_bible, shot, scene, characters, mode="storyboard")
            settings = dict(style_bible.get("global_rules", {}).get("generation_settings", {}))
            kind = "SHOT"
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
                raise VisualDevelopmentError(f"Unknown target: {target_id}")
            comparison_scene = None
            for sequence in analysis.get("sequences", []):
                for candidate_scene in sequence.get("scenes", []):
                    if (
                        candidate_scene.get("scene_id")
                        == candidate_set.get("comparison_scene_id")
                    ):
                        comparison_scene = candidate_scene
            built = build_candidate_prompt(
                candidate.get("style_prompt", ""), comparison_scene, characters
            )
            settings = {
                "seed": candidate_set.get("comparison_seed"),
                "model": "dreamshaper_8.safetensors",
            }
            kind = "ART_DIRECTION_CANDIDATE"

        merged = merge_prompt(built, override)
        resolved = effective_settings(settings, override)
        return {
            "target_id": target_id,
            "kind": kind,
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
            "override": override,
        }

    def save_override(self, project_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Store the user's own prompt and settings for a shot or a candidate."""
        from VISUAL_DEVELOPMENT.prompt_overrides import build_override, save_override
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        store = ProjectStore(self.project_dir(project_id))
        target_id = str(payload.get("target_id", ""))
        kind = str(payload.get("kind", ""))
        if not target_id:
            raise VisualDevelopmentError("target_id is required")
        override = build_override(
            target_id,
            kind or ("SHOT" if target_id.startswith("SHT_") else "ART_DIRECTION_CANDIDATE"),
            prompt_extra=str(payload.get("prompt_extra", "")),
            prompt_replace=payload.get("prompt_replace") or None,
            negative_extra=str(payload.get("negative_extra", "")),
            exclude_modules=list(payload.get("exclude_modules") or []),
            settings_override=dict(payload.get("settings_override") or {}),
            workflow_id=payload.get("workflow_id") or None,
            note=str(payload.get("note", "")),
            actor=str(payload.get("actor", "frontend")),
        )
        save_override(store, override)
        return {"status": "PASS", "override": override}

    def clear_override(self, project_id: str, target_id: str) -> dict[str, Any]:
        from VISUAL_DEVELOPMENT.prompt_overrides import clear_override
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        store = ProjectStore(self.project_dir(project_id))
        removed = clear_override(store, target_id)
        return {"status": "PASS" if removed else "NOTHING_TO_RESET", "removed": removed}

    def validate_workflow(self, project_id: str, workflow: dict[str, Any]) -> dict[str, Any]:
        """Check a user supplied API-format workflow against the live server."""
        from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient
        from VISUAL_DEVELOPMENT.workflows import validate_user_workflow

        client = ComfyUIClient()
        report = validate_user_workflow(client, workflow)
        return report

    def presets(self) -> list[dict[str, Any]]:
        """The generation presets a user can choose from."""
        from VISUAL_DEVELOPMENT.presets import preset_summary

        return preset_summary()

    def list_workflows(self, project_id: str) -> list[dict[str, Any]]:
        folder = self.project_dir(project_id) / "PROMPTS" / "workflows"
        if not folder.is_dir():
            return []
        return [
            {"workflow_id": path.stem, "path": f"PROMPTS/workflows/{path.name}"}
            for path in sorted(folder.glob("*.json"))
        ]

    def animatic(self, project_id: str) -> dict[str, Any]:
        """The animatic timeline and, when it was rendered, the video."""
        path = _latest_json(self.project_dir(project_id) / "animatic", "animatic")
        if path is None:
            return {"status": "NOT_RUN", "entries": [], "summary": {}}
        manifest = _read_json(path)
        video_path = manifest.get("video_path", "")
        # The manifest holds an absolute path from the machine that rendered it.
        # The package is what matters, so the path is reported relative to it.
        relative = ""
        if video_path:
            try:
                relative = (
                    Path(video_path).resolve().relative_to(self.project_dir(project_id)).as_posix()
                )
            except ValueError:
                relative = video_path
        manifest["video_relative_path"] = relative
        manifest["status"] = "PASS" if relative else "NOT_RENDERED"
        return manifest

    # ----------------------------------------------------------------- media

    def media(self, project_id: str, relative_path: str) -> Path:
        """Resolve a file inside a project package with containment enforced."""
        from VISUAL_DEVELOPMENT.common import contained_path

        project_dir = self.project_dir(project_id)
        try:
            resolved = contained_path(project_dir, relative_path)
        except ValueError as exc:
            raise VisualDevelopmentError(str(exc)) from exc
        if not resolved.is_file():
            raise VisualDevelopmentError(f"No such file in project: {relative_path}")
        return resolved

    # -------------------------------------------------------------- decisions

    def record_decision(
        self,
        project_id: str,
        action: str,
        target_type: str,
        target_id: str,
        actor: str = "frontend",
        note: str = "",
    ) -> dict[str, Any]:
        """Record a human decision in the module's own append-only event log."""
        from VISUAL_DEVELOPMENT.approved_script import ApprovedScriptError
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        project_dir = self.project_dir(project_id)
        store = ProjectStore(project_dir)
        if action == "SELECT":
            from VISUAL_DEVELOPMENT.art_direction import select_candidate
            from VISUAL_DEVELOPMENT.cli import _latest

            candidates_path = _latest(store, "art_direction", "candidates")
            if candidates_path is None:
                raise VisualDevelopmentError("This project has no art-direction candidate set.")
            candidate_set = store.read(candidates_path.relative_to(store.root).as_posix())
            select_candidate(candidate_set, target_id)
            store.update_json(
                candidates_path.relative_to(store.root).as_posix(),
                candidate_set,
                "candidate.schema.json",
            )
        elif action in {"APPROVE", "REJECT"}:
            status = {"APPROVE": "APPROVED", "REJECT": "REJECTED"}.get(action, action)
            for manifest_path in sorted(store.root.rglob("*.json")):
                relative = manifest_path.relative_to(store.root).as_posix()
                if relative.startswith(("source/", "analysis/", "style_bibles/", "reports/")):
                    continue
                try:
                    value = store.read(relative)
                except (ValueError, json.JSONDecodeError):
                    continue
                if not isinstance(value, dict) or not value.get("generation_id"):
                    continue
                if value.get("artifact_type") != target_type:
                    continue
                if value.get("shot_id") != target_id and value.get("generation_id") != target_id:
                    continue
                value["review_status"] = status
                store.update_json(relative, value)
        elif action == "REGENERATE":
            self._regenerate(project_id, target_id)
        else:
            raise VisualDevelopmentError(f"Unsupported decision action: {action!r}")

        from VISUAL_DEVELOPMENT.common import new_id, utc_now

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

    # --------------------------------------------------------- regeneration

    def approve_style_bible(self, project_id: str, actor: str = "frontend") -> dict[str, Any]:
        """Approve the current Style Bible.

        The Style Bible is immutable, so the approval is an event in the
        append-only log rather than an edit of the file.
        """
        from VISUAL_DEVELOPMENT.service import record_decision, style_bible_status
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        store = ProjectStore(self.project_dir(project_id))
        state = style_bible_status(store)
        if state["status"] == "NOT_FOUND":
            raise VisualDevelopmentError("This project has no Style Bible to approve.")
        if state["approved"]:
            return {"status": "PASS", "approved": True, "message": "Already approved."}
        record_decision(
            store,
            "APPROVE",
            "STYLE_BIBLE",
            state["style_bible_id"],
            actor=actor,
            note="Style Bible approved",
        )
        return {"status": "PASS", "approved": True, "style_bible_id": state["style_bible_id"]}

    def script(self, project_id: str) -> dict[str, Any]:
        """The script the package was built from.

        You cannot judge the boards of a script you cannot read, so the text
        is part of the workspace.
        """
        path = self.project_dir(project_id) / "source" / "approved_script.md"
        if not path.is_file():
            return {"status": "NOT_FOUND", "text": "", "source_format": ""}
        manifest = _read_json(
            self.project_dir(project_id) / "source" / "script_manifest.json"
        )
        return {
            "status": "PASS",
            "text": path.read_text(encoding="utf-8"),
            "script_id": manifest.get("script_id", ""),
            "approval_status": manifest.get("approval_status", "UNKNOWN"),
            "sha256": manifest.get("sha256", ""),
        }

    def plan(self, project_id: str, target_id: str) -> dict[str, Any]:
        """What would be sent to the image service for one target.

        The same plan the command line uses, so the user can see exactly what
        their override produces before spending a generation on it.
        """
        from VISUAL_DEVELOPMENT.service import resolve_plan
        from VISUAL_DEVELOPMENT.storage import ProjectStore

        store = ProjectStore(self.project_dir(project_id))
        try:
            plan = resolve_plan(store, target_id)
        except KeyError as exc:
            raise VisualDevelopmentError(str(exc)) from exc
        plan.pop("user_workflow", None)
        plan.pop("shot", None)
        plan.pop("scene", None)
        plan.pop("candidate", None)
        return plan

    def generate(self, project_id: str, target_id: str, artifact_type: str = "STORYBOARD") -> dict[str, Any]:
        """Generate one image for a target, with the user's prompt and settings.

        This is the path the workspace uses, and it is the same path the command
        line uses, so a picture made in the browser is the picture the command
        line would make.
        """
        from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient
        from VISUAL_DEVELOPMENT.service import regenerate

        store = ProjectStore(self.project_dir(project_id))
        try:
            return regenerate(
                store,
                ComfyUIClient(),
                target_id,
                artifact_type=artifact_type,
                actor="frontend",
            )
        except KeyError as exc:
            raise VisualDevelopmentError(str(exc)) from exc

    def _regenerate(self, project_id: str, shot_id: str) -> dict[str, Any]:
        """Regenerate one storyboard image through the module's ComfyUI client.

        The plan comes from the shared project service, so the image is made
        with the prompt, the settings and the workflow the user configured,
        exactly as the command line would make it. The approved image is never
        overwritten: the module always writes a new revision next to it.
        """
        from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient
        from VISUAL_DEVELOPMENT.service import regenerate

        store = ProjectStore(self.project_dir(project_id))
        try:
            return regenerate(
                store,
                ComfyUIClient(),
                shot_id,
                artifact_type="STORYBOARD",
                actor="frontend",
            )
        except KeyError as exc:
            raise VisualDevelopmentError(str(exc)) from exc
