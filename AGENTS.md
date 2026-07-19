# Repository Instructions

## Purpose

This is a public personal skills repository for Codex and Claude Code. CC Switch is the primary manager. Keep `skills/` as the only skill source; the two plugin manifests are lightweight fallback distribution entry points.

## Skill authoring

- Create each published skill at `skills/<skill-name>/SKILL.md`.
- Use lowercase kebab-case for the directory and make it match the frontmatter `name`.
- Keep one portable `SKILL.md` for both Codex and Claude Code.
- Use only the shared top-level fields `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`.
- Put Codex-specific UI or dependency metadata in `agents/openai.yaml` inside the skill when needed.
- Add `scripts/`, `references/`, `assets/`, and `evals/` only when the skill actually uses them.
- Keep temporary `skill-creator` evaluation workspaces beside the skill as `<skill-name>-workspace/`; they are ignored by Git.

## Skill lifecycle synchronization

Use `skill-creator` for skill creation and improvement when it is requested or applicable. A skill change is not complete until repository information is synchronized.

After adding, modifying, renaming, or removing a skill:

1. Run `python3 scripts/validate_skills.py --fix` to update the generated Skills section in `README.md`.
2. If distributed skill content changed, update both `.codex-plugin/plugin.json` and `.claude-plugin/plugin.json` to the same version.
3. Use a patch version for compatible fixes, a minor version for a new skill or compatible capability, and a major version for removals, renames, or breaking changes.
4. Run `python3 scripts/validate_skills.py`.
5. Run `python3 -m unittest discover -s tests -v`.
6. Review `git diff --check` and the final diff before declaring the skill complete.

Do not maintain a second skill registry. CC Switch and both plugin formats discover skills from the filesystem; only the human-facing catalog in `README.md` is generated.

## Repository validation

The validator has no third-party dependencies. It enforces the portable Agent Skills frontmatter, verifies local Markdown references, keeps the README catalog synchronized, and checks that fallback plugin versions agree.

An empty `skills/` directory is valid while the repository has no published skills.
