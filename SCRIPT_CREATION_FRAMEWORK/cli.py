"""Command line entry point for the isolated Script Creation Framework."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .runtime import count_file, estimate_runtime
from .validation import audit_claim_references, audit_script_map, parse_json_status, validate_schema
from .workspace import WorkspaceError, add_artifact, initialize_workspace, validate_manifest


def _print(value: object) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="script-framework", description="Local-first script project workspace and deterministic checks.")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Create a new workspace without overwriting existing work.")
    init.add_argument("--root", type=Path, required=True, help="Parent directory for the new workspace.")
    init.add_argument("--id", required=True, help="Lowercase project ID (2-64 chars).")
    init.add_argument("--title", required=True)

    add = commands.add_parser("add-artifact", help="Copy and register an immutable artifact revision.")
    add.add_argument("--project", type=Path, required=True)
    add.add_argument("--type", required=True, dest="artifact_type")
    add.add_argument("--source", type=Path, required=True)
    add.add_argument("--path", required=True, help="Workspace-relative destination, which must not exist.")

    manifest = commands.add_parser("validate-manifest", help="Parse and validate a manifest and its artifact hashes.")
    manifest.add_argument("--project", type=Path, required=True)

    parse = commands.add_parser("parse-json", help="Check JSON syntax only.")
    parse.add_argument("path", type=Path)

    schema = commands.add_parser("validate-json-schema", help="Run JSON syntax parsing and Draft 2020-12 validation against an explicit schema.")
    schema.add_argument("--path", type=Path, required=True)
    schema.add_argument("--schema", type=Path, required=True)

    count = commands.add_parser("count", help="Count [NARRATION] blocks only in a Markdown script.")
    count.add_argument("script", type=Path)
    count.add_argument("--rate-wpm", type=float)
    count.add_argument("--holds-min", type=float, default=0)
    count.add_argument("--holds-max", type=float, default=0)

    refs = commands.add_parser("check-claims", help="Check explicit <!-- CLAIM:id --> markers against a claim ledger.")
    refs.add_argument("--script", type=Path, required=True)
    refs.add_argument("--claims", type=Path, required=True)
    refs.add_argument("--sources", type=Path, help="Optional JSON source ledger; validates claim source IDs.")

    timecodes = commands.add_parser("check-map", help="Check ordered timed headings against Retention Map timecodes.")
    timecodes.add_argument("--script", type=Path, required=True)
    timecodes.add_argument("--map", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "init":
            path = initialize_workspace(args.root, args.id, args.title)
            _print({"status": "PASS", "project_path": str(path), "message": "Workspace created; no script content or approval was generated."})
            return 0
        if args.command == "add-artifact":
            _print(add_artifact(args.project, args.artifact_type, args.source, args.path))
            return 0
        if args.command == "validate-manifest":
            result = validate_manifest(args.project)
            _print(result)
            return 0 if result.get("schema_validation") == "PASS" and result.get("artifact_integrity", "PASS") == "PASS" else 1
        if args.command == "parse-json":
            result = parse_json_status(args.path)
            _print(result)
            return 0 if result["status"] == "PASS" else 1
        if args.command == "validate-json-schema":
            result = validate_schema(args.path, args.schema)
            _print(result)
            return 0 if result["status"] == "PASS" else 1
        if args.command == "count":
            result = count_file(args.script)
            if args.rate_wpm is not None:
                result["runtime"] = estimate_runtime(result["narration_word_count"], args.rate_wpm, args.holds_min, args.holds_max)
            _print(result)
            return 0
        if args.command == "check-claims":
            result = audit_claim_references(args.script, args.claims, args.sources)
            _print(result)
            return 0 if result["status"] == "PASS" else 1
        if args.command == "check-map":
            result = audit_script_map(args.script, args.map)
            _print(result)
            return 0 if result["status"] == "PASS" else 1
    except (WorkspaceError, FileNotFoundError, FileExistsError, json.JSONDecodeError, ValueError) as exc:
        _print({"status": "FAIL", "error": str(exc)})
        return 2
    return 2


if __name__ == "__main__":
    sys.exit(main())
