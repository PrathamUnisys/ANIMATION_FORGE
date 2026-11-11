from __future__ import annotations

import contextlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
import threading
import urllib.request
import wave
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from PIL import Image

import jsonschema
import pytest

from VISUAL_DEVELOPMENT.analyzer import parse_script
from VISUAL_DEVELOPMENT.approved_script import (
    ApprovedScriptError,
    load_approved_script,
    load_script_file,
)
from VISUAL_DEVELOPMENT.art_direction import build_candidates, select_candidate
from VISUAL_DEVELOPMENT.blocking import build_blocking_layout, render_blocking_png, render_blocking_svg
from VISUAL_DEVELOPMENT.comfyui_client import ComfyUIClient, ComfyUIError
from VISUAL_DEVELOPMENT.common import sha256_text
from VISUAL_DEVELOPMENT.continuity import validate_continuity
from VISUAL_DEVELOPMENT.handoff import build_handoff, render_handoff_markdown
from VISUAL_DEVELOPMENT.prompt_builder import build_candidate_prompt, build_shot_prompt
from VISUAL_DEVELOPMENT.prompt_overrides import build_override
from VISUAL_DEVELOPMENT.storage import ProjectStore
from VISUAL_DEVELOPMENT.style_bible import build_style_bible, revise_style_bible
from VISUAL_DEVELOPMENT.workflows import (
    txt2img_canny_workflow,
    txt2img_workflow,
    validate_workflow,
    workflow_settings,
)

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "VISUAL_DEVELOPMENT/schemas"
SCRIPT_ID = "SCR_PROJECT_001_V01"


@pytest.fixture
def database(tmp_path: Path) -> Path:
    source = ROOT / "animation_forge.db"
    target = tmp_path / "animation_forge.db"
    shutil.copy2(source, target)
    return target


@pytest.fixture
def script(database: Path) -> dict[str, Any]:
    return load_approved_script(database, SCRIPT_ID)


@pytest.fixture
def analysis(script: dict[str, Any]) -> dict[str, Any]:
    return parse_script(
        script["content_markdown"], script["project_id"], script["sha256"]
    )


@pytest.fixture
def store(tmp_path: Path, script: dict[str, Any]) -> ProjectStore:
    return ProjectStore.create(tmp_path / "project", script)


# ------------------------------------------------------------------- schemas


def test_every_module_schema_is_valid_draft_2020_12() -> None:
    for schema_path in SCHEMA_DIR.glob("*.schema.json"):
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)


