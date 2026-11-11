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
    # Eight style directions. More images, because a direction that was
    # regenerated with the user's own prompt keeps every image the artifact
    # store produced.
    assert summary["counts"]["art_direction_candidates"] == 8
    assert summary["counts"]["art_direction_images"] >= 9


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



def test_the_two_surfaces_report_the_same_package(workspace: Path) -> None:
    """The review page and the application must never disagree.

    They used to build the state separately, which is how the review page
    ended up serving a blank shell while the application showed the same data
    correctly. Now both read the same service.
    """
    from VISUAL_DEVELOPMENT.review_server import _collect_state
    from VISUAL_DEVELOPMENT.storage import ProjectStore

    bridge = VisualDevelopmentBridge(workspace)
    detail = bridge.detail(PILOT.name)
    state = _collect_state(ProjectStore(workspace / "PROJECTS" / PILOT.name))

    assert [shot["shot_id"] for shot in detail["shots"]] == [
        shot["shot_id"] for shot in state["shots"]
    ]
    assert [candidate["candidate_id"] for candidate in detail["candidates"]] == [
        candidate["candidate_id"] for candidate in state["candidates"]["candidates"]
    ]
    for shot in detail["shots"]:
        other = next(
            entry for entry in state["shots"] if entry["shot_id"] == shot["shot_id"]
        )
        assert shot["status"] == other["status"]
        assert shot["board_image_path"] == other["board_image_path"]
        assert shot["blocking_image_path"] == other["blocking_image_path"]



# --------------------------------------- the override must reach the image


def test_the_bridge_regeneration_uses_the_users_prompt(workspace: Path) -> None:
    """The headline feature, end to end through the bridge.

    The override the user saved must be what ComfyUI receives. The earlier
    code rebuilt the prompt from the Style Bible, so the user's own text was
    silently discarded at the moment the image was made.
    """
    from backend.integrations.visual_development import VisualDevelopmentBridge
    from VISUAL_DEVELOPMENT.prompt_overrides import build_override, save_override
    from VISUAL_DEVELOPMENT.storage import ProjectStore

    bridge = VisualDevelopmentBridge(workspace)
    store = ProjectStore(workspace / "PROJECTS" / PILOT.name)

    override = build_override(
        "ART_03",
        "ART_DIRECTION_CANDIDATE",
        prompt_extra="a direction the user wrote by hand",
        exclude_modules=["emphasis"],
        settings_override={"seed": 424242},
    )
    save_override(store, override)

    plan = bridge.plan(PILOT.name, "ART_03")
    assert "a direction the user wrote by hand" in plan["prompt"]
    assert "single continuous frame" not in plan["prompt"]
    assert plan["settings"]["seed"] == 424242
    assert plan["has_override"] is True
    assert "prompt_extra" in plan["applied_overrides"]
    assert "exclude_modules" in plan["applied_overrides"]


def test_the_plan_is_the_same_for_the_command_line_and_the_application(
    workspace: Path,
) -> None:
    """One plan, so a picture does not depend on where it was made."""
    from VISUAL_DEVELOPMENT.prompt_overrides import build_override, save_override
    from VISUAL_DEVELOPMENT.service import resolve_plan
    from VISUAL_DEVELOPMENT.storage import ProjectStore

    store = ProjectStore(workspace / "PROJECTS" / PILOT.name)
    save_override(
        store,
        build_override(
            "ART_03",
            "ART_DIRECTION_CANDIDATE",
            prompt_extra="the same words everywhere",
        ),
    )
    plan = resolve_plan(store, "ART_03")
    assert "the same words everywhere" in plan["prompt"]


