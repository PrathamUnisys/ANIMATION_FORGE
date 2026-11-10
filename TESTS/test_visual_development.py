from __future__ import annotations

import json
import shutil
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

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
                    "CLIPTextEncode": {
                        "input": {"required": {"text": ("STRING",), "clip": ("CLIP",)}}
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
            self._json({"prompt_id": "mock-prompt", "number": 1, "node_errors": {}})
        else:
            self._json({"error": "not found"}, 404)


@pytest.fixture
def mock_comfy():
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


def _unterminated_js_string(script: str) -> str | None:
    """Return the quote character of an unterminated JS string, or None.

    A single unbalanced quote in the served page silently blanks the whole
    review UI, because the browser refuses to run the script block at all.
    """
    index = 0
    length = len(script)
    while index < length:
        char = script[index]
        if char == "/" and index + 1 < length and script[index + 1] == "/":
            while index < length and script[index] != "\n":
                index += 1
            continue
        if char in "\"'`":
            quote = char
            index += 1
            while index < length:
                if script[index] == "\\":
                    index += 2
                    continue
                if script[index] == quote:
                    break
                index += 1
            if index >= length:
                return quote
        index += 1
    return None


def test_review_page_script_is_syntactically_balanced() -> None:
    """Regression guard: the review page must never serve a blank shell."""
    from VISUAL_DEVELOPMENT.review_server import PAGE_TEMPLATE

    state = {
        "project": {
            "project_id": "P",
            "source_script": {"script_id": "S", "approval_status": "APPROVED"},
        },
        "episode": {},
        "open_questions": [],
        "candidates": {"comparison_scene_id": "SCN_01", "candidates": []},
        "style_bible": {},
        "shots": [],
        "events": [],
        "comfyui": {},
        "continuity": {},
    }
    html = PAGE_TEMPLATE.replace("__STATE__", json.dumps(state)).replace("__PROJECT__", "P")
    assert "<script>" in html and "</script>" in html
    script = html.split("<script>", 1)[1].split("</script>", 1)[0]
    unterminated = _unterminated_js_string(script)
    assert unterminated is None, f"unterminated {unterminated!r} quote in the review page script"
    assert "onclick=" not in script, "use data attributes and a delegated handler, not inline onclick"
    assert "data-act=" in script
