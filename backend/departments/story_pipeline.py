import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import DatabaseManager
from backend.governance.approval_engine import ApprovalEngine
from backend.filesystem_security import is_safe_path_component


SCRIPT_DEVELOPMENT_PASSES = [
    "1_CONCEPT_ANALYSIS",
    "2_PREMISE_REFINEMENT",
    "3_NARRATIVE_STRUCTURE",
    "4_SCENE_DEVELOPMENT",
    "5_CHARACTER_MOTIVATION_REVIEW",
    "6_DIALOGUE_REFINEMENT",
    "7_COMEDY_OPTIMIZATION",
    "8_EMOTIONAL_STORYTELLING",
    "9_PACING_OPTIMIZATION",
    "10_VISUAL_STORYTELLING_ENHANCEMENT",
    "11_CONTINUITY_REVIEW",
    "12_PRODUCTION_FEASIBILITY_REVIEW",
    "13_FINAL_SCREENPLAY_FORMATTING",
]

SCORING_DIMENSIONS = [
    "narrative_coherence",
    "originality",
    "character_consistency",
    "dialogue_naturalness",
    "comedy_effectiveness",
    "emotional_engagement",
    "pacing",
    "visual_potential",
    "production_feasibility",
]


class ImmutableScriptError(Exception):
    """Raised when attempting to overwrite or mutate an approved screenplay revision."""


