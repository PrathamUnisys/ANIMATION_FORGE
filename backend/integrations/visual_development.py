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
        project_dir = self.project_dir(project_id)
        summary = self.summarize(project_id)
        analysis_path = _latest_json(project_dir / "analysis", "analysis")
        candidates_path = _latest_json(project_dir / "art_direction", "candidates")
        style_bible_path = _latest_json(project_dir / "style_bibles", "style_bible")

        analysis = _read_json(analysis_path) if analysis_path else {}
        candidate_set = _read_json(candidates_path) if candidates_path else {}
        style_bible = _read_json(style_bible_path) if style_bible_path else {}

        candidates = []
        for candidate in candidate_set.get("candidates", []):
            manifest = candidate.get("generation_manifest", {})
            candidates.append(
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

        shots = []
        for sequence in analysis.get("sequences", []):
            for scene in sequence.get("scenes", []):
                for shot in scene.get("shots", []):
                    shots.append(
                        {
                            "shot_id": shot.get("shot_id", ""),
                            "sequence_id": sequence.get("sequence_id", ""),
                            "scene_id": scene.get("scene_id", ""),
                            "scene_heading": scene.get("heading", ""),
                            "shot_size": shot.get("camera_shot_type", ""),
                            "purpose": shot.get("purpose", ""),
                            "description": shot.get("visual_description", ""),
                            "duration_sec": shot.get("estimated_duration_sec", 0.0),
                            "production_complexity": shot.get("production_complexity", ""),
                        }
                    )

        generations = self._generations(project_dir)

        return {
            **summary,
            "comparison_scene_id": candidate_set.get("comparison_scene_id", ""),
            "comparison_seed": candidate_set.get("comparison_seed"),
            "candidates": candidates,
            "shots": shots,
            "style_bible": style_bible,
            "generations": generations,
            "review_events": self._events(project_dir),
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

    def _regenerate(self, project_id: str, shot_id: str) -> dict[str, Any]:
        """Regenerate one storyboard image through the module's ComfyUI client.

        The approved image is never overwritten: the module always writes a new
        revision next to it.
        """
        from VISUAL_DEVELOPMENT.approved_script import ApprovedScriptError
        from VISUAL_DEVELOPMENT.cli import _latest
        from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient
        from VISUAL_DEVELOPMENT.generation import generate_image
        from VISUAL_DEVELOPMENT.prompt_builder import build_shot_prompt
        from VISUAL_DEVELOPMENT.style_bible import style_bible_hash

        project_dir = self.project_dir(project_id)
        store = ProjectStore(project_dir)

        analysis_path = _latest(store, "analysis", "analysis")
        style_path = _latest(store, "style_bibles", "style_bible")
        if analysis_path is None or style_path is None:
            raise VisualDevelopmentError("This project has no analysis or Style Bible yet.")
        analysis = store.read(analysis_path.relative_to(store.root).as_posix())
        style_bible = store.read(style_path.relative_to(store.root).as_posix())

        target = None
        for sequence in analysis.get("sequences", []):
            for scene in sequence.get("scenes", []):
                for shot in scene.get("shots", []):
                    if shot.get("shot_id") == shot_id:
                        target = (sequence, scene, shot)
        if target is None:
            raise VisualDevelopmentError(f"Unknown shot: {shot_id}")
        sequence, scene, shot = target

        character_index = {entry["name"]: entry for entry in analysis.get("characters", [])}
        built = build_shot_prompt(style_bible, shot, scene, character_index, mode="storyboard")
        settings = dict(style_bible.get("global_rules", {}).get("generation_settings", {}))
        settings["seed"] = int(settings.get("seed", 1)) + 1

        result = generate_image(
            ComfyUIClient(),
            store,
            artifact_type="STORYBOARD",
            relative_dir=(
                f"storyboard/{sequence['sequence_id']}/{scene['scene_id']}/{shot['shot_id']}"
            ),
            prompt=built["prompt"],
            negative_prompt=built["negative_prompt"],
            settings=settings,
            workflow_id="txt2img_v1",
            shot_id=shot["shot_id"],
            sequence_id=sequence["sequence_id"],
            scene_id=scene["scene_id"],
            style_bible_sha256=style_bible_hash(style_bible),
            source_script_sha256=analysis.get("source_script_sha256", ""),
            filename_prefix=f"SB_{shot['shot_id']}",
            actor="frontend",
        )
        return result