def test_a_user_workflow_with_a_controlnet_gets_the_prompt_in_the_right_node() -> None:
    """A ControlNet sits between the text and the sampler.

    Guessing by node order put the positive prompt into the negative node.
    The graph has to be walked back to the text.
    """
    from VISUAL_DEVELOPMENT.workflows import apply_to_user_workflow, resolve_prompt_nodes

    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "x.safetensors"}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "OLD NEGATIVE", "clip": ["1", 1]}},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "OLD POSITIVE", "clip": ["1", 1]}},
        "4": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "5": {"class_type": "ControlNetLoader", "inputs": {"control_net_name": "cn.pth"}},
        "6": {"class_type": "ControlNetApplyAdvanced", "inputs": {
            "positive": ["3", 0], "negative": ["2", 0], "control_net": ["5", 0],
            "image": ["4", 0], "vae": ["1", 2], "strength": 0.8,
            "start_percent": 0.0, "end_percent": 1.0,
        }},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["6", 0], "negative": ["6", 1],
            "latent_image": ["4", 0], "seed": 1, "steps": 20, "cfg": 7.0,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "u"}},
    }
    nodes = resolve_prompt_nodes(workflow)
    assert nodes["positive"] == "3"
    assert nodes["negative"] == "2"

    filled = apply_to_user_workflow(
        workflow, positive="NEW POSITIVE", negative="NEW NEGATIVE", settings={"seed": 999}
    )
    result = filled["workflow"]
    assert result["3"]["inputs"]["text"] == "NEW POSITIVE"
    assert result["2"]["inputs"]["text"] == "NEW NEGATIVE"
    assert result["7"]["inputs"]["seed"] == 999


def test_a_graph_that_cannot_be_resolved_is_refused_not_guessed() -> None:
    """Two text nodes and no path to the sampler: report it, do not guess."""
    from VISUAL_DEVELOPMENT.workflows import resolve_prompt_nodes

    workflow = {
        "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "a", "clip": ["9", 1]}},
        "2": {"class_type": "CLIPTextEncode", "inputs": {"text": "b", "clip": ["9", 1]}},
        "9": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "x"}},
    }
    nodes = resolve_prompt_nodes(workflow)
    assert nodes["sampler"] is None
    assert nodes["positive"] is None
    assert nodes["negative"] is None


def test_the_seed_is_not_dropped_on_a_sampler_that_calls_it_noise_seed() -> None:
    """KSamplerAdvanced names the seed noise_seed."""
    from VISUAL_DEVELOPMENT.workflows import apply_to_user_workflow

    workflow = {
        "1": {"class_type": "CLIPTextEncode", "inputs": {"text": "a", "clip": ["2", 1]}},
        "2": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "x"}},
        "3": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "4": {"class_type": "KSamplerAdvanced", "inputs": {
            "model": ["2", 0], "positive": ["1", 0], "negative": ["1", 0],
            "latent_image": ["3", 0], "noise_seed": 1, "steps": 20, "cfg": 7.0,
            "sampler_name": "euler", "scheduler": "normal", "denoise": 1.0,
        }},
        "5": {"class_type": "VAEDecode", "inputs": {"samples": ["4", 0], "vae": ["2", 2]}},
        "6": {"class_type": "SaveImage", "inputs": {"images": ["5", 0], "filename_prefix": "u"}},
    }
    filled = apply_to_user_workflow(workflow, positive="p", negative="n", settings={"seed": 999})
    assert filled["workflow"]["4"]["inputs"]["noise_seed"] == 999
    assert "missing" not in filled or "seed" not in filled["missing"]


def test_the_generation_counts_come_from_the_manifests(workspace: Path) -> None:
    """Eight directions are eight generations, not one."""
    from backend.integrations.visual_development import VisualDevelopmentBridge

    bridge = VisualDevelopmentBridge(workspace)
    pipeline = bridge.pipeline(PILOT.name)
    counts = pipeline["generations"]
    assert counts["total"] == sum(
        counts[key] for key in ("art_direction", "storyboard", "blocking")
    )
    assert counts["art_direction"] >= 8


def test_an_unapproved_script_is_not_a_complete_stage(workspace: Path) -> None:
    """The pilot is exploration only, and the rail must not say otherwise."""
    from backend.integrations.visual_development import VisualDevelopmentBridge

    bridge = VisualDevelopmentBridge(workspace)
    pipeline = bridge.pipeline(PILOT.name)
    script_stage = next(
        stage for stage in pipeline["stages"] if stage["stage_id"] == "SCRIPT"
    )
    assert pipeline["link"]["approval_status"] == "NOT_APPROVED"
    assert script_stage["complete"] is False

