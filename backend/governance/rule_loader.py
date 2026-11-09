import os
import re
import json
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import DatabaseManager


class RuleConflictError(Exception):
    """Raised when a lower-tier instruction contradicts a higher-tier rule."""


class MissingMandatoryRuleError(Exception):
    """Raised when a required rule or prompt file is missing or malformed."""


class ArchitectureLockError(Exception):
    """Raised when an unauthorized operating mode attempts to modify locked architecture."""


REQUIRED_FRONTMATTER_KEYS = {"prompt_id", "version", "modified_date", "description", "dependencies", "change_history"}

RULE_HIERARCHY_TIERS = [
    (1, "SYSTEM_INTEGRITY_AND_SECURITY", "CORE/SECURITY_POLICY.md"),
    (2, "GLOBAL_PRODUCTION_CONSTITUTION", "CORE/SYSTEM_CONSTITUTION.md"),
    (3, "PROJECT_LEVEL_RULES", None),
    (4, "SERIES_BIBLE", None),
    (5, "DEPARTMENT_INSTRUCTIONS", None),
    (6, "AGENT_SPECIFIC_INSTRUCTIONS", None),
    (7, "PROVIDER_SPECIFIC_INSTRUCTIONS", None),
    (8, "INDIVIDUAL_TASK_INSTRUCTIONS", None),
]


