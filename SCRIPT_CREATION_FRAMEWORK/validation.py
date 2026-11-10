"""Deterministic checks for factual-claim references and companion timestamps."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .workspace import SCHEMA_DIR, WorkspaceError, validate_json_file


CLAIM_MARKER_RE = re.compile(r"<!--\s*CLAIM:([A-Za-z0-9_-]+)\s*-->")
HEADING_TIME_RE = re.compile(r"^#{1,6}\s+(\d{1,2}:\d{2})\b", re.MULTILINE)


def parse_json_status(path: Path) -> dict[str, Any]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"check": "json_syntax", "status": "FAIL", "path": str(path), "error": str(exc)}
    return {"check": "json_syntax", "status": "PASS", "path": str(path)}


def validate_schema(path: Path, schema_path: Path | None = None) -> dict[str, Any]:
    schema_path = schema_path or (SCHEMA_DIR / "claims.schema.json")
    syntax = parse_json_status(path)
    if syntax["status"] != "PASS":
        return {
            "check": "json_schema",
            "json_syntax_status": "FAIL",
            "schema_validation_status": "NOT_EXECUTED",
            "status": "FAIL",
            "schema": str(schema_path),
            "errors": [syntax.get("error", "Invalid JSON")],
        }
    try:
        result = validate_json_file(path, schema_path)
    except WorkspaceError as exc:
        # The data JSON is valid; this means the supplied schema itself is unusable.
        return {
            "check": "json_schema",
            "json_syntax_status": "PASS",
            "schema_validation_status": "NOT_EXECUTED",
            "status": "FAIL",
            "schema": str(schema_path),
            "errors": [str(exc)],
        }
    return {
        "check": "json_schema",
        "json_syntax_status": result["json_parse"],
        "schema_validation_status": result["schema_validation"],
        "status": result["schema_validation"],
        "schema": result["schema"],
        "errors": result["errors"],
    }


def audit_claim_references(script_path: Path, claims_path: Path, sources_path: Path | None = None) -> dict[str, Any]:
    script = script_path.read_text(encoding="utf-8")
    claims_doc = json.loads(claims_path.read_text(encoding="utf-8"))
    known = {claim["claim_id"] for claim in claims_doc.get("claims", [])}
    used = set(CLAIM_MARKER_RE.findall(script))
    missing = sorted(used - known)
    unreferenced = sorted(known - used)
    missing_source_ids: list[str] = []
    if sources_path is not None:
        sources_doc = json.loads(sources_path.read_text(encoding="utf-8"))
        source_ids = {source["source_id"] for source in sources_doc.get("sources", [])}
        missing_source_ids = sorted({source_id for claim in claims_doc.get("claims", []) for source_id in claim.get("source_ids", []) if source_id not in source_ids})
    unresolved = sorted(
        claim["claim_id"]
        for claim in claims_doc.get("claims", [])
        if claim["claim_id"] in used and claim["verification_status"] not in {"VERIFIED", "QUALIFIED"}
    )
    return {
        "check": "claim_reference_integrity",
        "status": "PASS" if not missing and not unresolved and not missing_source_ids else "FAIL",
        "used_claim_ids": sorted(used),
        "missing_claim_ids": missing,
        "unreferenced_claim_ids": unreferenced,
        "used_unresolved_claim_ids": unresolved,
        "missing_source_ids": missing_source_ids,
        "source_check_performed": sources_path is not None,
        "limitation": "Checks explicit markers and ledger statuses only; does not prove semantic completeness or truth.",
    }


def audit_script_map(script_path: Path, map_path: Path) -> dict[str, Any]:
    script = script_path.read_text(encoding="utf-8")
    map_doc = json.loads(map_path.read_text(encoding="utf-8"))
    headings = HEADING_TIME_RE.findall(script)
    map_times = [entry["timecode"] for entry in map_doc.get("entries", [])]
    errors = []
    if headings != map_times:
        errors.append({"message": "Retention Map timecodes do not exactly match ordered timed headings", "headings": headings, "map": map_times})
    return {
        "check": "script_map_timecodes",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "limitation": "Checks heading/timecode equality only; does not judge map accuracy or timing realism.",
    }
