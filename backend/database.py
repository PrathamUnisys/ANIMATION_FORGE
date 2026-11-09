import os
import json
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.filesystem_security import is_safe_path_component

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "animation_forge.db")

SCHEMA_MIGRATIONS = [
    (1, "initial_36_entities_schema", """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TEXT NOT NULL
    );

    -- 1. Application settings
    CREATE TABLE IF NOT EXISTS application_settings (
        key TEXT PRIMARY KEY,
        value_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 2. Projects
    CREATE TABLE IF NOT EXISTS projects (
        project_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        synopsis TEXT NOT NULL,
        genre TEXT NOT NULL,
        target_audience TEXT NOT NULL,
        intended_runtime_sec INTEGER NOT NULL,
        language TEXT NOT NULL,
        creative_brief TEXT NOT NULL,
        visual_direction TEXT NOT NULL,
        animation_technique TEXT NOT NULL,
        production_goals_json TEXT NOT NULL,
        restrictions_json TEXT NOT NULL,
        status TEXT NOT NULL,
        current_stage TEXT NOT NULL,
        active_mode TEXT NOT NULL DEFAULT 'PRODUCTION_MODE',
        series_id TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 3. Series
    CREATE TABLE IF NOT EXISTS series (
        series_id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        bible_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 4. Episodes
    CREATE TABLE IF NOT EXISTS episodes (
        episode_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        series_id TEXT,
        episode_number INTEGER NOT NULL,
        title TEXT NOT NULL,
        animation_technique TEXT NOT NULL,
        status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 5. Agents
    CREATE TABLE IF NOT EXISTS agents (
        agent_id TEXT PRIMARY KEY,
        role_title TEXT NOT NULL,
        department TEXT NOT NULL,
        instruction_path TEXT NOT NULL,
        allowed_dirs_json TEXT NOT NULL,
        allowed_tools_json TEXT NOT NULL,
        forbidden_ops_json TEXT NOT NULL,
        output_schema_path TEXT NOT NULL
    );

    -- 6. Agent prompts
    CREATE TABLE IF NOT EXISTS agent_prompts (
        prompt_id TEXT NOT NULL,
        version TEXT NOT NULL,
        file_path TEXT NOT NULL,
        content_hash TEXT NOT NULL,
        modified_date TEXT NOT NULL,
        description TEXT NOT NULL,
        dependencies_json TEXT NOT NULL,
        change_history_json TEXT NOT NULL,
        PRIMARY KEY (prompt_id, version)
    );

    -- 7. Agent executions
    CREATE TABLE IF NOT EXISTS agent_executions (
        operation_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        operating_mode TEXT NOT NULL,
        prompt_versions_json TEXT NOT NULL,
        input_payload_json TEXT NOT NULL,
        output_envelope_json TEXT NOT NULL,
        status TEXT NOT NULL,
        started_at TEXT NOT NULL,
        completed_at TEXT NOT NULL
    );

    -- 8. Operating modes
    CREATE TABLE IF NOT EXISTS operating_modes (
        mode_id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        allowed_ops_json TEXT NOT NULL,
        forbidden_ops_json TEXT NOT NULL,
        is_restricted INTEGER NOT NULL DEFAULT 0
    );

    -- 9. Architecture versions
    CREATE TABLE IF NOT EXISTS architecture_versions (
        version_id TEXT PRIMARY KEY,
        parent_version_id TEXT,
        change_request_id TEXT,
        snapshot_json TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );

    -- 10. Change requests
    CREATE TABLE IF NOT EXISTS change_requests (
        change_request_id TEXT PRIMARY KEY,
        current_architecture_version TEXT NOT NULL,
        requested_modification TEXT NOT NULL,
        reason TEXT NOT NULL,
        affected_departments_json TEXT NOT NULL,
        affected_workflows_json TEXT NOT NULL,
        compatibility_impact TEXT NOT NULL,
        advantages TEXT NOT NULL,
        disadvantages TEXT NOT NULL,
        testing_requirements TEXT NOT NULL,
        rollback_plan TEXT NOT NULL,
        proposed_version TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        decided_at TEXT
    );

    -- 11. Research reports
    CREATE TABLE IF NOT EXISTS research_reports (
        report_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        research_date TEXT NOT NULL,
        search_methodology TEXT NOT NULL,
        requirements_json TEXT NOT NULL,
        sources_json TEXT NOT NULL,
        recommendations_json TEXT NOT NULL,
        poc_results_json TEXT NOT NULL,
        markdown_path TEXT NOT NULL,
        decision_status TEXT NOT NULL
    );

    -- 12. Tool candidates
    CREATE TABLE IF NOT EXISTS tool_candidates (
        tool_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        version TEXT NOT NULL,
        state TEXT NOT NULL,
        source_url TEXT NOT NULL,
        source_type TEXT NOT NULL,
        retrieved_at TEXT NOT NULL,
        license TEXT NOT NULL,
        commercial_use_allowed INTEGER NOT NULL,
        estimated_cost_usd REAL NOT NULL,
        hardware_compatible INTEGER NOT NULL
    );

    -- 13. Tool evaluations
    CREATE TABLE IF NOT EXISTS tool_evaluations (
        eval_id TEXT PRIMARY KEY,
        tool_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        scores_json TEXT NOT NULL,
        weighted_total REAL NOT NULL,
        evidence_notes TEXT NOT NULL,
        evaluated_at TEXT NOT NULL
    );

    -- 14. Toolchain profiles
    CREATE TABLE IF NOT EXISTS toolchain_profiles (
        toolchain_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        version INTEGER NOT NULL,
        locked INTEGER NOT NULL DEFAULT 0,
        profile_json TEXT NOT NULL,
        file_path TEXT NOT NULL,
        approved_by TEXT,
        approved_at TEXT
    );

    -- 15. Integrations
    CREATE TABLE IF NOT EXISTS integrations (
        integration_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        endpoint TEXT NOT NULL,
        version TEXT NOT NULL,
        health_status TEXT NOT NULL,
        last_health_check TEXT,
        capabilities_json TEXT NOT NULL,
        permissions_json TEXT NOT NULL
    );

    -- 16. MCP servers
    CREATE TABLE IF NOT EXISTS mcp_servers (
        server_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        endpoint_or_command TEXT NOT NULL,
        transport TEXT NOT NULL,
        version TEXT NOT NULL,
        connection_status TEXT NOT NULL,
        tools_json TEXT NOT NULL,
        resources_json TEXT NOT NULL,
        prompts_json TEXT NOT NULL,
        permissions_json TEXT NOT NULL,
        last_connected_at TEXT,
        error_history_json TEXT NOT NULL
    );

    -- 17. Plugin records
    CREATE TABLE IF NOT EXISTS plugin_records (
        plugin_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        developer TEXT NOT NULL,
        lifecycle_state TEXT NOT NULL,
        manifest_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 18. Tasks
    CREATE TABLE IF NOT EXISTS tasks (
        task_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        episode_id TEXT,
        department TEXT NOT NULL,
        assigned_agent TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        retry_count INTEGER NOT NULL DEFAULT 0,
        max_retries INTEGER NOT NULL DEFAULT 3,
        error_category TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 19. Dependencies
    CREATE TABLE IF NOT EXISTS dependencies (
        dependency_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        task_id TEXT NOT NULL,
        depends_on_task_id TEXT NOT NULL,
        dependency_type TEXT NOT NULL
    );

    -- 20. Assets
    CREATE TABLE IF NOT EXISTS assets (
        asset_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        type TEXT NOT NULL,
        description TEXT NOT NULL,
        project_id TEXT NOT NULL,
        character_id TEXT,
        scene_references_json TEXT NOT NULL,
        current_revision INTEGER NOT NULL,
        approval_status TEXT NOT NULL,
        license_info TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 21. Asset revisions
    CREATE TABLE IF NOT EXISTS asset_revisions (
        revision_id TEXT PRIMARY KEY,
        asset_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        revision INTEGER NOT NULL,
        file_location TEXT NOT NULL,
        file_sha256 TEXT NOT NULL,
        creation_agent TEXT NOT NULL,
        tool_used TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        workflow_json TEXT NOT NULL,
        prompt TEXT NOT NULL,
        negative_prompt TEXT,
        seed INTEGER,
        input_references_json TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 22. Asset references
    CREATE TABLE IF NOT EXISTS asset_references (
        ref_id TEXT PRIMARY KEY,
        source_asset_id TEXT NOT NULL,
        target_asset_id TEXT NOT NULL,
        relationship_type TEXT NOT NULL
    );

    -- 23. Characters
    CREATE TABLE IF NOT EXISTS characters (
        character_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        bible_json TEXT NOT NULL,
        visual_consistency_locks_json TEXT NOT NULL,
        voice_profile_json TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 24. Environments
    CREATE TABLE IF NOT EXISTS environments (
        location_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        name TEXT NOT NULL,
        environment_type TEXT NOT NULL,
        bible_json TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    -- 25. Scripts
    CREATE TABLE IF NOT EXISTS scripts (
        script_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        version INTEGER NOT NULL,
        previous_version INTEGER,
        change_summary TEXT NOT NULL,
        agent_responsible TEXT NOT NULL,
        reason_for_changes TEXT NOT NULL,
        reviewer_comments TEXT NOT NULL,
        scores_json TEXT NOT NULL,
        passes_completed_json TEXT NOT NULL,
        content_markdown TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        is_immutable INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    );

    -- 26. Scenes
    CREATE TABLE IF NOT EXISTS scenes (
        scene_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        title TEXT NOT NULL,
        location_id TEXT NOT NULL,
        characters_json TEXT NOT NULL,
        required_assets_json TEXT NOT NULL,
        duration_sec REAL NOT NULL,
        animation_method TEXT NOT NULL,
        required_shots_json TEXT NOT NULL,
        camera_requirements TEXT NOT NULL,
        audio_dependencies_json TEXT NOT NULL,
        lighting TEXT NOT NULL,
        vfx_json TEXT NOT NULL,
        production_dependencies_json TEXT NOT NULL,
        expected_outputs_json TEXT NOT NULL
    );

    -- 27. Shots
    CREATE TABLE IF NOT EXISTS shots (
        shot_id TEXT PRIMARY KEY,
        scene_id TEXT NOT NULL,
        project_id TEXT NOT NULL,
        camera_angle TEXT NOT NULL,
        shot_size TEXT NOT NULL,
        camera_position TEXT NOT NULL,
        camera_movement TEXT NOT NULL,
        focal_length_mm REAL NOT NULL,
        character_placement TEXT NOT NULL,
        character_movement TEXT NOT NULL,
        facial_expression TEXT NOT NULL,
        lighting TEXT NOT NULL,
        audio_cues_json TEXT NOT NULL,
        duration_sec REAL NOT NULL,
        fps INTEGER NOT NULL,
        resolution TEXT NOT NULL,
        required_assets_json TEXT NOT NULL,
        storyboard_panel_path TEXT,
        approval_status TEXT NOT NULL
    );

    -- 28. Audio assets
    CREATE TABLE IF NOT EXISTS audio_assets (
        audio_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        scene_id TEXT NOT NULL,
        line_id TEXT NOT NULL,
        character_id TEXT NOT NULL,
        spoken_text TEXT NOT NULL,
        emotion_direction TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        tts_payload_json TEXT NOT NULL,
        pronunciation_notes_json TEXT NOT NULL,
        file_path TEXT NOT NULL,
        duration_sec REAL NOT NULL,
        approval_status TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 29. Approvals
    CREATE TABLE IF NOT EXISTS approvals (
        approval_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        revision INTEGER NOT NULL,
        state TEXT NOT NULL,
        technical_qc_outcome TEXT,
        reviewer_type TEXT NOT NULL,
        reviewer_id TEXT NOT NULL,
        comments TEXT NOT NULL,
        decided_at TEXT NOT NULL
    );

    -- 30. QC reports
    CREATE TABLE IF NOT EXISTS qc_reports (
        qc_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        target_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        qc_category TEXT NOT NULL,
        outcome TEXT NOT NULL,
        checks_json TEXT NOT NULL,
        issues_json TEXT NOT NULL,
        recommendations_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );

    -- 31. Generation jobs
    CREATE TABLE IF NOT EXISTS generation_jobs (
        job_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        backend_type TEXT NOT NULL,
        workflow_id TEXT NOT NULL,
        status TEXT NOT NULL,
        input_params_json TEXT NOT NULL,
        output_paths_json TEXT NOT NULL,
        error_message TEXT,
        submitted_at TEXT NOT NULL,
        completed_at TEXT
    );

    -- 32. Execution logs
    CREATE TABLE IF NOT EXISTS execution_logs (
        log_id TEXT PRIMARY KEY,
        project_id TEXT,
        component TEXT NOT NULL,
        level TEXT NOT NULL,
        message_redacted TEXT NOT NULL,
        metadata_json TEXT NOT NULL,
        logged_at TEXT NOT NULL
    );

    -- 33. Creative decisions
    CREATE TABLE IF NOT EXISTS creative_decisions (
        decision_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        memory_layer TEXT NOT NULL,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        rationale TEXT NOT NULL,
        alternatives_rejected_json TEXT NOT NULL,
        approved_by TEXT NOT NULL,
        decided_at TEXT NOT NULL
    );

    -- 34. Provider usage
    CREATE TABLE IF NOT EXISTS provider_usage (
        usage_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        model_id TEXT NOT NULL,
        operation_type TEXT NOT NULL,
        prompt_tokens INTEGER NOT NULL DEFAULT 0,
        completion_tokens INTEGER NOT NULL DEFAULT 0,
        units_consumed REAL NOT NULL DEFAULT 0.0,
        recorded_at TEXT NOT NULL
    );

    -- 35. Cost records
    CREATE TABLE IF NOT EXISTS cost_records (
        cost_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        task_id TEXT,
        amount_usd REAL NOT NULL,
        is_estimated INTEGER NOT NULL DEFAULT 0,
        authorized_by_human INTEGER NOT NULL DEFAULT 0,
        recorded_at TEXT NOT NULL
    );

    -- 36. Audit events
    CREATE TABLE IF NOT EXISTS audit_events (
        event_id TEXT PRIMARY KEY,
        project_id TEXT,
        actor TEXT NOT NULL,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL,
        details_json TEXT NOT NULL,
        occurred_at TEXT NOT NULL
    );
    """),
    (2, "cr006_story_context_screenplay", """
    -- CR_006 M1: Versioned Series Bible (one row per revision; head pointer on series)
    CREATE TABLE IF NOT EXISTS story_bibles (
        bible_revision_id TEXT PRIMARY KEY,
        series_id TEXT NOT NULL,
        project_id TEXT,
        revision INTEGER NOT NULL,
        previous_revision INTEGER,
        status TEXT NOT NULL,
        content_json TEXT NOT NULL,
        content_hash_sha256 TEXT NOT NULL,
        provenance_json TEXT NOT NULL,
        rights_review_status TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(series_id, revision)
    );
    CREATE TABLE IF NOT EXISTS story_bible_heads (
        series_id TEXT PRIMARY KEY,
        project_id TEXT,
        head_revision INTEGER NOT NULL,
        head_status TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    -- CR_006 M1: Episode Brief (one row per revision)
    CREATE TABLE IF NOT EXISTS episode_briefs (
        brief_revision_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        episode_id TEXT,
        series_id TEXT,
        revision INTEGER NOT NULL,
        previous_revision INTEGER,
        status TEXT NOT NULL,
        content_json TEXT NOT NULL,
        content_hash_sha256 TEXT NOT NULL,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        UNIQUE(project_id, episode_id, revision)
    );
    -- CR_006 M3: Staged generation artifacts (one row per stage/revision)
    CREATE TABLE IF NOT EXISTS story_artifacts (
        artifact_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        episode_id TEXT,
        artifact_type TEXT NOT NULL,
        revision INTEGER NOT NULL,
        previous_revision INTEGER,
        status TEXT NOT NULL,
        content_json TEXT NOT NULL,
        content_hash_sha256 TEXT NOT NULL,
        context_hash_sha256 TEXT,
        provider_id TEXT,
        model_id TEXT,
        request_id TEXT,
        usage_json TEXT,
        created_at TEXT NOT NULL,
        UNIQUE(project_id, episode_id, artifact_type, revision)
    );
    -- CR_006 M4: Deterministic QC + creative critique findings
    CREATE TABLE IF NOT EXISTS screenplay_qc_reports (
        report_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        script_id TEXT NOT NULL,
        script_version INTEGER NOT NULL,
        validator_name TEXT NOT NULL,
        outcome TEXT NOT NULL,
        checks_json TEXT NOT NULL,
        issues_json TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    -- CR_006 M2: Provider request provenance (actual usage only when returned)
    CREATE TABLE IF NOT EXISTS provider_requests (
        request_id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        provider_id TEXT NOT NULL,
        model_id TEXT NOT NULL,
        status TEXT NOT NULL,
        latency_ms INTEGER,
        prompt_tokens INTEGER,
        completion_tokens INTEGER,
        total_tokens INTEGER,
        usage_source TEXT NOT NULL,
        error_category TEXT,
        error_detail TEXT,
        created_at TEXT NOT NULL
    );
    """)
]


