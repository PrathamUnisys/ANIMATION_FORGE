"""The animatic: the boards cut to a timeline, with the voice on it.

A storyboard is a set of stills. An animatic is those stills cut to time with
the words on them, and it is the thing a director actually watches to decide
whether the story works. It is the last cheap moment to change something.

The timeline is derived, never invented:

* the shots come from the analysis, in shot order, with the duration the
  analysis estimated for each one;
* the pictures come from the storyboard generations that exist on disk;
* the words come from the script itself, as dialogue for a screenplay and as
  narration for an explained segment.

Voice synthesis is optional and separate. The timeline always records what
should be said and who says it. Synthesising it needs a voice model, and
whether one is available must never decide whether a timeline can be built.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import wave
from pathlib import Path
from typing import Any

from .common import new_id, utc_now

# The voice model used when one is available. Kokoro runs in its own
# environment, so it is called as a subprocess.
KOKORO_VENV = Path(r"D:\Work\ANIMATION_FORGE\.venv-kokoro-test\Scripts\python.exe")
KOKORO_VOICE = "af_heart"
SAMPLE_RATE = 24000

# A shot is held on screen for at least this long, whatever the analysis said.
MIN_SHOT_SECONDS = 1.0
# A still that is held too long is dead air.
MAX_SHOT_SECONDS = 12.0


def _narration_for_scene(scene: dict[str, Any]) -> str:
    """The narration a scene carries, taken from the script facts."""
    parts = []
    for fact in scene.get("explicit_facts", []):
        text = str(fact)
        if text.lower().startswith("narration:"):
            parts.append(text.split(":", 1)[1].strip())
    return " ".join(parts).strip()


def _dialogue_for_shot(shot: dict[str, Any]) -> str:
    """The line a shot carries, if the shot is a line of dialogue."""
    if shot.get("dialogue"):
        return str(shot["dialogue"]).strip()
    for fact in shot.get("explicit_facts", []):
        text = str(fact)
        if text.lower().startswith("dialogue:"):
            return text.split(":", 1)[1].strip()
    return ""


def build_animatic(
    analysis: dict[str, Any],
    generations: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the animatic timeline for a parsed script.

    ``generations`` is the list of generation manifests, so the timeline can
    point at the picture that was actually produced for each shot.
    """
    boards: dict[str, str] = {}
    for generation in generations:
        if generation.get("artifact_type") != "STORYBOARD":
            continue
        shot_id = generation.get("shot_id", "")
        image_path = generation.get("image_path", "")
        if shot_id and image_path:
            boards[shot_id] = image_path

    entries: list[dict[str, Any]] = []
    voice_lines: list[dict[str, Any]] = []
    clock = 0.0

    for sequence in analysis.get("sequences", []):
        for scene in sequence.get("scenes", []):
            narration = _narration_for_scene(scene)
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", "")
                duration = float(shot.get("estimated_duration_sec") or 0.0)
                if duration <= 0:
                    duration = 2.0
                duration = max(MIN_SHOT_SECONDS, min(MAX_SHOT_SECONDS, duration))

                entry = {
                    "shot_id": shot_id,
                    "sequence_id": sequence.get("sequence_id", ""),
                    "scene_id": scene.get("scene_id", ""),
                    "scene_heading": scene.get("heading", ""),
                    "image_path": boards.get(shot_id, ""),
                    "start_sec": round(clock, 3),
                    "duration_sec": round(duration, 3),
                    "shot_size": shot.get("camera_shot_type", ""),
                    "camera": shot.get("camera_movement", "") or shot.get("camera_angle", ""),
                    "description": shot.get("visual_description", ""),
                    "dialogue": _dialogue_for_shot(shot),
                    "narration": narration if not _dialogue_for_shot(shot) else "",
                    "has_picture": shot_id in boards,
                }
                entries.append(entry)

                spoken = entry["dialogue"] or narration
                if spoken:
                    voice_lines.append(
                        {
                            "line_id": new_id("VOX"),
                            "shot_id": shot_id,
                            "speaker": (
                                entry["dialogue"]
                                and shot.get("characters", ["Narrator"])[0]
                                or "Narrator"
                            ),
                            "kind": "DIALOGUE" if entry["dialogue"] else "NARRATION",
                            "text": spoken,
                            "start_sec": round(clock, 3),
                            "duration_sec": round(duration, 3),
                        }
                    )
                clock += duration

    return {
        "schema_version": "1.0.0",
        "animatic_id": new_id("ANM"),
        "created_at": utc_now(),
        "source_format": analysis.get("source_format", ""),
        "entries": entries,
        "voice_lines": voice_lines,
        "summary": {
            "shot_count": len(entries),
            "picture_count": sum(1 for entry in entries if entry["has_picture"]),
            "voice_line_count": len(voice_lines),
            "total_duration_sec": round(clock, 3),
            "missing_pictures": [
                entry["shot_id"] for entry in entries if not entry["has_picture"]
            ],
        },
    }


# ------------------------------------------------------------------- voice


