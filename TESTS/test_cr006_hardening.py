"""CR_006 hardening regression tests (H1-H5, H8). Temp DB only."""
import os
import sys
import tempfile
import shutil
import threading
import json
import unittest
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from backend.database import DatabaseManager
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine, ApprovalPolicyViolationError
from backend.providers.manager import ProviderManager, SecureCredentialVault
from backend.departments.story_context import StoryContextService, BibleTransitionError
from backend.departments.story_pipeline import StoryAndScreenplayPipeline
from backend.qc.screenplay_qc import DeterministicValidator, CreativeCritique


class CR006HardeningTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="af_hardening_")
        cls.db_path = os.path.join(cls.temp_dir, "test_hardening.db")
        cls.db = DatabaseManager(cls.db_path)
        cls.governance = GovernanceEngine(ROOT, cls.db)
        cls.approvals = ApprovalEngine(cls.db)
        cls.providers = ProviderManager(cls.db, SecureCredentialVault())
        cls.ctx = StoryContextService(ROOT, cls.db)
        cls.pipe = StoryAndScreenplayPipeline(ROOT, cls.db, cls.approvals)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with cls.db.get_connection() as conn:
            for pid in ("PROJECT_HARD", "PROJECT_OTHER"):
                conn.execute(
                    """INSERT OR IGNORE INTO projects
                       (project_id, title, synopsis, genre, target_audience, intended_runtime_sec, language, creative_brief, visual_direction, animation_technique, production_goals_json, restrictions_json, status, current_stage, active_mode, series_id, created_at, updated_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', '[]', 'ACTIVE', 'USER_STORY_IDEA', 'PRODUCTION_MODE', ?, ?, ?)""",
                    (pid, "Hard test", "synopsis", "Fantasy", "General", 300, "en-US", "", "", "2D", "SER_HARD", now, now),
                )
            conn.execute("INSERT OR IGNORE INTO series (series_id, title, bible_json, created_at) VALUES (?, ?, ?, ?)",
                         ("SER_HARD", "Hard Series", "{}", now))
            conn.execute("INSERT OR IGNORE INTO characters (character_id, project_id, name, role, bible_json, visual_consistency_locks_json, voice_profile_json, approval_status, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                         ("CHAR_HARD_01", "PROJECT_HARD", "WREN", "lead", "{}", "{}", "{}", "DRAFT", now))
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _brief(self, episode_id="EP_H01", title="T"):
        return {
            "project_id": "PROJECT_HARD", "episode_id": episode_id, "title": title,
            "premise": "A lighthouse bell rings thirteen times.", "synopsis": "s",
            "primary_genre_id": "GENRE_FANTASY", "secondary_genre_ids": [],
            "protagonist": "WREN", "objective": "Stop the bell", "conflict": "Wardens",
            "opposition": "Wardens", "stakes": "Memory lost", "story_question": "Which memory?",
            "ending_direction": "Bell silenced", "characters": ["WREN"], "locations": ["Tower"],
            "clues_and_reveals": ["Inscription"], "required_beats": ["Bell tolls"],
        }

    def test_h1_artifact_ids_include_episode_and_are_unique(self):
        self.ctx.create_brief("PROJECT_HARD", self._brief("EP_H01"), episode_id="EP_H01")
        self.ctx.create_brief("PROJECT_HARD", self._brief("EP_H02"), episode_id="EP_H02")
        a1 = self.pipe._persist_artifact("PROJECT_HARD", "EP_H01", "STORY_ANALYSIS", {"x": 1})
        a2 = self.pipe._persist_artifact("PROJECT_HARD", "EP_H02", "STORY_ANALYSIS", {"x": 1})
        a3 = self.pipe._persist_artifact("PROJECT_HARD", "EP_H01", "STORY_ANALYSIS", {"x": 2})
        self.assertIn("EP_H01", a1["artifact_id"])
        self.assertIn("EP_H02", a2["artifact_id"])
        self.assertNotEqual(a1["artifact_id"], a2["artifact_id"])
        self.assertNotEqual(a1["artifact_id"], a3["artifact_id"])
        self.assertEqual(a3["revision"], 2)

    def test_h2_concurrent_artifact_creation_no_duplicate(self):
        errors = []
        def worker():
            try:
                for _ in range(5):
                    self.pipe._persist_artifact("PROJECT_HARD", "EP_CONC", "HOOKS", {"y": 1})
            except Exception as e:
                errors.append(e)
        # Need episodes distinct threads sharing project? Use same episode to test UNIQUE + retry
        threads = [threading.Thread(target=worker) for _ in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.assertEqual(errors, [])
        # 20 rows, unique artifact IDs, revisions 1..20
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT artifact_id, revision FROM story_artifacts WHERE project_id='PROJECT_HARD' AND episode_id='EP_CONC' AND artifact_type='HOOKS'").fetchall()
            self.assertEqual(len(rows), 20)
            self.assertEqual(len({r["artifact_id"] for r in rows}), 20)
            self.assertEqual(sorted(r["revision"] for r in rows), list(range(1, 21)))

    def test_h3_outline_gates(self):
        # No outline -> screenplay fails
        self.ctx.create_brief("PROJECT_HARD", self._brief("EP_GATE1"))
        brief = self.ctx.get_brief("PROJECT_HARD", "EP_GATE1")["content"]
        with self.assertRaises(PermissionError):
            self.pipe.generate_screenplay("PROJECT_HARD", "EP_GATE1", [], brief, {}, "T", "G", 60, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        analysis = self.pipe.generate_story_analysis("PROJECT_HARD", "EP_GATE1", brief, {}, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        outline = self.pipe.generate_outline("PROJECT_HARD", "EP_GATE1", analysis["analysis"], brief, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        # Unapproved latest -> scene cards + screenplay fail
        with self.assertRaises(PermissionError):
            self.pipe.generate_scene_cards("PROJECT_HARD", "EP_GATE1", outline["outline"], brief, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        with self.assertRaises(PermissionError):
            self.pipe.generate_screenplay("PROJECT_HARD", "EP_GATE1", [], brief, {}, "T", "G", 60, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        # AI cannot approve outline
        with self.assertRaises(PermissionError):
            self.pipe.approve_outline("PROJECT_HARD", "EP_GATE1", human_confirmed=False)
        self.pipe.approve_outline("PROJECT_HARD", "EP_GATE1", human_confirmed=True)
        cards = self.pipe.generate_scene_cards("PROJECT_HARD", "EP_GATE1", outline["outline"], brief, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        self.assertEqual(cards["revision"], 1)
        scr = self.pipe.generate_screenplay("PROJECT_HARD", "EP_GATE1", cards["scene_cards"], brief, {}, "T", "G", 60, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        self.assertIn("outline_revision", scr["source_refs"])
        # New outline supersedes old approval -> screenplay fails until re-approved
        outline2 = self.pipe.generate_outline("PROJECT_HARD", "EP_GATE1", analysis["analysis"], brief, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        with self.assertRaises(PermissionError):
            self.pipe.generate_screenplay("PROJECT_HARD", "EP_GATE1", cards["scene_cards"], brief, {}, "T", "G", 60, self.providers, "DETERMINISTIC_MOCK", "mock-42")
        # Previous revisions preserved
        with self.db.get_connection() as conn:
            revs = conn.execute("SELECT revision, status FROM story_artifacts WHERE project_id='PROJECT_HARD' AND episode_id='EP_GATE1' AND artifact_type='OUTLINE' ORDER BY revision").fetchall()
            self.assertEqual([r["revision"] for r in revs], [1, 2])
            self.assertEqual(revs[0]["status"], "SUPERSEDED")

    def test_h4_context_hash_and_genre_rules(self):
        self.ctx.create_brief("PROJECT_HARD", self._brief("EP_CTX"), episode_id="EP_CTX")
        self.ctx.create_bible("SER_HARD", {"series_id": "SER_HARD", "title": "t", "premise": "p", "genre": "Fantasy", "format": "Short", "world": {}, "characters": [{"id": "C1", "name": "WREN"}]}, project_id="PROJECT_HARD", status="DRAFT")
        h1 = self.ctx.assemble_context("PROJECT_HARD", "EP_CTX", "SER_HARD", "GENRE_FANTASY", [], None)["manifest"]["context_hash_sha256"]
        # Explicit different genre -> different hash
        h2 = self.ctx.assemble_context("PROJECT_HARD", "EP_CTX", "SER_HARD", "GENRE_COMEDY", [], None)["manifest"]["context_hash_sha256"]
        self.assertNotEqual(h1, h2)
        # Channel must reject when registry empty (never fabricate)
        with self.assertRaises(ValueError):
            self.ctx.assemble_context("PROJECT_HARD", "EP_CTX", "SER_HARD", "GENRE_FANTASY", [], "STYLE_UNKNOWN")
        # Draft bible is not canon
        self.assertIsNone(self.ctx.get_approved_canon("SER_HARD"))

    def test_h5_qc_isolation_and_not_tested(self):
        # Use EP_GATE1 artifacts; wrong project must be rejected
        with self.db.get_connection() as conn:
            scr = conn.execute("SELECT script_id FROM scripts WHERE project_id='PROJECT_HARD' ORDER BY version DESC LIMIT 1").fetchone()
        self.assertIsNotNone(scr)
        sid = scr["script_id"]
        validator = DeterministicValidator(self.db)
        with self.assertRaises(PermissionError):
            validator.validate("PROJECT_OTHER", sid, episode_id="EP_GATE1")
        # Canon missing -> NOT_TESTED, not PASS
        report = validator.validate("PROJECT_HARD", sid, brief_content=self._brief("EP_GATE1"), canon_content=None, episode_id="EP_GATE1")
        canon_checks = {k: v for k, v in report["checks"].items() if "canon" in k}
        self.assertIn("NOT_TESTED", list(canon_checks.values()))

    def test_h6_qc_repeat_and_approval_gate(self):
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT script_id, version, episode_id FROM scripts WHERE project_id='PROJECT_HARD' ORDER BY version DESC LIMIT 1").fetchone()
        sid, ver, ep = row["script_id"], row["version"], row["episode_id"]
        validator = DeterministicValidator(self.db)
        r1 = validator.validate("PROJECT_HARD", sid, brief_content=self._brief("EP_GATE1"), canon_content={"characters": [{"name": "WREN"}], "world": {}}, episode_id=ep)
        r2 = validator.validate("PROJECT_HARD", sid, brief_content=self._brief("EP_GATE1"), canon_content={"characters": [{"name": "WREN"}], "world": {}}, episode_id=ep)
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT report_id FROM screenplay_qc_reports WHERE script_id=? AND script_version=? AND validator_name='DETERMINISTIC_SCREENPLAY_VALIDATOR'", (sid, ver)).fetchall()
            self.assertGreaterEqual(len(rows), 2)
            self.assertEqual(len({x["report_id"] for x in rows}), len(rows))
        # Approval without critique must be blocked
        approval_id = f"APP_{sid}"
        gate = self.approvals.get_gate(approval_id)
        self.assertEqual(gate["state"], "AWAITING_HUMAN_REVIEW")
        with self.assertRaises(ApprovalPolicyViolationError):
            self.approvals.submit_human_decision(approval_id, "APPROVED", "HUMAN_HARD", "Approve without critique")
        # Add critique then approval should succeed (mock critique, no BLOCKER)
        critic = CreativeCritique(self.db, self.providers)
        crep = critic.critique("PROJECT_HARD", sid, "DETERMINISTIC_MOCK", "mock-42", episode_id=ep)
        self.assertGreaterEqual(len(crep["findings"]), 1)
        final = self.approvals.submit_human_decision(approval_id, "APPROVED", "HUMAN_HARD", "Approve screenplay revision")
        self.assertEqual(final["state"], "APPROVED")
        # Approved is immutable
        with self.assertRaises(ApprovalPolicyViolationError):
            self.approvals.submit_human_decision(approval_id, "APPROVED", "HUMAN_HARD", "again")


if __name__ == "__main__":
    unittest.main(verbosity=2)