class StoryAndScreenplayPipeline:
    def __init__(self, root_dir: str, db: DatabaseManager, approvals: ApprovalEngine):
        self.root_dir = root_dir
        self.db = db
        self.approvals = approvals

    def develop_screenplay_revision(
        self,
        project_id: str,
        title: str,
        premise: str,
        genre: str,
        target_audience: str,
        intended_duration_sec: int,
        tone: Optional[str] = None,
        change_reason: str = "Initial screenplay scaffold (automated generation unavailable)",
        reviewer_feedback: str = ""
    ) -> Dict[str, Any]:
        """Create a premise-specific scaffold without claiming AI generation or QC.

        The application currently has no live LLM screenplay-generation path.
        This method creates a human-editable scaffold, not a generated screenplay.
        """
        if not is_safe_path_component(project_id):
            raise ValueError("Project ID must be a single safe path component.")
        if not title or not title.strip():
            raise ValueError("A non-empty screenplay title is required.")
        if not premise or not premise.strip():
            raise ValueError("A non-empty story premise is required.")
        if intended_duration_sec < 1:
            raise ValueError("Target duration must be at least one second.")

        tone_text = tone.strip() if tone and tone.strip() else "Not specified by the user"
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(version) as max_v FROM scripts WHERE project_id = ?", (project_id,)
            ).fetchone()
            prev_ver = row["max_v"] if row and row["max_v"] is not None else None
            next_ver = (prev_ver or 0) + 1

        script_id = f"SCR_{project_id}_V{next_ver:02d}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        duration_minutes = intended_duration_sec // 60
        duration_seconds = intended_duration_sec % 60
        runtime_label = f"{duration_minutes}:{duration_seconds:02d}" if duration_minutes else f"{duration_seconds}s"
        passes_checklist = "\n".join(
            f"- [ ] {index + 1}. {pass_name}"
            for index, pass_name in enumerate(SCRIPT_DEVELOPMENT_PASSES)
        )

        screenplay_md = f"""# {title.strip()} — SCREENPLAY DEVELOPMENT SCAFFOLD (v{next_ver})

- **Project ID:** {project_id}
- **Script ID:** {script_id}
- **Status:** SCAFFOLD ONLY — NOT MODEL-GENERATED
- **Genre:** {genre}
- **Target audience:** {target_audience}
- **Target runtime:** {runtime_label} ({intended_duration_sec} seconds)
- **Tone:** {tone_text}

> This file is a human-editable development scaffold. No live LLM screenplay-generation request or automated critique has been executed. No creative scores or technical QC result are implied.

## User-provided premise

{premise.strip()}

## Story decisions to complete

- **Protagonist and immediate objective:** [To be developed]
- **Central conflict / opposition:** [To be developed]
- **Stakes:** [To be developed]
- **Central story question:** [To be developed]
- **Ending / resolution:** [To be developed]
- **Audience promise:** [To be developed and checked against the actual story]
- **Character and world constraints:** [Load from approved project canon before drafting]

## Proposed dramatic structure

### ACT I — SETUP

- Establish the protagonist, setting and immediate situation.
- Introduce the incident or decision that starts the story.
- State the dramatic question and stakes.
- **Scenes:** [Not yet drafted]

### ACT II — DEVELOPMENT

- Develop attempts, obstacles and consequences.
- Introduce evidence or reversals that follow from the premise.
- Track character decisions and changes in understanding.
- **Scenes:** [Not yet drafted]

### ACT III — CLIMAX AND RESOLUTION

- Bring the central conflict to a consequential choice or confrontation.
- Resolve the story question using information established earlier.
- Show the emotional consequence and any intentional unresolved thread.
- **Scenes:** [Not yet drafted]

## Screenplay pages

No scene prose has been generated. Draft each scene only after the protagonist, objective, conflict, story rules and ending have been agreed.

    INT./EXT. LOCATION – TIME

    ACTION:
    [Observable, filmable action.]

    DIALOGUE:
    CHARACTER: [Dialogue.]

    VISUAL:
    [Story-relevant staging or clue readability.]

    AUDIO:
    [Voice intent, ambience, music, silence or effects.]

## Development checklist

{passes_checklist}

**Completed passes:** 0 of {len(SCRIPT_DEVELOPMENT_PASSES)}.
**Creative scores:** Not assessed.
**Technical QC:** Manual inspection required.
"""
        projects_root = os.path.realpath(os.path.join(self.root_dir, "PROJECTS"))
        requested_project_dir = os.path.join(projects_root, project_id)
        if os.path.islink(requested_project_dir):
            raise ValueError("Project directory cannot be a symbolic link.")
        project_dir = os.path.realpath(requested_project_dir)
        try:
            contained = os.path.commonpath((projects_root, project_dir)) == projects_root
        except ValueError:
            contained = False
        if not contained:
            raise ValueError("Project directory resolves outside the PROJECTS root.")

        rel_path = f"PROJECTS/{project_id}/SCRIPTS/{script_id}.md"
        scripts_dir = os.path.join(project_dir, "SCRIPTS")
        if os.path.islink(scripts_dir):
            raise ValueError("Project SCRIPTS directory cannot be a symbolic link.")
        os.makedirs(scripts_dir, exist_ok=True)
        resolved_scripts_dir = os.path.realpath(scripts_dir)
        try:
            scripts_contained = os.path.commonpath((project_dir, resolved_scripts_dir)) == project_dir
        except ValueError:
            scripts_contained = False
        if not scripts_contained:
            raise ValueError("Project SCRIPTS directory resolves outside the project root.")
        full_path = os.path.join(resolved_scripts_dir, f"{script_id}.md")
        # Exclusive creation prevents a stale DB version counter from overwriting a file.
        with open(full_path, "x", encoding="utf-8") as f:
            f.write(screenplay_md)

        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO scripts
                   (script_id, project_id, version, previous_version, change_summary, agent_responsible, reason_for_changes, reviewer_comments, scores_json, passes_completed_json, content_markdown, approval_status, is_immutable, created_at)
                   VALUES (?, ?, ?, ?, ?, 'SCREENWRITER', ?, ?, ?, ?, ?, 'AWAITING_HUMAN_REVIEW', 0, ?)""",
                (
                    script_id, project_id, next_ver, prev_ver,
                    "Created a premise-specific scaffold; no automated screenplay passes executed",
                    change_reason, reviewer_feedback, json.dumps({}), json.dumps([]),
                    screenplay_md, now
                )
            )
            conn.commit()

        approval_id = f"APP_{script_id}"
        self.approvals.register_deliverable_gate(approval_id, project_id, "script", script_id, next_ver, "PROPOSED")
        self.approvals.advance_system_state(approval_id, "GENERATING", "SCREENWRITER")
        self.approvals.advance_system_state(
            approval_id, "QUALITY_CHECK", "SCRIPT_CRITIC",
            "MANUAL_INSPECTION_REQUIRED",
            "No automated screenplay generation or critique was executed; manual content review is required."
        )
        self.approvals.advance_system_state(
            approval_id, "AWAITING_HUMAN_REVIEW", "PRODUCTION_DIRECTOR",
            "MANUAL_INSPECTION_REQUIRED",
            "Premise-specific scaffold submitted for human review; no automated quality pass is claimed."
        )

        return {
            "script_id": script_id,
            "approval_id": approval_id,
            "version": next_ver,
            "previous_version": prev_ver,
            "passes_completed": [],
            "planned_passes": SCRIPT_DEVELOPMENT_PASSES,
            "advisory_scores": {},
            "assumptions": [],
            "execution_status": "SCAFFOLD_ONLY",
            "warnings": [
                "No live LLM request was made.",
                "No screenplay development passes were executed.",
                "No automated creative scores or technical QC result are available."
            ],
            "file_path": rel_path,
            "approval_status": "AWAITING_HUMAN_REVIEW",
            "technical_qc_outcome": "MANUAL_INSPECTION_REQUIRED"
        }

    def attempt_modify_script_in_place(self, script_id: str, new_text: str) -> None:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT is_immutable, approval_status FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            if row["is_immutable"] == 1 or row["approval_status"] == "APPROVED":
                raise ImmutableScriptError(
                    f"Screenplay '{script_id}' is APPROVED and immutable. Any modifications must create a new revision (v+1)."
                )

    def generate_production_breakdown(self, project_id: str, approved_script_id: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            scr = conn.execute("SELECT * FROM scripts WHERE script_id = ? AND project_id = ?", (approved_script_id, project_id)).fetchone()
            if not scr or scr["approval_status"] != "APPROVED":
                raise PermissionError(f"Cannot break down unapproved script '{approved_script_id}'.")

        scenes_data = [
            {
                "scene_id": "SCN_001",
                "project_id": project_id,
                "title": "The Crumbling Throne Room & Crown Discovery",
                "location_id": "LOC_THRONE_ROOM",
                "characters": ["CHAR_SIR_PIP", "CHAR_GLOOP"],
                "required_assets": ["PROP_RUSTED_CROWN", "PROP_TURNIP_CLOTH", "BG_THRONE_ROOM_2_5D"],
                "duration_sec": 15.0,
                "animation_method": "2.5D",
                "required_shots": ["SHT_001", "SHT_002"],
                "camera_requirements": "Slow 2.5D parallax push-in (35mm -> 50mm equivalent)",
                "audio_dependencies": ["AUD_LINE_001", "AUD_LINE_002"],
                "lighting": "Warm morning god-rays slicing through emerald dust motes",
                "vfx": ["VFX_DUST_MOTES"],
                "production_dependencies": ["CHAR_SIR_PIP", "CHAR_GLOOP", "LOC_THRONE_ROOM"],
                "expected_outputs": ["SCN_001_PASS.mp4"]
            },
            {
                "scene_id": "SCN_002",
                "project_id": project_id,
                "title": "The Awakening & Coronation of King Gloop",
                "location_id": "LOC_THRONE_ROOM",
                "characters": ["CHAR_SIR_PIP", "CHAR_GLOOP", "CHAR_STONE_GOLEM"],
                "required_assets": ["PROP_GLEAMING_CROWN", "PROP_STONE_CLIPBOARD", "BG_THRONE_ROOM_2_5D"],
                "duration_sec": 30.0,
                "animation_method": "HYBRID",
                "required_shots": ["SHT_003", "SHT_004"],
                "camera_requirements": "Low-angle Dutch tilt on Golem reveal; whip-pan to Crown coronation",
                "audio_dependencies": ["AUD_LINE_003", "AUD_LINE_004", "AUD_LINE_005", "AUD_LINE_006"],
                "lighting": "Golden rune glow + amber basalt rim lighting",
                "vfx": ["VFX_RUNE_FLARE", "VFX_CAMERA_SHAKE"],
                "production_dependencies": ["SCN_001", "CHAR_STONE_GOLEM"],
                "expected_outputs": ["SCN_002_PASS.mp4"]
            }
        ]

        with self.db.get_connection() as conn:
            for s in scenes_data:
                conn.execute(
                    """INSERT OR REPLACE INTO scenes
                       (scene_id, project_id, title, location_id, characters_json, required_assets_json, duration_sec, animation_method, required_shots_json, camera_requirements, audio_dependencies_json, lighting, vfx_json, production_dependencies_json, expected_outputs_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        s["scene_id"], project_id, s["title"], s["location_id"],
                        json.dumps(s["characters"]), json.dumps(s["required_assets"]),
                        s["duration_sec"], s["animation_method"], json.dumps(s["required_shots"]),
                        s["camera_requirements"], json.dumps(s["audio_dependencies"]),
                        s["lighting"], json.dumps(s["vfx"]),
                        json.dumps(s["production_dependencies"]), json.dumps(s["expected_outputs"])
                    )
                )
            conn.commit()
        return {"project_id": project_id, "scenes": scenes_data}
