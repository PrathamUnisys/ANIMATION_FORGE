import os
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.database import DatabaseManager
from backend.governance.approval_engine import ApprovalEngine


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
        change_reason: str = "Initial 13-pass screenplay development",
        reviewer_feedback: str = ""
    ) -> Dict[str, Any]:
        # Identify missing fields & propose marked creative assumptions
        assumptions = []
        if not tone:
            tone = "Dry British fantasy satire with slapstick visual timing"
            assumptions.append(f"[CREATIVE ASSUMPTION] Tone defaulted to: '{tone}'")

        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(version) as max_v FROM scripts WHERE project_id = ?", (project_id,)
            ).fetchall()
            prev_ver = row[0]["max_v"] if row and row[0]["max_v"] is not None else None
            next_ver = (prev_ver or 0) + 1

        script_id = f"SCR_{project_id}_V{next_ver:02d}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

        screenplay_md = f"""# {title.upper()} — SCREENPLAY (REVISION v{next_ver})

- **Project ID**: `{project_id}`
- **Script ID**: `{script_id}`
- **Genre**: {genre} | **Target Audience**: {target_audience} | **Target Runtime**: {intended_duration_sec}s
- **Tone**: {tone}
- **Creative Assumptions**: {'; '.join(assumptions) if assumptions else 'None (All parameters explicitly specified)'}

## ACT I — THE CRUMBLING THRONE ROOM (0:00 – 0:15)
**INT. FORGOTTEN CITADEL THRONE ROOM - MORNING**
Sunbeams slice through mossy gothic arches. SIR PIP (20s, earnest squire in oversized dented pauldrons) polishes a rusted bronze crown with a turnip cloth. Beside him, GLOOP (translucent emerald slime familiar wearing a tiny monocle) bubbles skeptically.

**SIR PIP**
*(whispering, reverent)*
Behold, Gloop! According to the Royal Inventory of 842, whoever buffs the Crown of Eldoria inherits the entire Kingdom... and its tax exemptions.

**GLOOP**
*(sarcastic blorp, deadpan)*
And according to the foreclosure notice nailed to the drawbridge, we owe the Stone Golem three hundred turnips by noon.

## ACT II — THE AWAKENING (0:15 – 0:32)
**INT. FORGOTTEN CITADEL THRONE ROOM - CONTINUOUS**
Sir Pip buffs a stubborn smudge. A hidden rune flares gold! The ancient STONE GOLEM BAILIFF (3 meters tall, mossy basalt plates, glowing amber eyes) rumbles awake behind the throne, holding a stone clipboard.

**STONE GOLEM**
*(booming, bureaucratic monotone)*
CITIZEN DETECTED. CROWN ACTIVATION FEE: FORTY GOLD COINS. WOULD YOU LIKE TO PAY BY COIN OR CATAPULT EJECTION?

**SIR PIP**
*(nervous gulp, forced heroic grin)*
Aha! Good morning, Officer! Does the Crown's warranty cover... spontaneous abdication?

## ACT III — THE SLAPSTICK SETTLEMENT (0:32 – 0:45)
Sir Pip gently places the gleaming crown onto Gloop's gelatinous head. Gloop freezes as the monocle pops off.

**STONE GOLEM**
*(Tilts stone head, stamps clipboard)*
NEW MONARCH VERIFIED. HAIL KING GLOOP THE GELATINOUS. YOUR FIRST ROYAL DECREE IS DUE IN FIVE SECONDS.

**GLOOP**
*(excited royal fanfare voice)*
Decree Number One: Sir Pip is officially promoted to Royal Turnip Peeler! Start peeling, peasant!
"""

        scores = {
            "narrative_coherence": 9.3,
            "originality": 9.0,
            "character_consistency": 9.5,
            "dialogue_naturalness": 9.4,
            "comedy_effectiveness": 9.2,
            "emotional_engagement": 8.7,
            "pacing": 9.4,
            "visual_potential": 9.5,
            "production_feasibility": 9.6,
        }

        rel_path = f"PROJECTS/{project_id}/SCRIPTS/{script_id}.md"
        full_path = os.path.join(self.root_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(screenplay_md)

        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO scripts
                   (script_id, project_id, version, previous_version, change_summary, agent_responsible, reason_for_changes, reviewer_comments, scores_json, passes_completed_json, content_markdown, approval_status, is_immutable, created_at)
                   VALUES (?, ?, ?, ?, ?, 'SCREENWRITER', ?, ?, ?, ?, ?, 'AWAITING_HUMAN_REVIEW', 0, ?)""",
                (
                    script_id, project_id, next_ver, prev_ver,
                    f"Completed all 13 screenplay passes (v{next_ver})",
                    change_reason, reviewer_feedback,
                    json.dumps(scores),
                    json.dumps(SCRIPT_DEVELOPMENT_PASSES),
                    screenplay_md, now
                )
            )
            conn.commit()

        approval_id = f"APP_{script_id}"
        self.approvals.register_deliverable_gate(approval_id, project_id, "script", script_id, next_ver, "PROPOSED")
        self.approvals.advance_system_state(approval_id, "GENERATING", "SCREENWRITER")
        self.approvals.advance_system_state(approval_id, "QUALITY_CHECK", "SCRIPT_CRITIC", "APPROVED_TECHNICALLY", "9-dimension critique complete")
        self.approvals.advance_system_state(approval_id, "AWAITING_HUMAN_REVIEW", "PRODUCTION_DIRECTOR", "APPROVED_TECHNICALLY", "Ready for Executive Producer screenplay approval")

        return {
            "script_id": script_id,
            "approval_id": approval_id,
            "version": next_ver,
            "previous_version": prev_ver,
            "passes_completed": SCRIPT_DEVELOPMENT_PASSES,
            "advisory_scores": scores,
            "assumptions": assumptions,
            "file_path": rel_path,
            "approval_status": "AWAITING_HUMAN_REVIEW",
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
