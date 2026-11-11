"""Script breakdown: every scene reduced to the elements a department needs.

A studio does not go from a screenplay to boards. It breaks the script down
scene by scene, tagging each element into a standard category so the art,
costume, sound and effects departments know what to prepare. That breakdown is
the document the rest of pre-production is planned from.

This module derives the breakdown from the script analysis that already
exists, and it derives **only what the script states**. Anything the script
does not say is left as an empty category for a human to tag, and is never
invented. Every detected element keeps the source span it came from, so a
reviewer can check it against the script in one click.

The taxonomy follows the convention used by script-breakdown software:

    cast, extras, props, set_dressing, costume, makeup, vehicle, stunt,
    vfx, livestock, sound, music, special_equipment

with two additions that animation pre-production needs and live-action
breakdown does not: ``location``, because an environment reference has to be
built, and the counts that tell the art department what to prioritise.
"""

from __future__ import annotations

import re
from typing import Any

from .common import new_id, utc_now

# The categories, the department that owns them, and the conventional hue the
# category is marked with in a breakdown sheet.
TAXONOMY: list[dict[str, str]] = [
    {"category": "cast", "department": "animation", "color": "#4a7fb5", "label": "Cast / Characters"},
    {"category": "extras", "department": "animation", "color": "#6f9ec4", "label": "Extras / Crowd"},
    {"category": "location", "department": "art", "color": "#8a6f4a", "label": "Location / Environment"},
    {"category": "props", "department": "art", "color": "#b08a3e", "label": "Props"},
    {"category": "set_dressing", "department": "art", "color": "#a3762f", "label": "Set Dressing"},
    {"category": "costume", "department": "costume", "color": "#9b4f9b", "label": "Costume"},
    {"category": "makeup", "department": "costume", "color": "#c26ba3", "label": "Makeup / Hair"},
    {"category": "vehicle", "department": "art", "color": "#7d6b4f", "label": "Vehicles"},
    {"category": "stunt", "department": "action", "color": "#b5453f", "label": "Stunts"},
    {"category": "vfx", "department": "effects", "color": "#3f9e8f", "label": "VFX / Graphics"},
    {"category": "livestock", "department": "action", "color": "#6f8f45", "label": "Animals / Livestock"},
    {"category": "sound", "department": "sound", "color": "#4f8fb5", "label": "Sound / SFX"},
    {"category": "music", "department": "sound", "color": "#7f7fb5", "label": "Music"},
    {"category": "special_equipment", "department": "camera", "color": "#7f7f7f", "label": "Special Equipment"},
]

CATEGORIES: list[str] = [entry["category"] for entry in TAXONOMY]
CATEGORY_COLORS: dict[str, str] = {entry["category"]: entry["color"] for entry in TAXONOMY}
CATEGORY_DEPARTMENTS: dict[str, str] = {
    entry["category"]: entry["department"] for entry in TAXONOMY
}

# A named role that is a crowd rather than a character. The analysis reports
# whatever the script names, so this is a name-shape rule and is recorded as
# an inference rather than a fact.
CROWD_PATTERN = re.compile(
    r"^(crowd|extras?|people|throng|audience|citizens?|townsfolk|passers[- ]?by|bystanders?)\b",
    re.IGNORECASE,
)

# A screenplay page holds roughly this much action text. It is an estimate and
# it is labelled as one: the number drives planning, not truth.
CHARS_PER_PAGE = 3000
EIGHTHS_PER_PAGE = 8


def _category_of(name: str) -> str:
    return "extras" if CROWD_PATTERN.match(name.strip()) else "cast"


def _count_occurrences(text: str, term: str) -> int:
    """Count how often a term appears in a scene body, word-boundary aware."""
    if not text:
        return 0
    pattern = re.compile(rf"\b{re.escape(term)}\w*\b", re.IGNORECASE)
    return len(pattern.findall(text))


def _character_index(analysis: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["name"]: entry for entry in analysis.get("characters", [])}


