"""The production spine: one ordered pipeline and one status vocabulary.

The module has two stores today. The screenplay lives in the Animation Forge
database under ``story_artifacts``, with approval gates. The visual artifacts
live in a project directory on disk. Nothing needs to move for one view to
span both: the project manifest already records which script a project came
from, including the approval status and the source hash.

This module is that vocabulary. It defines the order the work happens in, the
status a shot may hold, and how a status is derived from what is on disk. It
does not read the database and it does not write anything.

The stage order follows studio practice rather than the order the tools
happened to be built in:

    Script -> Breakdown -> Visual Direction -> Boards -> Previz -> Continuity -> Handoff

A studio does not jump from a screenplay to boards. It breaks the script down
per scene into tagged elements, because that breakdown is what the art
department works from. The breakdown therefore sits between the script and the
visuals, and it is a stage of the same spine rather than a side document.
"""

from __future__ import annotations

from typing import Any

# --------------------------------------------------------------------- stages

STAGES: list[dict[str, str]] = [
    {
        "stage_id": "SCRIPT",
        "label": "Script",
        "studio_name": "Screenplay",
        "owner": "script_pipeline",
        "description": "The written script, with its approval state.",
    },
    {
        "stage_id": "BREAKDOWN",
        "label": "Breakdown",
        "studio_name": "Script Breakdown",
        "owner": "visual_development",
        "description": "Every scene broken into tagged elements for the departments.",
    },
    {
        "stage_id": "VISUAL_DIRECTION",
        "label": "Visual Direction",
        "studio_name": "Art Direction",
        "owner": "visual_development",
        "description": "Style candidates, one human selection, one versioned Style Bible.",
    },
    {
        "stage_id": "BOARDS",
        "label": "Boards",
        "studio_name": "Storyboard",
        "owner": "visual_development",
        "description": "One frame per shot, in shot order, with its own prompt.",
    },
    {
        "stage_id": "PREVIZ",
        "label": "Previz",
        "studio_name": "Animatic / Layout",
        "owner": "visual_development",
        "description": "Blocking layouts and the timed cut of the boards.",
    },
    {
        "stage_id": "CONTINUITY",
        "label": "Continuity",
        "studio_name": "Continuity Check",
        "owner": "visual_development",
        "description": "Deterministic checks across the shots that were produced.",
    },
    {
        "stage_id": "HANDOFF",
        "label": "Handoff",
        "studio_name": "Package / Conform",
        "owner": "visual_development",
        "description": "The package the engine team receives.",
    },
]

STAGE_IDS: list[str] = [stage["stage_id"] for stage in STAGES]

# The order the project manifest stage advances in. A stage never goes
# backwards: re-running an earlier command must not un-finish a later one.
PROJECT_STAGE_ORDER: list[str] = [
    "SOURCE_IMPORTED",
    "ANALYZED",
    "BREAKDOWN_COMPLETE",
    "ART_DIRECTION_READY",
    "ART_DIRECTION_GENERATED",
    "DIRECTION_SELECTED",
    "STYLE_BIBLE_CREATED",
    "STORYBOARD_GENERATED",
    "BLOCKING_GENERATED",
    "CONTINUITY_CHECKED",
    "HANDOFF_EXPORTED",
]


def stage_rank(stage: str) -> int:
    """Where a project stage sits in the order. Unknown stages sort first."""
    try:
        return PROJECT_STAGE_ORDER.index(stage)
    except ValueError:
        return -1


def stage(stage_id: str) -> dict[str, str] | None:
    for entry in STAGES:
        if entry["stage_id"] == stage_id:
            return entry
    return None


# -------------------------------------------------------------------- statuses

# The status a shot holds, in the order the work happens. This is deliberately
# the order a board artist, a layout artist and a supervisor would recognise.
SHOT_STATUSES: list[str] = ["NOT_STARTED", "BOARDED", "PREVIZ", "APPROVED"]
BLOCKED = "BLOCKED"

# Every status a shot or an element may report.
ALL_STATUSES: list[str] = SHOT_STATUSES + [BLOCKED]

# The status of an element in a breakdown. A detected element is not the same
# as a confirmed one, and the difference matters to an art department.
ELEMENT_STATUSES: list[str] = ["DETECTED", "NEEDS_REFERENCE", "CONFIRMED", "NOT_APPLICABLE"]


def _generation_index(store: Any) -> dict[tuple[str, str], dict[str, Any]]:
    """Index every generation manifest on disk by artifact type and shot id."""
    from .cli import _collect_generations

    index: dict[tuple[str, str], dict[str, Any]] = {}
    for generation in _collect_generations(store):
        key = (generation.get("artifact_type", ""), generation.get("shot_id", ""))
        index[key] = generation
    return index