def parse_markdown_with_frontmatter(file_path: str) -> Dict[str, Any]:
    if not os.path.exists(file_path):
        raise MissingMandatoryRuleError(f"Mandatory instruction file missing: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        raw = f.read()
    if not raw.startswith("---"):
        raise MissingMandatoryRuleError(f"Instruction file lacks YAML frontmatter header: {file_path}")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise MissingMandatoryRuleError(f"Malformed frontmatter in: {file_path}")
    header_text, body = parts[1].strip(), parts[2].strip()
    meta: Dict[str, Any] = {}
    current_list_key = None
    for line in header_text.splitlines():
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    meta[k] = json.loads(v)
                except Exception:
                    meta[k] = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
                current_list_key = None
            elif v == "":
                meta[k] = []
                current_list_key = k
            else:
                meta[k] = v.strip('"').strip("'")
                current_list_key = None
        elif current_list_key is not None:
            meta[current_list_key].append(line.strip())

    missing = REQUIRED_FRONTMATTER_KEYS - set(meta.keys())
    if missing:
        raise MissingMandatoryRuleError(f"Prompt {file_path} missing required metadata keys: {missing}")

    meta["content_hash"] = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    meta["body"] = body
    meta["file_path"] = file_path
    return meta


class GovernanceEngine:
    def __init__(self, root_dir: str, db: DatabaseManager):
        self.root_dir = root_dir
        self.db = db
        self._ensure_initial_architecture_version()

    def _ensure_initial_architecture_version(self) -> None:
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT version_id FROM architecture_versions WHERE is_active = 1")
            if not cur.fetchone():
                snapshot = self._capture_core_snapshot()
                conn.execute(
                    "INSERT INTO architecture_versions (version_id, parent_version_id, change_request_id, snapshot_json, is_active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                    ("ARCH_V1.0.0", None, None, json.dumps(snapshot), datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
                )
                conn.commit()

    def _capture_core_snapshot(self) -> Dict[str, str]:
        snapshot = {}
        for sub in ["CORE", "MODES"]:
            folder = os.path.join(self.root_dir, sub)
            if os.path.exists(folder):
                for fname in sorted(os.listdir(folder)):
                    if fname.endswith(".md"):
                        fpath = os.path.join(folder, fname)
                        with open(fpath, "r", encoding="utf-8") as f:
                            snapshot[f"{sub}/{fname}"] = f.read()
        return snapshot

    def get_active_architecture_version(self) -> str:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT version_id FROM architecture_versions WHERE is_active = 1").fetchone()
            return row["version_id"] if row else "ARCH_V1.0.0"

    def build_agent_context(
        self,
        project_id: str,
        operating_mode: str,
        agent_id: str,
        department: str,
        provider_profile_rel_path: str,
        task_instructions: Dict[str, Any],
        agent_rel_path: Optional[str] = None,
    ) -> Dict[str, Any]:
        # 1. Read global constitution & security policy (Tiers 1 & 2)
        sec_doc = parse_markdown_with_frontmatter(os.path.join(self.root_dir, "CORE/SECURITY_POLICY.md"))
        const_doc = parse_markdown_with_frontmatter(os.path.join(self.root_dir, "CORE/SYSTEM_CONSTITUTION.md"))
        approval_doc = parse_markdown_with_frontmatter(os.path.join(self.root_dir, "CORE/HUMAN_APPROVAL_POLICY.md"))

        # 2. Read active operating mode
        mode_path = os.path.join(self.root_dir, f"MODES/{operating_mode}.md")
        mode_doc = parse_markdown_with_frontmatter(mode_path)

        # 3. Check for conflict between task instructions and higher-tier rules
        self._detect_rule_conflicts(operating_mode, mode_doc, task_instructions)

        # 4. Read department instructions (Tier 5)
        dept_path = os.path.join(self.root_dir, f"DEPARTMENTS/{department}/DEPARTMENT_RULES.md")
        dept_doc = parse_markdown_with_frontmatter(dept_path) if os.path.exists(dept_path) else None

        # 5. Read agent instructions (Tier 6)
        if not agent_rel_path:
            if agent_id == "PRODUCTION_DIRECTOR":
                agent_rel_path = "ORCHESTRATION/PRODUCTION_DIRECTOR/INSTRUCTION.md"
            else:
                agent_rel_path = f"AGENTS/{agent_id}/INSTRUCTION.md"
        agent_doc = parse_markdown_with_frontmatter(os.path.join(self.root_dir, agent_rel_path))

        # 6. Read provider profile (Tier 7)
        prov_doc = parse_markdown_with_frontmatter(os.path.join(self.root_dir, provider_profile_rel_path))

        # 7. Record prompt versions used in DB
        loaded_docs = [sec_doc, const_doc, approval_doc, mode_doc, agent_doc, prov_doc]
        if dept_doc:
            loaded_docs.append(dept_doc)

        version_manifest = {}
        with self.db.get_connection() as conn:
            for d in loaded_docs:
                version_manifest[d["prompt_id"]] = {
                    "version": d["version"],
                    "content_hash": d["content_hash"][:16],
                    "file_path": os.path.relpath(d["file_path"], self.root_dir)
                }
                conn.execute(
                    """INSERT OR REPLACE INTO agent_prompts
                       (prompt_id, version, file_path, content_hash, modified_date, description, dependencies_json, change_history_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        d["prompt_id"],
                        d["version"],
                        os.path.relpath(d["file_path"], self.root_dir),
                        d["content_hash"],
                        str(d["modified_date"]),
                        d["description"],
                        json.dumps(d["dependencies"]),
                        json.dumps(d["change_history"]),
                    )
                )
            conn.commit()

        # 8. Retrieve scoped creative memory for this project & department (do not dump unrelated projects)
        scoped_memory = self._load_scoped_creative_memory(project_id, department)

        return {
            "project_id": project_id,
            "operating_mode": operating_mode,
            "agent_id": agent_id,
            "department": department,
            "architecture_version": self.get_active_architecture_version(),
            "prompt_versions": version_manifest,
            "scoped_memory": scoped_memory,
            "task_instructions": task_instructions
        }

    def _detect_rule_conflicts(self, operating_mode: str, mode_doc: Dict[str, Any], task_instructions: Dict[str, Any]) -> None:
        # Tier 1 & 2 immutable checks
        if task_instructions.get("auto_approve") is True or task_instructions.get("bypass_human_review") is True:
            self._log_conflict("Task attempted to bypass mandatory human approval (Tier 2 violation).")
            raise RuleConflictError("Contradictory instruction: Task requested automatic creative approval, violating CORE/HUMAN_APPROVAL_POLICY.md.")

        if task_instructions.get("overwrite_approved_asset") is True:
            self._log_conflict("Task attempted to overwrite an immutable approved asset (Tier 2 violation).")
            raise RuleConflictError("Contradictory instruction: Task requested overwriting an approved asset, violating CORE/ASSET_VERSIONING.md.")

        if task_instructions.get("modify_architecture") is True and operating_mode != "ARCHITECTURE_MODE":
            self._log_conflict(f"Mode {operating_mode} attempted architecture modification.")
            raise ArchitectureLockError(f"Operating mode {operating_mode} is forbidden from modifying architecture. Switch to ARCHITECTURE_MODE with an approved Change Request.")

        if task_instructions.get("bypass_rnd_toolchain") is True:
            self._log_conflict("Task attempted to bypass mandatory R&D toolchain lock.")
            raise RuleConflictError("Contradictory instruction: Cannot bypass mandatory per-project R&D toolchain approval.")

        req_op = task_instructions.get("requested_operation")
        if req_op and f"- `{req_op}`" in mode_doc["body"].split("## Forbidden Operations")[-1]:
            self._log_conflict(f"Operation {req_op} is forbidden in {operating_mode}.")
            raise RuleConflictError(f"Operation '{req_op}' is explicitly forbidden in {operating_mode}.")

    def _load_scoped_creative_memory(self, project_id: str, department: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            decisions = conn.execute(
                "SELECT decision_id, category, title, rationale FROM creative_decisions WHERE project_id = ? ORDER BY decided_at DESC LIMIT 10",
                (project_id,)
            ).fetchall()
            memory: Dict[str, Any] = {"decisions": [dict(r) for r in decisions]}
            if department in ("CHARACTERS", "STORY", "AUDIO", "STORYBOARD", "ANIMATION"):
                chars = conn.execute(
                    "SELECT character_id, name, role, visual_consistency_locks_json, voice_profile_json FROM characters WHERE project_id = ?",
                    (project_id,)
                ).fetchall()
                memory["characters"] = [dict(r) for r in chars]
            if department in ("ENVIRONMENTS", "STORY", "STORYBOARD", "ANIMATION"):
                envs = conn.execute(
                    "SELECT location_id, name, environment_type, approval_status FROM environments WHERE project_id = ?",
                    (project_id,)
                ).fetchall()
                memory["environments"] = [dict(r) for r in envs]
            return memory

    def _log_conflict(self, details: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO audit_events (event_id, project_id, actor, event_type, severity, details_json, occurred_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    f"AUD_{int(datetime.now(timezone.utc).timestamp()*1000)}",
                    None,
                    "RULE_LOADER",
                    "RULE_CONFLICT_BLOCKED",
                    "CRITICAL",
                    json.dumps({"reason": details}),
                    datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
                )
            )
            conn.commit()

    def create_change_request(
        self,
        operating_mode: str,
        change_request_id: str,
        requested_modification: str,
        reason: str,
        affected_departments: List[str],
        affected_workflows: List[str],
        compatibility_impact: str,
        advantages: str,
        disadvantages: str,
        testing_requirements: str,
        rollback_plan: str,
        proposed_version: str
    ) -> Dict[str, Any]:
        if operating_mode != "ARCHITECTURE_MODE":
            raise ArchitectureLockError("Change Requests can only be created in ARCHITECTURE_MODE.")
        curr_ver = self.get_active_architecture_version()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO change_requests (
                    change_request_id, current_architecture_version, requested_modification, reason,
                    affected_departments_json, affected_workflows_json, compatibility_impact,
                    advantages, disadvantages, testing_requirements, rollback_plan,
                    proposed_version, approval_status, created_at, decided_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'AWAITING_HUMAN_REVIEW', ?, NULL)""",
                (
                    change_request_id, curr_ver, requested_modification, reason,
                    json.dumps(affected_departments), json.dumps(affected_workflows),
                    compatibility_impact, advantages, disadvantages, testing_requirements,
                    rollback_plan, proposed_version, now
                )
            )
            conn.commit()
        return {"change_request_id": change_request_id, "approval_status": "AWAITING_HUMAN_REVIEW", "proposed_version": proposed_version}

    def approve_and_apply_change_request(self, change_request_id: str, human_reviewer_id: str, file_updates: Dict[str, str]) -> Dict[str, Any]:
        # SECURITY GAP (CR_006): The HUMAN_ prefix alone is not authentication.
        # The trusted path is approve_change_request_with_human() which requires
        # native Windows confirmation. This legacy method is retained for
        # backward-compatible unit tests only and must NOT be used for live
        # architecture approvals; live callers use the secure method below.
        if not human_reviewer_id.startswith("HUMAN_"):
            raise ArchitectureLockError("Only a human reviewer can approve an architectural Change Request.")
        with self.db.get_connection() as conn:
            cr = conn.execute("SELECT * FROM change_requests WHERE change_request_id = ?", (change_request_id,)).fetchone()
            if not cr:
                raise ValueError(f"Change Request {change_request_id} not found")
            now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
            for rel_path, new_content in file_updates.items():
                full_p = os.path.join(self.root_dir, rel_path)
                with open(full_p, "w", encoding="utf-8") as f:
                    f.write(new_content)
            new_snapshot = self._capture_core_snapshot()
            conn.execute("UPDATE architecture_versions SET is_active = 0")
            conn.execute(
                "INSERT INTO architecture_versions (version_id, parent_version_id, change_request_id, snapshot_json, is_active, created_at) VALUES (?, ?, ?, ?, 1, ?)",
                (cr["proposed_version"], cr["current_architecture_version"], change_request_id, json.dumps(new_snapshot), now)
            )
            conn.execute(
                "UPDATE change_requests SET approval_status = 'APPROVED', decided_at = ? WHERE change_request_id = ?",
                (now, change_request_id)
            )
            conn.commit()
            return {"active_version": cr["proposed_version"], "status": "APPROVED"}

    def approve_change_request_with_human(self, change_request_id: str, action_summary: Optional[str] = None, file_updates: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Secure architecture approval: requires native Windows confirmation.

        Never invents a HUMAN_ ID. The reviewer identity returned by
        windows_reviewer (HUMAN_WINDOWS_<account>) is the only accepted
        identity for live approvals.
        """
        from backend.governance.windows_reviewer import confirm_windows_human_action
        summary = action_summary or f"Approve architecture change request {change_request_id}?"
        reviewer_id = confirm_windows_human_action(summary)
        # confirm_windows_human_action already proved a live Windows human;
        # delegate to apply logic with that trusted identity.
        return self.approve_and_apply_change_request(change_request_id, reviewer_id, file_updates or {})

    def reject_change_request(self, change_request_id: str, reason: str = "") -> Dict[str, Any]:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            cur = conn.execute("SELECT approval_status FROM change_requests WHERE change_request_id = ?", (change_request_id,)).fetchone()
            if not cur:
                raise ValueError(f"Change Request {change_request_id} not found")
            if cur["approval_status"] not in ("AWAITING_HUMAN_REVIEW",):
                raise ArchitectureLockError(f"Change Request {change_request_id} is {cur['approval_status']}, not AWAITING_HUMAN_REVIEW")
            conn.execute(
                "UPDATE change_requests SET approval_status = 'REJECTED', decided_at = ? WHERE change_request_id = ?",
                (now, change_request_id)
            )
            conn.commit()
        return {"change_request_id": change_request_id, "approval_status": "REJECTED"}

    def rollback_architecture(self, target_version_id: str, human_reviewer_id: str) -> Dict[str, Any]:
        if not human_reviewer_id.startswith("HUMAN_"):
            raise ArchitectureLockError("Only a human reviewer can trigger architecture rollback.")
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM architecture_versions WHERE version_id = ?", (target_version_id,)).fetchone()
            if not row:
                raise ValueError(f"Architecture version {target_version_id} not found")
            snapshot = json.loads(row["snapshot_json"])
            for rel_path, content in snapshot.items():
                full_p = os.path.join(self.root_dir, rel_path)
                with open(full_p, "w", encoding="utf-8") as f:
                    f.write(content)
            conn.execute("UPDATE architecture_versions SET is_active = 0")
            conn.execute("UPDATE architecture_versions SET is_active = 1 WHERE version_id = ?", (target_version_id,))
            conn.commit()
        return {"rolled_back_to": target_version_id, "status": "ROLLED_BACK"}
