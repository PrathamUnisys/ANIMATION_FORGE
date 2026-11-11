from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

import pytest

from backend.integrations.visual_development import (
    VisualDevelopmentBridge,
    VisualDevelopmentError,
)

ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "PROJECTS/VDEV_YS01_YS01_REVISED_V1"


@pytest.fixture
def workspace(tmp_path: Path) -> Path:
    """A throwaway copy of the pilot so decisions never touch the real project."""
    if not PILOT.is_dir():
        pytest.skip("YS01 pilot project is not present in this checkout.")
    projects = tmp_path / "PROJECTS"
    projects.mkdir(parents=True)
    shutil.copytree(PILOT, projects / PILOT.name)
    return tmp_path


def test_bridge_lists_the_copied_project(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    projects = bridge.list_projects()
    assert len(projects) == 1
    summary = projects[0]
    assert summary["source_script"]["approval_status"] == "NOT_APPROVED"
    assert summary["source_format"] == "NARRATOR"
    assert summary["counts"]["sequences"] == 6
    assert summary["counts"]["shots"] == 8
    # Eight style directions. Nine images, because one direction was
    # regenerated with the user's own prompt and workflow, and the artifact
    # store keeps every image it produced.
    assert summary["counts"]["art_direction_candidates"] == 8
    assert summary["counts"]["art_direction_images"] == 9


def test_bridge_detail_exposes_candidates_and_shots(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    detail = bridge.detail(PILOT.name)
    assert len(detail["candidates"]) == 8
    assert detail["comparison_scene_id"] == "SCN_01_01"
    assert detail["comparison_seed"]
    for candidate in detail["candidates"]:
        assert candidate["image_path"].endswith(".png")
        assert candidate["style_name"]
    assert len(detail["shots"]) == 8
    for shot in detail["shots"]:
        assert shot["shot_id"].startswith("SHT_")
        assert shot["source_spans"] if "source_spans" in shot else True


def test_bridge_serves_the_real_image_bytes(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    detail = bridge.detail(PILOT.name)
    relative = detail["candidates"][0]["image_path"]
    resolved = bridge.media(PILOT.name, relative)
    assert resolved.is_file()
    assert resolved.read_bytes().startswith(b"\x89PNG")


def test_bridge_refuses_path_traversal(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    for bad in ("../../../etc/passwd", "/etc/passwd", "..\\..\\Windows\\System32\\config\\SAM"):
        with pytest.raises(VisualDevelopmentError):
            bridge.media(PILOT.name, bad)


def test_bridge_refuses_dot_only_path_components(workspace: Path) -> None:
    """A '...' component is not a real directory and Windows collapses it."""
    bridge = VisualDevelopmentBridge(workspace)
    for bad in (
        "storyboard\\SEQ_02\\...\\GEN.png",
        "storyboard/SEQ_02/../GEN.png",
        "storyboard/SEQ_02/..../GEN.png",
    ):
        with pytest.raises(VisualDevelopmentError):
            bridge.media(PILOT.name, bad)


def test_bridge_accepts_a_plain_relative_reference(workspace: Path) -> None:
    """'./project.json' is a legitimate relative reference and must resolve."""
    bridge = VisualDevelopmentBridge(workspace)
    assert bridge.media(PILOT.name, "./project.json").is_file()


def test_bridge_refuses_an_unknown_project(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    with pytest.raises(VisualDevelopmentError):
        bridge.detail("VDEV_DOES_NOT_EXIST")
    with pytest.raises(VisualDevelopmentError):
        bridge.detail("PROJECT_001")


def test_bridge_records_a_selection_as_an_append_only_event(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    before = len(bridge.detail(PILOT.name)["review_events"])
    event = bridge.record_decision(
        PILOT.name, "SELECT", "ART_DIRECTION_CANDIDATE", "ART_03", actor="pytest", note="selftest"
    )
    assert event["action"] == "SELECT"
    assert event["target_id"] == "ART_03"
    after = bridge.detail(PILOT.name)
    assert len(after["review_events"]) == before + 1
    selected = [c for c in after["candidates"] if c["selected"]]
    assert [c["candidate_id"] for c in selected] == ["ART_03"]
    # The selection is persisted, not just returned.
    candidates_path = workspace / "PROJECTS" / PILOT.name / "art_direction" / "candidates_v001.json"
    stored = json.loads(candidates_path.read_text(encoding="utf-8"))
    assert [c["candidate_id"] for c in stored["candidates"] if c["selected"]] == ["ART_03"]


def test_bridge_rejects_an_unsupported_action(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    with pytest.raises(VisualDevelopmentError):
        bridge.record_decision(PILOT.name, "DELETE", "ART_DIRECTION_CANDIDATE", "ART_01")


def test_bridge_never_writes_to_the_animation_forge_database(workspace: Path) -> None:
    """The bridge must not create or modify the tracked database."""
    before = (ROOT / "animation_forge.db").stat().st_mtime
    bridge = VisualDevelopmentBridge(workspace)
    bridge.list_projects()
    assert (ROOT / "animation_forge.db").stat().st_mtime == before


# ------------------------------------------------------- production workspace


def test_bridge_reports_the_production_spine(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    pipeline = bridge.pipeline(PILOT.name)
    assert [stage["stage_id"] for stage in pipeline["stages"]] == [
        "SCRIPT",
        "BREAKDOWN",
        "VISUAL_DIRECTION",
        "BOARDS",
        "PREVIZ",
        "CONTINUITY",
        "HANDOFF",
    ]
    assert pipeline["link"]["script_id"] == "YS01_REVISED"
    assert pipeline["link"]["approval_status"] == "NOT_APPROVED"
    assert pipeline["shot_statuses"]["NOT_STARTED"] == 8
    assert len(pipeline["shots"]) == 8
    assert pipeline["stages"][1]["stage_id"] == "BREAKDOWN"


def test_bridge_reports_the_breakdown(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    breakdown = bridge.breakdown(PILOT.name)
    assert breakdown["scenes"]
    assert breakdown["summary"]["scene_count"] == 6
    assert breakdown["summary"]["element_count"] > 0
    for scene in breakdown["scenes"]:
        for element in scene["elements"]:
            assert element["source"] in {"SCRIPT", "INFERRED"}


def test_bridge_returns_the_effective_prompt_for_a_candidate(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    result = bridge.effective_prompt(PILOT.name, "ART_03")
    assert result["target_id"] == "ART_03"
    assert result["kind"] == "ART_DIRECTION_CANDIDATE"
    assert result["generated_prompt"]
    assert result["effective_prompt"]
    # The pilot carries an override for this candidate, so the merged prompt
    # must differ from the generated one.
    assert result["changed"] is True
    assert "1920s archive photograph" in result["effective_prompt"]
    assert "single continuous frame" not in result["effective_prompt"]
    assert "exclude_modules" in result["applied_overrides"]


def test_bridge_saves_and_clears_an_override(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    saved = bridge.save_override(
        PILOT.name,
        {
            "target_id": "ART_05",
            "kind": "ART_DIRECTION_CANDIDATE",
            "prompt_extra": "a direction the user wrote",
            "settings_override": {"seed": 12345},
        },
    )
    assert saved["status"] == "PASS"
    result = bridge.effective_prompt(PILOT.name, "ART_05")
    assert "a direction the user wrote" in result["effective_prompt"]
    assert result["settings"]["seed"] == 12345

    cleared = bridge.clear_override(PILOT.name, "ART_05")
    assert cleared["removed"] is True
    result = bridge.effective_prompt(PILOT.name, "ART_05")
    assert "a direction the user wrote" not in result["effective_prompt"]


def test_bridge_refuses_settings_that_cannot_be_overridden(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    with pytest.raises(ValueError):
        bridge.save_override(
            PILOT.name,
            {
                "target_id": "ART_05",
                "kind": "ART_DIRECTION_CANDIDATE",
                "settings_override": {"not_a_setting": 1},
            },
        )


def test_bridge_lists_the_stored_workflows(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    workflows = bridge.list_workflows(PILOT.name)
    assert workflows
    assert any(entry["workflow_id"] == "WF_USER_DEMO" for entry in workflows)


def test_bridge_rejects_an_unknown_target(workspace: Path) -> None:
    bridge = VisualDevelopmentBridge(workspace)
    with pytest.raises(VisualDevelopmentError):
        bridge.effective_prompt(PILOT.name, "ART_99")

