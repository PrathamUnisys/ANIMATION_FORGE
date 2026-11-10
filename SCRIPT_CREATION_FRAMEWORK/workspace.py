"""Safe filesystem workspace setup and immutable artifact helpers."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


MODULE_ROOT = Path(__file__).resolve().parent
SCHEMA_DIR = MODULE_ROOT / "schemas"
TEMPLATE_DIR = MODULE_ROOT / "templates"
PROJECT_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{1,63}$")
PROJECT_LAYOUT = (
    "brief",
    "research/sources",
    "research/claims",
    "concepts",
    "architecture",
    "scripts/original",
    "scripts/revised",
    "reviews/creative",
    "reviews/fact_check",
    "qc",
    "production_notes",
    "handoff",
)


class WorkspaceError(ValueError):
    """Raised when a workspace operation is unsafe or invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise WorkspaceError(f"JSON_PARSE_FAIL: {path}: {exc}") from exc


def validate_json_file(path: Path, schema_path: Path) -> dict[str, Any]:
    """Parse JSON first, then run Draft 2020-12 Schema validation separately."""
    data = _read_json(path)
    schema = _read_json(schema_path)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda err: list(map(str, err.absolute_path)))
    return {
        "json_parse": "PASS",
        "schema_validation": "PASS" if not errors else "FAIL",
        "schema": str(schema_path),
        "errors": [
            {
                "path": "/" + "/".join(str(part) for part in error.absolute_path),
                "message": error.message,
            }
            for error in errors
        ],
    }


def initialize_workspace(root: Path, project_id: str, title: str) -> Path:
    """Create a new project workspace without overwriting an existing path."""
    if not PROJECT_ID_RE.fullmatch(project_id):
        raise WorkspaceError("Project ID must be 2-64 lowercase letters, digits, '_' or '-' and start with a letter or digit.")
    if not title.strip():
        raise WorkspaceError("Project title must not be empty.")

    root = root.expanduser().resolve()
    root.mkdir(parents=True, exist_ok=True)
    project_path = root / project_id
    if project_path.exists():
        raise FileExistsError(f"Project already exists; refusing to overwrite: {project_path}")

    created: list[Path] = []
    try:
        project_path.mkdir()
        created.append(project_path)
        for relative in PROJECT_LAYOUT:
            directory = project_path / relative
            directory.mkdir(parents=True, exist_ok=True)
            created.append(directory)

        template_destinations = {
            "01_BRIEF_TEMPLATE.md": "brief/brief.md",
            "02_SOURCE_DOSSIER_TEMPLATE.md": "research/sources/source_dossier.md",
            "07_SOURCE_LEDGER_TEMPLATE.json": "research/sources/sources.json",
            "03_SCRIPT_TEMPLATE.md": "scripts/original/script_template.md",
            "04_CLAIM_LEDGER_TEMPLATE.json": "research/claims/claims.json",
            "05_RETENTION_MAP_TEMPLATE.json": "scripts/revised/retention_map.template.json",
            "06_REVIEW_TEMPLATE.json": "reviews/creative/review.template.json",
        }
        for template_name, relative_destination in template_destinations.items():
            source = TEMPLATE_DIR / template_name
            destination = project_path / relative_destination
            shutil.copyfile(source, destination)

        manifest = {
            "schema_version": "1.0.0",
            "project_id": project_id,
            "title": title.strip(),
            "created_at": utc_now(),
            "stage": "IDEA_INTAKE",
            "approval_status": "NOT_SUBMITTED",
            "artifacts": [],
            "checks": [],
        }
        manifest_path = project_path / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        result = validate_json_file(manifest_path, SCHEMA_DIR / "project_manifest.schema.json")
        if result["schema_validation"] != "PASS":
            raise WorkspaceError(f"New manifest failed schema validation: {result['errors']}")
        return project_path
    except Exception:
        # Only remove the exact newly-created target. Never recurse into an existing project.
        if project_path.exists() and project_path.is_dir():
            shutil.rmtree(project_path)
        raise


def add_artifact(project_path: Path, artifact_type: str, source_path: Path, relative_path: str) -> dict[str, Any]:
    """Copy an artifact into an unused path and register its hash in manifest."""
    project_path = project_path.resolve()
    manifest_path = project_path / "manifest.json"
    manifest = _read_json(manifest_path)
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise WorkspaceError(f"Artifact source does not exist or is not a file: {source_path}")

    candidate = (project_path / relative_path).resolve()
    if not candidate.is_relative_to(project_path):
        raise WorkspaceError("Artifact destination must remain inside the project workspace.")
    if candidate.exists():
        raise FileExistsError(f"Artifact destination already exists; revisions are never overwritten: {candidate}")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source_path, candidate)
    record = {
        "artifact_type": artifact_type,
        "path": candidate.relative_to(project_path).as_posix(),
        "revision": 1,
        "sha256": sha256_file(candidate),
        "created_at": utc_now(),
        "status": "DRAFT",
    }
    manifest["artifacts"].append(record)
    temporary_manifest = manifest_path.with_name(f".{manifest_path.name}.{record['sha256'][:8]}.tmp")
    try:
        with temporary_manifest.open("x", encoding="utf-8") as stream:
            json.dump(manifest, stream, indent=2)
            stream.write("\n")
        result = validate_json_file(temporary_manifest, SCHEMA_DIR / "project_manifest.schema.json")
        if result["schema_validation"] != "PASS":
            raise WorkspaceError(f"Manifest schema validation failed: {result['errors']}")
        temporary_manifest.replace(manifest_path)
    except Exception:
        temporary_manifest.unlink(missing_ok=True)
        candidate.unlink(missing_ok=True)
        raise
    return record


def validate_manifest(project_path: Path) -> dict[str, Any]:
    project_path = project_path.resolve()
    result = validate_json_file(project_path / "manifest.json", SCHEMA_DIR / "project_manifest.schema.json")
    if result["schema_validation"] != "PASS":
        return result

    manifest = _read_json(project_path / "manifest.json")
    link_errors = []
    for index, artifact in enumerate(manifest["artifacts"]):
        artifact_path = (project_path / artifact["path"]).resolve()
        if not artifact_path.is_relative_to(project_path):
            link_errors.append({"index": index, "message": "artifact path escapes workspace"})
        elif not artifact_path.is_file():
            link_errors.append({"index": index, "message": f"missing artifact: {artifact['path']}"})
        elif sha256_file(artifact_path) != artifact["sha256"]:
            link_errors.append({"index": index, "message": f"hash mismatch: {artifact['path']}"})
    result["artifact_integrity"] = "PASS" if not link_errors else "FAIL"
    result["artifact_errors"] = link_errors
    return result