def derive_shot_status(store: Any, shot_id: str) -> str:
    """Derive the status of one shot from the artifacts and events on disk.

    The order matters: an approval wins over everything, an explicit block
    wins over an approval only if it is newer, and a shot with no boards has
    not started.
    """
    events = [event for event in store.events() if event.get("target_id") == shot_id]
    approved = False
    blocked = False
    for event in events:
        action = event.get("action")
        if action == "APPROVE":
            approved = True
        elif action == "BLOCK":
            blocked = True

    generations = _generation_index(store)
    boarded = ("STORYBOARD", shot_id) in generations
    previz = ("BLOCKING", shot_id) in generations

    if blocked:
        return BLOCKED
    if approved and boarded:
        return "APPROVED"
    if previz:
        return "PREVIZ"
    if boarded:
        return "BOARDED"
    return "NOT_STARTED"


def shot_status_rollup(statuses: list[str]) -> dict[str, int]:
    """Count shots per status, always reporting every status."""
    counts = {status: 0 for status in ALL_STATUSES}
    for status in statuses:
        if status in counts:
            counts[status] += 1
    return counts


def production_link(store: Any) -> dict[str, Any]:
    """Describe how this project connects to the script it came from.

    The link is already recorded in the project manifest. Nothing is resolved
    and nothing is fetched: this only reports what the manifest says, so the
    user can see whether the script behind the visuals is approved.
    """
    project = store.read("project.json")
    source = project.get("source_script", {})
    return {
        "project_id": project.get("project_id", ""),
        "project_status": project.get("status", ""),
        "stage": project.get("stage", ""),
        "script_id": source.get("script_id", ""),
        "project_ref": source.get("project_id", ""),
        "episode_id": source.get("episode_id"),
        "version": source.get("version"),
        "approval_status": source.get("approval_status", "UNKNOWN"),
        "source_type": source.get("source_type", "UNKNOWN"),
        "source_sha256": source.get("sha256", ""),
    }


def pipeline_status(store: Any) -> dict[str, Any]:
    """The whole spine for one project: stages, statuses and the script link."""
    from .cli import _analysis, _candidate_set, _latest, _style_bible

    link = production_link(store)
    analysis = _analysis(store) if _latest(store, "analysis", "analysis") else {}
    candidates = _candidate_set(store) if _latest(store, "art_direction", "candidates") else {}
    style_bible = _style_bible(store) if _latest(store, "style_bibles", "style_bible") else {}

    generations = _generation_index(store)
    shot_ids: list[str] = []
    for sequence in analysis.get("sequences", []):
        for scene in sequence.get("scenes", []):
            for shot in scene.get("shots", []):
                shot_ids.append(shot["shot_id"])

    statuses = [derive_shot_status(store, shot_id) for shot_id in shot_ids]
    rollup = shot_status_rollup(statuses)

    selected = [
        candidate["candidate_id"]
        for candidate in candidates.get("candidates", [])
        if candidate.get("selected")
    ]

    has_breakdown = _latest(store, "breakdown", "breakdown") is not None
    has_continuity = _latest(store, "reports", "continuity") is not None
    has_handoff = _latest(store, "handoff", "handoff") is not None

    stage_state = {
        "SCRIPT": link["approval_status"] in {"APPROVED", "NOT_APPROVED"}
        and bool(link["script_id"]),
        "BREAKDOWN": has_breakdown,
        "VISUAL_DIRECTION": bool(style_bible),
        "BOARDS": rollup["BOARDED"] + rollup["PREVIZ"] + rollup["APPROVED"] > 0,
        "PREVIZ": rollup["PREVIZ"] + rollup["APPROVED"] > 0,
        "CONTINUITY": has_continuity,
        "HANDOFF": has_handoff,
    }

    return {
        "link": link,
        "stages": [
            {
                **entry,
                "complete": stage_state.get(entry["stage_id"], False),
            }
            for entry in STAGES
        ],
        "shots": {
            "total": len(shot_ids),
            "statuses": rollup,
        },
        "art_direction": {
            "candidate_count": len(candidates.get("candidates", [])),
            "selected": selected,
            "style_identity": style_bible.get("style_identity", ""),
            "style_bible_version": style_bible.get("version"),
        },
        "generations": {
            "total": len(generations),
            "art_direction": sum(1 for key in generations if key[0] == "ART_DIRECTION"),
            "storyboard": sum(1 for key in generations if key[0] == "STORYBOARD"),
            "blocking": sum(1 for key in generations if key[0] == "BLOCKING"),
        },
    }
