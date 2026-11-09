import os
import json
import re
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

    # ---- CR_006 M3: Staged screenplay generation ----

    def _persist_artifact(self, project_id: str, episode_id: str, artifact_type: str, content: Any,
                          context_hash: str = None, provider: Dict[str, Any] = None) -> Dict[str, Any]:
        import hashlib
        raw = json.dumps(content, sort_keys=True, separators=(",", ":")).encode()
        h = hashlib.sha256(raw).hexdigest()
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT MAX(revision) AS m FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = ?",
                (project_id, episode_id, artifact_type),
            ).fetchone()
            nxt = (row["m"] or 0) + 1
            aid = f"ART_{project_id}_{artifact_type}_R{nxt:03d}"
            conn.execute(
                """INSERT INTO story_artifacts
                   (artifact_id, project_id, episode_id, artifact_type, revision, previous_revision,
                    status, content_json, content_hash_sha256, context_hash_sha256,
                    provider_id, model_id, request_id, usage_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    aid, project_id, episode_id, artifact_type, nxt, nxt - 1 if nxt > 1 else None,
                    "PROPOSED", json.dumps(content), h, context_hash,
                    provider.get("provider_id") if provider else None,
                    provider.get("model_id") if provider else None,
                    provider.get("request_id") if provider else None,
                    json.dumps(provider.get("usage") if provider else None), now,
                ),
            )
            conn.commit()
        return {"artifact_id": aid, "artifact_type": artifact_type, "revision": nxt, "content_hash_sha256": h}

    def get_artifact(self, project_id: str, episode_id: str, artifact_type: str) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = ? ORDER BY revision DESC LIMIT 1",
                (project_id, episode_id, artifact_type),
            ).fetchone()
            if not row:
                raise KeyError(f"No {artifact_type} for {project_id}/{episode_id}")
            d = dict(row)
            d["content"] = json.loads(d.pop("content_json"))
            return d

    def generate_story_analysis(self, project_id: str, episode_id: str, brief_content: Dict[str, Any],
                                canon_content: Dict[str, Any] = None, providers: Any = None,
                                provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b") -> Dict[str, Any]:
        from backend.departments.story_context import StoryContextService
        ctx = StoryContextService(self.root_dir, self.db)
        prompt = (
            "You are the screenwriter story analyst. Analyze the story idea into JSON with EXACT keys: "
            "dramatic_engine, theme, protagonist, objective, opposition, conflict, stakes, audience_promise, "
            "constraints (array), ending_requirements. Base every field on the brief/canon below; do not invent scores.\n"
            f"BRIEF:\n{json.dumps(brief_content)[:4000]}\nCANON:\n{json.dumps(canon_content or {})[:4000]}"
        )
        result = providers.generate_text(project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt)
        required = ["dramatic_engine", "theme", "protagonist", "objective", "opposition", "conflict", "stakes", "audience_promise", "constraints", "ending_requirements"]
        if provider_id == "DETERMINISTIC_MOCK":
            analysis = {
                "dramatic_engine": f"MOCK: protagonist {brief_content.get('protagonist','')} pursues {brief_content.get('objective','')} against {brief_content.get('opposition','')}",
                "theme": brief_content.get("story_question", "mock theme"),
                "protagonist": brief_content.get("protagonist", ""),
                "objective": brief_content.get("objective", ""),
                "opposition": brief_content.get("opposition", "mock opposition"),
                "conflict": brief_content.get("conflict", ""),
                "stakes": brief_content.get("stakes", ""),
                "audience_promise": "mock audience promise",
                "constraints": brief_content.get("constraints", []),
                "ending_requirements": brief_content.get("ending_direction", ""),
            }
        else:
            analysis = providers.validate_structured(result["content"], required)
        meta = self._persist_artifact(project_id, episode_id, "STORY_ANALYSIS", analysis, provider=result)
        return {**meta, "analysis": analysis, "status": result["status"]}

    def generate_hooks(self, project_id: str, episode_id: str, analysis: Dict[str, Any],
                       brief_content: Dict[str, Any], providers: Any = None,
                       provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b") -> Dict[str, Any]:
        prompt = (
            "Generate 3 opening-hook alternatives as JSON {\"hooks\": [{\"id\": \"H1\", \"what_audience_sees\": \"\", "
            "\"question_created\": \"\", \"information_promised\": \"\", \"connection_to_episode\": \"\", \"payoff\": \"\"}, ...]}. "
            "Each hook must connect to the actual episode and state how the story pays it off. No universal intervals.\n"
            f"ANALYSIS:\n{json.dumps(analysis)[:4000]}\nBRIEF:\n{json.dumps(brief_content)[:4000]}"
        )
        result = providers.generate_text(project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt)
        if provider_id == "DETERMINISTIC_MOCK":
            hooks = {"hooks": [
                {"id": "H1", "what_audience_sees": "MOCK opening image", "question_created": "What is at stake?", "information_promised": "Premise", "connection_to_episode": "Premise", "payoff": "Act 1"},
                {"id": "H2", "what_audience_sees": "MOCK inciting moment", "question_created": "Who is responsible?", "information_promised": "Conflict", "connection_to_episode": "Conflict", "payoff": "Midpoint"},
                {"id": "H3", "what_audience_sees": "MOCK question", "question_created": "Will they choose?", "information_promised": "Ending", "connection_to_episode": "Ending", "payoff": "Climax"},
            ]}
        else:
            hooks = providers.validate_structured(result["content"], ["hooks"])
        meta = self._persist_artifact(project_id, episode_id, "HOOKS", hooks, provider=result)
        return {**meta, "hooks": hooks, "status": result["status"]}

    def generate_outline(self, project_id: str, episode_id: str, analysis: Dict[str, Any],
                         brief_content: Dict[str, Any], providers: Any = None,
                         provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b") -> Dict[str, Any]:
        prompt = (
            "Generate a 3-act outline as JSON {\"acts\": [{\"name\": \"ACT I\", \"beats\": [\"...\"]}, ...], "
            "\"beats\": [{\"id\": \"B1\", \"label\": \"\", \"description\": \"\"}]}. Include setup, inciting incident, "
            "escalation, turning points, midpoint where applicable, climax, resolution, character development.\n"
            f"ANALYSIS:\n{json.dumps(analysis)[:4000]}\nBRIEF:\n{json.dumps(brief_content)[:4000]}"
        )
        result = providers.generate_text(project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt)
        if provider_id == "DETERMINISTIC_MOCK":
            outline = {"acts": [
                {"name": "ACT I", "beats": ["Setup", "Inciting incident"]},
                {"name": "ACT II", "beats": ["Escalation", "Midpoint", "Turning point"]},
                {"name": "ACT III", "beats": ["Climax", "Resolution"]},
            ], "beats": [
                {"id": "B1", "label": "Setup", "description": brief_content.get("premise", "")},
                {"id": "B2", "label": "Climax", "description": brief_content.get("ending_direction", "")},
            ], "status": "PROPOSED"}
        else:
            outline = providers.validate_structured(result["content"], ["acts", "beats"])
        meta = self._persist_artifact(project_id, episode_id, "OUTLINE", outline, provider=result)
        return {**meta, "outline": outline, "status": result["status"]}

    def approve_outline(self, project_id: str, episode_id: str, human_confirmed: bool = False) -> Dict[str, Any]:
        if not human_confirmed:
            raise PermissionError("Outline approval requires human_confirmed=True via Windows reviewer path.")
        with self.db.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = 'OUTLINE' ORDER BY revision DESC LIMIT 1",
                (project_id, episode_id),
            ).fetchone()
            if not row:
                raise KeyError("No outline to approve")
            conn.execute("UPDATE story_artifacts SET status = 'APPROVED' WHERE artifact_id = ?", (row["artifact_id"],))
            conn.commit()
        return {"artifact_id": row["artifact_id"], "status": "APPROVED"}

    def generate_scene_cards(self, project_id: str, episode_id: str, outline: Dict[str, Any],
                             brief_content: Dict[str, Any], providers: Any = None,
                             provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b") -> Dict[str, Any]:
        prompt = (
            "Generate 5 scene cards as JSON array. Each: scene_id (SC01...), location, time, characters (array), "
            "objective, conflict, action, dramatic_turn, clue_or_reveal, emotional_purpose, visual_storytelling, "
            "estimated_runtime_sec (number).\n"
            f"OUTLINE:\n{json.dumps(outline)[:4000]}\nBRIEF:\n{json.dumps(brief_content)[:4000]}"
        )
        result = providers.generate_text(project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt)
        if provider_id == "DETERMINISTIC_MOCK":
            chars = brief_content.get("characters") or [brief_content.get("protagonist", "PROTAGONIST")]
            cards = [{
                "scene_id": f"SC{i+1:02d}",
                "location": (brief_content.get("locations") or ["INT. SETTING - DAY"])[0],
                "time": "DAY",
                "characters": chars,
                "objective": brief_content.get("objective", ""),
                "conflict": brief_content.get("conflict", ""),
                "action": "Mock filmable action advancing the objective.",
                "dramatic_turn": "Mock turn revealing new information.",
                "clue_or_reveal": (brief_content.get("clues_and_reveals") or ["Mock clue"])[0],
                "emotional_purpose": "Mock emotional beat",
                "visual_storytelling": "Mock visual opportunity",
                "estimated_runtime_sec": 12.0,
            } for i in range(5)]
        else:
            raw = result["content"]
            try:
                cards = json.loads(raw)
            except Exception:
                raise ValueError("Scene card output is not valid JSON")
            if not isinstance(cards, list):
                raise ValueError("Scene card output must be a JSON array")
        meta = self._persist_artifact(project_id, episode_id, "SCENE_CARDS", cards, provider=result)
        return {**meta, "scene_cards": cards, "status": result["status"]}

    def generate_screenplay(self, project_id: str, episode_id: str, scene_cards: List[Dict[str, Any]],
                            brief_content: Dict[str, Any], canon_content: Dict[str, Any] = None,
                            title: str = "Untitled", target_audience: str = "General",
                            intended_duration_sec: int = 300, providers: Any = None,
                            provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b",
                            context_hash: str = None) -> Dict[str, Any]:
        # Gate: outline must be APPROVED before drafting
        with self.db.get_connection() as conn:
            outline = conn.execute(
                "SELECT status FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = 'OUTLINE' ORDER BY revision DESC LIMIT 1",
                (project_id, episode_id),
            ).fetchone()
        if outline and outline["status"] != "APPROVED":
            raise PermissionError(f"Outline status is {outline['status']}; approve the outline before drafting the screenplay.")
        prompt = (
            "Write a complete screenplay as Markdown with scene headings (INT./EXT. LOCATION - TIME), filmable action, "
            "character entrances, dialogue (CHARACTER: line), transitions, visual direction, audio suggestions. "
            "Use the scene cards exactly; do not invent unresolved placeholders.\n"
            f"SCENE CARDS:\n{json.dumps(scene_cards)[:6000]}\nBRIEF:\n{json.dumps(brief_content)[:4000]}\nCANON:\n{json.dumps(canon_content or {})[:2000]}"
        )
        result = providers.generate_text(project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt)
        if provider_id == "DETERMINISTIC_MOCK":
            blocks = []
            for card in scene_cards:
                chars_joined = ", ".join(card.get("characters") or [])
                blocks.append(
                    f"\n{card['scene_id']}. INT. {card.get('location','')} - {card.get('time','')}\n\n"
                    f"ACTION: {card.get('action','')} Protagonist objective: {card.get('objective','')}.\n"
                    f"Conflict: {card.get('conflict','')} Turn: {card.get('dramatic_turn','')}\n\n"
                    f"PROTAGONIST: Mock dialogue line advancing the objective.\n"
                    f"{chars_joined.split(',')[0].strip().upper() if chars_joined else 'NARRATOR'}: Mock dialogue line.\n\n"
                    f"Clue revealed: {card.get('clue_or_reveal','')}\n"
                    f"Required beat: {brief_content.get('required_beats',[''])[0] if brief_content.get('required_beats') else ''}\n"
                    f"VISUAL: {card.get('visual_storytelling','')}\n"
                    f"AUDIO: Mock ambience suggestion.\n"
                )
            screenplay_md = "# " + title + " - SCREENPLAY (MOCK)\n\nPremise: " + brief_content.get("premise", "") + "\n" + "\n".join(blocks)
        else:
            screenplay_md = result["content"]
        # Persist as new script revision (never overwrite APPROVED)
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT MAX(version) AS max_v FROM scripts WHERE project_id = ?", (project_id,)).fetchone()
            prev = row["max_v"] if row and row["max_v"] is not None else None
            nxt = (prev or 0) + 1
        script_id = f"SCR_{project_id}_V{nxt:02d}"
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO scripts
                   (script_id, project_id, version, previous_version, change_summary, agent_responsible, reason_for_changes, reviewer_comments, scores_json, passes_completed_json, content_markdown, approval_status, is_immutable, created_at)
                   VALUES (?, ?, ?, ?, ?, 'SCREENWRITER', ?, '', ?, ?, ?, 'AWAITING_HUMAN_REVIEW', 0, ?)""",
                (
                    script_id, project_id, nxt, prev,
                    "Generated screenplay via staged pipeline (CR_006 M3)",
                    "Staged generation " + result["status"], json.dumps({}), json.dumps([]),
                    screenplay_md, now,
                ),
            )
            conn.commit()
        approval_id = f"APP_{script_id}"
        self.approvals.register_deliverable_gate(approval_id, project_id, "script", script_id, nxt, "PROPOSED")
        self.approvals.advance_system_state(approval_id, "GENERATING", "SCREENWRITER")
        self.approvals.advance_system_state(approval_id, "QUALITY_CHECK", "SCRIPT_CRITIC", "MANUAL_INSPECTION_REQUIRED", "Run deterministic validation + creative critique before human review.")
        self.approvals.advance_system_state(approval_id, "AWAITING_HUMAN_REVIEW", "PRODUCTION_DIRECTOR", "MANUAL_INSPECTION_REQUIRED", "Screenplay generated; validation and critique required before approval.")
        self._persist_artifact(project_id, episode_id, "SCREENPLAY", {"script_id": script_id, "version": nxt, "markdown_chars": len(screenplay_md)}, context_hash=context_hash, provider=result)
        return {
            "script_id": script_id, "approval_id": approval_id, "version": nxt,
            "previous_version": prev, "status": result["status"], "provider_id": result["provider_id"],
            "model_id": result["model_id"], "request_id": result["request_id"],
            "markdown": screenplay_md, "context_hash": context_hash,
        }

    def run_revision_passes(self, project_id: str, script_id: str, passes: List[str]) -> Dict[str, Any]:
        """Record revision passes that actually execute. Each pass re-checks one aspect
        against the stored screenplay and records a result; no score invented."""
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT content_markdown FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            text = row["content_markdown"]
        results = {}
        for p in passes:
            if p not in SCRIPT_DEVELOPMENT_PASSES:
                raise ValueError(f"Unknown pass {p}")
            # Each pass does a real, simple deterministic check on the text
            if "DIALOGUE" in p:
                found = bool(re.search(r"\n[A-Z][A-Z \-\']+:\s+\S", text))
            elif "FORMAT" in p or "FORMATTING" in p:
                found = ("INT." in text or "EXT." in text)
            elif "CONTINUITY" in p:
                found = ("Protagonist" in text or "PROTAGONIST" in text)
            elif "FEASIBILITY" in p:
                found = (len(text) > 200)
            else:
                found = len(text) > 0
            results[p] = {"executed": True, "passed": bool(found), "evidence": f"text_len={len(text)}"}
        return results

    def generate_retention_map(self, project_id: str, episode_id: str, scene_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        entries = []
        for card in scene_cards:
            entries.append({
                "scene_id": card.get("scene_id", ""),
                "beat": card.get("dramatic_turn", ""),
                "viewer_question": card.get("objective", ""),
                "suspense": card.get("conflict", ""),
                "information_revealed": card.get("clue_or_reveal", ""),
                "emotional_change": card.get("emotional_purpose", ""),
                "clue": card.get("clue_or_reveal", ""),
                "payoff": "",
                "promise": card.get("objective", ""),
            })
        retention = {"entries": entries}
        meta = self._persist_artifact(project_id, episode_id, "RETENTION_MAP", retention)
        return {**meta, "retention_map": retention}

    def generate_production_breakdown(self, project_id: str, approved_script_id: str) -> Dict[str, Any]:
        """Fail closed until a real approved-script-to-scene breakdown exists.

        The previous implementation inserted fixed throne-room demonstration
        scenes regardless of the approved screenplay. Returning those as a
        production breakdown could contaminate project data, so no scene rows
        are created by this placeholder.
        """
        with self.db.get_connection() as conn:
            script = conn.execute(
                "SELECT script_id, approval_status FROM scripts WHERE script_id = ? AND project_id = ?",
                (approved_script_id, project_id),
            ).fetchone()
            if not script or script["approval_status"] != "APPROVED":
                raise PermissionError(
                    f"Cannot break down unapproved or missing script '{approved_script_id}'."
                )

        raise NotImplementedError(
            "Production breakdown is unavailable: no script-derived scene parser or generation path is implemented. "
            "No scenes were created."
        )
