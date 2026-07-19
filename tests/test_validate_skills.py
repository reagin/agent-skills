from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "scripts" / "validate_skills.py"


def load_validator():
    if not VALIDATOR_PATH.is_file():
        return None
    spec = importlib.util.spec_from_file_location("validate_skills", VALIDATOR_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class ValidatorBootstrapTests(unittest.TestCase):
    def test_validator_module_exists(self):
        self.assertTrue(
            VALIDATOR_PATH.is_file(),
            "scripts/validate_skills.py must provide the repository validator",
        )


@unittest.skipIf(validator is None, "validator module has not been implemented")
class ValidatorBehaviorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        (self.root / "skills").mkdir()
        (self.root / "README.md").write_text(
            "# Test repository\n\n"
            "## Skills\n\n"
            "<!-- skills:start -->\n\n"
            "No skills have been published yet.\n\n"
            "<!-- skills:end -->\n",
            encoding="utf-8",
        )

    def write_skill(
        self,
        directory: str,
        description: str,
        *,
        name: str | None = None,
        extra: str = "",
        body: str = "Follow the requested workflow.",
    ) -> None:
        skill_dir = self.root / "skills" / directory
        skill_dir.mkdir(parents=True)
        lines = [
            "---",
            f"name: {name or directory}",
            f"description: {description}",
        ]
        if extra:
            lines.extend(extra.splitlines())
        lines.extend(["---", "", body, ""])
        (skill_dir / "SKILL.md").write_text("\n".join(lines), encoding="utf-8")

    def write_block_description_skill(self) -> None:
        skill_dir = self.root / "skills" / "code-review"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            "name: code-review\n"
            "description: >-\n"
            "  Reviews code changes.\n"
            "  Use when the user requests a review.\n"
            "---\n\n"
            "Review the supplied changes.\n",
            encoding="utf-8",
        )

    def write_manifests(self, codex_version: str, claude_version: str) -> None:
        for folder, version in (
            (".codex-plugin", codex_version),
            (".claude-plugin", claude_version),
        ):
            manifest_dir = self.root / folder
            manifest_dir.mkdir()
            payload = {
                "name": "agent-skills",
                "version": version,
                "description": "Test skills",
                "skills": "./skills/",
            }
            (manifest_dir / "plugin.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )

    def readme(self) -> str:
        return (self.root / "README.md").read_text(encoding="utf-8")

    def assert_issue(self, expected: str) -> None:
        issues = validator.validate_repository(self.root)
        messages = "\n".join(issue.message for issue in issues)
        self.assertIn(expected, messages)

    def test_valid_skill_passes_and_fix_updates_catalog(self):
        self.write_skill(
            "code-review", "Reviews code changes. Use for review requests."
        )

        issues = validator.validate_repository(self.root, fix=True)

        self.assertEqual([], issues)
        self.assertIn("[code-review](skills/code-review/)", self.readme())

    def test_block_scalar_description_is_supported(self):
        self.write_block_description_skill()

        issues = validator.validate_repository(self.root, fix=True)

        self.assertEqual([], issues)
        self.assertIn("Reviews code changes.", self.readme())

    def test_rejects_directory_name_mismatch(self):
        self.write_skill("code-review", "Reviews code.", name="review-code")

        self.assert_issue("must match directory")

    def test_rejects_unknown_frontmatter_field(self):
        self.write_skill("code-review", "Reviews code.", extra="context: fork")

        self.assert_issue("non-portable frontmatter field")

    def test_rejects_missing_relative_markdown_link(self):
        self.write_skill(
            "code-review",
            "Reviews code.",
            body="See [the guide](references/guide.md).",
        )

        self.assert_issue("referenced file does not exist")

    def test_detects_stale_catalog_without_fix(self):
        self.write_skill("code-review", "Reviews code.")

        self.assert_issue("README skill catalog is stale")

    def test_rejects_mismatched_plugin_versions(self):
        self.write_manifests("0.1.0", "0.2.0")

        self.assert_issue("plugin versions must match")


if __name__ == "__main__":
    unittest.main()
