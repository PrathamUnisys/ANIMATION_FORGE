import os
import json
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from backend.database import DatabaseManager, DEFAULT_DB_PATH
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine, ApprovalPolicyViolationError
from backend.rnd.research_engine import ProductionRndEngine
from backend.integrations.mcp_gateway import AnimationForgeMcpGateway
from backend.integrations.comfyui_adapter import ComfyUIAdapter
from backend.qc.quality_controller import QualityControlEngine

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCAL_IPC_TOKEN = os.environ.get("ANIMATION_FORGE_IPC_TOKEN", "af-local-ipc-token-2026")

app = FastAPI(
    title="Animation Forge Local Production Engine",
    version="1.0.0",
    description="Tool-Agnostic, AI-Driven, Human-Directed Animation Production OS Sidecar API"
)

db = DatabaseManager(DEFAULT_DB_PATH)
governance = GovernanceEngine(ROOT_DIR, db)
approvals = ApprovalEngine(db)
rnd_engine = ProductionRndEngine(ROOT_DIR, db, approvals)
mcp_gateway = AnimationForgeMcpGateway(db)
comfyui = ComfyUIAdapter(ROOT_DIR, db)
qc_engine = QualityControlEngine(db)


def verify_local_ipc_token(x_forge_token: str = Header(default="af-local-ipc-token-2026")) -> str:
    if x_forge_token != LOCAL_IPC_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized local IPC token")
    return x_forge_token


class HumanDecisionPayload(BaseModel):
    approval_id: str
    decision: str
    human_user_id: str = "HUMAN_EXEC_PRODUCER"
    comments: str
    rationale: Optional[str] = None


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
def create_project(payload: CreateProjectPayload, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
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
def submit_approval_decision(payload: HumanDecisionPayload, _: str = Depends(verify_local_ipc_token)) -> Dict[str, Any]:
    try:
        return approvals.submit_human_decision(
            approval_id=payload.approval_id,
            decision=payload.decision,
            human_user_id=payload.human_user_id,
            comments=payload.comments,
            rationale_for_memory=payload.rationale
        )
    except ApprovalPolicyViolationError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
