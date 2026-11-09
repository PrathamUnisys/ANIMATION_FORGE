"""CR_006 tests: Story Bible, Episode Brief, provider, staged generation, QC."""
import os
import sys
import tempfile
import shutil
import unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from backend.database import DatabaseManager
from backend.governance.rule_loader import GovernanceEngine
from backend.governance.approval_engine import ApprovalEngine
from backend.providers.manager import ProviderManager, SecureCredentialVault, ProviderError
from backend.departments.story_context import StoryContextService, BibleTransitionError
from backend.departments.story_pipeline import StoryAndScreenplayPipeline
from backend.qc.screenplay_qc import DeterministicValidator, CreativeCritique

class CR006TestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="af_cr006_")
        cls.db_path = os.path.join(cls.temp_dir, "test_cr006.db")
        cls.db = DatabaseManager(cls.db_path)
        cls.governance = GovernanceEngine(ROOT, cls.db)
        cls.approvals = ApprovalEngine(cls.db)
        cls.providers = ProviderManager(cls.db, SecureCredentialVault())
        cls.ctx = StoryContextService(ROOT, cls.db)
        cls.pipe = StoryAndScreenplayPipeline(ROOT, cls.db, cls.approvals)
        # Minimal project/series rows (no demo runner)
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        with cls.db.get_connection() as conn:
            conn.execute(
                """INSERT OR IGNORE INTO projects
                   (project_id, title, synopsis, genre, target_audience, intended_runtime_sec, language, creative_brief, visual_direction, animation_technique, production_goals_json, restrictions_json, status, current_stage, active_mode, series_id, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '[]', '[]', 'ACTIVE', 'USER_STORY_IDEA', 'PRODUCTION_MODE', ?, ?, ?)""",
                ("PROJECT_CR006", "Pilot", "Pilot premise", "Fantasy", "General", 300, "en-US", "", "", "2D", "SER_CR006", now, now),
            )
            conn.execute(
                "INSERT OR IGNORE INTO series (series_id, title, bible_json, created_at) VALUES (?, ?, ?, ?)",
                ("SER_CR006", "Pilot Series", "{}", now),
            )
            conn.commit()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def test_b01_bible_create_hash_and_revision(self):
        content = {"series_id": "SER_CR006", "title": "Pilot", "premise": "A bell rings", "genre": "Fantasy", "format": "Short", "world": {"overview": "St Jude"}, "characters": [{"id": "C1", "name": "MARROW", "role": "lead", "motivation": "find witness", "goal": "stop the bell", "flaw": "doubt", "fear": "dark"}]}
        res = self.ctx.create_bible("SER_CR006", content, "PROJECT_CR006", "DRAFT", "HUMAN_OWNER")
        self.assertEqual(res["revision"], 1)
        self.assertEqual(len(res["content_hash_sha256"]), 64)
        got = self.ctx.get_bible("SER_CR006")
        self.assertEqual(got["content"]["premise"], "A bell rings")
        revs = self.ctx.list_bible_revisions("SER_CR006")
        self.assertEqual(len(revs), 1)

    def test_b02_ai_cannot_auto_approve_canon(self):
        with self.assertRaises(BibleTransitionError):
            self.ctx.create_bible("SER_CR006", {"series_id": "SER_CR006", "title": "t", "premise": "p", "genre": "Fantasy", "format": "Short", "world": {}, "characters": []}, status="APPROVED")
        res = self.ctx.create_bible("SER_CR006", {"series_id": "SER_CR006", "title": "t2", "premise": "p2", "genre": "Fantasy", "format": "Short", "world": {}, "characters": []}, status="PROPOSED", created_by="SCREENWRITER")
        with self.assertRaises(BibleTransitionError):
            self.ctx.transition_bible(res["bible_revision_id"], "APPROVED", "SCREENWRITER", human_confirmed=False)
        # Human-confirmed path works
        self.ctx.transition_bible(res["bible_revision_id"], "DRAFT", "HUMAN_OWNER", human_confirmed=False)
        self.ctx.transition_bible(res["bible_revision_id"], "IN_REVIEW", "HUMAN_OWNER", human_confirmed=False)
        self.ctx.transition_bible(res["bible_revision_id"], "APPROVED", "HUMAN_WINDOWS_TEST", human_confirmed=True)
        self.assertIsNotNone(self.ctx.get_approved_canon("SER_CR006"))

    def test_b03_brief_persistence_and_genre_validation(self):
        brief = {
            "project_id": "PROJECT_CR006", "episode_id": "EP001", "title": "Bell", "premise": "Bell rings",
            "synopsis": "s", "primary_genre_id": "GENRE_FANTASY", "secondary_genre_ids": ["GENRE_COMEDY"],
            "protagonist": "MARROW", "objective": "Stop the bell", "conflict": "Wardens", "stakes": "Town fate",
            "ending_direction": "Bell silenced", "characters": ["MARROW"], "locations": ["Bell Tower"],
            "clues_and_reveals": ["Inscription"], "required_beats": ["Bell tolls"],
        }
        res = self.ctx.create_brief("PROJECT_CR006", brief, episode_id="EP001")
        self.assertEqual(res["revision"], 1)
        got = self.ctx.get_brief("PROJECT_CR006", "EP001")
        self.assertEqual(got["content"]["objective"], "Stop the bell")
        with self.assertRaises(ValueError):
            self.ctx.create_brief("PROJECT_CR006", {**brief, "primary_genre_id": "GENRE_UNKNOWN"}, episode_id="EP002")

    def test_b04_provider_mock_determinism_and_no_fake_usage(self):
        a = self.providers.generate_text("PROJECT_CR006", "DETERMINISTIC_MOCK", "mock-42", "JSON please")
        b = self.providers.generate_text("PROJECT_CR006", "DETERMINISTIC_MOCK", "mock-42", "JSON please")
        self.assertEqual(a["status"], "MOCK")
        self.assertEqual(a["content"], b["content"])
        with self.db.get_connection() as conn:
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM provider_usage WHERE project_id='PROJECT_CR006'").fetchone()[0], 0)

    def test_b05_provider_failure_is_explicit_not_fallback(self):
        # Ollama may be running (opencode local provider installed).
        # Success means LIVE with real content; failure must be explicit, never a fake fallback.
        try:
            result = self.providers.generate_text("PROJECT_CR006", "OLLAMA_OPENAI_COMPATIBLE", "ornith:9b", "hello", timeout_sec=10)
            self.assertEqual(result["status"], "LIVE")
            self.assertTrue(len(result["content"]) > 0)
        except ProviderError as exc:
            self.assertIn(exc.category, {"CONNECTION_ERROR", "TIMEOUT", "HTTP_ERROR", "INVALID_RESPONSE", "INVALID_JSON", "SCHEMA_VALIDATION", "AUTHENTICATION", "RATE_LIMIT", "NOT_CONFIGURED", "UNSUPPORTED", "UNKNOWN"})

    def test_b06_context_assembly_exact_genre_and_hash(self):
        ctx = self.ctx.assemble_context("PROJECT_CR006", "EP001", "SER_CR006", "GENRE_FANTASY", ["GENRE_COMEDY"], None)
        self.assertEqual(ctx["manifest"]["primary_genre"]["profile_id"], "GENRE_FANTASY")
        self.assertEqual(len(ctx["manifest"]["context_hash_sha256"]), 64)
        self.assertIsNotNone(ctx["brief"])
        self.assertIsNotNone(ctx["canon"])

    def test_b07_staged_generation_end_to_end_mock(self):
        brief = self.ctx.get_brief("PROJECT_CR006", "EP001")["content"]
        canon = self.ctx.get_approved_canon("SER_CR006")["content"]
        prov = "DETERMINISTIC_MOCK"
        analysis = self.pipe.generate_story_analysis("PROJECT_CR006", "EP001", brief, canon, self.providers, prov, "mock-42")
        self.assertIn("dramatic_engine", analysis["analysis"])
        hooks = self.pipe.generate_hooks("PROJECT_CR006", "EP001", analysis["analysis"], brief, self.providers, prov, "mock-42")
        self.assertEqual(len(hooks["hooks"]["hooks"]), 3)
        outline = self.pipe.generate_outline("PROJECT_CR006", "EP001", analysis["analysis"], brief, self.providers, prov, "mock-42")
        self.assertIn("acts", outline["outline"])
        with self.assertRaises(PermissionError):
            self.pipe.approve_outline("PROJECT_CR006", "EP001", human_confirmed=False)
        self.pipe.approve_outline("PROJECT_CR006", "EP001", human_confirmed=True)
        cards = self.pipe.generate_scene_cards("PROJECT_CR006", "EP001", outline["outline"], brief, self.providers, prov, "mock-42")
        self.assertEqual(len(cards["scene_cards"]), 5)
        scr = self.pipe.generate_screenplay("PROJECT_CR006", "EP001", cards["scene_cards"], brief, canon, "Bell", "General", 60, self.providers, prov, "mock-42")
        self.assertIn("INT.", scr["markdown"])
        self.assertIn("PROTAGONIST:", scr["markdown"])
        retention = self.pipe.generate_retention_map("PROJECT_CR006", "EP001", cards["scene_cards"])
        self.assertEqual(len(retention["retention_map"]["entries"]), 5)

    def test_b08_deterministic_qc_catches_placeholder_and_pass(self):
        scr = self.pipe.generate_screenplay(
            "PROJECT_CR006", "EP001",
            self.pipe.get_artifact("PROJECT_CR006", "EP001", "SCENE_CARDS")["content"],
            self.ctx.get_brief("PROJECT_CR006", "EP001")["content"],
            self.ctx.get_approved_canon("SER_CR006")["content"],
            "Bell2", "General", 60, self.providers, "DETERMINISTIC_MOCK", "mock-42",
        )
        validator = DeterministicValidator(self.db)
        report = validator.validate("PROJECT_CR006", scr["script_id"], self.ctx.get_brief("PROJECT_CR006", "EP001")["content"], self.ctx.get_approved_canon("SER_CR006")["content"])
        self.assertIn("checks", report)
        self.assertFalse(report["grants_creative_approval"])
        critic = CreativeCritique(self.db, self.providers)
        creport = critic.critique("PROJECT_CR006", scr["script_id"], "DETERMINISTIC_MOCK", "mock-42")
        self.assertTrue(len(creport["findings"]) >= 1)
        self.assertFalse(creport["grants_creative_approval"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
