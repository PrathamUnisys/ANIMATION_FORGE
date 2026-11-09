import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.database import DatabaseManager


class ApprovalPolicyViolationError(Exception):
    """Raised when an invalid state transition or automated creative approval is attempted."""


VALID_DELIVERABLE_STATES = [
    "PROPOSED",
    "GENERATING",
    "QUALITY_CHECK",
    "AWAITING_HUMAN_REVIEW",
    "APPROVED",
    "REVISION_REQUESTED",
    "REJECTED",
]

ALLOWED_TRANSITIONS = {
    "PROPOSED": {"GENERATING"},
    "GENERATING": {"QUALITY_CHECK", "PROPOSED"},
    "QUALITY_CHECK": {"AWAITING_HUMAN_REVIEW", "REVISION_REQUESTED", "REJECTED"},
    "AWAITING_HUMAN_REVIEW": {"APPROVED", "REVISION_REQUESTED", "REJECTED"},
    "REVISION_REQUESTED": {"GENERATING", "PROPOSED"},
    "REJECTED": {"PROPOSED"},
    "APPROVED": set(),  # Immutable! Any further changes must create revision + 1
}


class ApprovalEngine:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def register_deliverable_gate(
        self,
        approval_id: str,
        project_id: str,
        target_type: str,
        target_id: str,
        revision: int,
        initial_state: str = "PROPOSED"
    ) -> Dict[str, Any]:
        if initial_state not in ("PROPOSED", "GENERATING"):
            raise ApprovalPolicyViolationError(f"Cannot initialize deliverable directly in state '{initial_state}'.")
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO approvals
                   (approval_id, project_id, target_type, target_id, revision, state, technical_qc_outcome, reviewer_type, reviewer_id, comments, decided_at)
                   VALUES (?, ?, ?, ?, ?, ?, NULL, 'SYSTEM_TECHNICAL_QC', 'ORCHESTRATOR', 'Initialized deliverable gate', ?)""",
                (approval_id, project_id, target_type, target_id, revision, initial_state, now)
            )
            conn.commit()
        return self.get_gate(approval_id)

    def advance_system_state(
        self,
        approval_id: str,
        new_state: str,
        actor_agent_id: str,
        technical_qc_outcome: Optional[str] = None,
        comments: str = ""
    ) -> Dict[str, Any]:
        if new_state == "APPROVED":
            raise ApprovalPolicyViolationError(
                f"Agent '{actor_agent_id}' attempted to set state='APPROVED'. Creative deliverables can NEVER be approved automatically by an AI agent or technical QC."
            )
        gate = self.get_gate(approval_id)
        curr_state = gate["state"]
        if new_state not in ALLOWED_TRANSITIONS.get(curr_state, set()):
            raise ApprovalPolicyViolationError(f"Illegal state transition from '{curr_state}' to '{new_state}'.")

        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """UPDATE approvals
                   SET state = ?, technical_qc_outcome = COALESCE(?, technical_qc_outcome),
                       reviewer_type = 'SYSTEM_TECHNICAL_QC', reviewer_id = ?, comments = ?, decided_at = ?
                   WHERE approval_id = ?""",
                (new_state, technical_qc_outcome, actor_agent_id, comments, now, approval_id)
            )
            conn.commit()
        return self.get_gate(approval_id)

    def submit_human_decision(
        self,
        approval_id: str,
        decision: str,
        human_user_id: str,
        comments: str,
        rationale_for_memory: Optional[str] = None
    ) -> Dict[str, Any]:
        if not human_user_id.startswith("HUMAN_"):
            raise ApprovalPolicyViolationError("Creative review decisions require a human reviewer ID.")
        if decision not in ("APPROVED", "REVISION_REQUESTED", "REJECTED"):
            raise ApprovalPolicyViolationError(f"Invalid human review decision: {decision}")

        gate = self.get_gate(approval_id)
        if gate["state"] != "AWAITING_HUMAN_REVIEW":
            raise ApprovalPolicyViolationError(
                f"Deliverable '{gate['target_id']}' (rev {gate['revision']}) is in state '{gate['state']}', not 'AWAITING_HUMAN_REVIEW'."
            )
        # HARD GATE (H5): staged screenplays (episode_id set) require exact-revision QC.
        # Legacy scaffolds (episode_id NULL) keep MANUAL_INSPECTION history.
        if decision == "APPROVED" and gate["target_type"] == "script":
            with self.db.get_connection() as conn:
                script_row = conn.execute(
                    "SELECT episode_id FROM scripts WHERE script_id = ?", (gate["target_id"],)
                ).fetchone()
                staged = bool(script_row and script_row["episode_id"])
            if staged:
                with self.db.get_connection() as conn:
                    qc = conn.execute(
                        "SELECT * FROM screenplay_qc_reports WHERE project_id = ? AND script_id = ? AND script_version = ? AND validator_name = 'DETERMINISTIC_SCREENPLAY_VALIDATOR' ORDER BY created_at DESC LIMIT 1",
                        (gate["project_id"], gate["target_id"], gate["revision"]),
                    ).fetchone()
                    if not qc:
                        raise ApprovalPolicyViolationError(
                            f"Cannot approve script {gate['target_id']} v{gate['revision']}: no deterministic QC report for this exact revision."
                        )
                    issues = json.loads(qc["issues_json"] or "[]")
                    blockers = [i for i in issues if i.get("severity") == "BLOCKER"]
                    if blockers:
                        raise ApprovalPolicyViolationError(
                            f"Cannot approve script {gate['target_id']} v{gate['revision']}: {len(blockers)} unresolved BLOCKER finding(s) in {qc['report_id']}."
                        )
                    if qc["outcome"] == "FAIL":
                        raise ApprovalPolicyViolationError(
                            f"Cannot approve script {gate['target_id']} v{gate['revision']}: deterministic QC outcome is FAIL ({qc['report_id']})."
                        )
                    critique = conn.execute(
                        "SELECT * FROM screenplay_qc_reports WHERE project_id = ? AND script_id = ? AND script_version = ? AND validator_name = 'SCRIPT_CRITIC_CREATIVE_REVIEW' ORDER BY created_at DESC LIMIT 1",
                        (gate["project_id"], gate["target_id"], gate["revision"]),
                    ).fetchone()
                    if critique is None:
                        raise ApprovalPolicyViolationError(
                            f"Cannot approve script {gate['target_id']} v{gate['revision']}: creative critique missing."
                        )
                    critique_issues = json.loads(critique["issues_json"] or "[]")
                    majors = [i for i in critique_issues if i.get("severity") == "MAJOR"]
                    if majors and "acknowledge" not in (comments or "").lower():
                        raise ApprovalPolicyViolationError(
                            f"Script has {len(majors)} MAJOR creative findings. Acknowledge them in the approval comments before approving."
                        )


        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """UPDATE approvals
                   SET state = ?, reviewer_type = 'HUMAN_EXECUTIVE_PRODUCER', reviewer_id = ?, comments = ?, decided_at = ?
                   WHERE approval_id = ?""",
                (decision, human_user_id, comments, now, approval_id)
            )
            # Propagate status to target table
            t_type = gate["target_type"]
            t_id = gate["target_id"]
            if t_type == "script":
                conn.execute(
                    "UPDATE scripts SET approval_status = ?, reviewer_comments = ?, is_immutable = ? WHERE script_id = ?",
                    (decision, comments, 1 if decision == "APPROVED" else 0, t_id)
                )
            elif t_type == "asset":
                conn.execute("UPDATE assets SET approval_status = ? WHERE asset_id = ?", (decision, t_id))
                conn.execute(
                    "UPDATE asset_revisions SET approval_status = ? WHERE asset_id = ? AND revision = ?",
                    (decision, t_id, gate["revision"])
                )
            elif t_type == "toolchain":
                conn.execute(
                    "UPDATE toolchain_profiles SET locked = ?, approved_by = ?, approved_at = ? WHERE toolchain_id = ?",
                    (1 if decision == "APPROVED" else 0, human_user_id, now, t_id)
                )
            elif t_type == "character":
                conn.execute("UPDATE characters SET approval_status = ? WHERE character_id = ?", (decision, t_id))
            elif t_type == "environment":
                conn.execute("UPDATE environments SET approval_status = ? WHERE location_id = ?", (decision, t_id))
            elif t_type == "audio":
                conn.execute("UPDATE audio_assets SET approval_status = ? WHERE audio_id = ?", (decision, t_id))
            elif t_type == "shot":
                conn.execute("UPDATE shots SET approval_status = ? WHERE shot_id = ?", (decision, t_id))

            if rationale_for_memory:
                conn.execute(
                    """INSERT INTO creative_decisions
                       (decision_id, project_id, memory_layer, category, title, rationale, alternatives_rejected_json, approved_by, decided_at)
                       VALUES (?, ?, 'PROJECT', ?, ?, ?, '[]', ?, ?)""",
                    (
                        f"DEC_{approval_id}",
                        gate["project_id"],
                        t_type.upper(),
                        f"{decision}: {t_type} {t_id} (v{gate['revision']})",
                        rationale_for_memory,
                        human_user_id,
                        now
                    )
                )
            conn.commit()
        return self.get_gate(approval_id)

    def get_gate(self, approval_id: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM approvals WHERE approval_id = ?", (approval_id,)).fetchone()
            if not row:
                raise KeyError(f"Approval gate {approval_id} not found")
            return dict(row)