import hashlib
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._runtime_db_path = self._resolve_working_sqlite_path(self.db_path)
        self.apply_migrations()

    def _resolve_working_sqlite_path(self, target_path: str) -> str:
        # Test direct SQLite lock support (works natively on Windows/macOS/standard Linux; falls back to /tmp shadow on 9p/gVisor mounts)
        try:
            conn = sqlite3.connect(target_path)
            conn.execute("PRAGMA journal_mode = MEMORY;")
            conn.execute("CREATE TABLE IF NOT EXISTS _lock_probe (id INT);")
            conn.close()
            return target_path
        except sqlite3.OperationalError:
            h = hashlib.sha256(target_path.encode("utf-8")).hexdigest()[:16]
            tmp_path = f"/tmp/af_sqlite_{h}_{os.path.basename(target_path)}"
            if os.path.exists(target_path) and os.path.getsize(target_path) > 0 and not os.path.exists(tmp_path):
                shutil.copyfile(target_path, tmp_path)
            return tmp_path

    def _sync_to_target(self) -> None:
        if self._runtime_db_path != self.db_path and os.path.exists(self._runtime_db_path):
            shutil.copyfile(self._runtime_db_path, self.db_path)

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self._runtime_db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
        finally:
            conn.close()
            self._sync_to_target()

    def apply_migrations(self) -> List[int]:
        applied = []
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TEXT NOT NULL
                );
            """)
            cur = conn.execute("SELECT version FROM schema_migrations")
            existing = {row["version"] for row in cur.fetchall()}
            for ver, name, sql in SCHEMA_MIGRATIONS:
                if ver not in existing:
                    conn.executescript(sql)
                    conn.execute(
                        "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
                        (ver, name, datetime.now(timezone.utc).isoformat().replace("+00:00","Z"))
                    )
                    applied.append(ver)
            conn.commit()
        return applied

    def list_tables(self) -> List[str]:
        with self.get_connection() as conn:
            cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
            return [r["name"] for r in cur.fetchall()]

    def run_integrity_check(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cur = conn.execute("PRAGMA integrity_check;")
            result = [r[0] for r in cur.fetchall()]
            tables = self.list_tables()
            return {
                "ok": result == ["ok"],
                "pragma_result": result,
                "table_count": len(tables),
                "checked_at": datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
            }

    def create_backup(self, backup_dir: str) -> str:
        os.makedirs(backup_dir, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
        backup_path = os.path.join(backup_dir, f"animation_forge_backup_{ts}.db")
        self._sync_to_target()
        shutil.copyfile(self._runtime_db_path, backup_path)
        return backup_path

    def restore_backup(self, backup_path: str) -> bool:
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        shutil.copyfile(backup_path, self._runtime_db_path)
        self._sync_to_target()
        return self.run_integrity_check()["ok"]

    def export_project_bundle(self, project_id: str, project_root_dir: str, output_zip_path: str) -> str:
        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
        with self.get_connection() as conn:
            proj = conn.execute("SELECT * FROM projects WHERE project_id = ?", (project_id,)).fetchone()
            if not proj:
                raise ValueError(f"Project {project_id} not found")
            export_data = {"project": dict(proj), "tables": {}}
            for tbl in ["episodes", "tasks", "dependencies", "assets", "asset_revisions", "characters",
                        "environments", "scripts", "scenes", "shots", "audio_assets", "approvals",
                        "qc_reports", "research_reports", "tool_candidates", "toolchain_profiles", "creative_decisions"]:
                rows = conn.execute(f"SELECT * FROM {tbl} WHERE project_id = ?", (project_id,)).fetchall()
                export_data["tables"][tbl] = [dict(r) for r in rows]

        with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("project_db_export.json", json.dumps(export_data, indent=2))
            if os.path.exists(project_root_dir):
                for root, _, files in os.walk(project_root_dir):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel = os.path.relpath(full_path, project_root_dir)
                        zf.write(full_path, os.path.join("project_files", rel))
        return output_zip_path

    def import_project_bundle(self, zip_path: str, projects_base_dir: str, new_project_id: Optional[str] = None) -> str:
        with zipfile.ZipFile(zip_path, "r") as zf:
            export_data = json.loads(zf.read("project_db_export.json").decode("utf-8"))
            if not isinstance(export_data, dict) or not isinstance(export_data.get("project"), dict):
                raise ValueError("Project bundle manifest must contain a project object")
            proj = export_data["project"]
            old_id = proj.get("project_id")
            target_id = new_project_id if new_project_id is not None else old_id
            if not is_safe_path_component(target_id):
                raise ValueError("Project ID must be a single safe path component")

            proj["project_id"] = target_id
            proj["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

            with self.get_connection() as conn:
                project_columns = {
                    row["name"]: row for row in conn.execute("PRAGMA table_info(projects)").fetchall()
                }
            if not proj or set(proj) - project_columns.keys():
                raise ValueError("Project bundle contains unknown project fields")
            required_columns = {
                name
                for name, row in project_columns.items()
                if row["notnull"] and row["dflt_value"] is None
            }
            required_columns.add("project_id")
            if not required_columns.issubset(proj):
                raise ValueError("Project bundle is missing required project fields")

            project_files = []
            seen_paths = set()
            for info in zf.infolist():
                member = info.filename
                if member == "project_files/":
                    continue
                if not member.startswith("project_files/"):
                    continue

                relative_path = member[len("project_files/"):]
                path_value = relative_path[:-1] if info.is_dir() and relative_path.endswith("/") else relative_path
                path_parts = path_value.split("/")
                if not path_value or any(not is_safe_path_component(part) for part in path_parts):
                    raise ValueError(f"Unsafe project bundle path: {member!r}")

                mode = (info.external_attr >> 16) & 0xFFFF
                file_type = stat.S_IFMT(mode)
                if file_type not in (0, stat.S_IFREG, stat.S_IFDIR):
                    raise ValueError(f"Unsupported project bundle entry type: {member!r}")
                if info.is_dir():
                    continue
                if file_type == stat.S_IFDIR:
                    raise ValueError(f"Project bundle file entry is a directory: {member!r}")

                normalized_path = os.path.normcase(os.path.normpath(relative_path))
                if normalized_path in seen_paths:
                    raise ValueError(f"Duplicate project bundle path: {member!r}")
                seen_paths.add(normalized_path)
                project_files.append((info, path_parts))

            for _, path_parts in project_files:
                normalized_parts = [os.path.normcase(part) for part in path_parts]
                if any(
                    os.path.normcase(os.path.normpath(os.path.join(*normalized_parts[:index]))) in seen_paths
                    for index in range(1, len(normalized_parts))
                ):
                    raise ValueError("Project bundle file path conflicts with a parent file")

            project_root = os.path.realpath(projects_base_dir)
            os.makedirs(project_root, exist_ok=True)
            target_dir = os.path.join(project_root, target_id)
            if os.path.commonpath((project_root, os.path.realpath(target_dir))) != project_root:
                raise ValueError("Project bundle destination escapes the projects directory")
            if os.path.lexists(target_dir):
                raise FileExistsError(f"Project destination already exists: {target_id}")

            staging_dir = tempfile.mkdtemp(prefix=".project-import-", dir=project_root)
            target_created = False
            try:
                for info, path_parts in project_files:
                    destination = os.path.join(staging_dir, *path_parts)
                    if os.path.commonpath((staging_dir, os.path.realpath(destination))) != staging_dir:
                        raise ValueError(f"Unsafe project bundle path: {info.filename!r}")
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    with zf.open(info, "r") as source, open(destination, "xb") as output:
                        shutil.copyfileobj(source, output)

                with self.get_connection() as conn:
                    placeholders = ", ".join(["?"] * len(proj))
                    columns = ", ".join(proj)
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute(
                        f"INSERT INTO projects ({columns}) VALUES ({placeholders})",
                        [proj[column] for column in proj]
                    )
                    os.rename(staging_dir, target_dir)
                    target_created = True
                    conn.commit()
            except Exception:
                if target_created:
                    shutil.rmtree(target_dir)
                raise
            finally:
                if os.path.isdir(staging_dir):
                    shutil.rmtree(staging_dir)
            return target_id
