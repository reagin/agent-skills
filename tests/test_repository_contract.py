from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RepositoryContractTests(unittest.TestCase):
    def test_required_scaffold_and_shared_versions(self):
        required = [
            "AGENTS.md",
            "CLAUDE.md",
            ".gitignore",
            ".codex-plugin/plugin.json",
            ".claude-plugin/plugin.json",
            ".github/workflows/validate-skills.yml",
        ]
        missing = [relative for relative in required if not (ROOT / relative).is_file()]
        self.assertEqual([], missing, f"missing scaffold files: {missing}")

        codex = json.loads(
            (ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8")
        )
        claude = json.loads(
            (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("./skills/", codex["skills"])
        self.assertEqual("./skills/", claude["skills"])
        self.assertEqual(codex["version"], claude["version"])

    def test_agent_rules_require_catalog_sync(self):
        rules_path = ROOT / "AGENTS.md"
        self.assertTrue(rules_path.is_file(), "AGENTS.md is required")
        rules = rules_path.read_text(encoding="utf-8")

        self.assertIn("validate_skills.py --fix", rules)
        self.assertIn("README.md", rules)
        self.assertIn("skill-creator", rules)
        self.assertEqual(
            "@AGENTS.md\n", (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        )

    def test_ci_runs_validator_and_unit_tests(self):
        workflow_path = ROOT / ".github/workflows/validate-skills.yml"
        self.assertTrue(workflow_path.is_file(), "validation workflow is required")
        workflow = workflow_path.read_text(encoding="utf-8")

        self.assertIn("python3 scripts/validate_skills.py", workflow)
        self.assertIn("python3 -m unittest discover -s tests -v", workflow)


if __name__ == "__main__":
    unittest.main()