def test_analysis_matches_the_analysis_schema(analysis: dict[str, Any]) -> None:
    schema = json.loads((SCHEMA_DIR / "analysis.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(analysis, schema)


# ------------------------------------------------------------------ analyzer


def test_analysis_structure_and_unique_ids(analysis: dict[str, Any]) -> None:
    assert len(analysis["sequences"]) == 3
    shot_ids = [
        shot["shot_id"]
        for sequence in analysis["sequences"]
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    ]
    assert len(shot_ids) == 9
    assert len(set(shot_ids)) == len(shot_ids), "shot ids must be globally unique"


def test_every_shot_traces_back_to_the_screenplay(analysis: dict[str, Any], script: dict[str, Any]) -> None:
    text = script["content_markdown"]
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            for shot in scene["shots"]:
                assert shot["source_spans"], "every shot needs a source reference"
                for span in shot["source_spans"]:
                    assert text[span["start"] : span["end"]] == span["text"]


def test_missing_scene_heading_becomes_an_open_question(analysis: dict[str, Any]) -> None:
    assert analysis["open_questions"], "a missing scene heading must be reported, not invented"
    implicit = [
        scene
        for sequence in analysis["sequences"]
        for scene in sequence["scenes"]
        if scene["implicit"]
    ]
    assert len(implicit) == 1
    assert implicit[0]["location"] == "", "an implicit scene must not invent a location"


def test_dialogue_mentions_are_not_treated_as_present_characters(analysis: dict[str, Any]) -> None:
    scene = analysis["sequences"][0]["scenes"][0]
    assert "Stone Golem" not in scene["characters"]
    assert scene["characters"] == ["Sir Pip", "Gloop"]


def test_shot_durations_sum_to_the_sequence_timecode(analysis: dict[str, Any]) -> None:
    sequence = analysis["sequences"][0]
    total = sum(
        shot["estimated_duration_sec"]
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    )
    assert total == pytest.approx(15.0)


# ------------------------------------------------------------- art direction


def test_candidates_share_one_comparison_scene(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    assert len(candidate_set["candidates"]) == 8
    scenes = {candidate["comparison_scene_id"] for candidate in candidate_set["candidates"]}
    assert scenes == {candidate_set["comparison_scene_id"]}
    assert candidate_set["comparison_seed"]


def test_only_one_candidate_can_be_selected(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_02")
    selected = [c for c in candidate_set["candidates"] if c["selected"]]
    assert len(selected) == 1
    assert selected[0]["candidate_id"] == "ART_02"
    select_candidate(candidate_set, "ART_05")
    selected = [c for c in candidate_set["candidates"] if c["selected"]]
    assert len(selected) == 1
    assert selected[0]["candidate_id"] == "ART_05"


# --------------------------------------------------------------- style bible


def test_style_bible_requires_a_human_selection(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    with pytest.raises(ValueError):
        build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    select_candidate(candidate_set, "ART_01")
    bible = build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    assert bible["status"] == "DRAFT"
    assert bible["version"] == 1
    schema = json.loads((SCHEMA_DIR / "style_bible.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(bible, schema)


def test_style_bible_rules_do_not_repeat_each_other(analysis: dict[str, Any]) -> None:
    """Composition and atmosphere must carry their own direction.

    Copying the camera and lighting text into them produced a Style Bible
    where two rules repeated two others and carried no information.
    """
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_02")
    bible = build_style_bible(candidate_set, "ART_02", "PROJECT_001")
    rules = bible["global_rules"]
    assert rules["composition"] != rules["camera_language"]
    assert rules["atmosphere"] != rules["lighting"]
    for candidate in candidate_set["candidates"]:
        assert candidate["composition"] != candidate["camera"]
        assert candidate["atmosphere"] != candidate["lighting"]
        assert candidate["composition"]
        assert candidate["atmosphere"]


def test_style_bible_revision_creates_a_new_version(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_01")
    bible = build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    revised = revise_style_bible(bible, {"color_palette": "amber and slate"})
    assert revised["version"] == bible["version"] + 1
    assert revised["global_rules"]["color_palette"] == "amber and slate"
    assert bible["global_rules"]["color_palette"] != "amber and slate"
    with pytest.raises(ValueError):
        revise_style_bible(bible, {"not_a_rule": "x"})


# ------------------------------------------------------------------ blocking


def test_blocking_layout_is_normalized_and_deterministic(analysis: dict[str, Any]) -> None:
    scene = analysis["sequences"][0]["scenes"][0]
    shot = scene["shots"][0]
    first = build_blocking_layout(shot, scene)
    second = build_blocking_layout(shot, scene)
    assert first == second
    assert first["coordinate_space"] == "NORMALIZED_STAGE_0_TO_1"
    assert first["not_world_coordinates"] is True
    for character in first["characters"]:
        assert 0.0 <= character["x"] <= 1.0
        assert 0.0 <= character["y"] <= 1.0


def test_blocking_renders_svg_and_png(analysis: dict[str, Any]) -> None:
    scene = analysis["sequences"][0]["scenes"][0]
    layout = build_blocking_layout(scene["shots"][0], scene)
    svg = render_blocking_svg(layout)
    png = render_blocking_png(layout)
    assert svg.startswith("<svg")
    assert "not Blender/Unreal coordinates" in svg
    assert png.startswith(b"\x89PNG")


# -------------------------------------------------------------- prompt build


def test_prompt_builder_preserves_the_structured_shot_spec(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_02")
    bible = build_style_bible(candidate_set, "ART_02", "PROJECT_001")
    scene = analysis["sequences"][0]["scenes"][0]
    shot = scene["shots"][0]
    index = {entry["name"]: entry for entry in analysis["characters"]}
    built = build_shot_prompt(bible, shot, scene, index)
    assert built["shot_spec"] == shot
    assert built["modules"]["style"]
    assert built["modules"]["camera"]
    assert "watermark" in built["negative_prompt"]
    assert built["prompt"]


def test_candidate_prompt_uses_the_shared_scene(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    scene = next(
        scene
        for sequence in analysis["sequences"]
        for scene in sequence["scenes"]
        if scene["scene_id"] == candidate_set["comparison_scene_id"]
    )
    index = {entry["name"]: entry for entry in analysis["characters"]}
    built = build_candidate_prompt("graphic novel noir", scene, index)
    assert "graphic novel noir" in built["prompt"]
    assert scene["location"] in built["prompt"]


# ------------------------------------------------------------------ storage


def test_project_refuses_to_overwrite(store: ProjectStore, script: dict[str, Any]) -> None:
    with pytest.raises(FileExistsError):
        ProjectStore.create(store.root, script)


def test_generation_artifact_is_written_with_a_manifest(store: ProjectStore) -> None:
    image_path, manifest_path = store.write_generation_artifact(
        "storyboard/SEQ_01/SCN_01/SHT_001",
        b"\x89PNG\r\n\x1a\nfake",
        {"artifact_type": "STORYBOARD", "shot_id": "SHT_001", "prompt": "p", "seed": 1},
    )
    assert store.path(image_path).is_file()
    manifest = store.read(manifest_path)
    assert manifest["artifact_type"] == "STORYBOARD"
    assert manifest["seed"] == 1
    assert manifest["image_sha256"]


def test_generation_artifact_leaves_no_orphan_image(store: ProjectStore) -> None:
    with pytest.raises(jsonschema.ValidationError):
        store.write_generation_artifact(
            "storyboard/SEQ_01/SCN_01/SHT_002",
            b"not-a-png",
            {"artifact_type": "STORYBOARD", "seed": "not-an-integer"},
        )
    assert not list(store.path("storyboard").rglob("*.png"))


def test_review_events_are_append_only(store: ProjectStore) -> None:
    event = {
        "event_id": "EVT_1",
        "timestamp": "2026-11-10T00:00:00Z",
        "actor": "tester",
        "action": "APPROVE",
        "target_type": "STORYBOARD",
        "target_id": "SHT_001",
    }
    store.append_event(event)
    store.append_event({**event, "event_id": "EVT_2"})
    events = store.events()
    assert [entry["event_id"] for entry in events] == ["EVT_1", "EVT_2"]


def test_approved_script_gate_rejects_unapproved_records(database: Path) -> None:
    with pytest.raises(ApprovedScriptError):
        load_approved_script(database, "SCR_SCRIPT_LAB_10_V01")
    with pytest.raises(ApprovedScriptError):
        load_approved_script(database, "SCR_DOES_NOT_EXIST")


# ---------------------------------------------------------- comfyui boundary


class _MockComfyHandler(BaseHTTPRequestHandler):
    # Every graph submitted to /prompt, so a test can assert what was sent.
    submitted: list[dict[str, Any]] = []

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        return

    def _json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path.startswith("/system_stats"):
            self._json({"system": {"comfyui_version": "0.34.2"}, "devices": []})
        elif self.path.startswith("/object_info"):
            self._json(
                {
                    "CheckpointLoaderSimple": {
                        "input": {"required": {"ckpt_name": [["dreamshaper_8.safetensors"]]}}
                    },
                    "LoraLoader": {
                        "input": {
                            "required": {
                                "lora_name": (["arcane_offset.safetensors"],),
                                "strength_model": ("FLOAT",),
                                "strength_clip": ("FLOAT",),
                                "model": ("MODEL",),
                                "clip": ("CLIP",),
                            }
                        }
                    },
                    "CLIPTextEncode": {
                        "input": {"required": {"text": ("STRING",), "clip": ("CLIP",)}}
                    },
                    "KSampler": {
                        "input": {
                            "required": {
                                "seed": ("INT",),
                                "steps": ("INT",),
                                "cfg": ("FLOAT",),
                                "sampler_name": (["euler"],),
                                "scheduler": (["simple"],),
                                "denoise": ("FLOAT",),
                                "model": ("MODEL",),
                                "positive": ("CONDITIONING",),
                                "negative": ("CONDITIONING",),
                                "latent_image": ("LATENT",),
                            }
                        }
                    },
                    "VAEDecode": {
                        "input": {"required": {"samples": ("LATENT",), "vae": ("VAE",)}}
                    },
                    "VAELoader": {
                        "input": {
                            "required": {
                                "vae_name": (
                                    [
                                        "sdxl_vae_fp16_fix.safetensors",
                                        "dreamshaper_8.safetensors",
                                    ],
                                )
                            }
                        }
                    },
                    "SaveImage": {
                        "input": {
                            "required": {"filename_prefix": ("STRING",), "images": ("IMAGE",)}
                        }
                    },
                    "ImageScale": {
                        "input": {
                            "required": {
                                "upscale_method": (["bicubic"],),
                                "width": ("INT",),
                                "height": ("INT",),
                                "crop": (["disabled"],),
                                "image": ("IMAGE",),
                            }
                        }
                    },
                    "EmptyLatentImage": {
                        "input": {
                            "required": {
                                "width": ("INT",),
                                "height": ("INT",),
                                "batch_size": ("INT",),
                            }
                        }
                    },
                }
            )
        elif self.path.startswith("/models/"):
            self._json(["dreamshaper_8.safetensors"])
        elif self.path.startswith("/history/"):
            self._json(
                {
                    "mock-prompt": {
                        "status": {"status_str": "success", "completed": True},
                        "outputs": {
                            "8": {
                                "images": [
                                    {"filename": "mock.png", "subfolder": "", "type": "output"}
                                ]
                            }
                        },
                    }
                }
            )
        elif self.path.startswith("/view"):
            body = b"\x89PNG\r\n\x1a\nmock"
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self._json({"error": "not found"}, 404)

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        if self.path.startswith("/prompt"):
            if "prompt" not in payload:
                self._json({"error": "missing prompt"}, 400)
                return
            # Keep the submitted graph so a test can assert what was actually
            # sent to ComfyUI, not what the caller believed it sent.
            _MockComfyHandler.submitted.append(payload["prompt"])
            self._json({"prompt_id": "mock-prompt", "number": 1, "node_errors": {}})
        else:
            self._json({"error": "not found"}, 404)


@pytest.fixture
def mock_comfy():
    _MockComfyHandler.submitted = []
    server = ThreadingHTTPServer(("127.0.0.1", 0), _MockComfyHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address
    yield f"http://{host}:{port}"
    server.shutdown()
    server.server_close()


def test_client_generates_and_fetches_against_the_boundary(mock_comfy: str) -> None:
    client = ComfyUIClient(mock_comfy)
    assert client.system_stats()["system"]["comfyui_version"] == "0.34.2"
    assert client.list_models("checkpoints") == ["dreamshaper_8.safetensors"]
    workflow = txt2img_workflow(positive="a throne room", model="dreamshaper_8.safetensors")
    result = client.generate(workflow, poll_interval=0.1, timeout=30)
    assert result["outputs"][0]["filename"] == "mock.png"
    assert client.fetch_image(result["outputs"][0]).startswith(b"\x89PNG")


def test_client_reports_an_unreachable_server() -> None:
    client = ComfyUIClient("http://127.0.0.1:9", timeout=2)
    with pytest.raises(ComfyUIError):
        client.system_stats()


def test_workflow_templates_use_valid_api_references() -> None:
    workflow = txt2img_workflow(positive="x", lora="arcane_offset.safetensors")
    for node_id, node in workflow.items():
        assert node["class_type"]
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                assert value[0] in workflow, f"{node_id} references missing node {value[0]}"
    settings = workflow_settings(workflow)
    assert settings["model"] == "dreamshaper_8.safetensors"
    assert settings["lora"] == "arcane_offset.safetensors"
    assert settings["seed"] == 536354036775427


def test_canny_workflow_adds_controlnet_conditioning() -> None:
    workflow = txt2img_canny_workflow(positive="x", control_image="layout.png")
    assert workflow["9"]["class_type"] == "LoadImage"
    assert workflow["10"]["class_type"] == "Canny"
    assert workflow["12"]["class_type"] == "ControlNetApplyAdvanced"
    assert workflow["6"]["inputs"]["positive"] == ["12", 0]


def test_workflow_validation_reports_missing_nodes(mock_comfy: str) -> None:
    client = ComfyUIClient(mock_comfy)
    result = validate_workflow(client, {"1": {"class_type": "NotARealNode", "inputs": {}}})
    assert result["status"] == "FAIL"
    assert result["missing_nodes"]


# ---------------------------------------------------------------- continuity


def test_continuity_detects_duplicate_shot_ids(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_01")
    bible = build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    broken = json.loads(json.dumps(analysis))
    broken["sequences"][1]["scenes"][0]["shots"][0]["shot_id"] = (
        broken["sequences"][0]["scenes"][0]["shots"][0]["shot_id"]
    )
    report = validate_continuity(broken, bible, [], broken["source_script_sha256"])
    assert report["status"] == "FAIL"
    assert any(check["check_id"] == "shot_ids_unique" and check["status"] == "FAIL" for check in report["checks"])


def test_continuity_never_claims_visual_identity(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_01")
    bible = build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    report = validate_continuity(analysis, bible, [], analysis["source_script_sha256"])
    identity = next(c for c in report["checks"] if c["check_id"] == "visual_identity_between_images")
    assert identity["status"] == "NOT_CHECKED"


def test_continuity_flags_a_stale_source_hash(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_01")
    bible = build_style_bible(candidate_set, "ART_01", "PROJECT_001")
    generations = [
        {
            "generation_id": "GEN_1",
            "source_script_sha256": "deadbeef",
            "prompt": "p",
            "seed": 1,
            "model": "m",
            "workflow_id": "w",
        }
    ]
    report = validate_continuity(analysis, bible, generations, analysis["source_script_sha256"])
    assert any(check["check_id"] == "source_hash_current" and check["status"] == "FAIL" for check in report["checks"])


# ------------------------------------------------------------------- handoff


def test_handoff_contains_the_required_sections(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_02")
    bible = build_style_bible(candidate_set, "ART_02", "PROJECT_001")
    generations = [
        {
            "generation_id": "GEN_1",
            "artifact_type": "STORYBOARD",
            "shot_id": "SHT_SCN_01_01_001",
            "image_path": "storyboard/x.png",
            "review_status": "APPROVED",
        }
    ]
    package = build_handoff(
        analysis,
        bible,
        generations,
        [],
        {"script_id": SCRIPT_ID, "approval_status": "APPROVED", "sha256": "abc"},
        None,
    )
    for key in (
        "source_script",
        "style_bible",
        "sequences",
        "approved_storyboard_images",
        "approved_blocking_images",
        "camera_notes",
        "lighting_notes",
        "animation_requirements",
        "environment_construction_requirements",
        "production_complexity",
        "unresolved_issues",
        "engine_notes",
    ):
        assert key in package, key
    assert package["approved_storyboard_images"][0]["generation_id"] == "GEN_1"
    assert package["engine_notes"]["world_coordinates"] is False
    assert package["engine_notes"]["coordinate_space"] == "NONE"


def test_handoff_markdown_does_not_promise_3d_geometry(analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(analysis, "PROJECT_001")
    select_candidate(candidate_set, "ART_02")
    bible = build_style_bible(candidate_set, "ART_02", "PROJECT_001")
    package = build_handoff(analysis, bible, [], [], {"script_id": SCRIPT_ID}, None)
    markdown = render_handoff_markdown(package)
    assert "not a 3D scene" in markdown
    assert "No images are approved yet" in markdown


def test_committed_pilot_artifacts_are_internally_consistent() -> None:
    """Every committed generation manifest must match its image byte for byte."""
    import hashlib

    root = ROOT / "PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1"
    if not root.is_dir():
        pytest.skip("Pilot project is not present in this checkout.")
    checked = 0
    for manifest_path in sorted(root.rglob("GEN_*.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        image = root / manifest["image_path"]
        assert image.is_file(), f"missing image {manifest['image_path']}"
        assert hashlib.sha256(image.read_bytes()).hexdigest() == manifest["image_sha256"], (
            f"hash mismatch for {manifest['image_path']}"
        )
        checked += 1
    assert checked == 26, f"expected 26 committed generations, found {checked}"


def test_committed_pilot_review_events_reference_existing_generations() -> None:
    root = ROOT / "PROJECTS/VDEV_PROJECT_001_SCR_PROJECT_001_V01_V1"
    if not root.is_dir():
        pytest.skip("Pilot project is not present in this checkout.")
    generations = {
        json.loads(path.read_text(encoding="utf-8"))["generation_id"]
        for path in root.rglob("GEN_*.json")
    }
    events = [
        json.loads(line)
        for line in (root / "reviews/review_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]
    assert events, "the pilot must record review events"
    for event in events:
        generation_id = (event.get("metadata") or {}).get("generation_id")
        if generation_id:
            assert generation_id in generations, f"event points at missing {generation_id}"


# --------------------------------------------------------- narrator format


YS01_REVISED = (
    ROOT / "PROJECTS/YOUTUBE_SCRIPT_EXPERIMENT/SCRIPTS/REVISED/YS01_THE_FOG_THAT_CHANGED_THE_AIR.md"
)


@pytest.fixture
def ys01_analysis() -> dict[str, Any]:
    if not YS01_REVISED.is_file():
        pytest.skip("YS01 revised script is not present in this checkout.")
    text = YS01_REVISED.read_text(encoding="utf-8")
    return parse_script(text, "YS01", sha256_text(text))


def test_narrator_format_is_detected_and_screenplay_is_not(ys01_analysis: dict[str, Any]) -> None:
    assert ys01_analysis["source_format"] == "NARRATOR"
    assert len(ys01_analysis["sequences"]) == 6
    schema = json.loads((SCHEMA_DIR / "analysis.schema.json").read_text(encoding="utf-8"))
    jsonschema.validate(ys01_analysis, schema)


def test_narrator_shots_reference_the_script(ys01_analysis: dict[str, Any]) -> None:
    text = YS01_REVISED.read_text(encoding="utf-8")
    shots = [
        shot
        for sequence in ys01_analysis["sequences"]
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    ]
    assert len(shots) == 8
    for shot in shots:
        assert shot["source_spans"], "every narrator shot needs a source reference"
        for span in shot["source_spans"]:
            assert text[span["start"] : span["end"]] == span["text"]


def test_narrator_segments_run_from_zero_to_the_stated_runtime(ys01_analysis: dict[str, Any]) -> None:
    sequences = ys01_analysis["sequences"]
    assert sequences[0]["start_seconds"] == 0
    assert sequences[-1]["end_seconds"] == ys01_analysis["episode"]["target_runtime_sec"]
    for index, sequence in enumerate(sequences):
        if index + 1 < len(sequences):
            assert sequence["end_seconds"] == sequences[index + 1]["start_seconds"]
    total = sum(
        shot["estimated_duration_sec"]
        for sequence in sequences
        for scene in sequence["scenes"]
        for shot in scene["shots"]
    )
    assert total == pytest.approx(ys01_analysis["episode"]["target_runtime_sec"], abs=1.0)


def test_narrator_narration_and_sound_are_facts_not_shots(ys01_analysis: dict[str, Any]) -> None:
    scene = ys01_analysis["sequences"][0]["scenes"][0]
    facts = " ".join(scene["explicit_facts"])
    assert "Narration:" in facts
    assert "Sound:" in facts
    for shot in scene["shots"]:
        assert not shot["visual_description"].startswith("Narration:")


def test_art_direction_comparison_frame_is_a_single_concrete_subject(
    ys01_analysis: dict[str, Any],
) -> None:
    candidate_set = build_candidates(ys01_analysis, "YS01")
    assert candidate_set["comparison_scene_id"] == "SCN_01_01"
    subject = candidate_set["candidates"][0]["comparison_subject"]
    assert subject
    assert ". " not in subject, "the comparison subject must be one frame, not a paragraph"
    for candidate in candidate_set["candidates"]:
        assert "split panel" in candidate["comparison_negative_prompt"]
        assert "no split panels" in candidate["comparison_prompt"]


def test_comparison_prompt_forbids_multi_panel_layout(ys01_analysis: dict[str, Any]) -> None:
    candidate_set = build_candidates(ys01_analysis, "YS01")
    scene = next(
        scene
        for sequence in ys01_analysis["sequences"]
        for scene in sequence["scenes"]
        if scene["scene_id"] == candidate_set["comparison_scene_id"]
    )
    built = build_candidate_prompt(
        candidate_set["candidates"][0]["style_prompt"], scene, {}
    )
    assert "no split panels" in built["prompt"]
    assert "split panel" in built["negative_prompt"]
    assert "labels appearing" not in built["prompt"]


# ------------------------------------------------- unapproved source files

def test_script_file_import_is_never_marked_approved(tmp_path: Path) -> None:
    script_file = tmp_path / "draft.md"
    script_file.write_text("# Draft\n\nSome narration.\n", encoding="utf-8")
    record = load_script_file(script_file, "DRAFT_01", "DRAFT")
    assert record["approval_status"] == "NOT_APPROVED"
    assert record["is_immutable"] is False
    assert record["source_type"] == "FILE"
    assert record["sha256"] == sha256_text("# Draft\n\nSome narration.\n")
    assert record["approval_note"]


def test_approved_script_gate_still_rejects_unapproved_database_rows(database: Path) -> None:
    """The file-import path must not weaken the database approval gate."""
    with pytest.raises(ApprovedScriptError):
        load_approved_script(database, "SCR_SCRIPT_LAB_10_V01")
    record = load_approved_script(database, SCRIPT_ID)
    assert record["approval_status"] == "APPROVED"


# ------------------------------------------------------- review page script


@contextlib.contextmanager
def _review_server(project_dir: Path):
    """Run the real review server and yield its base URL."""
    from VISUAL_DEVELOPMENT.review_server import make_handler

    store = ProjectStore(project_dir)
    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(store))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def _served_review_page(project_dir: Path) -> str:
    """Fetch the review page from the real server over real HTTP.

    The page must be checked in its *served* form. The template still contains
    Python escape sequences that are resolved during rendering, and the browser
    only ever sees the rendered bytes.
    """
    with _review_server(project_dir) as base:
        with urllib.request.urlopen(base + "/", timeout=15) as response:
            return response.read().decode("utf-8")


def _headless_browser() -> str | None:
    """Locate a headless browser, or None when none is installed."""
    for candidate in (
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ):
        if Path(candidate).is_file():
            return candidate
    return shutil.which("msedge") or shutil.which("chrome")


def _unterminated_js_string(script: str) -> str | None:
    """Return the quote character of an unterminated JS string, or None.

    A single unbalanced quote in the served page silently blanks the whole
    review UI, because the browser refuses to run the script block at all.

    The scanner tracks string, template, comment and regular-expression
    literals, so a quote that sits inside one of them is not mistaken for the
    start of another string.
    """
    length = len(script)
    index = 0
    previous = ""  # last significant character seen in code position
    while index < length:
        char = script[index]
        following = script[index + 1] if index + 1 < length else ""
        if char == "/" and following == "/":
            while index < length and script[index] != "\n":
                index += 1
            continue
        if char == "/" and following == "*":
            index += 2
            while index < length and not (
                script[index] == "*"
                and index + 1 < length
                and script[index + 1] == "/"
            ):
                index += 1
            index += 2
            continue
        if char == "/" and (previous == "" or previous in "=(,:[!&|?{};+-*%~^"):
            index += 1
            in_class = False
            while index < length:
                current = script[index]
                if current == "\\":
                    index += 2
                    continue
                if current == "[":
                    in_class = True
                elif current == "]":
                    in_class = False
                elif current == "/" and not in_class:
                    break
                elif current == "\n":
                    break
                index += 1
            index += 1
            previous = "/"
            continue
        if char in "\"'`":
            quote = char
            index += 1
            while index < length:
                current = script[index]
                if current == "\\":
                    index += 2
                    continue
                if current == quote:
                    break
                if quote == "`" and current == "$" and index + 1 < length and script[index + 1] == "{":
                    depth = 1
                    index += 2
                    while index < length and depth:
                        if script[index] == "{":
                            depth += 1
                        elif script[index] == "}":
                            depth -= 1
                        index += 1
                    continue
                index += 1
            if index >= length:
                return quote
            index += 1
            previous = quote
            continue
        if not char.isspace():
            previous = char
        index += 1
    return None


@pytest.fixture
def review_store(store: ProjectStore, analysis: dict[str, Any]) -> ProjectStore:
    """A project with an analysis and an art-direction candidate set.

    The candidate set matters: the image markup only exists once there is
    something to show, which is exactly where the page used to break.
    """
    candidate_set = build_candidates(analysis, "PROJECT_001")
    for candidate in candidate_set["candidates"]:
        candidate["generation_manifest"] = {
            "image_path": f"art_direction/candidate_{candidate['candidate_id']}/GEN_TEST.png"
        }
    store.write_json("analysis/analysis_v001.json", analysis, "analysis.schema.json")
    store.write_json("art_direction/candidates_v001.json", candidate_set, "candidate.schema.json")
    return store


def test_the_pipeline_advances_the_project_stage(store: ProjectStore) -> None:
    """The project manifest must report how far the pipeline got.

    It used to stay on SOURCE_IMPORTED for the whole life of a project, so
    the stage could not be used to tell where something stood.
    """
    import argparse

    from VISUAL_DEVELOPMENT.cli import cmd_analyze, cmd_art_direction

    assert store.read("project.json")["stage"] == "SOURCE_IMPORTED"
    cmd_analyze(argparse.Namespace(project_dir=store.root))
    assert store.read("project.json")["stage"] == "ANALYZED"
    cmd_art_direction(
        argparse.Namespace(project_dir=store.root, comparison_scene=None)
    )
    assert store.read("project.json")["stage"] == "ART_DIRECTION_READY"


def test_review_page_script_is_syntactically_balanced(review_store: ProjectStore) -> None:
    """Regression guard: the review page must never serve a blank shell.

    The check runs against the bytes the server actually sends, not the
    template. Checking the template misses escaped quotes that Python
    resolves during rendering, which is how a broken page passed review.
    """
    html = _served_review_page(review_store.root)
    assert "<script>" in html and "</script>" in html
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    unterminated = _unterminated_js_string(script)
    assert unterminated is None, f"unterminated {unterminated!r} quote in the served review page script"


def test_review_page_has_no_inline_event_handlers(review_store: ProjectStore) -> None:
    """No inline event handler may appear anywhere in the served page.

    An inline handler such as onerror="..." puts a raw double quote inside a
    double-quoted JavaScript string and kills the whole script block.
    """
    html = _served_review_page(review_store.root)
    handlers = sorted(set(re.findall(r"\son([a-z]+)\s*=", html, flags=re.IGNORECASE)))
    assert not handlers, f"inline event handlers in the served page: {handlers}"
    assert "data-act=" in html, "actions must use data attributes and a delegated handler"


def test_review_page_script_passes_a_javascript_parser(review_store: ProjectStore) -> None:
    """The served script block must parse as JavaScript.

    A real parser is the only check that cannot be fooled by the quote
    scanner: the historical defect had balanced quotes and was still a
    syntax error. Node is a hard dependency of the frontend build, so it is
    required here rather than skipped.
    """
    node = shutil.which("node")
    if node is None:
        pytest.fail(
            "node is required to parse the review page script; the frontend build "
            "needs it too, so install node instead of skipping this guard"
        )
    html = _served_review_page(review_store.root)
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / "review_page.js"
        target.write_text(script, encoding="utf-8")
        result = subprocess.run(
            [node, "--check", str(target)], capture_output=True, text=True, timeout=60
        )
    assert result.returncode == 0, f"served review page script does not parse:\n{result.stderr}"


def test_the_guard_rejects_the_historical_defect() -> None:
    """The guards must fail on the markup that actually broke the page.

    This is the script block exactly as it was served before the fix. The
    inline onerror attribute closes the JavaScript string early, so the
    browser stops parsing the whole block and the page renders empty.

    Note that the quotes in it are balanced: the defect is a syntax error,
    not an unterminated string. A quote scanner cannot see it. The inline
    handler rule catches it, and the real parser catches it.
    """
    broken = (
        '"<figure><img loading=\'lazy\' src=\'/media/"+encodeURI(c.image_path||"")+'
        '"\' onerror="this.style.background=\'#3a2020\';this.alt=\'no image\'">"'
    )
    assert re.findall(r"\son([a-z]+)\s*=", broken, flags=re.IGNORECASE) == ["error"]
    assert _unterminated_js_string(broken) is None, (
        "this defect is a syntax error, not an unbalanced quote; the quote scanner "
        "alone cannot catch it, which is why a real parser is required"
    )
    node = shutil.which("node")
    if node is None:
        pytest.fail("node is required to parse the review page script")
    with tempfile.TemporaryDirectory() as folder:
        target = Path(folder) / "broken.js"
        target.write_text(broken, encoding="utf-8")
        result = subprocess.run(
            [node, "--check", str(target)], capture_output=True, text=True, timeout=60
        )
    assert result.returncode != 0, "the historical defect must not parse"


def test_review_page_renders_the_gallery_in_a_real_browser(review_store: ProjectStore) -> None:
    """A real browser must render the gallery, not an empty shell.

    The served bytes can be well formed while the page still shows nothing:
    the stylesheet hides every section unless it carries the active class,
    and the renderer has to switch that class on. Only a browser sees that.
    """
    browser = _headless_browser()
    if browser is None:
        pytest.skip("no headless browser is installed")
    with _review_server(review_store.root) as base:
        with tempfile.TemporaryDirectory() as profile:
            result = subprocess.run(
                [
                    browser,
                    "--headless=new",
                    "--disable-gpu",
                    "--no-sandbox",
                    f"--user-data-dir={profile}",
                    "--virtual-time-budget=15000",
                    "--dump-dom",
                    base + "/",
                ],
                capture_output=True,
                text=True,
                timeout=240,
            )
    dom = result.stdout
    assert "ART_01" in dom, "the browser must render the candidate gallery"
    assert "<img" in dom, "the browser must render the generated images"
    visible = re.findall(r'<section id="([^"]+)" class="active"', dom)
    assert len(visible) == 1, f"exactly one section must be visible, found {visible}"


def test_review_page_renders_images_and_controls(review_store: ProjectStore) -> None:
    """The served page must carry the gallery, not an empty shell."""
    html = _served_review_page(review_store.root)
    assert "<figure><img" in html, "the served page must build image figures"
    assert "art_direction/candidate_ART_01/GEN_TEST.png" in html, "image paths must reach the client"
    assert "data-act='SELECT'" in html, "the candidate selection control must be present"
    assert "Art Direction" in html and "Style Bible" in html


# --------------------------------------------- breakdown, spine and overrides


def _user_workflow() -> dict[str, Any]:
    """A user graph with an extra node the built-in templates never use."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "dreamshaper_8.safetensors"}},
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": "arcane_offset.safetensors",
                "strength_model": 0.65,
                "strength_clip": 0.65,
            },
        },
        "3": {"class_type": "CLIPTextEncode", "inputs": {"text": "PLACEHOLDER", "clip": ["2", 1]}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"text": "PLACEHOLDER", "clip": ["2", 1]}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
        "6": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": 1,
                "steps": 20,
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
            },
        },
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["7", 0],
                "upscale_method": "bicubic",
                "width": 1024,
                "height": 1024,
                "crop": "disabled",
            },
        },
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": "UserWorkflow"}},
    }


def test_breakdown_derives_only_what_the_script_states(analysis: dict[str, Any]) -> None:
    """Every element must be traceable to the script, never invented."""
    from VISUAL_DEVELOPMENT.breakdown import build_breakdown

    breakdown = build_breakdown(analysis, "PROJECT_001")
    assert breakdown["scenes"]
    known = {entry["name"].lower() for entry in analysis.get("characters", [])}
    located_by_id = {scene["scene_id"]: scene for scene in breakdown["scenes"]}
    for sequence in analysis["sequences"]:
        for scene in sequence["scenes"]:
            body = " ".join(
                [scene.get("action") or ""]
                + [str(fact) for fact in scene.get("explicit_facts", [])]
            ).lower()
            located = located_by_id[scene["scene_id"]]
            for element in located["elements"]:
                assert element["source"] in {"SCRIPT", "INFERRED"}
                assert element["category"]
                assert element["name"]
                if element["category"] == "location":
                    continue
                assert (
                    element["name"].lower() in body
                    or element["name"].lower() in known
                ), f"{element['name']} is not traceable to the script"
    assert breakdown["summary"]["scene_count"] == len(breakdown["scenes"])
    assert breakdown["summary"]["element_count"] > 0


def test_breakdown_uses_the_industry_taxonomy(analysis: dict[str, Any]) -> None:
    """The categories are the ones a breakdown sheet carries."""
    from VISUAL_DEVELOPMENT.breakdown import CATEGORIES, build_breakdown

    breakdown = build_breakdown(analysis, "PROJECT_001")
    for expected in ("cast", "props", "set_dressing", "costume", "vfx", "sound", "music"):
        assert expected in CATEGORIES
    for scene in breakdown["scenes"]:
        # Categories the script does not mention stay visible rather than vanish.
        assert set(scene["untagged_categories"]).issubset(set(CATEGORIES))
        assert scene["untagged_categories"]


def test_breakdown_tags_cast_and_props_from_the_scene(analysis: dict[str, Any]) -> None:
    from VISUAL_DEVELOPMENT.breakdown import build_breakdown

    breakdown = build_breakdown(analysis, "PROJECT_001")
    scene = breakdown["scenes"][0]
    categories = {element["category"] for element in scene["elements"]}
    assert "cast" in categories
    assert "props" in categories
    cast = [e for e in scene["elements"] if e["category"] == "cast"]
    assert all(element["status"] == "NEEDS_REFERENCE" for element in cast)


def test_production_spine_lists_the_stages_in_studio_order(store: ProjectStore) -> None:
    from VISUAL_DEVELOPMENT.production import STAGE_IDS

    assert STAGE_IDS == [
        "SCRIPT",
        "BREAKDOWN",
        "VISUAL_DIRECTION",
        "BOARDS",
        "PREVIZ",
        "CONTINUITY",
        "HANDOFF",
    ]


def test_production_status_links_the_script_to_the_visuals(store: ProjectStore) -> None:
    import argparse

    from VISUAL_DEVELOPMENT.cli import cmd_analyze
    from VISUAL_DEVELOPMENT.production import pipeline_status

    cmd_analyze(argparse.Namespace(project_dir=store.root))
    status = pipeline_status(store)
    assert status["link"]["script_id"] == SCRIPT_ID
    assert status["link"]["approval_status"] == "APPROVED"
    assert status["shots"]["total"] == 9
    assert status["shots"]["statuses"]["NOT_STARTED"] == 9
    assert status["stages"][0]["stage_id"] == "SCRIPT"
    assert status["stages"][0]["complete"] is True


def test_shot_status_follows_the_work_that_was_done(
    store: ProjectStore, analysis: dict[str, Any]
) -> None:
    import argparse

    from VISUAL_DEVELOPMENT.cli import cmd_analyze
    from VISUAL_DEVELOPMENT.production import derive_shot_status

    cmd_analyze(argparse.Namespace(project_dir=store.root))
    shot_id = analysis["sequences"][0]["scenes"][0]["shots"][0]["shot_id"]
    assert derive_shot_status(store, shot_id) == "NOT_STARTED"

    from VISUAL_DEVELOPMENT.common import new_id, utc_now

    store.write_json(
        f"storyboard/{shot_id}/GEN_TEST.json",
        {
            "generation_id": "GEN_TEST",
            "artifact_type": "STORYBOARD",
            "shot_id": shot_id,
            "image_path": f"storyboard/{shot_id}/GEN_TEST.png",
            "image_sha256": "0" * 64,
            "prompt": "x",
            "negative_prompt": "y",
            "created_at": utc_now(),
        },
        "generation_manifest.schema.json",
    )
    assert derive_shot_status(store, shot_id) == "BOARDED"

    store.append_event(
        {
            "event_id": new_id("EVT"),
            "timestamp": utc_now(),
            "actor": "operator",
            "action": "APPROVE",
            "target_type": "STORYBOARD",
            "target_id": shot_id,
            "note": "",
            "metadata": {},
        }
    )
    assert derive_shot_status(store, shot_id) == "APPROVED"


def test_prompt_override_appends_the_users_text() -> None:
    from VISUAL_DEVELOPMENT.prompt_overrides import effective_prompt

    built = {"prompt": "s", "negative_prompt": "gen negative", "modules": {"style": "s"}}
    override = build_override("SHT_1", "SHOT", prompt_extra="my own direction")
    merged = effective_prompt(built, override)
    assert merged["prompt"] == "s, my own direction"
    assert merged["changed"] is True
    assert "prompt_extra" in merged["applied_overrides"]


def test_prompt_override_can_exclude_a_module() -> None:
    from VISUAL_DEVELOPMENT.prompt_overrides import effective_prompt

    built = {
        "prompt": "style, camera, lighting",
        "negative_prompt": "n",
        "modules": {"style": "style", "camera": "camera", "lighting": "lighting"},
    }
    override = build_override("SHT_1", "SHOT", exclude_modules=["camera"])
    merged = effective_prompt(built, override)
    assert "camera" not in merged["modules"]
    assert "camera" not in merged["prompt"]
    assert "style" in merged["prompt"]


def test_prompt_override_can_replace_the_prompt() -> None:
    from VISUAL_DEVELOPMENT.prompt_overrides import effective_prompt

    built = {"prompt": "generated", "negative_prompt": "n", "modules": {"style": "s"}}
    override = build_override("SHT_1", "SHOT", prompt_replace="only my words")
    merged = effective_prompt(built, override)
    assert merged["prompt"] == "only my words"


def test_prompt_override_settings_are_applied_and_bounded() -> None:
    from VISUAL_DEVELOPMENT.prompt_overrides import effective_settings

    override = build_override(
        "SHT_1", "SHOT", settings_override={"seed": 42, "steps": 30}
    )
    resolved = effective_settings({"seed": 1, "steps": 25, "model": "m"}, override)
    assert resolved["settings"]["seed"] == 42
    assert resolved["settings"]["steps"] == 30
    assert resolved["settings"]["model"] == "m"
    assert sorted(resolved["applied_overrides"]) == ["seed", "steps"]

    with pytest.raises(ValueError):
        build_override("SHT_1", "SHOT", settings_override={"not_a_setting": 1})


def test_prompt_override_persists_and_can_be_cleared(store: ProjectStore) -> None:
    from VISUAL_DEVELOPMENT.prompt_overrides import (
        clear_override,
        get_override,
        load_overrides,
        save_override,
    )

    override = build_override("SHT_1", "SHOT", prompt_extra="keep me")
    save_override(store, override)
    assert get_override(store, "SHT_1")["prompt_extra"] == "keep me"
    assert "SHT_1" in load_overrides(store)
    assert clear_override(store, "SHT_1") is True
    assert get_override(store, "SHT_1") is None
    assert clear_override(store, "SHT_1") is False


def test_user_workflow_prompt_nodes_are_found_by_following_the_graph() -> None:
    from VISUAL_DEVELOPMENT.workflows import resolve_prompt_nodes

    nodes = resolve_prompt_nodes(_user_workflow())
    assert nodes["sampler"] == "6"
    assert nodes["positive"] == "3"
    assert nodes["negative"] == "4"
    assert nodes["latent"] == "5"


def test_user_workflow_keeps_the_nodes_the_user_built() -> None:
    """Only the prompt text and the sampling inputs may change."""
    from VISUAL_DEVELOPMENT.workflows import apply_to_user_workflow

    original = _user_workflow()
    filled = apply_to_user_workflow(
        original,
        positive="my prompt",
        negative="my negative",
        settings={"seed": 99, "steps": 30, "width": 768, "height": 768},
    )
    workflow = filled["workflow"]
    assert workflow["3"]["inputs"]["text"] == "my prompt"
    assert workflow["4"]["inputs"]["text"] == "my negative"
    assert workflow["6"]["inputs"]["seed"] == 99
    assert workflow["6"]["inputs"]["steps"] == 30
    assert workflow["5"]["inputs"]["width"] == 768
    # The user's own nodes and links are untouched.
    assert workflow["8"]["class_type"] == "ImageScale"
    assert workflow["8"]["inputs"]["width"] == 1024
    assert workflow["9"]["inputs"]["images"] == ["8", 0]
    assert workflow["6"]["inputs"]["model"] == ["2", 0]
    # The original is not mutated.
    assert original["3"]["inputs"]["text"] == "PLACEHOLDER"


def test_user_workflow_is_validated_against_the_server(mock_comfy: str) -> None:
    from VISUAL_DEVELOPMENT.workflows import validate_user_workflow

    client = ComfyUIClient(mock_comfy)
    report = validate_user_workflow(client, _user_workflow())
    assert report["status"] == "PASS"
    assert report["can_take_prompt"] is True

    without_text = {
        node_id: node
        for node_id, node in _user_workflow().items()
        if node.get("class_type") != "CLIPTextEncode"
    }
    report = validate_user_workflow(client, without_text)
    assert report["status"] == "FAIL"
    assert report["can_take_prompt"] is False


def test_generation_sends_the_users_prompt_to_comfyui(
    store: ProjectStore, mock_comfy: str
) -> None:
    """The end to end proof: what the user typed is what ComfyUI received."""
    from VISUAL_DEVELOPMENT.generation import generate_image

    client = ComfyUIClient(mock_comfy)
    result = generate_image(
        client,
        store,
        artifact_type="STORYBOARD",
        relative_dir="storyboard/SHT_TEST",
        prompt="generated text, my own direction",
        negative_prompt="generated negative, my own negative",
        settings={"model": "dreamshaper_8.safetensors", "seed": 42, "steps": 30},
        workflow_id="txt2img_v1",
        shot_id="SHT_TEST",
        user_workflow=_user_workflow(),
        override_applied=["prompt_extra"],
    )
    assert result["status"] == "PASS"
    assert _MockComfyHandler.submitted, "nothing was submitted to ComfyUI"
    submitted = _MockComfyHandler.submitted[-1]
    texts = [
        node["inputs"]["text"]
        for node in submitted.values()
        if node.get("class_type") == "CLIPTextEncode"
    ]
    assert "generated text, my own direction" in texts
    assert "generated negative, my own negative" in texts
    # The user's extra node survived the round trip.
    assert any(node.get("class_type") == "ImageScale" for node in submitted.values())

    manifest = store.read(result["manifest_path"])
    assert manifest["workflow_source"] == "USER"
    assert "prompt_extra" in manifest["prompt_overrides_applied"]
    assert manifest["seed"] == 42


def test_the_project_stage_never_goes_backwards(store: ProjectStore) -> None:
    """Re-running an earlier command must not un-finish a later stage."""
    import argparse

    from VISUAL_DEVELOPMENT.cli import cmd_analyze, cmd_breakdown, cmd_handoff

    cmd_analyze(argparse.Namespace(project_dir=store.root))
    assert store.read("project.json")["stage"] == "ANALYZED"
    cmd_breakdown(argparse.Namespace(project_dir=store.root))
    assert store.read("project.json")["stage"] == "BREAKDOWN_COMPLETE"

    # Pretend the handoff already ran, then run the breakdown again.
    project = store.read("project.json")
    project["stage"] = "HANDOFF_EXPORTED"
    store.update_json("project.json", project, "project.schema.json")
    cmd_breakdown(argparse.Namespace(project_dir=store.root))
    assert store.read("project.json")["stage"] == "HANDOFF_EXPORTED"


def test_breakdown_command_writes_a_breakdown(store: ProjectStore) -> None:
    import argparse

    from VISUAL_DEVELOPMENT.cli import cmd_analyze, cmd_breakdown

    cmd_analyze(argparse.Namespace(project_dir=store.root))
    cmd_breakdown(argparse.Namespace(project_dir=store.root))
    assert store.path("breakdown/breakdown_v001.json").is_file()
    assert store.read("project.json")["stage"] == "BREAKDOWN_COMPLETE"



# ------------------------------------------------------------------- animatic


def test_animatic_timeline_follows_the_shots(analysis: dict[str, Any]) -> None:
    """The timeline is the shots in order, held for the time the analysis gave."""
    from VISUAL_DEVELOPMENT.animatic import build_animatic

    timeline = build_animatic(analysis, [])
    assert len(timeline["entries"]) == 9
    assert timeline["summary"]["shot_count"] == 9
    assert timeline["summary"]["picture_count"] == 0
    # The first entry starts at zero and the rest follow on.
    assert timeline["entries"][0]["start_sec"] == 0.0
    for previous, entry in zip(timeline["entries"], timeline["entries"][1:]):
        assert entry["start_sec"] == pytest.approx(
            previous["start_sec"] + previous["duration_sec"], abs=0.01
        )
    assert timeline["summary"]["total_duration_sec"] > 0


def test_animatic_uses_the_boards_that_exist() -> None:
    """A shot with a storyboard generation points at that picture."""
    from VISUAL_DEVELOPMENT.animatic import build_animatic

    analysis = {
        "source_format": "SCREENPLAY",
        "sequences": [
            {
                "sequence_id": "SEQ_01",
                "scenes": [
                    {
                        "scene_id": "SCN_01_01",
                        "heading": "INT. ROOM - DAY",
                        "shots": [
                            {
                                "shot_id": "SHT_01",
                                "estimated_duration_sec": 3.0,
                                "visual_description": "A thing happens",
                                "characters": [],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    generations = [
        {
            "artifact_type": "STORYBOARD",
            "shot_id": "SHT_01",
            "image_path": "storyboard/SHT_01/GEN_A.png",
        }
    ]
    timeline = build_animatic(analysis, generations)
    assert timeline["entries"][0]["image_path"] == "storyboard/SHT_01/GEN_A.png"
    assert timeline["entries"][0]["has_picture"] is True
    assert timeline["summary"]["picture_count"] == 1
    assert timeline["summary"]["missing_pictures"] == []


def test_animatic_carries_the_words_from_the_script() -> None:
    """Dialogue and narration are read from the script, never invented."""
    from VISUAL_DEVELOPMENT.animatic import build_animatic

    analysis = {
        "source_format": "NARRATOR",
        "sequences": [
            {
                "sequence_id": "SEQ_01",
                "scenes": [
                    {
                        "scene_id": "SCN_01_01",
                        "heading": "00:00 - Opening",
                        "explicit_facts": ["Narration: The fog came first."],
                        "shots": [
                            {
                                "shot_id": "SHT_01",
                                "estimated_duration_sec": 4.0,
                                "visual_description": "A street fades.",
                                "characters": [],
                            }
                        ],
                    }
                ],
            }
        ],
    }
    timeline = build_animatic(analysis, [])
    assert timeline["voice_lines"]
    line = timeline["voice_lines"][0]
    assert line["kind"] == "NARRATION"
    assert line["text"] == "The fog came first."
    assert line["start_sec"] == 0.0


def test_animatic_survives_a_missing_voice_model(tmp_path: Path) -> None:
    """No voice model is not an error: the line is recorded as silent."""
    from VISUAL_DEVELOPMENT.animatic import synthesize_voice

    result = synthesize_voice(
        "hello", tmp_path / "line.wav", venv_python=tmp_path / "no-such-python.exe"
    )
    assert result["status"] == "NO_VOICE_MODEL"
    assert result["duration_sec"] == 0.0


def test_animatic_mixes_the_voice_onto_one_track(tmp_path: Path) -> None:
    """Each clip lands at its start time on a single track."""
    from VISUAL_DEVELOPMENT.animatic import mix_voice_track

    def write_wav(path: Path, seconds: float, value: int) -> None:
        with wave.open(str(path), "wb") as handle:
            handle.setnchannels(1)
            handle.setsampwidth(2)
            handle.setframerate(24000)
            handle.writeframes(
                struct.pack("<" + "h" * int(seconds * 24000), *([value] * int(seconds * 24000)))
            )

    first = tmp_path / "a.wav"
    second = tmp_path / "b.wav"
    write_wav(first, 0.5, 1000)
    write_wav(second, 0.5, 2000)
    out = tmp_path / "voice.wav"

    result = mix_voice_track([(first, 0.0), (second, 2.0)], out, total_seconds=4.0)
    assert result["status"] == "PASS"
    assert result["clips_placed"] == 2
    with wave.open(str(out), "rb") as handle:
        assert handle.getnframes() == int(4.0 * 24000)
        frames = handle.readframes(handle.getnframes())
    samples = struct.unpack("<" + "h" * (len(frames) // 2), frames)
    assert samples[0] == 1000
    # The second clip starts two seconds in.
    assert samples[int(2.0 * 24000)] == 2000
    # And nothing is spoken between the two.
    assert samples[int(1.0 * 24000)] == 0


def test_animatic_refuses_to_render_without_pictures(tmp_path: Path) -> None:
    from VISUAL_DEVELOPMENT.animatic import build_animatic, render_animatic

    timeline = build_animatic({"sequences": []}, [])
    result = render_animatic(timeline, tmp_path / "out.mp4")
    assert result["status"] == "NO_PICTURES"


def test_animatic_cuts_a_real_video(tmp_path: Path, analysis: dict[str, Any]) -> None:
    """The boards are cut to a playable file with the right duration."""
    import shutil

    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg is not installed")
    from VISUAL_DEVELOPMENT.animatic import build_animatic, render_animatic

    image = tmp_path / "board.png"
    Image.new("RGB", (64, 64), (20, 90, 60)).save(image)
    analysis = {
        "sequences": [
            {
                "sequence_id": "SEQ_01",
                "scenes": [
                    {
                        "scene_id": "SCN_01_01",
                        "heading": "INT. ROOM - DAY",
                        "shots": [
                            {
                                "shot_id": "SHT_01",
                                "estimated_duration_sec": 2.0,
                                "visual_description": "A thing",
                                "characters": [],
                            },
                            {
                                "shot_id": "SHT_02",
                                "estimated_duration_sec": 1.5,
                                "visual_description": "Another thing",
                                "characters": [],
                            },
                        ],
                    }
                ],
            }
        ],
    }
    generations = [
        {"artifact_type": "STORYBOARD", "shot_id": "SHT_01", "image_path": "a.png"},
        {"artifact_type": "STORYBOARD", "shot_id": "SHT_02", "image_path": "b.png"},
    ]
    timeline = build_animatic(analysis, generations)
    # The pictures live next to the timeline for the test.
    (tmp_path / "a.png").write_bytes(image.read_bytes())
    (tmp_path / "b.png").write_bytes(image.read_bytes())
    result = render_animatic(
        timeline, tmp_path / "out.mp4", project_root=tmp_path, width=64
    )
    assert result["status"] == "PASS"
    assert (tmp_path / "out.mp4").exists()
    assert result["duration_sec"] == pytest.approx(3.5, abs=0.2)


def test_handoff_carries_the_breakdown_prompts_and_status(
    analysis: dict[str, Any]
) -> None:
    """The package says what was asked, what was decided and what came out."""
    from VISUAL_DEVELOPMENT.handoff import build_handoff

    style_bible = {
        "style_bible_id": "STYLE_TEST",
        "version": 1,
        "status": "DRAFT",
        "style_identity": "Test",
        "global_rules": {"lighting": "soft", "atmosphere": "calm"},
        "scene_variables": {},
    }
    package = build_handoff(
        analysis,
        style_bible,
        [],
        [],
        {"script_id": "S", "approval_status": "APPROVED", "sha256": "0" * 64},
        breakdown={"scenes": [{"scene_id": "SCN_01", "heading": "H", "elements": []}],
                   "summary": {"scene_count": 1, "element_count": 0, "total_page_eighths": 1.0}},
        prompt_overrides={"ART_01": {"kind": "ART_DIRECTION_CANDIDATE", "prompt_extra": "mine"}},
        shot_statuses={"SHT_01": "BOARDED"},
        animatic={"summary": {"shot_count": 1}, "video_path": "animatic/x.mp4"},
    )
    assert package["breakdown"]["summary"]["scene_count"] == 1
    assert package["prompt_overrides"]["ART_01"]["prompt_extra"] == "mine"
    assert package["shot_statuses"]["SHT_01"] == "BOARDED"
    assert package["animatic"]["video_path"] == "animatic/x.mp4"


def test_handoff_markdown_reports_the_new_sections(analysis: dict[str, Any]) -> None:
    from VISUAL_DEVELOPMENT.handoff import build_handoff, render_handoff_markdown

    style_bible = {
        "style_bible_id": "STYLE_TEST",
        "version": 1,
        "status": "DRAFT",
        "style_identity": "Test",
        "global_rules": {"lighting": "soft", "atmosphere": "calm"},
        "scene_variables": {},
    }
    package = build_handoff(
        analysis,
        style_bible,
        [],
        [],
        {"script_id": "S", "approval_status": "APPROVED", "sha256": "0" * 64},
        breakdown={"scenes": [{"scene_id": "SCN_01", "heading": "H", "elements": []}],
                   "summary": {"scene_count": 1, "element_count": 0, "total_page_eighths": 1.0}},
        prompt_overrides={"ART_01": {"kind": "ART_DIRECTION_CANDIDATE", "prompt_extra": "mine"}},
        shot_statuses={"SHT_01": "BOARDED"},
        animatic={"summary": {"shot_count": 1}, "video_path": "animatic/x.mp4"},
    )
    markdown = render_handoff_markdown(package)
    assert "## Script breakdown" in markdown
    assert "## Prompt overrides" in markdown
    assert "## Shot status" in markdown
    assert "## Animatic" in markdown



# -------------------------------------------------------------------- presets


def test_presets_describe_pipelines_that_work_on_this_machine() -> None:
    """A preset is a coherent set, not a loose bag of numbers."""
    from VISUAL_DEVELOPMENT.presets import PRESETS_BY_ID, preset_settings

    for preset_id, preset in PRESETS_BY_ID.items():
        assert preset["model"]
        assert preset["steps"] >= 1
        assert preset["width"] >= 512
        assert preset["measured"], f"{preset_id} must say what it costs"
        settings = preset_settings(preset_id)
        assert settings["model"] == preset["model"]
        assert settings["preset"] == preset_id


def test_the_sdxl_preset_carries_the_settings_its_pipeline_needs() -> None:
    """Four steps, guidance one and the sgm_uniform scheduler go together."""
    from VISUAL_DEVELOPMENT.presets import preset_settings

    settings = preset_settings("sdxl_lightning_4step")
    assert settings["steps"] == 4
    assert settings["cfg"] == 1.0
    assert settings["scheduler"] == "sgm_uniform"
    assert settings["width"] == 1024
    assert settings["vae"] == "sdxl_vae_fp16_fix.safetensors"
    assert settings["model"] == "sd_xl_base_1.0.safetensors"


def test_a_preset_is_applied_before_the_users_own_numbers() -> None:
    """The preset sets the pipeline, the user may still change one value."""
    from VISUAL_DEVELOPMENT.prompt_overrides import build_override, effective_settings

    override = build_override(
        "SHT_01",
        "SHOT",
        settings_override={"preset": "sdxl_lightning_4step", "steps": 6},
    )
    resolved = effective_settings(
        {"model": "dreamshaper_8.safetensors", "steps": 25, "cfg": 8.0}, override
    )
    settings = resolved["settings"]
    assert settings["model"] == "sd_xl_base_1.0.safetensors"
    assert settings["cfg"] == 1.0
    assert settings["steps"] == 6, "the user's own number wins over the preset"
    assert "preset" in resolved["applied_overrides"]


def test_the_sdxl_workflow_is_a_valid_graph() -> None:
    """Every node reference points at a node that exists."""
    from VISUAL_DEVELOPMENT.workflows import (
        resolve_prompt_nodes,
        txt2img_sdxl_lightning_canny_workflow,
        txt2img_sdxl_lightning_workflow,
    )

    workflow = txt2img_sdxl_lightning_workflow(positive="a throne room")
    for node_id, node in workflow.items():
        for value in node["inputs"].values():
            if isinstance(value, list) and len(value) == 2 and isinstance(value[0], str):
                assert value[0] in workflow, f"{node_id} references missing node {value[0]}"
    nodes = resolve_prompt_nodes(workflow)
    assert nodes["positive"] is not None
    assert nodes["negative"] is not None
    assert nodes["latent"] is not None
    assert workflow["7"]["class_type"] == "VAELoader"
    assert workflow["7"]["inputs"]["vae_name"] == "sdxl_vae_fp16_fix.safetensors"

    canny = txt2img_sdxl_lightning_canny_workflow(
        positive="a throne room", control_image="layout.png"
    )
    assert canny["13"]["class_type"] == "ControlNetApplyAdvanced"
    assert canny["6"]["inputs"]["positive"] == ["13", 0]


def test_generation_uses_the_sdxl_template_when_the_preset_asks_for_it(
    store: ProjectStore, mock_comfy: str
) -> None:
    """The submitted graph must be the SDXL one, with the fixed VAE."""
    from VISUAL_DEVELOPMENT.generation import generate_image
    from VISUAL_DEVELOPMENT.presets import preset_settings

    client = ComfyUIClient(mock_comfy)
    result = generate_image(
        client,
        store,
        artifact_type="STORYBOARD",
        relative_dir="storyboard/SHT_SDXL",
        prompt="a throne room",
        negative_prompt="text",
        settings=preset_settings("sdxl_lightning_4step"),
        workflow_id="txt2img_v1",
        shot_id="SHT_SDXL",
    )
    assert result["status"] == "PASS"
    submitted = _MockComfyHandler.submitted[-1]
    classes = {node.get("class_type") for node in submitted.values()}
    assert "VAELoader" in classes
    vae = next(
        node for node in submitted.values() if node.get("class_type") == "VAELoader"
    )
    assert vae["inputs"]["vae_name"] == "sdxl_vae_fp16_fix.safetensors"
    sampler = next(
        node for node in submitted.values() if node.get("class_type") == "KSampler"
    )
    assert sampler["inputs"]["steps"] == 4
    assert sampler["inputs"]["cfg"] == 1.0
    assert sampler["inputs"]["scheduler"] == "sgm_uniform"

