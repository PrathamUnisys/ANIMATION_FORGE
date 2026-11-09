import os
import json
import mimetypes
import uvicorn
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field
from backend.database import DatabaseManager, DEFAULT_DB_PATH
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine, ApprovalPolicyViolationError
from backend.governance.local_ipc import TRUSTED_IPC_ORIGINS, verify_local_ipc_token
from backend.governance.windows_reviewer import (
    HumanConfirmationDeclinedError,
    WindowsReviewerUnavailableError,
    confirm_windows_human_decision,
)
from backend.rnd.research_engine import ProductionRndEngine
from backend.integrations.mcp_gateway import AnimationForgeMcpGateway
from backend.integrations.comfyui_adapter import ComfyUIAdapter
from backend.qc.quality_controller import QualityControlEngine
from backend.qc.screenplay_qc import DeterministicValidator, CreativeCritique
from backend.providers.manager import ProviderManager, ProviderError
from backend.departments.story_pipeline import StoryAndScreenplayPipeline
from backend.departments.story_context import StoryContextService
from backend.filesystem_security import is_safe_path_component

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Animation Forge Local Production Engine",
    version="1.0.0",
    description="Tool-Agnostic, AI-Driven, Human-Directed Animation Production OS Sidecar API"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(TRUSTED_IPC_ORIGINS),
    allow_methods=["GET", "POST"],
    allow_headers=["content-type", "x-forge-token"],
)

db = DatabaseManager(DEFAULT_DB_PATH)
governance = GovernanceEngine(ROOT_DIR, db)
approvals = ApprovalEngine(db)
rnd_engine = ProductionRndEngine(ROOT_DIR, db, approvals)
mcp_gateway = AnimationForgeMcpGateway(db)
comfyui = ComfyUIAdapter(ROOT_DIR, db)
qc_engine = QualityControlEngine(db)
provider_manager = ProviderManager(db)
story_pipeline = StoryAndScreenplayPipeline(ROOT_DIR, db, approvals)
story_ctx = StoryContextService(ROOT_DIR, db)


class HumanDecisionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    approval_id: str
    decision: str
    comments: str = Field(max_length=4000)
    rationale: Optional[str] = Field(default=None, max_length=4000)


class CreateProjectPayload(BaseModel):
    project_id: str
    title: str
    synopsis: str
    genre: str
    target_audience: str
    intended_runtime_sec: int
    language: str = "en-US"
    creative_brief: str = ""
    visual_direction: str = ""
    animation_technique: str = "HYBRID"


