"""Narration-only word counting and transparent SCRIPT_ESTIMATE arithmetic."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)*")
NARRATION_TAG_RE = re.compile(r"^\s*(?:\*\*)?\[NARRATION\](?:\*\*)?\s*$", re.MULTILINE | re.IGNORECASE)
BLOCK_END_RE = re.compile(r"^\s*(?:\*\*)?\[[A-Z][A-Z_ ]*\](?:\*\*)?|#{1,6}\s|---\s*$", re.MULTILINE)


def extract_narration_blocks(markdown: str) -> list[str]:
    """Read text after [NARRATION] until the next direction tag/heading/rule."""
    tags = list(NARRATION_TAG_RE.finditer(markdown))
    blocks: list[str] = []
    for tag in tags:
        end = len(markdown)
        match = BLOCK_END_RE.search(markdown, tag.end())
        if match:
            end = match.start()
        blocks.append(markdown[tag.end():end].strip())
    return blocks


def count_narration(markdown: str) -> dict[str, Any]:
    blocks = extract_narration_blocks(markdown)
    words = sum(len(WORD_RE.findall(block)) for block in blocks)
    return {"narration_word_count": words, "block_count": len(blocks), "method": "NARRATION_TAGS_ONLY"}


def estimate_runtime(word_count: int, rate_wpm: float, hold_min_sec: float, hold_max_sec: float) -> dict[str, Any]:
    if word_count < 0 or rate_wpm <= 0 or hold_min_sec < 0 or hold_max_sec < hold_min_sec:
        raise ValueError("Word count/rate/hold range is invalid.")
    spoken_seconds = word_count / rate_wpm * 60
    total_min = spoken_seconds + hold_min_sec
    total_max = spoken_seconds + hold_max_sec
    return {
        "status": "SCRIPT_ESTIMATE",
        "word_count": word_count,
        "rate_wpm": rate_wpm,
        "spoken_seconds_estimate": round(spoken_seconds, 2),
        "hold_min_sec": hold_min_sec,
        "hold_max_sec": hold_max_sec,
        "total_min_sec": round(total_min, 2),
        "total_max_sec": round(total_max, 2),
        "method": "narration_words / rate_wpm * 60 + separately_planned_holds",
        "measured_runtime_available": False,
    }


def count_file(path: Path) -> dict[str, Any]:
    return count_narration(path.read_text(encoding="utf-8"))
