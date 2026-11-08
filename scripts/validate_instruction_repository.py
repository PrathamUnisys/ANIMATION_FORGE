"""Validate governed instruction Markdown and its cross-file contracts."""

from __future__ import annotations

import argparse
import json
import re
import jsonschema
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


REQUIRED_FRONTMATTER = {
    "prompt_id",
    "version",
    "modified_date",
    "description",
    "dependencies",
    "change_history",
}
VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
PROMPT_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]+$")
MCP_OPERATION_PATTERN = re.compile(r'"(forge\.[A-Za-z0-9_.]+)"\s*,')
ROUTE_PATTERN = re.compile(
    r'@app\.(get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)
OPERATION_REFERENCE_PATTERN = re.compile(r"`(forge\.[A-Za-z0-9_.]+)`")
HTTP_REFERENCE_PATTERN = re.compile(r"`((?:GET|POST|PUT|PATCH|DELETE) /api/[A-Za-z0-9_{}./-]+)`")
MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.rule}: {self.path}: {self.message}"


def governed_markdown(root: Path) -> list[Path]:
    patterns = (
        "CORE/*.md",
        "MODES/*.md",
        "GENRES/**/*.md",
        "STYLES/**/*.md",
        "TOOLS/**/*.md",
        "LIBRARY/**/*.md",
        "AGENTS/*/INSTRUCTION.md",
        "DEPARTMENTS/*/DEPARTMENT_RULES.md",
        "ORCHESTRATION/PRODUCTION_DIRECTOR/INSTRUCTION.md",
        "PROVIDERS/**/*.md",
        "DOCS/CHANGE_REQUESTS/*.md",
        "DOCS/SCREENPLAY_CONTEXT_ASSEMBLY.md",
        "DOCS/CAPABILITY_REGISTRY.md",
        "DOCS/AGENT_GUIDE.md",
        "DOCS/INSTRUCTION_REPOSITORY_AUDIT.md",
        "DOCS/TOOL_RND_GUIDE.md",
        "DOCS/*_INTEGRATION_GUIDE.md",
        "DOCS/TOOL_INTELLIGENCE/*.md",
        "DOCS/INTEGRATIONS/*.md",
        "DOCS/TEMPLATES/*.md",
    )
    files = {path.resolve() for pattern in patterns for path in root.glob(pattern) if path.is_file()}
    return sorted(files, key=lambda path: path.as_posix().casefold())


def relative(path: Path, root: Path) -> str:
    return path.relative_to(root.resolve()).as_posix()


def parse_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str, str | None]:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, raw, "missing opening YAML front matter delimiter"
    closing = next((index for index in range(1, len(lines)) if lines[index].strip() == "---"), None)
    if closing is None:
        return None, raw, "missing closing YAML front matter delimiter"
    header = "\n".join(lines[1:closing])
    try:
        parsed = yaml.safe_load(header)
    except yaml.YAMLError as exc:
        return None, "\n".join(lines[closing + 1 :]), f"invalid YAML: {exc}"
    if not isinstance(parsed, dict):
        return None, "\n".join(lines[closing + 1 :]), "front matter must be a YAML mapping"
    return parsed, "\n".join(lines[closing + 1 :]), None


def expected_operations(root: Path) -> set[str]:
    gateway = (root / "backend/integrations/mcp_gateway.py").read_text(encoding="utf-8")
    main = (root / "backend/main.py").read_text(encoding="utf-8")
    operations = set(MCP_OPERATION_PATTERN.findall(gateway))
    operations.update(
        f"{method.upper()} {route}"
        for method, route in ROUTE_PATTERN.findall(main)
        if route.startswith("/api/")
    )
    return operations


