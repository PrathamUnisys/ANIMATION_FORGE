import json
import jsonschema
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional
from backend.database import DatabaseManager


PERMISSION_TIERS = {
    "READ_ONLY",
    "DRAFT_CREATION",
    "LOCAL_MODIFICATION",
    "EXTERNAL_NETWORK",
    "PAID_OPERATION",
    "DESTRUCTIVE_OPERATION",
}

VALID_TRANSPORTS = {"STDIO", "STREAMABLE_HTTP"}


class McpPermissionDeniedError(Exception):
    """Raised when an MCP tool invocation violates its permission classification policy."""


class McpConnectionError(Exception):
    """Raised when an MCP server fails health check or is unreachable."""


class AnimationForgeMcpGateway:
    """
    Operates as both:
    1. An MCP Client connecting to external STDIO / Streamable HTTP MCP servers with strict permission enforcement.
    2. An MCP Server exposing controlled Animation Forge tools (Project, Creative, Production, Review) without arbitrary file modification.
    """
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.exposed_server_tools: Dict[str, Dict[str, Any]] = {}
        self._register_builtin_server_tools()

    def _register_builtin_server_tools(self) -> None:
        builtins = [
            # Project tools
            ("forge.project.get_info", "PROJECT", "READ_ONLY", "Get project metadata and current stage"),
            ("forge.project.get_approved_screenplay", "PROJECT", "READ_ONLY", "Get immutable approved screenplay"),
            ("forge.project.get_character_info", "PROJECT", "READ_ONLY", "Get character bible and visual locks"),
            ("forge.project.get_asset_registry", "PROJECT", "READ_ONLY", "List registered project assets and revisions"),
            ("forge.project.get_production_status", "PROJECT", "READ_ONLY", "Get active tasks, approvals, and milestones"),
            # Creative tools
            ("forge.creative.submit_script_revision", "CREATIVE", "DRAFT_CREATION", "Submit a new screenplay draft revision"),
            ("forge.creative.submit_character_proposal", "CREATIVE", "DRAFT_CREATION", "Submit a character design concept draft"),
            ("forge.creative.generate_scene_breakdown", "CREATIVE", "DRAFT_CREATION", "Generate structured scene breakdown draft"),
            ("forge.creative.create_storyboard_spec", "CREATIVE", "DRAFT_CREATION", "Create shot and storyboard panel specification"),
            # Production tools
            ("forge.production.submit_generation_job", "PRODUCTION", "PAID_OPERATION", "Submit an authorized generation job"),
            ("forge.production.get_job_status", "PRODUCTION", "READ_ONLY", "Retrieve generation job status"),
            ("forge.production.get_approved_workflow", "PRODUCTION", "READ_ONLY", "Retrieve locked toolchain workflow definition"),
            ("forge.production.register_output_asset", "PRODUCTION", "DRAFT_CREATION", "Register newly generated draft asset"),
            ("forge.production.submit_for_review", "PRODUCTION", "LOCAL_MODIFICATION", "Transition deliverable to AWAITING_HUMAN_REVIEW"),
            # Review tools
            ("forge.review.get_status", "REVIEW", "READ_ONLY", "Retrieve deliverable approval state"),
            ("forge.review.submit_revision_request", "REVIEW", "LOCAL_MODIFICATION", "Submit technical or human revision request"),
            ("forge.review.get_approval_history", "REVIEW", "READ_ONLY", "Retrieve immutable approval audit trail"),
        ]
        for name, cat, perm, desc in builtins:
            self.exposed_server_tools[name] = {
                "name": name,
                "category": cat,
                "permission_tier": perm,
                "description": desc,
            }

    def register_external_mcp_server(
        self,
        server_id: str,
        name: str,
        endpoint_or_command: str,
        transport: str,
        version: str,
        tools: List[Dict[str, Any]],
        human_approved_install: bool = False
    ) -> Dict[str, Any]:
        if not human_approved_install:
            raise McpPermissionDeniedError(f"Installing/registering external MCP server '{name}' requires explicit human approval.")
        if transport not in VALID_TRANSPORTS:
            raise ValueError(f"Unsupported MCP transport '{transport}'. Supported: {sorted(VALID_TRANSPORTS)}")

        for t in tools:
            if t.get("permission_tier") not in PERMISSION_TIERS:
                raise ValueError(f"Tool '{t.get('name')}' missing valid permission_tier in {PERMISSION_TIERS}")

        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO mcp_servers
                   (server_id, name, endpoint_or_command, transport, version, connection_status, tools_json, resources_json, prompts_json, permissions_json, last_connected_at, error_history_json)
                   VALUES (?, ?, ?, ?, ?, 'DISCONNECTED', ?, '[]', '[]', ?, NULL, '[]')""",
                (
                    server_id, name, endpoint_or_command, transport, version,
                    json.dumps(tools),
                    json.dumps([t["permission_tier"] for t in tools])
                )
            )
            conn.commit()
        return self.get_mcp_server(server_id)

    def run_server_health_check(self, server_id: str, simulate_reachable: bool = True) -> Dict[str, Any]:
        srv = self.get_mcp_server(server_id)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            if simulate_reachable:
                conn.execute(
                    "UPDATE mcp_servers SET connection_status = 'CONNECTED', last_connected_at = ? WHERE server_id = ?",
                    (now, server_id)
                )
            else:
                errors = json.loads(srv["error_history_json"])
                errors.append({"timestamp": now, "error": "Connection timeout / health check failed"})
                conn.execute(
                    "UPDATE mcp_servers SET connection_status = 'UNREACHABLE', error_history_json = ? WHERE server_id = ?",
                    (json.dumps(errors), server_id)
                )
            conn.commit()
        return self.get_mcp_server(server_id)

    def execute_mcp_tool(
        self,
        server_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
        has_approved_production_instructions: bool = False,
        has_paid_budget_authorization: bool = False,
        has_individual_destructive_authorization: bool = False,
    ) -> Dict[str, Any]:
        srv = self.get_mcp_server(server_id)
        if srv["connection_status"] != "CONNECTED":
            raise McpConnectionError(f"MCP Server '{server_id}' is not CONNECTED (current status: {srv['connection_status']}). Run health check first.")

        tools = json.loads(srv["tools_json"])
        tool_spec = next((t for t in tools if t["name"] == tool_name), None)
        if not tool_spec:
            raise KeyError(f"Tool '{tool_name}' not found on MCP server '{server_id}'")

        tier = tool_spec["permission_tier"]
        if tier == "DRAFT_CREATION" and not has_approved_production_instructions:
            raise McpPermissionDeniedError(f"Tool '{tool_name}' (DRAFT_CREATION) requires approved production instructions.")
        if tier == "PAID_OPERATION" and not has_paid_budget_authorization:
            raise McpPermissionDeniedError(f"Tool '{tool_name}' (PAID_OPERATION) requires explicit budget/spending authorization.")
        if tier == "DESTRUCTIVE_OPERATION" and not has_individual_destructive_authorization:
            raise McpPermissionDeniedError(f"Tool '{tool_name}' (DESTRUCTIVE_OPERATION) requires explicit individual human authorization.")

        return {
            "server_id": server_id,
            "tool_name": tool_name,
            "permission_tier": tier,
            "status": "executed",
            "result": {"acknowledged": True, "echo_args": arguments},
            "executed_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        }

    def get_mcp_server(self, server_id: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM mcp_servers WHERE server_id = ?", (server_id,)).fetchone()
            if not row:
                raise KeyError(f"MCP server {server_id} not found")
            return dict(row)