@app.get("/api/health")
def get_health(_: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    integrity = db.run_integrity_check()
    return {
        "status": "healthy" if integrity["ok"] else "degraded",
        "architecture_version": governance.get_active_architecture_version(),
        "database_integrity": integrity,
        "bound_interface": "127.0.0.1"
    }


@app.get("/api/dashboard")
def get_dashboard_summary(_: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        projects = [dict(r) for r in conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()]
        pending_approvals = [dict(r) for r in conn.execute("SELECT * FROM approvals WHERE state = 'AWAITING_HUMAN_REVIEW'").fetchall()]
        all_approvals = [dict(r) for r in conn.execute("SELECT * FROM approvals ORDER BY decided_at DESC LIMIT 25").fetchall()]
        assets = [dict(r) for r in conn.execute("SELECT * FROM assets ORDER BY created_at DESC").fetchall()]
        toolchains = [dict(r) for r in conn.execute("SELECT * FROM toolchain_profiles ORDER BY version DESC").fetchall()]
        integrations = [dict(r) for r in conn.execute("SELECT * FROM integrations").fetchall()]
        decisions = [dict(r) for r in conn.execute("SELECT * FROM creative_decisions ORDER BY decided_at DESC LIMIT 15").fetchall()]
        qc_reports = [dict(r) for r in conn.execute("SELECT * FROM qc_reports ORDER BY created_at DESC").fetchall()]
    return {
        "projects": projects,
        "pending_approvals": pending_approvals,
        "recent_approvals": all_approvals,
        "recent_assets": assets,
        "toolchains": toolchains,
        "integrations": integrations,
        "creative_decisions": decisions,
        "qc_reports": qc_reports,
    }


@app.post("/api/projects")
def create_project(
    payload: CreateProjectPayload,
    _: str = Depends(verify_local_ipc_token),
) -> Dict[str, Any]:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    with db.get_connection() as conn:
        conn.execute(
            """INSERT INTO projects
               (project_id, title, synopsis, genre, target_audience, intended_runtime_sec, language, creative_brief, visual_direction, animation_technique, production_goals_json, restrictions_json, status, current_stage, active_mode, series_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', '[]', 'ACTIVE', 'USER_STORY_IDEA', 'PRODUCTION_MODE', NULL, ?, ?)""",
            (
                payload.project_id, payload.title, payload.synopsis, payload.genre,
                payload.target_audience, payload.intended_runtime_sec, payload.language,
                payload.creative_brief, payload.visual_direction, payload.animation_technique,
                now, now
            )
        )
        conn.commit()
    return {"project_id": payload.project_id, "status": "ACTIVE", "current_stage": "USER_STORY_IDEA"}


@app.post("/api/approvals/decide")
def submit_approval_decision(
    payload: HumanDecisionPayload,
    _: str = Depends(verify_local_ipc_token),
) -> Dict[str, Any]:
    try:
        if payload.decision not in {"APPROVED", "REVISION_REQUESTED", "REJECTED"}:
            raise ApprovalPolicyViolationError(f"Invalid human review decision: {payload.decision}")
        gate = approvals.get_gate(payload.approval_id)
        if gate["state"] != "AWAITING_HUMAN_REVIEW":
            raise ApprovalPolicyViolationError(
                f"Deliverable is in state '{gate['state']}', not 'AWAITING_HUMAN_REVIEW'."
            )
        human_user_id = confirm_windows_human_decision(
            gate,
            payload.decision,
            payload.comments,
            payload.rationale,
        )
        return approvals.submit_human_decision(
            approval_id=payload.approval_id,
            decision=payload.decision,
            human_user_id=human_user_id,
            comments=payload.comments,
            rationale_for_memory=payload.rationale
        )
    except ApprovalPolicyViolationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except HumanConfirmationDeclinedError as exc:
        raise HTTPException(status_code=403, detail="Windows reviewer declined the decision") from exc
    except WindowsReviewerUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# CR_004: Project workspace read layer (Workflow Stepper, Output Viewer &
# Debug Explorer). All routes are read-only, IPC-token protected, and return
# only records/files that actually exist. Missing values are null / labelled
# NOT_TRACKED, PLANNED_UNAVAILABLE, SIMULATED or NOT_AVAILABLE — never invented.
# ---------------------------------------------------------------------------

WORKFLOW_STAGES: List[str] = [
    "USER_STORY_IDEA",
    "STORY_ANALYSIS",
    "SCRIPT_DEVELOPMENT",
    "SCREENPLAY_APPROVAL",
    "PRODUCTION_REQUIREMENT_ANALYSIS",
    "ONLINE_TOOL_RESEARCH_AND_RND",
    "TOOL_COMPARISON",
    "PROOF_OF_CONCEPT",
    "HUMAN_TOOLCHAIN_APPROVAL",
    "PRODUCTION_PLANNING",
    "AUDIO_AND_VISUAL_PRODUCTION",
    "STORYBOARD_AND_ANIMATIC",
    "ANIMATION",
    "POST_PRODUCTION",
    "QUALITY_CONTROL",
    "HUMAN_FINAL_APPROVAL",
    "COMPLETED_PRODUCTION_PACKAGE",
]

# Honest capability maturity per stage (README.md implementation-status table).
STAGE_CAPABILITY: Dict[str, str] = {
    "USER_STORY_IDEA": "IMPLEMENTED",
    "STORY_ANALYSIS": "PARTIAL",
    "SCRIPT_DEVELOPMENT": "PARTIAL",
    "SCREENPLAY_APPROVAL": "PARTIAL",
    "PRODUCTION_REQUIREMENT_ANALYSIS": "PARTIAL",
    "ONLINE_TOOL_RESEARCH_AND_RND": "PARTIAL",
    "TOOL_COMPARISON": "PARTIAL",
    "PROOF_OF_CONCEPT": "NOT_VERIFIED",
    "HUMAN_TOOLCHAIN_APPROVAL": "PARTIAL",
    "PRODUCTION_PLANNING": "PARTIAL",
    "AUDIO_AND_VISUAL_PRODUCTION": "SIMULATED",
    "STORYBOARD_AND_ANIMATIC": "PARTIAL",
    "ANIMATION": "UNAVAILABLE",
    "POST_PRODUCTION": "SIMULATED",
    "QUALITY_CONTROL": "SIMULATED",
    "HUMAN_FINAL_APPROVAL": "PARTIAL",
    "COMPLETED_PRODUCTION_PACKAGE": "NOT_VERIFIED",
}

STAGE_CAPABILITY_NOTES: Dict[str, str] = {
    "SCRIPT_DEVELOPMENT": "Current pipeline emits a fixed demonstration screenplay, not premise-driven LLM generation.",
    "AUDIO_AND_VISUAL_PRODUCTION": "Audio WAVs are sine-tone demo files; image/storyboard files come from the demo runner. No live TTS/ComfyUI/Blender execution.",
    "ANIMATION": "No animation execution capability is implemented.",
    "POST_PRODUCTION": "Subtitle/timeline files exist from the demo runner; no live editor execution is verified.",
    "QUALITY_CONTROL": "QC reports are predetermined checks (quality_controller.py); no media inspection occurs.",
    "HUMAN_FINAL_APPROVAL": "Approval route exists but reviewer identity is not securely authenticated (see HUMAN_APPROVAL_POLICY).",
}

_ALLOWED_FILE_EXTENSIONS = {
    ".md", ".txt", ".json", ".srt", ".otio", ".py",
    ".png", ".jpg", ".jpeg", ".wav", ".mp4",
}
_MAX_FILE_BYTES = 25 * 1024 * 1024
_SECRET_KEY_HINTS = ("secret", "token", "password", "passwd", "api_key", "apikey", "credential", "private_key", "access_key")


def _rows(conn: Any, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def _parse_json(value: Any, fallback: Any = None) -> Any:
    if value is None:
        return fallback
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return fallback


def _redact(obj: Any) -> Any:
    """Server-side redaction for debug payloads: never leak secret-like fields."""
    if isinstance(obj, dict):
        out: Dict[str, Any] = {}
        for key, val in obj.items():
            lowered = str(key).lower()
            if any(hint in lowered for hint in _SECRET_KEY_HINTS):
                out[key] = "[REDACTED]"
            else:
                out[key] = _redact(val)
        return out
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


def _require_project(conn: Any, project_id: str) -> Dict[str, Any]:
    if not is_safe_path_component(project_id):
        raise HTTPException(status_code=400, detail="Invalid project_id")
    row = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    return dict(row)


def _project_dir(project_id: str) -> Path:
    return (Path(ROOT_DIR) / "PROJECTS" / project_id).resolve()


def _list_project_files(project_id: str) -> List[str]:
    base = _project_dir(project_id)
    found: List[str] = []
    if not base.is_dir():
        return found
    for path in sorted(base.rglob("*")):
        if path.is_file() and path.suffix.lower() in _ALLOWED_FILE_EXTENSIONS:
            found.append(path.relative_to(base).as_posix())
    return found


def _resolve_project_file(project_id: str, rel_path: str) -> Path:
    if not is_safe_path_component(project_id):
        raise HTTPException(status_code=400, detail="Invalid project_id")
    if not rel_path or "\\" in rel_path or rel_path.startswith("/") or ":" in rel_path:
        raise HTTPException(status_code=400, detail="Invalid file path")
    parts = [p for p in rel_path.split("/") if p not in ("", ".")]
    if not parts or any(p == ".." for p in parts):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if Path(rel_path).suffix.lower() not in _ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="File type not allowed")
    base = _project_dir(project_id)
    candidate = (base / Path(*parts)).resolve()
    # Containment check after resolve(): defeats traversal and symlink escapes.
    if candidate != base and base not in candidate.parents:
        raise HTTPException(status_code=403, detail="File is outside the project directory")
    if not candidate.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    if candidate.stat().st_size > _MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large to serve")
    return candidate


def _count(conn: Any, table: str, project_id: str) -> int:
    try:
        row = conn.execute(f"SELECT COUNT(*) AS c FROM {table} WHERE project_id = ?", (project_id,)).fetchone()
        return int(row["c"]) if row else 0
    except Exception:
        return 0


def _latest_approval_state(conn: Any, project_id: str, target_type: str) -> Optional[str]:
    row = conn.execute(
        "SELECT state FROM approvals WHERE project_id = ? AND target_type = ? ORDER BY decided_at DESC LIMIT 1",
        (project_id, target_type),
    ).fetchone()
    return row["state"] if row else None


def _build_steps(conn: Any, project: Dict[str, Any]) -> List[Dict[str, Any]]:
    project_id = project["project_id"]
    current = project.get("current_stage")
    files = _list_project_files(project_id)
    by_folder: Dict[str, int] = {}
    for rel in files:
        folder = rel.split("/")[0] if "/" in rel else ""
        by_folder[folder] = by_folder.get(folder, 0) + 1

    counts: Dict[str, int] = {
        table: _count(conn, table, project_id)
        for table in (
            "scripts", "scenes", "shots", "audio_assets", "assets", "asset_revisions",
            "research_reports", "tool_candidates", "tool_evaluations", "toolchain_profiles",
            "tasks", "qc_reports", "agent_executions", "generation_jobs", "approvals",
            "characters", "environments",
        )
    }
    script_approval = _latest_approval_state(conn, project_id, "script")

    # stage -> (output_count, approval_state, not_tracked_when_empty)
    stage_evidence: Dict[str, Any] = {
        "USER_STORY_IDEA": (1, None, False),
        "STORY_ANALYSIS": (by_folder.get("STORY_BIBLE", 0), None, False),
        "SCRIPT_DEVELOPMENT": (counts["scripts"], None, False),
        "SCREENPLAY_APPROVAL": (_count(conn, "approvals", project_id) if script_approval else 0, script_approval, False),
        "PRODUCTION_REQUIREMENT_ANALYSIS": (counts["scenes"], None, True),
        "ONLINE_TOOL_RESEARCH_AND_RND": (counts["research_reports"] + by_folder.get("RND", 0), None, False),
        "TOOL_COMPARISON": (counts["tool_candidates"] + counts["tool_evaluations"], None, False),
        "PROOF_OF_CONCEPT": (counts["generation_jobs"], None, True),
        "HUMAN_TOOLCHAIN_APPROVAL": (counts["toolchain_profiles"] + by_folder.get("TOOLCHAIN", 0), _latest_approval_state(conn, project_id, "asset"), False),
        "PRODUCTION_PLANNING": (counts["tasks"], None, True),
        "AUDIO_AND_VISUAL_PRODUCTION": (counts["audio_assets"] + counts["assets"] + counts["asset_revisions"], None, False),
        "STORYBOARD_AND_ANIMATIC": (counts["shots"] + by_folder.get("STORYBOARDS", 0) + by_folder.get("ANIMATICS", 0), None, False),
        "ANIMATION": (by_folder.get("DRAFTS", 0), None, True),
        "POST_PRODUCTION": (by_folder.get("EDITING", 0), None, True),
        "QUALITY_CONTROL": (counts["qc_reports"], None, False),
        "HUMAN_FINAL_APPROVAL": (counts["approvals"], _latest_approval_state(conn, project_id, "asset"), False),
        "COMPLETED_PRODUCTION_PACKAGE": (0, None, True),
    }

    steps: List[Dict[str, Any]] = []
    for index, stage in enumerate(WORKFLOW_STAGES, start=1):
        outputs, approval_state, not_tracked = stage_evidence[stage]
        capability = STAGE_CAPABILITY[stage]
        if stage == "USER_STORY_IDEA" and outputs > 0:
            progress = "DONE"
        elif capability == "UNAVAILABLE":
            # No execution capability exists; draft files are not stage outputs.
            progress = "PLANNED_UNAVAILABLE"
        elif stage == "COMPLETED_PRODUCTION_PACKAGE" and outputs == 0:
            # Never show COMPLETED when deliverables/approvals are unverifiable.
            progress = "NOT_TRACKED"
        elif outputs > 0:
            progress = "DONE" if approval_state == "APPROVED" else "CURRENT"
        elif stage == current:
            progress = "CURRENT"
        elif not_tracked:
            progress = "NOT_TRACKED"
        else:
            progress = "NOT_STARTED"
        blockers: List[str] = []
        if approval_state == "AWAITING_HUMAN_REVIEW":
            blockers.append("Awaiting human review (not an execution failure)")
        if capability in ("UNAVAILABLE",):
            blockers.append("No implemented capability for this stage")
        steps.append({
            "stage_number": index,
            "stage": stage,
            "progress": progress,
            "capability_status": capability,
            "capability_note": STAGE_CAPABILITY_NOTES.get(stage),
            "evidence_status": "AVAILABLE" if outputs > 0 else "MISSING",
            "input_count": 1 if index > 1 else 0,
            "output_count": outputs,
            "approval_state": approval_state,
            "is_current_stage": stage == current,
            "blockers": blockers,
            "warnings": [],
        })
    return steps


@app.get("/api/projects")
def list_projects(_: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        projects = _rows(conn, "SELECT * FROM projects ORDER BY updated_at DESC")
    return {"projects": projects, "count": len(projects)}


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        project = _require_project(conn, project_id)
        return {"project": project}


@app.get("/api/projects/{project_id}/steps")
def get_project_steps(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        project = _require_project(conn, project_id)
        steps = _build_steps(conn, project)
    return {"project_id": project_id, "current_stage": project.get("current_stage"), "steps": steps}


@app.get("/api/projects/{project_id}/scripts")
def list_scripts(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        rows = _rows(conn, "SELECT script_id, project_id, version, previous_version, change_summary, agent_responsible, reason_for_changes, reviewer_comments, scores_json, passes_completed_json, approval_status, is_immutable, created_at FROM scripts WHERE project_id = ? ORDER BY version DESC", (project_id,))
    for row in rows:
        row["scores"] = _parse_json(row.pop("scores_json"), {})
        row["passes_completed"] = _parse_json(row.pop("passes_completed_json"), [])
    return {"project_id": project_id, "scripts": rows, "count": len(rows)}


@app.get("/api/projects/{project_id}/scripts/{script_id}")
def get_script(project_id: str, script_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        row = conn.execute("SELECT * FROM scripts WHERE project_id = ? AND script_id = ?", (project_id, script_id)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Script '{script_id}' not found")
        script = dict(row)
    script["scores"] = _parse_json(script.pop("scores_json"), {})
    script["passes_completed"] = _parse_json(script.pop("passes_completed_json"), [])
    # Detect DB-vs-file disagreement; never silently pick one.
    file_rel = f"SCRIPTS/{script_id}.md"
    file_markdown: Optional[str] = None
    consistent: Optional[bool] = None
    try:
        file_path = _resolve_project_file(project_id, file_rel)
        file_markdown = file_path.read_text(encoding="utf-8")
        consistent = file_markdown.strip() == (script.get("content_markdown") or "").strip()
    except HTTPException:
        file_markdown = None
        consistent = None
    script["file_path"] = file_rel if file_markdown is not None else None
    script["file_content_markdown"] = file_markdown
    script["db_file_consistent"] = consistent
    if consistent is False:
        script["warnings"] = ["Database screenplay differs from SCRIPTS file; both are shown, neither was silently preferred."]
    return {"project_id": project_id, "script": script}


@app.get("/api/projects/{project_id}/audio")
def list_audio(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        rows = _rows(conn, "SELECT * FROM audio_assets WHERE project_id = ? ORDER BY line_id", (project_id,))
    for row in rows:
        payload = _parse_json(row.pop("tts_payload_json"), {})
        row["tts_payload"] = _redact(payload)
        # Model is recorded only inside the TTS payload, not as a DB column.
        row["model"] = payload.get("model_id") if isinstance(payload, dict) else None
        row["pronunciation_notes"] = _parse_json(row.pop("pronunciation_notes_json"), {})
        row["synthesis_note"] = "Current backend writes sine-tone demo WAVs, not provider speech. Playback is a tone, not spoken dialogue."
    return {"project_id": project_id, "audio_lines": rows, "count": len(rows)}


@app.get("/api/projects/{project_id}/assets")
def list_assets(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        assets = _rows(conn, "SELECT * FROM assets WHERE project_id = ? ORDER BY asset_id", (project_id,))
        revisions = _rows(conn, "SELECT * FROM asset_revisions WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    by_asset: Dict[str, List[Dict[str, Any]]] = {}
    for rev in revisions:
        rev["workflow"] = _redact(_parse_json(rev.pop("workflow_json"), {}))
        rev["input_references"] = _parse_json(rev.pop("input_references_json"), [])
        by_asset.setdefault(rev["asset_id"], []).append(rev)
    for asset in assets:
        asset["scene_references"] = _parse_json(asset.pop("scene_references_json"), [])
        asset["revisions"] = by_asset.get(asset["asset_id"], [])
    return {"project_id": project_id, "assets": assets, "count": len(assets)}


@app.get("/api/projects/{project_id}/scenes")
def list_scenes(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        rows = _rows(conn, "SELECT * FROM scenes WHERE project_id = ? ORDER BY scene_id", (project_id,))
    for row in rows:
        for field in ("characters_json", "required_assets_json", "required_shots_json", "audio_dependencies_json", "vfx_json", "production_dependencies_json", "expected_outputs_json"):
            row[field.replace("_json", "")] = _parse_json(row.pop(field), [])
    return {"project_id": project_id, "scenes": rows, "count": len(rows)}


@app.get("/api/projects/{project_id}/shots")
def list_shots(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        rows = _rows(conn, "SELECT * FROM shots WHERE project_id = ? ORDER BY shot_id", (project_id,))
    for row in rows:
        row["audio_cues"] = _parse_json(row.pop("audio_cues_json"), [])
        row["required_assets"] = _parse_json(row.pop("required_assets_json"), [])
    return {"project_id": project_id, "shots": rows, "count": len(rows)}


@app.get("/api/projects/{project_id}/research")
def get_research(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        reports = _rows(conn, "SELECT * FROM research_reports WHERE project_id = ? ORDER BY research_date DESC", (project_id,))
        candidates = _rows(conn, "SELECT * FROM tool_candidates WHERE project_id = ? ORDER BY name", (project_id,))
        evaluations = _rows(conn, "SELECT * FROM tool_evaluations WHERE project_id = ? ORDER BY evaluated_at DESC", (project_id,))
        toolchains = _rows(conn, "SELECT * FROM toolchain_profiles WHERE project_id = ? ORDER BY version DESC", (project_id,))
    for rep in reports:
        for field in ("requirements_json", "sources_json", "recommendations_json", "poc_results_json"):
            rep[field.replace("_json", "")] = _redact(_parse_json(rep.pop(field), []))
        rep["research_note"] = "Preconfigured research data; not a live web search unless sources show otherwise."
    for ev in evaluations:
        ev["scores"] = _parse_json(ev.pop("scores_json"), {})
    for tc in toolchains:
        tc["profile"] = _redact(_parse_json(tc.pop("profile_json"), {}))
    return {
        "project_id": project_id,
        "research_reports": reports,
        "tool_candidates": candidates,
        "tool_evaluations": evaluations,
        "toolchain_profiles": toolchains,
    }


@app.get("/api/projects/{project_id}/tasks")
def list_tasks(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        tasks = _rows(conn, "SELECT * FROM tasks WHERE project_id = ? ORDER BY task_id", (project_id,))
        deps = _rows(conn, "SELECT * FROM dependencies WHERE project_id = ? ORDER BY task_id", (project_id,))
        jobs = _rows(conn, "SELECT * FROM generation_jobs WHERE project_id = ? ORDER BY submitted_at DESC", (project_id,))
    by_task: Dict[str, List[Dict[str, Any]]] = {}
    for dep in deps:
        by_task.setdefault(dep["task_id"], []).append(dep)
    for job in jobs:
        job["input_params"] = _redact(_parse_json(job.pop("input_params_json"), {}))
        job["output_paths"] = _parse_json(job.pop("output_paths_json"), [])
    for task in tasks:
        task["dependencies"] = by_task.get(task["task_id"], [])
        # Tool/expected-output columns do not exist on tasks; say so instead of inventing.
        task["selected_tool"] = None
        task["expected_outputs"] = None
        task["actual_outputs"] = None
        task["tool_note"] = "Tasks table records no selected tool or outputs; see tool_candidates / generation_jobs."
    return {"project_id": project_id, "tasks": tasks, "generation_jobs": jobs, "count": len(tasks)}


@app.get("/api/projects/{project_id}/qc")
def list_qc(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        rows = _rows(conn, "SELECT * FROM qc_reports WHERE project_id = ? ORDER BY created_at DESC", (project_id,))
    for row in rows:
        row["checks"] = _parse_json(row.pop("checks_json"), {})
        row["issues"] = _parse_json(row.pop("issues_json"), [])
        row["recommendations"] = _parse_json(row.pop("recommendations_json"), [])
        row["inspection_note"] = "Predetermined checks from QualityControlEngine; no media inspection was performed. Technical QC is not creative approval."
        row["grants_creative_approval"] = False
    return {"project_id": project_id, "qc_reports": rows, "count": len(rows)}


@app.get("/api/projects/{project_id}/executions")
def list_executions(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
        executions = _rows(conn, "SELECT * FROM agent_executions WHERE project_id = ? ORDER BY started_at DESC", (project_id,))
        prompts = _rows(conn, "SELECT * FROM agent_prompts ORDER BY prompt_id, version")
        logs = _rows(conn, "SELECT * FROM execution_logs WHERE project_id = ? ORDER BY logged_at DESC LIMIT 100", (project_id,))
    for ex in executions:
        ex["prompt_versions"] = _parse_json(ex.pop("prompt_versions_json"), {})
        ex["input_payload"] = _redact(_parse_json(ex.pop("input_payload_json"), {}))
        ex["output_envelope"] = _redact(_parse_json(ex.pop("output_envelope_json"), {}))
    for log in logs:
        log["metadata"] = _redact(_parse_json(log.pop("metadata_json"), {}))
    # agent_prompts holds metadata+hash only; there is no prompt body to return.
    return {
        "project_id": project_id,
        "agent_executions": executions,
        "agent_prompts": prompts,
        "agent_prompts_note": "Metadata and content hashes only; no full prompt bodies are stored in this table.",
        "execution_logs": logs,
    }


@app.get("/api/projects/{project_id}/files")
def list_project_files(project_id: str, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
    files = _list_project_files(project_id)
    return {"project_id": project_id, "files": files, "count": len(files)}


@app.get("/api/projects/{project_id}/file")
def get_project_file(project_id: str, path: str = Query(..., min_length=1), _: str = Depends(verify_local_ipc_token)) -> FileResponse:
    with db.get_connection() as conn:
        _require_project(conn, project_id)
    resolved = _resolve_project_file(project_id, path)
    media_type, _ = mimetypes.guess_type(resolved.name)
    return FileResponse(resolved, media_type=media_type or "application/octet-stream", filename=resolved.name)


# ---------------------------------------------------------------------------
# CR_006: Story Bible, Episode Brief, staged screenplay, QC, provider
# ---------------------------------------------------------------------------

class StoryBiblePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    series_id: str
    project_id: Optional[str] = None
    content: Dict[str, Any]
    status: str = "DRAFT"
    created_by: str = "HUMAN_OWNER"

class BibleTransitionPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    new_status: str
    actor: str = "HUMAN_OWNER"
    # Human confirmation is verified server-side via Windows dialog for
    # APPROVED transitions; the flag below is accepted only for
    # non-canon transitions or when the caller already passed the dialog.
    human_confirmed: bool = False

class EpisodeBriefPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: Dict[str, Any]
    status: str = "DRAFT"
    created_by: str = "HUMAN_OWNER"

class GenerationPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    episode_id: str
    series_id: Optional[str] = None
    provider_id: str = "OLLAMA_OPENAI_COMPATIBLE"
    model_id: str = "ornith:9b"
    title: str = "Untitled"
    target_audience: str = "General"
    intended_duration_sec: int = 300

class QCValidatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    script_id: str
    episode_id: str = ""

class OutlineApprovePayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    episode_id: str

class ChangeRequestPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")
    change_request_id: str
    requested_modification: str
    reason: str
    affected_departments: List[str]
    affected_workflows: List[str]
    compatibility_impact: str
    advantages: str
    disadvantages: str
    testing_requirements: str
    rollback_plan: str
    proposed_version: str

@app.post("/api/change-requests")
def create_change_request_api(payload: ChangeRequestPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        with db.get_connection() as conn:
            existing = conn.execute("SELECT change_request_id FROM change_requests WHERE change_request_id = ?", (payload.change_request_id,)).fetchone()
            if existing:
                raise HTTPException(status_code=409, detail=f"Change Request {payload.change_request_id} already exists")
        return governance.create_change_request(
            operating_mode="ARCHITECTURE_MODE",
            change_request_id=payload.change_request_id,
            requested_modification=payload.requested_modification,
            reason=payload.reason,
            affected_departments=payload.affected_departments,
            affected_workflows=payload.affected_workflows,
            compatibility_impact=payload.compatibility_impact,
            advantages=payload.advantages,
            disadvantages=payload.disadvantages,
            testing_requirements=payload.testing_requirements,
            rollback_plan=payload.rollback_plan,
            proposed_version=payload.proposed_version,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/story-bibles/{series_id}")
def get_story_bible(series_id: str, revision: int = Query(default=None), _: str = Depends(verify_local_ipc_token)):
    try:
        return story_ctx.get_bible(series_id, revision)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.get("/api/story-bibles/{series_id}/revisions")
def list_story_bible_revisions(series_id: str, _: str = Depends(verify_local_ipc_token)):
    return {"series_id": series_id, "revisions": story_ctx.list_bible_revisions(series_id), "count": len(story_ctx.list_bible_revisions(series_id))}

@app.post("/api/story-bibles")
def create_story_bible_api(payload: StoryBiblePayload, _: str = Depends(verify_local_ipc_token)):
    try:
        return story_ctx.create_bible(payload.series_id, payload.content, payload.project_id, payload.status, payload.created_by)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/story-bibles/{bible_revision_id}/transition")
def transition_bible_api(bible_revision_id: str, payload: BibleTransitionPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        # APPROVED canon requires live Windows confirmation (trusted reviewer identity).
        confirmed = payload.human_confirmed
        if payload.new_status == "APPROVED":
            try:
                reviewer = confirm_windows_human_decision(
                    {"project_id": "ARCHITECTURE", "target_type": "bible", "target_id": bible_revision_id, "revision": 0},
                    "APPROVED", "Approve Series Bible revision as canon",
                )
                confirmed = True
                actor = reviewer
            except Exception as exc:
                raise HTTPException(status_code=503, detail=f"Windows reviewer required for APPROVED: {exc}") from exc
        else:
            actor = payload.actor
        return story_ctx.transition_bible(bible_revision_id, payload.new_status, actor, confirmed)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/story-bibles/{series_id}/canon")
def get_approved_canon_api(series_id: str, _: str = Depends(verify_local_ipc_token)):
    canon = story_ctx.get_approved_canon(series_id)
    return {"series_id": series_id, "canon": canon}

@app.post("/api/projects/{project_id}/episode-briefs/{episode_id}")
def create_episode_brief_api(project_id: str, episode_id: str, payload: EpisodeBriefPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        with db.get_connection() as conn:
            _require_project(conn, project_id)
        return story_ctx.create_brief(project_id, payload.content, episode_id, payload.content.get("series_id"), payload.status, payload.created_by)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/projects/{project_id}/episode-briefs/{episode_id}")
def get_episode_brief_api(project_id: str, episode_id: str, _: str = Depends(verify_local_ipc_token)):
    try:
        with db.get_connection() as conn:
            _require_project(conn, project_id)
        return story_ctx.get_brief(project_id, episode_id)
    except HTTPException:
        raise
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

@app.get("/api/projects/{project_id}/story-context")
def get_story_context_api(project_id: str, episode_id: str = Query(..., min_length=1), series_id: str = Query(default=None),
                          primary_genre_id: str = Query(default="GENRE_FANTASY"), channel_style_id: str = Query(default=None),
                          _: str = Depends(verify_local_ipc_token)):
    try:
        return story_ctx.assemble_context(project_id, episode_id, series_id, primary_genre_id, channel_style_id=channel_style_id)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/analysis")
def post_story_analysis_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        brief = story_ctx.get_brief(project_id, payload.episode_id)
        canon = story_ctx.get_approved_canon(payload.series_id) if payload.series_id else None
        return story_pipeline.generate_story_analysis(project_id, payload.episode_id, brief["content"], canon["content"] if canon else None, provider_manager, payload.provider_id, payload.model_id)
    except HTTPException:
        raise
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/hooks")
def post_hooks_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        analysis = story_pipeline.get_artifact(project_id, payload.episode_id, "STORY_ANALYSIS")["content"]
        brief = story_ctx.get_brief(project_id, payload.episode_id)["content"]
        return story_pipeline.generate_hooks(project_id, payload.episode_id, analysis, brief, provider_manager, payload.provider_id, payload.model_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/outline")
def post_outline_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        analysis = story_pipeline.get_artifact(project_id, payload.episode_id, "STORY_ANALYSIS")["content"]
        brief = story_ctx.get_brief(project_id, payload.episode_id)["content"]
        return story_pipeline.generate_outline(project_id, payload.episode_id, analysis, brief, provider_manager, payload.provider_id, payload.model_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/outline/approve")
def post_outline_approve_api(project_id: str, payload: OutlineApprovePayload, _: str = Depends(verify_local_ipc_token)):
    try:
        # Trusted human path: native Windows confirmation produces the reviewer identity.
        reviewer = confirm_windows_human_action(f"Approve OUTLINE for {project_id}/{payload.episode_id} before screenplay drafting?")
        return story_pipeline.approve_outline(project_id, payload.episode_id, human_confirmed=True)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Windows reviewer required: {exc}") from exc

@app.post("/api/projects/{project_id}/story/scene-cards")
def post_scene_cards_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        outline = story_pipeline.get_artifact(project_id, payload.episode_id, "OUTLINE")["content"]
        brief = story_ctx.get_brief(project_id, payload.episode_id)["content"]
        return story_pipeline.generate_scene_cards(project_id, payload.episode_id, outline, brief, provider_manager, payload.provider_id, payload.model_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/screenplay")
def post_screenplay_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        brief_row = story_ctx.get_brief(project_id, payload.episode_id)
        cards = story_pipeline.get_artifact(project_id, payload.episode_id, "SCENE_CARDS")["content"]
        canon = story_ctx.get_approved_canon(payload.series_id) if payload.series_id else None
        ctx = story_ctx.assemble_context(project_id, payload.episode_id, payload.series_id)
        return story_pipeline.generate_screenplay(
            project_id, payload.episode_id, cards, brief_row["content"], canon["content"] if canon else None,
            payload.title, payload.target_audience, payload.intended_duration_sec, provider_manager,
            payload.provider_id, payload.model_id, ctx["manifest"]["context_hash_sha256"],
        )
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/retention-map")
def post_retention_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        cards = story_pipeline.get_artifact(project_id, payload.episode_id, "SCENE_CARDS")["content"]
        return story_pipeline.generate_retention_map(project_id, payload.episode_id, cards)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/qc/validate")
def post_qc_validate_api(project_id: str, payload: QCValidatePayload, _: str = Depends(verify_local_ipc_token)):
    try:
        brief = None
        canon = None
        try:
            brief = story_ctx.get_brief(project_id, payload.episode_id)["content"] if payload.episode_id else None
        except Exception:
            pass
        validator = DeterministicValidator(db)
        return validator.validate(project_id, payload.script_id, brief, canon)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post("/api/projects/{project_id}/story/qc/critique")
def post_qc_critique_api(project_id: str, payload: GenerationPayload, _: str = Depends(verify_local_ipc_token)):
    try:
        critique = CreativeCritique(db, provider_manager)
        # payload.episode_id reused as script_id for this route's contract; prefer body below
        script_id = payload.episode_id
        return critique.critique(project_id, script_id, payload.provider_id, payload.model_id)
    except ProviderError as exc:
        raise HTTPException(status_code=502, detail=f"{exc.category}: {exc.detail}") from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get("/api/projects/{project_id}/story/artifacts/{artifact_type}")
def get_artifact_api(project_id: str, artifact_type: str, episode_id: str = Query(..., min_length=1), _: str = Depends(verify_local_ipc_token)):
    try:
        return story_pipeline.get_artifact(project_id, episode_id, artifact_type)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


if __name__ == "__main__":
    port = int(os.environ.get("ANIMATION_FORGE_PORT", "8765"))
    if not 1 <= port <= 65535:
        raise ValueError("ANIMATION_FORGE_PORT must be between 1 and 65535")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
