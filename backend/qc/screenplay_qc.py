"""CR_006 M4: Deterministic screenplay validation + creative critique.

Two independent outputs:
- DeterministicValidator: checks actual screenplay data (schema, refs, placeholders,
  canon agreement, required beats/clues, runtime estimate).
- CreativeCritique: LLM-backed review via SCRIPT_CRITIC contract; every finding
  cites scene/passage, separates evidence/interpretation/preference, no scores.
Neither can approve creative work.
"""
import json
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.database import DatabaseManager
from backend.providers.manager import ProviderManager


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


PLACEHOLDER_PATTERNS = [
    re.compile(r"\[To be developed\]"),
    re.compile(r"\[Not yet drafted\]"),
    re.compile(r"\[Observable[^\]]*\]"),
    re.compile(r"\[Dialogue[^\]]*\]"),
    re.compile(r"\{[a-z_]+\}"),  # {variable} unexpanded
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
]


class DeterministicValidator:
    """Runs deterministic checks against a stored screenplay revision."""

    VALIDATOR_VERSION = "1.1.0"
    SEVERITIES = {"BLOCKER", "MAJOR", "MINOR", "NOTE"}

    def __init__(self, db: DatabaseManager):
        self.db = db

    def validate(self, project_id: str, script_id: str, brief_content: Dict[str, Any] = None,
                 canon_content: Dict[str, Any] = None, episode_id: str = None,
                 series_id: str = None, context_hash: str = None,
                 source_refs: Dict[str, Any] = None) -> Dict[str, Any]:
        from backend.departments.story_context import StoryContextService
        import uuid
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            row = dict(row)
            if row.get("project_id") != project_id:
                raise PermissionError(f"Script {script_id} belongs to project {row.get('project_id')}, not {project_id}.")
            screenplay = row["content_markdown"]
            version = row["version"]
            # Episode isolation: must resolve an exact episode.
            resolved_episode = episode_id or row.get("episode_id")
            if not resolved_episode:
                # Try the latest scene-cards artifact to infer the episode (only as fallback discovery, then enforce isolation below)
                latest_cards = conn.execute(
                    "SELECT episode_id FROM story_artifacts WHERE project_id = ? AND artifact_type = 'SCENE_CARDS' ORDER BY revision DESC LIMIT 1",
                    (project_id,),
                ).fetchone()
                if not latest_cards:
                    raise ValueError("Cannot resolve episode for QC: no episode_id supplied and no scene cards exist.")
                raise ValueError(f"Episode not supplied for QC of {script_id}; latest cards episode is {latest_cards['episode_id']}. Pass episode_id explicitly.")
            effective_episode = resolved_episode
            # Exact scene cards for this project+episode, latest revision only.
            cards = conn.execute(
                "SELECT * FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = 'SCENE_CARDS' ORDER BY revision DESC LIMIT 1",
                (project_id, effective_episode),
            ).fetchall()
            cards_row = dict(cards[0]) if cards else None
            card_scenes: List[Dict[str, Any]] = []
            cards_revision = None
            cards_artifact_id = None
            for c in cards:
                cards_revision = c["revision"]
                cards_artifact_id = c["artifact_id"]
                try:
                    arr = json.loads(c["content_json"])
                    if isinstance(arr, list):
                        card_scenes.extend(arr)
                except Exception:
                    pass
            # Characters in project
            chars = conn.execute("SELECT character_id, name FROM characters WHERE project_id = ?", (project_id,)).fetchall()
            char_names = {r["name"] for r in chars}
            # Locations / environments
            envs = conn.execute("SELECT name FROM environments WHERE project_id = ?", (project_id,)).fetchall()
            env_names = {r["name"] for r in envs}
        # Load brief/canon if not supplied (never silently pass canon=None as success)
        if brief_content is None:
            try:
                svc = StoryContextService("DUMMY_ROOT_PLACEHOLDER", self.db)
                # root is needed only for genre file reads during validation; use repo root via database path parent
                import os
                repo_root = os.path.dirname(self.db.db_path)
                svc = StoryContextService(repo_root, self.db)
                brief_row = svc.get_brief(project_id, effective_episode)
                brief_content = brief_row["content"]
            except Exception:
                brief_content = None
        if canon_content is None:
            try:
                import os
                repo_root = os.path.dirname(self.db.db_path)
                svc = StoryContextService(repo_root, self.db)
                if series_id is None and brief_content:
                    series_id = brief_content.get("series_id")
                if series_id:
                    canon_row = svc.get_approved_canon(series_id)
                    if canon_row:
                        canon_content = canon_row["content"]
            except Exception:
                pass

        checks: Dict[str, bool] = {}
        issues: List[Dict[str, Any]] = []

        def fail(check: str, scene_id: str, detail: str, severity: str = "MAJOR"):
            checks[check] = False
            issues.append({"check": check, "scene_id": scene_id, "detail": detail, "severity": severity})

        def ok(check: str):
            checks.setdefault(check, True)

        # 1. Scene structure: scene cards exist & have required fields
        if not card_scenes:
            fail("scene_cards_present", "", "No scene cards generated for this project", "BLOCKER")
        else:
            ok("scene_cards_present")
            ids = [c.get("scene_id") for c in card_scenes]
            if len(ids) != len(set(ids)):
                fail("scene_ids_unique", "", f"Duplicate scene IDs: {ids}", "BLOCKER")
            else:
                ok("scene_ids_unique")
            for c in card_scenes:
                sid = c.get("scene_id", "?")
                for req in ("location", "characters", "objective", "conflict", "estimated_runtime_sec"):
                    if not c.get(req):
                        fail("scene_card_fields", sid, f"Missing required field {req}", "MAJOR")
                    else:
                        ok("scene_card_fields")
                # Character references resolve
                for ch in (c.get("characters") or []):
                    if ch and ch not in char_names and canon_content:
                        # Allow protagonist names from brief/canon even if not in characters table
                        brief_chars = set((brief_content or {}).get("characters") or [])
                        if ch not in brief_chars:
                            fail("character_references", sid, f"Character {ch!r} has no record (characters table / brief)", "MINOR")
                        else:
                            ok("character_references")
                    else:
                        ok("character_references")

        # 2. Screenplay placeholders
        for pat in PLACEHOLDER_PATTERNS:
            for m in pat.finditer(screenplay):
                fail("no_placeholders", "", f"Unresolved placeholder {m.group(0)!r}", "MAJOR")
        if not any(i["check"] == "no_placeholders" for i in issues):
            ok("no_placeholders")

        # 3. Dialogue present (CHARACTER: line pattern)
        if not re.search(r"\n[A-Z][A-Z \-\']+:\s+\S", screenplay):
            fail("dialogue_present", "", "No dialogue pattern (CHARACTER: line) found in screenplay", "MAJOR")
        else:
            ok("dialogue_present")

        # 4. Scene headings present (INT./EXT. or SCxx)
        scenes_in_text = re.findall(r"(INT\.|EXT\.|SC\d+)", screenplay)
        if len(scenes_in_text) < 1:
            fail("scene_headings", "", "No scene headings found", "MAJOR")
        else:
            ok("scene_headings")

        # 5. Continuity vs canon: character names + world rules + locations/constraints.
        # Missing evidence is NOT_TESTED, never PASS.
        if canon_content:
            canon_chars = {c.get("name") for c in (canon_content.get("characters") or []) if c.get("name")}
            for name in canon_chars:
                if name in screenplay:
                    ok("canon_agreement")
                else:
                    pass
            # World rules: each rule name should appear if it is load-bearing in the brief; otherwise NOTE.
            rules = ((canon_content.get("world") or {}).get("rules") or [])
            for rule in rules:
                rname = rule.get("name") if isinstance(rule, dict) else rule
                if rname and rname not in screenplay and (brief_content or {}).get("required_beats"):
                    issues.append({"check": "canon_world_rules", "scene_id": "", "detail": f"World rule {rname!r} not mentioned (deterministic mention check only)", "severity": "NOTE"})
                    checks.setdefault("canon_world_rules", "NOT_TESTED")
                elif rname in screenplay:
                    ok("canon_world_rules")
            # Locations: brief locations should appear in cards/screenplay
            for loc in ((brief_content or {}).get("locations") or []):
                if loc and loc not in screenplay and loc not in json.dumps(card_scenes):
                    fail("location_references", "", f"Brief location {loc!r} not found in screenplay/cards", "MINOR")
                else:
                    ok("location_references")
        else:
            issues.append({"check": "canon_agreement", "scene_id": "", "detail": "No approved canon available; check NOT_TESTED", "severity": "NOTE"})
            checks["canon_agreement"] = "NOT_TESTED"

        # 6. Required beats/clues present
        if brief_content is not None:
            for beat in (brief_content.get("required_beats") or []):
                if beat.strip().lower() not in screenplay.lower() and beat.strip().lower() not in json.dumps(card_scenes).lower():
                    fail("required_beats", "", f"Required beat {beat!r} not found in screenplay or cards", "MAJOR")
                else:
                    ok("required_beats")
            for clue in (brief_content.get("clues_and_reveals") or []):
                if clue.strip().lower() not in screenplay.lower():
                    issues.append({"check": "required_clues", "scene_id": "", "detail": f"Clue {clue!r} not found verbatim (may be paraphrased)", "severity": "MINOR"})
                    checks["required_clues"] = False
                else:
                    ok("required_clues")
            # Scene-card/screenplay correspondence: every card scene_id must appear in the screenplay.
            for c in card_scenes:
                sid = c.get("scene_id")
                if sid and sid not in screenplay and sid not in ("SC01",):
                    issues.append({"check": "scene_correspondence", "scene_id": sid, "detail": f"Scene {sid} from cards missing in screenplay text", "severity": "MINOR"})
                    checks["scene_correspondence"] = False
                elif sid:
                    ok("scene_correspondence")
        else:
            issues.append({"check": "required_beats", "scene_id": "", "detail": "No Episode Brief available; check NOT_TESTED", "severity": "NOTE"})
            checks["required_beats"] = "NOT_TESTED"
            issues.append({"check": "required_clues", "scene_id": "", "detail": "No Episode Brief available; check NOT_TESTED", "severity": "NOTE"})
            checks["required_clues"] = "NOT_TESTED"

        # 7. Runtime estimate (documented method: sum of card runtimes)
        total = sum(float(c.get("estimated_runtime_sec") or 0) for c in card_scenes)
        runtime = {"total_sec": total, "method": "SUM_SCENE_CARDS", "uncertainty": "Estimate only; not measured playback"}
        checks["runtime_estimate"] = True if card_scenes else False

        if any(v is False for v in checks.values()):
            outcome = "FAIL"
        elif all(v is True for v in checks.values()):
            outcome = "PASS"
        else:
            outcome = "NOT_TESTED"
        source_refs_full = {
            "scene_cards_artifact_id": cards_artifact_id,
            "scene_cards_revision": cards_revision,
            **(source_refs or {}),
        }
        report = {
            "validator": "DETERMINISTIC_SCREENPLAY_VALIDATOR",
            "validator_version": self.VALIDATOR_VERSION,
            "outcome": outcome,
            "checks": checks,
            "issues": issues,
            "runtime_estimate": runtime,
            "source_refs": source_refs_full,
            "episode_id": effective_episode,
            "grants_creative_approval": False,
        }
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO screenplay_qc_reports
                   (report_id, project_id, script_id, script_version, validator_name, outcome, checks_json, issues_json, created_at, episode_id, context_hash_sha256, validator_version, source_refs_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"QCDET_{script_id}_V{version}_{uuid.uuid4().hex[:8].upper()}", project_id, script_id, version,
                    "DETERMINISTIC_SCREENPLAY_VALIDATOR", outcome,
                    json.dumps(checks), json.dumps(issues), _now(), effective_episode, context_hash, self.VALIDATOR_VERSION, json.dumps(source_refs_full),
                ),
            )
            conn.commit()
        return report