def registry_operations(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return set(OPERATION_REFERENCE_PATTERN.findall(text)) | set(HTTP_REFERENCE_PATTERN.findall(text))


def _resolve_dependency(dep: str, source: Path, root: Path, ids: dict[str, Path]) -> Path | None:
    if dep in ids:
        return ids[dep]
    normalized = dep.replace("\\", "/")
    if normalized.lower().endswith(".md") or "/" in normalized:
        candidates = [root / normalized, source.parent / normalized]
        for candidate in candidates:
            if candidate.exists():
                return candidate.resolve()
    return None


def _find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    active: list[str] = []
    completed: set[str] = set()

    def visit(node: str) -> None:
        if node in active:
            start = active.index(node)
            cycles.append(active[start:] + [node])
            return
        if node in completed:
            return
        active.append(node)
        for neighbor in sorted(graph.get(node, set())):
            visit(neighbor)
        active.pop()
        completed.add(node)

    for node in sorted(graph):
        visit(node)
    return cycles


def _resolve_markdown_link(target: str, source: Path, root: Path) -> Path | None:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    parsed = urlsplit(target)
    if parsed.scheme or not parsed.path:
        return None
    path_text = unquote(parsed.path).replace("\\", "/")
    if path_text.startswith("/"):
        candidate = root / path_text.lstrip("/")
    else:
        candidate = source.parent / path_text
        if not candidate.exists():
            candidate = root / path_text
    return candidate


def _schema_enum(schema_path: Path, property_name: str, nested: str | None = None) -> set[str]:
    data = json.loads(schema_path.read_text(encoding="utf-8"))
    node: Any = data["properties"][property_name]
    if nested is not None:
        node = node["items"]["properties"][nested]
    return set(node.get("enum", []))


def _validate_status_contracts(root: Path) -> list[str]:
    schemas = root / "SCHEMAS"
    approval = _schema_enum(schemas / "APPROVAL.schema.json", "state")
    asset = _schema_enum(schemas / "ASSET.schema.json", "approval_status")
    task = _schema_enum(schemas / "TASK.schema.json", "status")
    agent = _schema_enum(schemas / "AGENT.schema.json", "status")
    agent_approval = _schema_enum(schemas / "AGENT.schema.json", "outputs", "approval_status")
    tool = _schema_enum(schemas / "TOOL.schema.json", "state")
    research = _schema_enum(schemas / "RESEARCH_REPORT.schema.json", "decision_status")

    checks = {
        "Asset approval states must equal approval states plus ARCHIVED": asset == approval | {"ARCHIVED"},
        "Task states must equal approval states plus BLOCKED": task == approval | {"BLOCKED"},
        "Agent output approval states must preserve the documented summary vocabulary": agent_approval == {
            "pending",
            "awaiting_human_review",
            "approved",
            "revision_requested",
            "rejected",
        } and agent_approval - {"pending"} == {value.lower() for value in approval if value in {
            "AWAITING_HUMAN_REVIEW",
            "APPROVED",
            "REVISION_REQUESTED",
            "REJECTED",
        }},
        "Agent operation states must match the documented envelope": agent == {"awaiting_review", "completed_analysis", "failed", "blocked"},
        "Tool candidate lifecycle states must remain complete": tool == {"DISCOVERED", "RESEARCHED", "TESTED", "RECOMMENDED", "APPROVED", "REJECTED", "RETIRED"},
        "Research decision states must remain explicit": research == {"AWAITING_HUMAN_APPROVAL", "APPROVED", "REJECTED", "ADDITIONAL_RESEARCH_REQUESTED"},
    }
    return [message for message, passed in checks.items() if not passed]


def _validate_reference_catalogues(root: Path) -> list[str]:
    """Validate modular creative profiles, tool task mappings, and asset index contracts."""
    errors: list[str] = []

    def load_json(relative_path: str) -> Any:
        path = root / relative_path
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative_path}: could not load valid JSON: {exc}")
            return None

    def validate_document(data: Any, schema_path: str, label: str) -> None:
        schema = load_json(schema_path)
        if data is None or schema is None:
            return
        try:
            validator = jsonschema.Draft202012Validator(schema)
            for error in validator.iter_errors(data):
                errors.append(f"{label}: {error.message} at {'/'.join(str(part) for part in error.absolute_path)}")
        except Exception as exc:
            errors.append(f"{schema_path}: schema validation failed: {exc}")

    genres = load_json("GENRES/REGISTRY.json")
    validate_document(genres, "SCHEMAS/GENRE_REGISTRY.schema.json", "GENRES/REGISTRY.json")
    if isinstance(genres, dict):
        seen_genres: set[str] = set()
        for profile in genres.get("profiles", []):
            profile_id = profile.get("genre_id")
            if profile_id in seen_genres:
                errors.append(f"GENRES/REGISTRY.json: duplicate genre ID {profile_id}")
            seen_genres.add(profile_id)
            source_path = root / profile.get("instruction_path", "")
            if not source_path.is_file():
                errors.append(f"GENRES/REGISTRY.json: missing profile file for {profile_id}")
                continue
            metadata, _, parse_error = parse_frontmatter(source_path)
            if parse_error or not metadata:
                errors.append(f"GENRES/REGISTRY.json: invalid front matter for {profile_id}: {parse_error}")
            elif metadata.get("prompt_id") != profile_id or metadata.get("version") != profile.get("version"):
                errors.append(f"GENRES/REGISTRY.json: ID/version mismatch for {profile_id}")

    channels = load_json("STYLES/CHANNELS.json")
    validate_document(channels, "SCHEMAS/CHANNEL_STYLE_REGISTRY.schema.json", "STYLES/CHANNELS.json")
    if isinstance(channels, dict):
        seen_channels: set[str] = set()
        for profile in channels.get("channels", []):
            profile_id = profile.get("channel_style_id")
            if profile_id in seen_channels:
                errors.append(f"STYLES/CHANNELS.json: duplicate channel style ID {profile_id}")
            seen_channels.add(profile_id)
            guide_path = root / profile.get("guide_path", "")
            if not guide_path.is_file():
                errors.append(f"STYLES/CHANNELS.json: missing style guide for {profile_id}")
                continue
            metadata, _, parse_error = parse_frontmatter(guide_path)
            if parse_error or not metadata:
                errors.append(f"STYLES/CHANNELS.json: invalid front matter for {profile_id}: {parse_error}")
            elif metadata.get("prompt_id") != profile_id or metadata.get("version") != profile.get("version"):
                errors.append(f"STYLES/CHANNELS.json: ID/version mismatch for {profile_id}")

    catalogue = load_json("TOOLS/CATALOG.json")
    validate_document(catalogue, "SCHEMAS/TOOL_CATALOG.schema.json", "TOOLS/CATALOG.json")
    tool_profile_schema = load_json("SCHEMAS/TOOL_PROFILE.schema.json")
    if isinstance(catalogue, dict):
        tools = {item.get("tool_id"): item for item in catalogue.get("tools", [])}
        groups = {item.get("task_id"): item for item in catalogue.get("task_groups", [])}
        if len(tools) != len(catalogue.get("tools", [])):
            errors.append("TOOLS/CATALOG.json: duplicate tool IDs")
        if len(groups) != len(catalogue.get("task_groups", [])):
            errors.append("TOOLS/CATALOG.json: duplicate task IDs")
        for tool_id, tool in tools.items():
            if tool_profile_schema is not None:
                try:
                    for schema_error in jsonschema.Draft202012Validator(tool_profile_schema).iter_errors(tool):
                        errors.append(f"TOOLS/CATALOG.json: invalid profile {tool_id}: {schema_error.message}")
                except jsonschema.SchemaError as exc:
                    errors.append(f"SCHEMAS/TOOL_PROFILE.schema.json: invalid schema: {exc}")
            manual = root / tool.get("manual_path", "")
            if not manual.is_file():
                errors.append(f"TOOLS/CATALOG.json: missing manual for {tool_id}")
            else:
                manual_metadata, _, manual_error = parse_frontmatter(manual)
                if manual_error or not manual_metadata:
                    errors.append(f"TOOLS/CATALOG.json: invalid manual front matter for {tool_id}: {manual_error}")
                elif manual_metadata.get("prompt_id") != f"TOOL_{tool_id}":
                    errors.append(f"TOOLS/CATALOG.json: manual prompt ID mismatch for {tool_id}")
            for task_id in tool.get("tasks", []):
                if task_id not in groups:
                    errors.append(f"TOOLS/CATALOG.json: {tool_id} references unknown task {task_id}")
                elif tool_id not in groups[task_id].get("candidate_tool_ids", []):
                    errors.append(f"TOOLS/CATALOG.json: task {task_id} omits candidate {tool_id}")
            if tool.get("availability_status") in {"INSTALLED", "CONNECTED"} and not tool.get("evidence"):
                errors.append(f"TOOLS/CATALOG.json: {tool_id} claims availability without verification evidence")
            if tool.get("integration_status") == "END_TO_END_VERIFIED" and not tool.get("evidence"):
                errors.append(f"TOOLS/CATALOG.json: {tool_id} claims end-to-end verification without evidence")
        for task_id, group in groups.items():
            for tool_id in group.get("candidate_tool_ids", []):
                if tool_id not in tools:
                    errors.append(f"TOOLS/CATALOG.json: task {task_id} references unknown tool {tool_id}")
                elif task_id not in tools[tool_id].get("tasks", []):
                    errors.append(f"TOOLS/CATALOG.json: {tool_id} does not list task {task_id}")

    storage_roots = load_json("LIBRARY/STORAGE_ROOTS.example.json")
    validate_document(storage_roots, "SCHEMAS/STORAGE_ROOTS.schema.json", "LIBRARY/STORAGE_ROOTS.example.json")

    asset_index = load_json("LIBRARY/ASSET_INDEX.json")
    validate_document(asset_index, "SCHEMAS/LIBRARY_INDEX.schema.json", "LIBRARY/ASSET_INDEX.json")
    taxonomy = load_json("LIBRARY/TAG_TAXONOMY.json")
    if isinstance(asset_index, dict):
        asset_ids = [asset.get("asset_id") for asset in asset_index.get("assets", [])]
        if len(asset_ids) != len(set(asset_ids)):
            errors.append("LIBRARY/ASSET_INDEX.json: duplicate asset IDs")
        storage_ids = {root_item.get("root_id") for root_item in (storage_roots or {}).get("storage_roots", [])}
        dimensions = (taxonomy or {}).get("dimensions", {})
        reference_dimensions = (taxonomy or {}).get("reference_dimensions", {})
        for asset in asset_index.get("assets", []):
            if asset.get("storage_root_id") not in storage_ids:
                errors.append(f"LIBRARY/ASSET_INDEX.json: unknown storage root {asset.get(chr(115)+chr(116)+chr(111)+chr(114)+chr(97)+chr(103)+chr(101)+chr(95)+chr(114)+chr(111)+chr(111)+chr(116)+chr(95)+chr(105)+chr(100))} for {asset.get(chr(97)+chr(115)+chr(115)+chr(101)+chr(116)+chr(95)+chr(105)+chr(100))}")
            for tag in asset.get("tags", []):
                if tag.startswith("custom:") and len(tag) > len("custom:"):
                    continue
                dimension, separator, value = tag.partition(":")
                if not separator or not value:
                    errors.append(f"LIBRARY/ASSET_INDEX.json: malformed tag {tag!r}")
                elif dimension in dimensions and value not in dimensions[dimension]:
                    errors.append(f"LIBRARY/ASSET_INDEX.json: unknown {dimension} tag value {value!r}")
                elif dimension not in dimensions and dimension not in reference_dimensions:
                    errors.append(f"LIBRARY/ASSET_INDEX.json: unknown tag dimension {dimension!r}")

    return errors


