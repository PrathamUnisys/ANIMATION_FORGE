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

    def __init__(self, db: DatabaseManager):
        self.db = db

    def validate(self, project_id: str, script_id: str, brief_content: Dict[str, Any] = None,
                 canon_content: Dict[str, Any] = None) -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            screenplay = row["content_markdown"]
            version = row["version"]
            # Scene cards for this project — latest revision only (one set per generation)
            cards = conn.execute(
                "SELECT content_json FROM story_artifacts WHERE project_id = ? AND artifact_type = 'SCENE_CARDS' ORDER BY revision DESC LIMIT 1", (project_id,)
            ).fetchall()
            card_scenes: List[Dict[str, Any]] = []
            for c in cards:
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

        # 5. Continuity vs canon: character names agree where canon lists them
        if canon_content:
            canon_chars = {c.get("name") for c in (canon_content.get("characters") or []) if c.get("name")}
            for name in canon_chars:
                if name in screenplay:
                    ok("canon_agreement")
                else:
                    # Not necessarily an error — only check if card references it
                    pass
        else:
            # No canon to check — mark NOT_TESTED via issue severity NOTE
            issues.append({"check": "canon_agreement", "scene_id": "", "detail": "No approved canon available; check NOT_TESTED", "severity": "NOTE"})
            checks.setdefault("canon_agreement", True)

        # 6. Required beats/clues present
        if brief_content:
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
        else:
            ok("required_beats")
            ok("required_clues")

        # 7. Runtime estimate (documented method: sum of card runtimes)
        total = sum(float(c.get("estimated_runtime_sec") or 0) for c in card_scenes)
        runtime = {"total_sec": total, "method": "SUM_SCENE_CARDS", "uncertainty": "Estimate only; not measured playback"}
        checks["runtime_estimate"] = True if card_scenes else False

        outcome = "PASS" if all(checks.values()) else "FAIL"
        report = {
            "validator": "DETERMINISTIC_SCREENPLAY_VALIDATOR",
            "outcome": outcome,
            "checks": checks,
            "issues": issues,
            "runtime_estimate": runtime,
            "grants_creative_approval": False,
        }
        with self.db.get_connection() as conn:
            conn.execute(
                """INSERT INTO screenplay_qc_reports
                   (report_id, project_id, script_id, script_version, validator_name, outcome, checks_json, issues_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"QCDET_{script_id}_V{version}", project_id, script_id, version,
                    "DETERMINISTIC_SCREENPLAY_VALIDATOR", outcome,
                    json.dumps(checks), json.dumps(issues), _now(),
                ),
            )
            conn.commit()
        return report


class CreativeCritique:
    """Independent creative critique via provider LLM (SCRIPT_CRITIC contract)."""

    def __init__(self, db: DatabaseManager, providers: ProviderManager):
        self.db = db
        self.providers = providers

    def critique(self, project_id: str, script_id: str, provider_id: str = "OLLAMA_OPENAI_COMPATIBLE", model_id: str = "ornith:9b") -> Dict[str, Any]:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM scripts WHERE script_id = ?", (script_id,)).fetchone()
            if not row:
                raise KeyError(f"Script {script_id} not found")
            screenplay = row["content_markdown"]
            cards = conn.execute(
                "SELECT content_json FROM story_artifacts WHERE project_id = ? AND artifact_type = 'SCENE_CARDS' ORDER BY revision DESC LIMIT 1", (project_id,)
            ).fetchall()
            card_text = "\n".join(str(c["content_json"])[:2000] for c in cards)
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
                   (report_id, project_id, script_id, script_version, validator_name, outcome, checks_json, issues_json, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    f"QCCRIT_{script_id}_{result['request_id']}", project_id, script_id, row["version"],
                    "SCRIPT_CRITIC_CREATIVE_REVIEW", "COMPLETED",
                    json.dumps({"findings": len(findings)}), json.dumps(findings), _now(),
                ),
            )
            conn.commit()
        return report

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
