# Repository Instructions

## Purpose

This is a public personal skills repository for Codex and Claude Code. CC Switch is the primary manager. Keep `skills/` as the only skill source; the two plugin manifests are lightweight fallback distribution entry points.

## Skill authoring

`skills/` contains only skill directories—no top-level README or sibling workspace folders. CC Switch scans recursively for `SKILL.md`, but this repository accepts published skills only at `skills/<skill-name>/SKILL.md`.

```text
skills/
└── skill-name/
    ├── SKILL.md
    ├── agents/openai.yaml   # optional; Codex UI / invocation extras
    ├── assets/              # optional; only when the skill needs them
    ├── references/          # optional; only when SKILL.md links them
    ├── scripts/             # optional; only when the skill runs them
    ├── evals/               # optional; skill-creator eval specs (gitignored)
    └── workspace/           # optional; skill-creator eval workspace (gitignored)
```

- Use lowercase kebab-case for the directory and make it match the frontmatter `name`.
- Keep one portable `SKILL.md` for both Codex and Claude Code.
- Use only the shared top-level fields `name`, `description`, `license`, `compatibility`, `metadata`, and `allowed-tools`.
- Put Codex-specific UI or dependency metadata in `agents/openai.yaml` inside the skill when needed.
- Publish only what the skill needs at runtime: typically `SKILL.md`, plus optional `agents/`, `scripts/`, `references/`, or `assets/`. Do not create empty resource directories to reserve structure.
- Keep `skill-creator` evaluation artifacts local and untracked: `skills/<skill-name>/workspace/` and `skills/<skill-name>/evals/` are gitignored. Do not place `<skill-name>-workspace/` beside the skill.
- When a skill interviews the user, try the host structured-input tool for option cards (`request_user_input`, `AskUserQuestion`, or equivalent); if unavailable, fall back to A/B/C in chat and allow a free-form answer.

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