def validate(root: Path) -> tuple[list[Finding], dict[str, Any]]:
    root = root.resolve()
    files = governed_markdown(root)
    findings: list[Finding] = []
    metadata_by_path: dict[Path, dict[str, Any]] = {}
    ids: dict[str, Path] = {}
    duplicate_ids: set[str] = set()
    bodies: dict[Path, str] = {}

    if not files:
        return [Finding("inventory", ".", "no governed instruction Markdown files were found")], {"files": 0}

    # Rule 1: parse YAML and validate required metadata.
    for path in files:
        rel = relative(path, root)
        metadata, body, parse_error = parse_frontmatter(path)
        bodies[path] = body
        if parse_error:
            findings.append(Finding("frontmatter", rel, parse_error))
            continue
        assert metadata is not None
        metadata_by_path[path] = metadata
        missing = REQUIRED_FRONTMATTER - metadata.keys()
        if missing:
            findings.append(Finding("frontmatter", rel, f"missing keys: {', '.join(sorted(missing))}"))
        prompt_id = metadata.get("prompt_id")
        if not isinstance(prompt_id, str) or not PROMPT_ID_PATTERN.fullmatch(prompt_id):
            findings.append(Finding("frontmatter", rel, "prompt_id must be a unique uppercase identifier"))
        elif prompt_id in ids:
            duplicate_ids.add(prompt_id)
            findings.append(Finding("unique-id", rel, f"{prompt_id} is already used by {relative(ids[prompt_id], root)}"))
        else:
            ids[prompt_id] = path
        if not isinstance(metadata.get("version"), str) or not VERSION_PATTERN.fullmatch(metadata["version"]):
            findings.append(Finding("frontmatter", rel, "version must use MAJOR.MINOR.PATCH"))
        try:
            modified_date = metadata.get("modified_date")
            if isinstance(modified_date, date):
                pass
            elif isinstance(modified_date, str):
                date.fromisoformat(modified_date)
            else:
                raise ValueError
        except ValueError:
            findings.append(Finding("frontmatter", rel, "modified_date must be an ISO 8601 date"))
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            findings.append(Finding("frontmatter", rel, "description must be non-empty text"))
        dependencies = metadata.get("dependencies")
        if not isinstance(dependencies, list) or not all(isinstance(dep, str) for dep in dependencies):
            findings.append(Finding("frontmatter", rel, "dependencies must be a list of strings"))
        history = metadata.get("change_history")
        if not isinstance(history, list) or not history:
            findings.append(Finding("frontmatter", rel, "change_history must be a non-empty list"))
        elif any(
            not isinstance(item, dict)
            or not {"version", "date", "summary"} <= item.keys()
            or not isinstance(item.get("version"), str)
            or not item["version"].strip()
            or not isinstance(item.get("summary"), str)
            or not item["summary"].strip()
            or not isinstance(item.get("date"), (str, date))
            for item in history
        ):
            findings.append(Finding("frontmatter", rel, "each change_history item needs non-empty version, date, and summary"))

    # Rule 2: resolve references and build the instruction dependency graph.
    graph: dict[str, set[str]] = defaultdict(set)
    for path, metadata in metadata_by_path.items():
        prompt_id = metadata.get("prompt_id")
        if not isinstance(prompt_id, str) or prompt_id in duplicate_ids:
            continue
        for dep in metadata.get("dependencies", []):
            resolved = _resolve_dependency(dep, path, root, ids)
            if resolved is None:
                findings.append(Finding("dependency", relative(path, root), f"unresolved dependency: {dep}"))
            elif resolved in metadata_by_path:
                dep_id = metadata_by_path[resolved].get("prompt_id")
                if isinstance(dep_id, str):
                    graph[prompt_id].add(dep_id)
    for cycle in _find_cycles(graph):
        findings.append(Finding("dependency-cycle", "instruction graph", " -> ".join(cycle)))

    # Rule 3: check relative Markdown links in the governed corpus.
    for path, body in bodies.items():
        for match in MARKDOWN_LINK_PATTERN.finditer(body):
            target = match.group(1).split(maxsplit=1)[0]
            resolved = _resolve_markdown_link(target, path, root)
            if resolved is not None and not resolved.exists():
                findings.append(Finding("internal-link", relative(path, root), f"broken link: {target}"))

    # Rule 4: keep documented operation IDs synchronized with source.
    registry_path = root / "DOCS/CAPABILITY_REGISTRY.md"
    actual_operations = expected_operations(root)
    documented_operations = registry_operations(registry_path)
    for operation in sorted(actual_operations - documented_operations):
        findings.append(Finding("capability-registry", "DOCS/CAPABILITY_REGISTRY.md", f"missing source operation: {operation}"))
    for operation in sorted(documented_operations - actual_operations):
        findings.append(Finding("capability-registry", "DOCS/CAPABILITY_REGISTRY.md", f"not found in source: {operation}"))
    for path, body in bodies.items():
        referenced = set(OPERATION_REFERENCE_PATTERN.findall(body)) | set(HTTP_REFERENCE_PATTERN.findall(body))
        for operation in sorted(referenced - documented_operations):
            findings.append(Finding("undefined-operation", relative(path, root), f"operation is not in the capability registry: {operation}"))

    # Rule 5: validate versioned genre/style registries, tool mappings and asset metadata.
    for message in _validate_reference_catalogues(root):
        findings.append(Finding("reference-catalogues", "GENRES/STYLES/TOOLS/LIBRARY", message))

    # Rule 5: keep schema status vocabularies aligned where schemas define a mapping.
    for message in _validate_status_contracts(root):
        findings.append(Finding("status-vocabulary", "SCHEMAS/", message))

    # Rule 6: each specialized agent must have distinct operational and approval boundaries.
    agent_files = sorted((root / "AGENTS").glob("*/INSTRUCTION.md"))
    agent_files.append(root / "ORCHESTRATION/PRODUCTION_DIRECTOR/INSTRUCTION.md")
    forbidden_allowed = ("auto_approve", "human_approve", "bypass_human_approval", "apply_unapproved_change")
    for path in agent_files:
        if not path.exists():
            continue
        rel = relative(path, root)
        text = path.read_text(encoding="utf-8")
        headings = list(re.finditer(r"(?im)^##\s+(.+)$", text))
        sections: dict[str, str] = {}
        for index, match in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            sections[match.group(1).strip().lower()] = text[match.end() : end]
        allowed = next((content for title, content in sections.items() if title.startswith("allowed")), "")
        for operation in forbidden_allowed:
            if re.search(rf"\b{re.escape(operation)}\b", allowed, re.IGNORECASE):
                findings.append(Finding("permissions", rel, f"forbidden capability appears in allowed section: {operation}"))
        approval = next((content for title, content in sections.items() if "approval" in title), "")
        human_boundary = "human" in text.lower() and re.search(
            r"\bnever\b|\bmust not\b|\bcannot\b|\bonly\b.{0,80}\bhuman\b",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not approval or not human_boundary:
            findings.append(Finding("approval-boundary", rel, "approval section must explicitly reserve approval to a human"))
        if "SCHEMAS/" not in text and "CORE/OUTPUT_CONTRACTS.md" not in text:
            findings.append(Finding("output-contract", rel, "agent instruction must reference a schema or the output contract"))
        required_headings = {
            "required inputs": ("required inputs", "activation and context", "inputs"),
            "execution procedure": ("execution procedure", "procedure", "workflow"),
            "failure handling": ("failure handling", "failure", "conflicts, and failure"),
        }
        for required, aliases in required_headings.items():
            if not any(any(alias in title for alias in aliases) for title in sections):
                findings.append(Finding("agent-completeness", rel, f"missing section: {required}"))

    # Rule 7: operating modes and departments must cover their required workflow concerns.
    mode_markers = (
        "purpose",
        "scope",
        "activation",
        "context",
        "allowed",
        "forbidden",
        "permission",
        "procedure",
        "approval",
        "output",
        "memory",
        "conflict",
        "failure",
        "success",
    )
    for path in sorted((root / "MODES").glob("*.md")):
        text = path.read_text(encoding="utf-8").lower()
        missing = [marker for marker in mode_markers if marker not in text]
        if missing:
            findings.append(Finding("mode-completeness", relative(path, root), f"missing concepts: {', '.join(missing)}"))
    department_markers = (
        "entry requirements",
        "inputs",
        "workflow",
        "outputs",
        "dependencies",
        "gate",
        "exceptions",
        "handoff",
    )
    for path in sorted((root / "DEPARTMENTS").glob("*/DEPARTMENT_RULES.md")):
        text = path.read_text(encoding="utf-8").lower()
        missing = [marker for marker in department_markers if marker not in text]
        if missing:
            findings.append(Finding("department-completeness", relative(path, root), f"missing concepts: {', '.join(missing)}"))

    # Rule 8: make sure the audit inventory points to every governed document.
    audit_path = root / "DOCS/INSTRUCTION_REPOSITORY_AUDIT.md"
    if audit_path.exists():
        audit_text = audit_path.read_text(encoding="utf-8").replace("\\", "/")
        for path in files:
            rel = relative(path, root)
            if rel not in audit_text:
                findings.append(Finding("audit-inventory", "DOCS/INSTRUCTION_REPOSITORY_AUDIT.md", f"missing governed file: {rel}"))
    else:
        findings.append(Finding("audit-inventory", "DOCS/INSTRUCTION_REPOSITORY_AUDIT.md", "audit report is missing"))

    summary = {
        "governed_markdown_files": len(files),
        "unique_prompt_ids": len(ids),
        "capability_operations": len(actual_operations),
        "validation_rules": 9,
        "findings": len(findings),
    }
    return findings, summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", help="emit machine-readable results")
    args = parser.parse_args(argv)
    findings, summary = validate(args.root)
    if args.json:
        print(json.dumps({"summary": summary, "findings": [finding.__dict__ for finding in findings]}, indent=2))
    else:
        print(f"Instruction repository: {summary['governed_markdown_files']} files, {summary['validation_rules']} rules, {summary['findings']} findings")
        for finding in findings:
            print(f"- {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
