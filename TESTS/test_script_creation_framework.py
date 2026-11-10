from __future__ import annotations

import json
from pathlib import Path

import pytest

from SCRIPT_CREATION_FRAMEWORK.runtime import count_narration, estimate_runtime
from SCRIPT_CREATION_FRAMEWORK.validation import audit_claim_references, audit_script_map, parse_json_status, validate_schema
from SCRIPT_CREATION_FRAMEWORK.workspace import WorkspaceError, add_artifact, initialize_workspace, validate_manifest


ROOT = Path(__file__).resolve().parents[1]


def test_json_parse_and_schema_validation_are_separate(tmp_path: Path) -> None:
    data = tmp_path / "data.json"
    schema = ROOT / "SCRIPT_CREATION_FRAMEWORK/schemas/claims.schema.json"
    data.write_text('{"bad":', encoding="utf-8")
    assert parse_json_status(data)["status"] == "FAIL"
    result = validate_schema(data, schema)
    assert result["json_syntax_status"] == "FAIL"
    assert result["schema_validation_status"] == "NOT_EXECUTED"
    data.write_text(json.dumps({"schema_version": "1.0.0", "project_id": "p", "claims": []}), encoding="utf-8")
    result = validate_schema(data, schema)
    assert result["json_syntax_status"] == "PASS"
    assert result["schema_validation_status"] == "PASS"
    assert result["status"] == "PASS"
    data.write_text(json.dumps({"schema_version": "1.0.0", "project_id": "p", "claims": [], "extra": True}), encoding="utf-8")
    result = validate_schema(data, schema)
    assert result["json_syntax_status"] == "PASS"
    assert result["schema_validation_status"] == "FAIL"
    assert result["status"] == "FAIL"


def test_every_module_schema_is_valid_draft_2020_12() -> None:
    from jsonschema import Draft202012Validator

    for schema_path in (ROOT / "SCRIPT_CREATION_FRAMEWORK/schemas").glob("*.schema.json"):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)


def test_narration_count_handles_bold_tags_and_excludes_direction() -> None:
    sample = """### 00:00 — Start
**[NARRATION]**
One short spoken sentence.
**[VISUAL]**
Do not count these direction words.
"""
    assert count_narration(sample)["narration_word_count"] == 4
    estimate = estimate_runtime(120, 120, 2, 5)
    assert estimate["status"] == "SCRIPT_ESTIMATE"
    assert estimate["total_min_sec"] == 62
    assert estimate["total_max_sec"] == 65


def test_counter_matches_experiment_revised_script_10() -> None:
    script = ROOT / "PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS10_THE_TRAFFIC_JAM_WITH_NO_CAUSE.md"
    assert count_narration(script.read_text(encoding="utf-8"))["narration_word_count"] == 789


def test_workspace_add_validate_hash_and_no_overwrite(tmp_path: Path) -> None:
    project = initialize_workspace(tmp_path, "demo-01", "Demo")
    source = tmp_path / "input.md"
    source.write_text("draft", encoding="utf-8")
    artifact = add_artifact(project, "SCRIPT", source, "scripts/original/draft.md")
    assert artifact["revision"] == 1
    assert validate_manifest(project)["artifact_integrity"] == "PASS"
    with pytest.raises(FileExistsError):
        add_artifact(project, "SCRIPT", source, "scripts/original/draft.md")
    with pytest.raises(WorkspaceError, match="remain inside"):
        add_artifact(project, "SCRIPT", source, "../outside.md")
    with pytest.raises(FileExistsError):
        initialize_workspace(tmp_path, "demo-01", "Again")


def test_claim_markers_check_claim_and_source_references(tmp_path: Path) -> None:
    script = tmp_path / "script.md"
    claims = tmp_path / "claims.json"
    sources = tmp_path / "sources.json"
    script.write_text("Claim <!-- CLAIM:C1 -->", encoding="utf-8")
    claims.write_text(json.dumps({"claims": [{"claim_id": "C1", "source_ids": ["S1"], "verification_status": "VERIFIED"}]}), encoding="utf-8")
    sources.write_text(json.dumps({"sources": [{"source_id": "S1"}]}), encoding="utf-8")
    assert audit_claim_references(script, claims, sources)["status"] == "PASS"
    sources.write_text(json.dumps({"sources": []}), encoding="utf-8")
    result = audit_claim_references(script, claims, sources)
    assert result["status"] == "FAIL"
    assert result["missing_source_ids"] == ["S1"]


def test_retention_map_timecodes_match_script_headings(tmp_path: Path) -> None:
    script = tmp_path / "script.md"
    retention = tmp_path / "map.json"
    script.write_text("## 00:00 — Start\n\n## 01:25 — Turn\n", encoding="utf-8")
    retention.write_text(json.dumps({"entries": [{"timecode": "00:00"}, {"timecode": "01:25"}]}), encoding="utf-8")
    assert audit_script_map(script, retention)["status"] == "PASS"
    retention.write_text(json.dumps({"entries": [{"timecode": "00:00"}]}), encoding="utf-8")
    assert audit_script_map(script, retention)["status"] == "FAIL"
