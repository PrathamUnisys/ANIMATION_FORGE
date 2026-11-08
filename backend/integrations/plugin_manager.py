import os
import json
import jsonschema
from datetime import datetime, timezone
from typing import Any, Dict
from backend.database import DatabaseManager


VALID_PLUGIN_LIFECYCLE = [
    "DISCOVERED",
    "EVALUATED",
    "INSTALLATION_PROPOSED",
    "APPROVED_FOR_INSTALLATION",
    "INSTALLED",
    "TESTED",
    "ENABLED",
    "DISABLED",
    "REMOVED",
]


class PluginLifecycleError(Exception):
    """Raised when a third-party plugin attempts automatic installation or skips human approval."""


class PluginManager:
    def __init__(self, root_dir: str, db: DatabaseManager):
        self.root_dir = root_dir
        self.db = db
        with open(os.path.join(self.root_dir, "PLUGINS/MANIFEST_SCHEMA.json"), "r", encoding="utf-8") as f:
            self.manifest_schema = json.load(f)

    def register_discovered_plugin(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        jsonschema.validate(instance=manifest, schema=self.manifest_schema)
        pid = manifest["plugin_id"]
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO plugin_records
                   (plugin_id, name, version, developer, lifecycle_state, manifest_json, updated_at)
                   VALUES (?, ?, ?, ?, 'DISCOVERED', ?, ?)""",
                (pid, manifest["name"], manifest["version"], manifest["developer"], json.dumps(manifest), now)
            )
            conn.commit()
        return self.get_plugin(pid)

    def transition_plugin_state(self, plugin_id: str, target_state: str, human_authorized: bool = False) -> Dict[str, Any]:
        if target_state not in VALID_PLUGIN_LIFECYCLE:
            raise ValueError(f"Invalid plugin state: {target_state}")
        rec = self.get_plugin(plugin_id)
        curr = rec["lifecycle_state"]

        if target_state in ("APPROVED_FOR_INSTALLATION", "INSTALLED", "ENABLED") and not human_authorized:
            raise PluginLifecycleError(
                f"Cannot transition plugin '{plugin_id}' from '{curr}' to '{target_state}' without explicit human authorization."
            )
        if target_state == "INSTALLED" and curr != "APPROVED_FOR_INSTALLATION":
            raise PluginLifecycleError(
                f"Plugin '{plugin_id}' must be in state 'APPROVED_FOR_INSTALLATION' before installation (current: '{curr}')."
            )

        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
        with self.db.get_connection() as conn:
            conn.execute(
                "UPDATE plugin_records SET lifecycle_state = ?, updated_at = ? WHERE plugin_id = ?",
                (target_state, now, plugin_id)
            )
            conn.commit()
        return self.get_plugin(plugin_id)

    def get_plugin(self, plugin_id: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM plugin_records WHERE plugin_id = ?", (plugin_id,)).fetchone()
            if not row:
                raise KeyError(f"Plugin {plugin_id} not found")
            return dict(row)