class CreativeCritique:
    """Independent creative critique via provider LLM (SCRIPT_CRITIC contract)."""

    def __init__(self, db: DatabaseManager, providers: ProviderManager):
        self.db = db
        self.providers = providers

    def critique(self, project_id: str, script_id: str, provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b", episode_id: str = None) -> Dict[str, Any]:
        import uuid
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            row_d = dict(row)
            if row_d.get("project_id") != project_id:
                raise PermissionError(f"Script {script_id} belongs to project {row_d.get('project_id')}, not {project_id}.")
            screenplay = row_d["content_markdown"]
            resolved_episode = episode_id or row_d.get("episode_id")
            version = row_d["version"]
            cards = []
            if resolved_episode:
                cards = conn.execute(
                    "SELECT content_json FROM story_artifacts WHERE project_id = ? AND episode_id = ? AND artifact_type = 'SCENE_CARDS' ORDER BY revision DESC LIMIT 1", (project_id, resolved_episode)
                ).fetchall()
            card_text = "\n".join(str(c["content_json"])[:2000] for c in cards)
            card_scenes = []
            for c in cards:
                try:
                    arr = json.loads(c["content_json"])
                    if isinstance(arr, list):
                        card_scenes.extend(arr)
                except Exception:
                    pass
            valid_scene_ids = {c.get("scene_id") for c in card_scenes if isinstance(c, dict) and c.get("scene_id")}
        prompt = (
            "You are SCRIPT_CRITIC, an independent screenplay reviewer. Critique the screenplay below.\n"
            "For each finding: scene_id, severity (BLOCKER|MAJOR|MINOR|NOTE), category, evidence (exact passage), "
            "interpretation, recommendation. Separate evidence from interpretation and subjective preference. "
            "Review: narrative coherence, character consistency/motivation, dialogue, genre consistency, "
            "hook fulfillment, mystery/clue fairness, suspense/pacing, emotional impact, visual storytelling, production feasibility.\n"
            "Return ONLY valid JSON: {\"findings\": [{\"scene_id\": \"\", \"severity\": \"MINOR\", \"category\": \"\", "
            "\"evidence\": \"\", \"interpretation\": \"\", \"recommendation\": \"\"}]}\n\n"
            f"SCENE CARDS:\n{card_text}\n\nSCREENPLAY:\n{screenplay[:8000]}"
        )
        result = self.providers.generate_text(
            project_id=project_id, provider_id=provider_id, model_id=model_id, prompt=prompt
        )
        # Validate structured output; raises ProviderError if malformed (no fake review)
        if provider_id == "DETERMINISTIC_MOCK":
            # Mock returns non-critique JSON; synthesize deterministic findings from actual text scan
            findings = self._mock_findings(screenplay, result)
        else:
            data = self.providers.validate_structured(result["content"], ["findings"])
            findings = data["findings"]
            findings = self.validate_findings(findings, screenplay, valid_scene_ids)
        report = {
            "validator": "SCRIPT_CRITIC_CREATIVE_REVIEW",
            "status": result["status"],
            "provider_id": result["provider_id"],
            "model_id": result["model_id"],
            "request_id": result["request_id"],
            "findings": findings,
            "grants_creative_approval": False,
        }
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO screenplay_qc_reports
                   (report_id, project_id, script_id, script_version, validator_name, outcome, checks_json, issues_json, created_at, episode_id, context_hash_sha256, validator_version, source_refs_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"QCCRIT_{script_id}_{uuid.uuid4().hex[:8].upper()}", project_id, script_id, version,
                    "SCRIPT_CRITIC_CREATIVE_REVIEW", "COMPLETED",
                    json.dumps({"findings": len(findings)}), json.dumps(findings), _now(),
                    resolved_episode, None, "1.0.0", json.dumps({"status": result["status"]}),
                ),
            )
            conn.commit()
        return report

    def validate_findings(self, findings: Any, screenplay: str, valid_scene_ids: set) -> List[Dict[str, Any]]:
        if not isinstance(findings, list) or not findings:
            raise ValueError("Creative critique returned no findings; refusing to fabricate.")
        allowed = {"BLOCKER", "MAJOR", "MINOR", "NOTE"}
        for i, f in enumerate(findings):
            if not isinstance(f, dict):
                raise ValueError(f"Finding {i} is not an object")
            sev = f.get("severity")
            if sev not in allowed:
                raise ValueError(f"Finding {i} has invalid severity {sev!r}")
            if not (f.get("evidence") or "").strip():
                raise ValueError(f"Finding {i} is missing evidence")
            if not (f.get("category") or "").strip() or not (f.get("interpretation") or "").strip() or not (f.get("recommendation") or "").strip():
                raise ValueError(f"Finding {i} missing category/interpretation/recommendation")
            sid = f.get("scene_id")
            if sid and valid_scene_ids and sid not in valid_scene_ids and sid not in screenplay:
                raise ValueError(f"Finding {i} references nonexistent scene {sid!r}")
            f["finding_id"] = f.get("finding_id") or f"FIND_{i+1:03d}"
        return findings

    def _mock_findings(self, screenplay: str, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        if "[To be developed]" in screenplay:
            findings.append({
                "scene_id": "", "severity": "MAJOR", "category": "completeness",
                "evidence": "[To be developed] placeholder found in screenplay",
                "interpretation": "Unfinished scaffolding reduces production readiness.",
                "recommendation": "Develop all placeholders before human approval.",
            })
        if not re.search(r"\n[A-Z][A-Z \-\']+:\s+\S", screenplay):
            findings.append({
                "scene_id": "", "severity": "MAJOR", "category": "dialogue",
                "evidence": "No dialogue pattern found",
                "interpretation": "Dialogue may be missing for character voices.",
                "recommendation": "Add filmable dialogue lines per scene.",
            })
        if not findings:
            findings.append({
                "scene_id": "", "severity": "NOTE", "category": "mock_review",
                "evidence": f"Screenplay length {len(screenplay)} chars; mock reviewer ran deterministically",
                "interpretation": "Mock provider cannot judge quality; live review required for real critique.",
                "recommendation": "Run with OLLAMA_OPENAI_COMPATIBLE for live creative critique.",
            })
        return findings