def synthesize_voice(
    text: str,
    out_path: Path,
    voice: str = KOKORO_VOICE,
    venv_python: Path = KOKORO_VENV,
) -> dict[str, Any]:
    """Synthesise one line of voice, if a voice model is available.

    A missing voice model is not an error for the animatic: the line is
    recorded as silent and the timeline still works.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not venv_python.exists():
        return {"status": "NO_VOICE_MODEL", "path": "", "duration_sec": 0.0}
    code = (
        "from kokoro import KPipeline\n"
        "import soundfile as sf\n"
        f'pipe = KPipeline(lang_code="a")\n'
        f'gen = pipe({text!r}, voice={voice!r})\n'
        "for _, _, audio in gen:\n"
        f"    sf.write({str(out_path)!r}, audio, {SAMPLE_RATE})\n"
        "    break\n"
    )
    result = subprocess.run(
        [str(venv_python), "-c", code],
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0 or not out_path.exists():
        return {
            "status": "VOICE_FAILED",
            "path": "",
            "duration_sec": 0.0,
            "error": (result.stderr or "")[-400:],
        }
    return {
        "status": "PASS",
        "path": str(out_path),
        "duration_sec": _wav_duration(out_path),
        "voice": voice,
    }


def _wav_duration(path: Path) -> float:
    try:
        with wave.open(str(path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate() or SAMPLE_RATE
            return round(frames / float(rate), 3)
    except (OSError, wave.Error):
        return 0.0


def mix_voice_track(
    clips: list[tuple[Path, float]],
    out_path: Path,
    total_seconds: float,
) -> dict[str, Any]:
    """Lay every voice clip on one track at its start time.

    ``clips`` is a list of (path, start_seconds). The result is a single
    silent-then-spoken track, so the video can be muxed with one audio
    stream instead of a filter graph that grows with every line.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    total_frames = int(max(total_seconds, 0.1) * SAMPLE_RATE)
    track = bytearray(total_frames * 2)  # 16 bit mono

    placed = 0
    for path, start in clips:
        if not path.exists():
            continue
        try:
            with wave.open(str(path), "rb") as handle:
                if handle.getnchannels() != 1 or handle.getsampwidth() != 2:
                    continue
                if handle.getframerate() != SAMPLE_RATE:
                    continue
                data = handle.readframes(handle.getnframes())
        except (OSError, wave.Error):
            continue
        offset = int(start * SAMPLE_RATE) * 2
        end = min(offset + len(data), len(track))
        if offset >= len(track):
            continue
        track[offset:end] = data[: end - offset]
        placed += 1

    with wave.open(str(out_path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(bytes(track))
    return {
        "status": "PASS",
        "path": str(out_path),
        "clips_placed": placed,
        "duration_sec": round(total_seconds, 3),
    }


# ------------------------------------------------------------------ render


def render_animatic(
    timeline: dict[str, Any],
    out_path: Path,
    *,
    project_root: Path | None = None,
    audio_path: Path | None = None,
    ffmpeg: str = "ffmpeg",
    fps: int = 24,
    width: int = 768,
) -> dict[str, Any]:
    """Cut the boards to a playable animatic.

    The pictures are cut with the ffmpeg concat demuxer, which holds each
    still for its time in one pass. The voice, when there is one, is a single
    mixed track that is muxed alongside.
    """
    if shutil.which(ffmpeg) is None:
        return {"status": "FFMPEG_MISSING", "path": "", "message": f"{ffmpeg} is not on PATH."}

    entries = [entry for entry in timeline.get("entries", []) if entry.get("image_path")]
    if not entries:
        return {
            "status": "NO_PICTURES",
            "path": "",
            "message": "No board has been generated for this project yet.",
        }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    listing = out_path.with_suffix(".concat.txt")
    lines: list[str] = []
    for entry in entries:
        image = entry["image_path"]
        if project_root is not None:
            image = str((project_root / image).resolve())
        # The concat demuxer needs forward slashes and quotes the path.
        image = image.replace("\\", "/").replace("'", r"'\''")
        lines.append(f"file '{image}'")
        lines.append(f"duration {entry['duration_sec']}")
    # The demuxer ignores the duration of the last entry unless it is repeated.
    if entries:
        last = entries[-1]["image_path"]
        if project_root is not None:
            last = str((project_root / last).resolve())
        last = last.replace("\\", "/").replace("'", r"'\''")
        lines.append(f"file '{last}'")
    listing.write_text("\n".join(lines) + "\n", encoding="utf-8")

    command = [
        ffmpeg,
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(listing),
    ]
    if audio_path is not None and audio_path.exists():
        command += ["-i", str(audio_path)]
    command += [
        "-vf",
        f"scale={width}:-2:flags=lanczos,format=yuv420p",
        "-r",
        str(fps),
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "20",
    ]
    if audio_path is not None and audio_path.exists():
        command += ["-c:a", "aac", "-b:a", "128k", "-shortest"]
    command += [str(out_path)]

    result = subprocess.run(command, capture_output=True, text=True, timeout=1800)
    listing.unlink(missing_ok=True)
    if result.returncode != 0 or not out_path.exists():
        return {
            "status": "RENDER_FAILED",
            "path": "",
            "error": (result.stderr or "")[-800:],
        }
    return {
        "status": "PASS",
        "path": str(out_path),
        "bytes": out_path.stat().st_size,
        "shot_count": len(entries),
        "duration_sec": timeline.get("summary", {}).get("total_duration_sec", 0.0),
    }


def animatic_manifest(timeline: dict[str, Any], video: dict[str, Any]) -> dict[str, Any]:
    """The animatic artifact written next to the other package files."""
    return {
        "schema_version": "1.0.0",
        "animatic_id": timeline.get("animatic_id", ""),
        "created_at": utc_now(),
        "source_format": timeline.get("source_format", ""),
        "summary": timeline.get("summary", {}),
        "entries": timeline.get("entries", []),
        "voice_lines": [
            {key: value for key, value in line.items() if key != "path"}
            for line in timeline.get("voice_lines", [])
        ],
        "video_path": video.get("path", ""),
        "video_status": video.get("status", ""),
    }
