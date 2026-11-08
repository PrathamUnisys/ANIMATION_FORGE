import os
import re
import json
import jsonschema
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from backend.database import DatabaseManager
from backend.filesystem_security import is_safe_path_component
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine
from backend.providers.manager import ProviderManager, redact_secrets


class SecurityViolationError(Exception):
    """Raised on path traversal, unauthorized directory access, overwriting approved files, or prompt injection."""


class SchemaValidationError(Exception):
    """Raised when an agent output fails JSON schema validation."""


def _path_is_within(base_path: str, candidate_path: str) -> bool:
    try:
        return os.path.normcase(os.path.commonpath((base_path, candidate_path))) == os.path.normcase(base_path)
    except ValueError:
        return False


INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?previous\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+system\s+constitution", re.IGNORECASE),
    re.compile(r"print\s+all\s+api\s+keys", re.IGNORECASE),
    re.compile(r"override\s+human\s+approval", re.IGNORECASE),
]


class AgentExecutor:
    def __init__(
        self,
        root_dir: str,
        db: DatabaseManager,
        governance: GovernanceEngine,
        approvals: ApprovalEngine,
        providers: ProviderManager,
    ):
        self.root_dir = os.path.abspath(root_dir)
        self.db = db
        self.governance = governance
        self.approvals = approvals
        self.providers = providers
        with open(os.path.join(self.root_dir, "SCHEMAS/AGENT.schema.json"), "r", encoding="utf-8") as f:
            self.agent_envelope_schema = json.load(f)

    def scan_untrusted_input(self, text: str) -> str:
        for pat in INJECTION_PATTERNS:
            if pat.search(text):
                self._log_security_event("PROMPT_INJECTION_BLOCKED", f"Blocked pattern: {pat.pattern}")
                raise SecurityViolationError(f"Prompt injection attempt detected and blocked: '{pat.pattern}'")
        return "<untrusted_external_data>\n" + text + "\n</untrusted_external_data>"

    def resolve_safe_project_path(self, project_id: str, rel_subpath: str, allowed_subdirs: List[str], write_mode: bool = False) -> str:
        if not is_safe_path_component(project_id):
            self._log_security_event("PROJECT_ID_SANDBOX_VIOLATION", "Blocked unsafe project ID")
            raise SecurityViolationError("Unsafe project ID blocked")

        if not isinstance(rel_subpath, str) or not rel_subpath or any(
            not is_safe_path_component(part) for part in rel_subpath.split("/")
        ):
            self._log_security_event("PATH_TRAVERSAL_BLOCKED", f"Blocked path: {rel_subpath}")
            raise SecurityViolationError(f"Path traversal or absolute path blocked: {rel_subpath}")

        projects_root = os.path.realpath(os.path.join(self.root_dir, "PROJECTS"))
        project_path = os.path.join(projects_root, project_id)
        if os.path.islink(project_path):
            raise SecurityViolationError(f"Project directory cannot be a symbolic link: {project_id}")
        proj_base = os.path.realpath(project_path)
        if not _path_is_within(projects_root, proj_base):
            raise SecurityViolationError(f"Project directory escapes the projects root: {project_id}")

        target_full = os.path.realpath(os.path.join(proj_base, *rel_subpath.split("/")))
        if not _path_is_within(proj_base, target_full):
            raise SecurityViolationError(f"Path escapes project sandbox: {rel_subpath}")

        top_subdir = rel_subpath.split("/")[0]
        if top_subdir not in allowed_subdirs:
            self._log_security_event("SANDBOX_DIR_VIOLATION", f"Subdir '{top_subdir}' not in {allowed_subdirs}")
            raise SecurityViolationError(f"Agent is not permitted to access project subdirectory '{top_subdir}'. Allowed: {allowed_subdirs}")

        allowed_base_path = os.path.join(proj_base, top_subdir)
        if os.path.islink(allowed_base_path):
            raise SecurityViolationError(f"Project subdirectory cannot be a symbolic link: {top_subdir}")
        allowed_base = os.path.realpath(allowed_base_path)
        if not _path_is_within(proj_base, allowed_base) or not _path_is_within(allowed_base, target_full):
            raise SecurityViolationError(f"Path escapes allowed project subdirectory: {rel_subpath}")

        if write_mode:
            if os.path.normcase(top_subdir) == os.path.normcase("APPROVED"):
                raise SecurityViolationError("Direct agent writes to APPROVED/ are strictly prohibited.")
            if os.path.exists(target_full):
                # Check if existing file is locked as approved in DB
                rel_from_root = os.path.relpath(target_full, self.root_dir)
                with self.db.get_connection() as conn:
                    row = conn.execute(
                        "SELECT approval_status FROM asset_revisions WHERE file_location = ? AND approval_status = 'APPROVED'",
                        (rel_from_root,)
                    ).fetchone()
                    if row:
                        raise SecurityViolationError(f"Cannot overwrite approved asset file: {rel_from_root}")
        return target_full

    def execute_agent_operation(
        self,
        operation_id: str,
        project_id: str,
        agent_id: str,
        department: str,
        operating_mode: str,
        provider_profile_rel_path: str,
        task_instructions: Dict[str, Any],
        handler_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
    ) -> Dict[str, Any]:
        started_at = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        context = self.governance.build_agent_context(
            project_id=project_id,
            operating_mode=operating_mode,
            agent_id=agent_id,
            department=department,
            provider_profile_rel_path=provider_profile_rel_path,
            task_instructions=task_instructions,
        )

        envelope = handler_fn(context)
        try:
            jsonschema.validate(instance=envelope, schema=self.agent_envelope_schema)
        except jsonschema.ValidationError as exc:
            raise SchemaValidationError(f"Agent '{agent_id}' returned malformed output envelope: {exc.message}") from exc

        # Enforce human approval policy on all creative outputs
        for out in envelope.get("outputs", []):
            if out.get("approval_status") == "approved":
                raise SecurityViolationError(f"Agent '{agent_id}' illegally marked output '{out.get('asset_id')}' as approved.")

        completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO agent_executions
                   (operation_id, project_id, agent_id, operating_mode, prompt_versions_json, input_payload_json, output_envelope_json, status, started_at, completed_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    operation_id,
                    project_id,
                    agent_id,
                    operating_mode,
                    json.dumps(context["prompt_versions"]),
                    redact_secrets(json.dumps(task_instructions)),
                    redact_secrets(json.dumps(envelope)),
                    envelope["status"],
                    started_at,
                    completed_at,
                )
            )
            conn.commit()
        return envelope

    def _log_security_event(self, event_type: str, msg: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO audit_events (event_id, project_id, actor, event_type, severity, details_json, occurred_at) VALUES (?, NULL, 'AGENT_EXECUTOR', ?, 'HIGH', ?, ?)",
                (f"SEC_{int(datetime.now(timezone.utc).timestamp()*1000000)}", event_type, json.dumps({"message": redact_secrets(msg)}), datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
            )
            conn.commit()
