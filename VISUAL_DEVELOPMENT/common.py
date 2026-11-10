from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_DIR = Path(__file__).resolve().parent / "schemas"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12].upper()}"


def slug(value: str, max_length: int = 52) -> str:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_").upper()
    return (normalized or "ITEM")[:max_length].rstrip("_")


def safe_relative_path(value: str) -> PurePosixPath:
    path = PurePosixPath(value.replace("\\", "/"))
    if path.is_absolute() or not path.parts or any(part in {".", ".."} for part in path.parts):
        raise ValueError(f"Expected a safe project-relative path, got {value!r}")
    return path


def contained_path(root: Path, relative: str) -> Path:
    rel = safe_relative_path(relative)
    resolved_root = root.resolve()
    resolved = (resolved_root / Path(*rel.parts)).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError("Path escapes the project directory") from exc
    return resolved


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_new(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)


def write_bytes_new(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(value)


def validate_schema(value: Any, name: str) -> None:
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("JSON Schema checks require the repository jsonschema dependency") from exc
    schema = read_json(SCHEMA_DIR / name)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(value, schema)
