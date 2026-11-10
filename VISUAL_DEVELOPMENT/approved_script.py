from __future__ import annotations

import sqlite3
from pathlib import Path
from urllib.parse import quote
from typing import Any

from .common import sha256_text


class ApprovedScriptError(ValueError):
    pass


def load_approved_script(database_path: str | Path, script_id: str) -> dict[str, Any]:
    """Read one immutable, APPROVED screenplay row without opening the DB for writes."""
    db_path = Path(database_path).resolve()
    if not db_path.is_file():
        raise ApprovedScriptError(f"Database file does not exist: {db_path}")
    uri = f"file:{quote(db_path.as_posix(), safe='/:')}?mode=ro"
    try:
        connection = sqlite3.connect(uri, uri=True, timeout=3)
        connection.row_factory = sqlite3.Row
        try:
            row = connection.execute(
                """SELECT script_id, project_id, episode_id, version, approval_status,
                          is_immutable, content_markdown, created_at
                   FROM scripts WHERE script_id = ?""",
                (script_id,),
            ).fetchone()
        finally:
            connection.close()
    except sqlite3.Error as exc:
        raise ApprovedScriptError(f"Could not read approved script record: {exc}") from exc
    if row is None:
        raise ApprovedScriptError(f"No screenplay record found for {script_id!r}")
    if row["approval_status"] != "APPROVED":
        raise ApprovedScriptError(
            f"Script {script_id!r} has status {row['approval_status']!r}; APPROVED is required"
        )
    if not bool(row["is_immutable"]):
        raise ApprovedScriptError(f"Script {script_id!r} is not marked immutable")
    content = row["content_markdown"]
    if not isinstance(content, str) or not content.strip():
        raise ApprovedScriptError(f"Script {script_id!r} has no screenplay text")
    return {
        "script_id": row["script_id"],
        "project_id": row["project_id"],
        "episode_id": row["episode_id"],
        "version": row["version"],
        "approval_status": row["approval_status"],
        "is_immutable": bool(row["is_immutable"]),
        "created_at": row["created_at"],
        "content_markdown": content,
        "sha256": sha256_text(content),
        "database_path": str(db_path),
    }
