import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_instruction_repository import (
    _find_cycles,
    _resolve_dependency,
    _resolve_markdown_link,
    _validate_status_contracts,
    _validate_reference_catalogues,
    expected_operations,
    parse_frontmatter,
    registry_operations,
    validate,
)


ROOT = Path(__file__).resolve().parents[1]


class FrontMatterTests(unittest.TestCase):
    def test_valid_yaml_front_matter_parses(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "valid.md"
            path.write_text(
                "---\nprompt_id: TEST_VALID\nversion: 1.0.0\n"
                "dependencies: [CORE_SYSTEM]\n---\n# Body\n",
                encoding="utf-8",
            )
            metadata, body, error = parse_frontmatter(path)
        self.assertIsNone(error)
        self.assertEqual(metadata["prompt_id"], "TEST_VALID")
        self.assertIn("# Body", body)

    def test_invalid_yaml_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.md"
            path.write_text("---\nprompt_id: [unfinished\n---\n", encoding="utf-8")
            metadata, _, error = parse_frontmatter(path)
        self.assertIsNone(metadata)
        self.assertIn("invalid YAML", error)

    def test_missing_front_matter_delimiter_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "missing.md"
            path.write_text("# No metadata\n", encoding="utf-8")
            metadata, _, error = parse_frontmatter(path)
        self.assertIsNone(metadata)
        self.assertIn("missing opening", error)


class DependencyTests(unittest.TestCase):
    def test_dependency_cycles_are_detected(self):
        graph = {"A": {"B"}, "B": {"C"}, "C": {"A"}}
        self.assertEqual(_find_cycles(graph), [["A", "B", "C", "A"]])

    def test_dependency_resolves_prompt_id_and_file_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "MODES" / "MODE.md"
            target = root / "CORE" / "RULE.md"
            source.parent.mkdir()
            target.parent.mkdir()
            source.touch()
            target.touch()
            self.assertEqual(_resolve_dependency("CORE_RULE", source, root, {"CORE_RULE": target}), target)
            self.assertEqual(_resolve_dependency("CORE/RULE.md", source, root, {}), target)
            self.assertIsNone(_resolve_dependency("MISSING", source, root, {}))

    def test_internal_markdown_links_resolve_relative_and_root_paths(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "DOCS" / "guide.md"
            relative_target = root / "DOCS" / "details.md"
            root_target = root / "CORE" / "policy.md"
            source.parent.mkdir()
            root_target.parent.mkdir()
            source.touch()
            relative_target.touch()
            root_target.touch()
            self.assertEqual(_resolve_markdown_link("details.md#section", source, root), relative_target)
            self.assertEqual(_resolve_markdown_link("/CORE/policy.md", source, root), root_target)
            self.assertIsNone(_resolve_markdown_link("https://example.test", source, root))


class ContractTests(unittest.TestCase):
    def test_schema_status_vocabularies_are_consistent(self):
        self.assertEqual(_validate_status_contracts(ROOT), [])

    def test_registry_matches_routes_and_registered_mcp_tools(self):
        self.assertEqual(
            expected_operations(ROOT),
            registry_operations(ROOT / "DOCS/CAPABILITY_REGISTRY.md"),
        )

    def test_complete_instruction_repository_passes(self):
        findings, summary = validate(ROOT)
        self.assertGreater(summary["governed_markdown_files"], 0)
        self.assertEqual(findings, [])


    def test_genre_style_tool_and_asset_registries_validate(self):
        self.assertEqual(_validate_reference_catalogues(ROOT), [])

    def test_project_schema_keeps_genre_and_channel_style_separate(self):
        schema = json.loads((ROOT / "SCHEMAS/PROJECT.schema.json").read_text(encoding="utf-8"))
        properties = schema["properties"]
        self.assertIn("primary_genre_id", properties)
        self.assertIn("secondary_genre_ids", properties)
        self.assertIn("channel_style_id", properties)
        self.assertNotIn("channel_style_id", properties["genre"])

    def test_screenplay_context_manifest_records_profile_versions(self):
        schema = json.loads((ROOT / "SCHEMAS/SCREENPLAY_CONTEXT.schema.json").read_text(encoding="utf-8"))
        required = set(schema["required"])
        self.assertTrue({"primary_genre", "secondary_genres", "channel_style", "screenwriter_instruction"} <= required)
        self.assertTrue({"version", "content_hash_sha256", "source_path"} <= set(schema["$defs"]["profileRef"]["required"]))


if __name__ == "__main__":
    unittest.main()
