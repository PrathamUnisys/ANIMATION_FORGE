from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .common import (
    contained_path,
    new_id,
    read_json,
    safe_relative_path,
    sha256_bytes,
    utc_now,
    validate_schema,
    write_bytes_new,
    write_json_new,
)


class ProjectStore:
    def __init__(self, project_dir: str | Path):
        self.root = Path(project_dir).resolve()
        if not self.root.is_dir() or not (self.root / "project.json").is_file():
            raise FileNotFoundError(f"Not a Visual Development project: {self.root}")

    @classmethod
    def create(cls, project_dir: str | Path, approved_script: dict[str, Any]) -> "ProjectStore":
        root = Path(project_dir).resolve()
        if root.exists():
            raise FileExistsError(f"Refusing to overwrite existing project directory: {root}")
        root.mkdir(parents=True)
        content = approved_script["content_markdown"]
        project_id = f"VDEV_{approved_script['project_id']}_{approved_script['script_id']}_V{approved_script['version']}"
        project_id = re.sub(r"[^A-Za-z0-9_-]", "_", project_id)[:120]
        source_ref = {key: value for key, value in approved_script.items() if key != "content_markdown"}
        source_ref["imported_at"] = utc_now()
        manifest = {
            "schema_version": "1.0.0",
            "project_id": project_id,
            "title": approved_script["script_id"],
            "created_at": utc_now(),
            "status": "DRAFT",
            "source_script": source_ref,
            "stage": "SOURCE_IMPORTED",
        }
        try:
            validate_schema(manifest, "project.schema.json")
            write_bytes_new(root / "source" / "approved_script.md", content.encode("utf-8"))
            write_json_new(root / "source" / "script_manifest.json", source_ref)
            write_json_new(root / "project.json", manifest)
        except Exception:
            # Do not silently reuse a partial directory; it remains visible for diagnosis.
            raise
        return cls(root)

    def path(self, relative: str) -> Path:
        return contained_path(self.root, relative)

    def read(self, relative: str) -> Any:
        return read_json(self.path(relative))

    def write_json(self, relative: str, value: Any, schema: str | None = None) -> Path:
        if schema:
            validate_schema(value, schema)
        path = self.path(relative)
        write_json_new(path, value)
        return path

    def update_json(self, relative: str, value: Any, schema: str | None = None) -> Path:
        """Atomically replace an existing JSON file.

        Used only for mutable working state such as the candidate set. Immutable
        generation artifacts are always written with write_json so revisions are
        never overwritten.
        """
        if schema:
            validate_schema(value, schema)
        path = self.path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        temporary.replace(path)
        return path

    def write_bytes(self, relative: str, value: bytes) -> Path:
        path = self.path(relative)
        write_bytes_new(path, value)
        return path

    def source(self) -> tuple[str, dict[str, Any]]:
        text = self.path("source/approved_script.md").read_text(encoding="utf-8")
        manifest = self.read("source/script_manifest.json")
        actual = sha256_bytes(text.encode("utf-8"))
        if actual != manifest.get("sha256"):
            raise ValueError("The imported screenplay source hash changed; analysis is blocked")
        return text, manifest

    def latest_number(self, directory: str, prefix: str) -> int:
        folder = self.path(directory)
        if not folder.exists():
            return 1
        found = []
        for path in folder.glob(f"{prefix}_v*.json"):
            match = re.search(r"_v(\d+)\.json$", path.name)
            if match:
                found.append(int(match.group(1)))
        return max(found, default=0) + 1

    def append_event(self, event: dict[str, Any]) -> None:
        validate_schema(event, "review_event.schema.json")
        path = self.path("reviews/review_events.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")

    def events(self) -> list[dict[str, Any]]:
        path = self.path("reviews/review_events.jsonl")
        if not path.exists():
            return []
        events = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    def write_generation_artifact(
        self,
        relative_dir: str,
        image_bytes: bytes,
        manifest: dict[str, Any],
        extension: str = ".png",
    ) -> tuple[str, str]:
        revision_id = new_id("GEN")
        image_path = f"{relative_dir.rstrip('/')}/{revision_id}{extension}"
        manifest_path = f"{relative_dir.rstrip('/')}/{revision_id}.json"
        manifest = dict(manifest)
        manifest["generation_id"] = revision_id
        manifest["image_path"] = image_path
        manifest["image_sha256"] = sha256_bytes(image_bytes)
        manifest["created_at"] = utc_now()
        try:
            self.write_bytes(image_path, image_bytes)
            self.write_json(manifest_path, manifest, "generation_manifest.schema.json")
        except Exception:
            # Do not leave an image without its provenance manifest.
            self.path(image_path).unlink(missing_ok=True)
            raise
        return image_path, manifest_path