def _scene_elements(
    scene: dict[str, Any],
    characters: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extract every element a scene states, and nothing else."""
    elements: list[dict[str, Any]] = []
    body = scene.get("action", "") or ""

    # A character can speak in a scene without ever appearing in it. The
    # analyzer records who is on screen per shot, so the difference is known.
    visible: set[str] = set()
    for shot in scene.get("shots", []):
        visible.update(shot.get("characters", []) or [])

    for name in scene.get("characters", []):
        entry = characters.get(name, {})
        on_screen = name in visible
        elements.append(
            {
                "category": _category_of(name),
                "name": name,
                "quantity": 1,
                "detail": (
                    entry.get("description", "")
                    if on_screen
                    else f"{entry.get('description', '')} Speaks in this scene but is not shown.".strip()
                ),
                "status": "NEEDS_REFERENCE" if on_screen else "DETECTED",
                "source_span": (entry.get("source_spans") or [None])[0],
                "source": "SCRIPT",
            }
        )

    for prop in scene.get("props", []):
        elements.append(
            {
                "category": "props",
                "name": prop,
                "quantity": max(1, _count_occurrences(body, prop)),
                "detail": "",
                "status": "NEEDS_REFERENCE",
                "source_span": None,
                "source": "SCRIPT",
            }
        )

    location = scene.get("location", "")
    if location:
        # A screenplay heading states the location. The narrated format has no
        # heading, so its location is a working label the analyzer derived from
        # the visual direction. It is recorded as inferred, not as a fact.
        inferred = scene.get("int_ext", "") == "NARRATED"
        elements.append(
            {
                "category": "location",
                "name": location,
                "quantity": 1,
                "detail": (
                    "Working label from the visual direction; the script does not "
                    "name a location."
                    if inferred
                    else f"{scene.get('int_ext', '')} {scene.get('time', '')}".strip()
                ),
                "status": "NEEDS_REFERENCE",
                "source_span": (scene.get("source_spans") or [None])[0],
                "source": "INFERRED" if inferred else "SCRIPT",
            }
        )

    # Sound and music are explicit facts in the narrated format, written as
    # "Sound: ..." and "Music: ...". They are taken verbatim.
    for fact in scene.get("explicit_facts", []):
        match = re.match(r"^(Sound|Music)\s*:\s*(.+)$", fact, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            continue
        category = "sound" if match.group(1).lower() == "sound" else "music"
        elements.append(
            {
                "category": category,
                "name": match.group(2).strip()[:120],
                "quantity": 1,
                "detail": fact,
                "status": "DETECTED",
                "source_span": None,
                "source": "SCRIPT",
            }
        )

    return elements


def _page_eighths(scene: dict[str, Any]) -> float:
    """Estimate the length of a scene in eighths of a script page."""
    body = scene.get("action", "") or ""
    return round(len(body) / CHARS_PER_PAGE * EIGHTHS_PER_PAGE, 2)


def build_breakdown(
    analysis: dict[str, Any],
    project_id: str,
) -> dict[str, Any]:
    """Build the script breakdown for a parsed script."""
    characters = _character_index(analysis)
    scenes: list[dict[str, Any]] = []

    for sequence in analysis.get("sequences", []):
        for scene in sequence.get("scenes", []):
            elements = _scene_elements(scene, characters)
            tagged = {element["category"] for element in elements}
            scenes.append(
                {
                    "scene_id": scene["scene_id"],
                    "sequence_id": sequence.get("sequence_id", ""),
                    "heading": scene.get("heading", ""),
                    "int_ext": scene.get("int_ext", ""),
                    "location": scene.get("location", ""),
                    "time": scene.get("time", ""),
                    "page_eighths": _page_eighths(scene),
                    "shot_count": len(scene.get("shots", [])),
                    "elements": elements,
                    # Categories the script does not mention. They stay visible
                    # so a human can tag them; they are not silently dropped.
                    "untagged_categories": [
                        category for category in CATEGORIES if category not in tagged
                    ],
                    "source_spans": scene.get("source_spans", []),
                }
            )

    all_elements = [element for scene in scenes for element in scene["elements"]]
    by_department: dict[str, list[dict[str, Any]]] = {}
    for element in all_elements:
        department = CATEGORY_DEPARTMENTS.get(element["category"], "other")
        by_department.setdefault(department, []).append(element)

    return {
        "schema_version": "1.0.0",
        "breakdown_id": new_id("BRK"),
        "project_id": project_id,
        "analysis_id": analysis.get("analysis_id", ""),
        "source_script_sha256": analysis.get("source_script_sha256", ""),
        "source_format": analysis.get("source_format", ""),
        "created_at": utc_now(),
        "taxonomy": TAXONOMY,
        "scenes": scenes,
        "summary": {
            "scene_count": len(scenes),
            "element_count": len(all_elements),
            "total_page_eighths": round(sum(scene["page_eighths"] for scene in scenes), 2),
            "by_category": {
                category: sum(
                    1 for element in all_elements if element["category"] == category
                )
                for category in CATEGORIES
            },
            "by_department": {
                department: len(elements) for department, elements in sorted(by_department.items())
            },
            "needs_reference": sorted(
                {
                    element["name"]
                    for element in all_elements
                    if element["status"] == "NEEDS_REFERENCE"
                }
            ),
        },
        "open_questions": analysis.get("open_questions", []),
    }
