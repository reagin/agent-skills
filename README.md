# Personal Agent Skills

A focused, public skills repository for personal development with Codex and Claude Code. Skills are authored once, kept portable by default, and managed primarily through [CC Switch](https://github.com/farion1231/cc-switch).

## Design principles

- Keep `skills/` as the single source of truth.
- Target the shared Agent Skills format supported by Codex and Claude Code.
- Put platform-specific metadata beside a skill only when the shared format is insufficient.
- Let CC Switch handle discovery, installation, updates, and synchronization.
- Keep plugin manifests as lightweight fallback distribution entry points.
- Add files and directories only when a real skill needs them.
- Keep repository documentation synchronized whenever a skill changes.

## Repository layout

```text
.
├── .claude-plugin/plugin.json # Claude Code fallback plugin manifest
├── .codex-plugin/plugin.json  # Codex fallback plugin manifest
├── .github/workflows/         # Continuous validation
├── scripts/                   # Repository-level validation tooling
├── skills/                    # Canonical skill sources
├── tests/                     # Validator tests
├── AGENTS.md                  # Shared agent authoring rules
├── CLAUDE.md                  # Claude Code entry point for shared rules
└── README.md                  # Repository guide and skill catalog
```

Each published skill lives at `skills/<skill-name>/SKILL.md`. Optional runtime companions (`scripts/`, `references/`, `assets/`, `agents/openai.yaml`) belong inside that skill and are created only when needed. Local `skill-creator` evaluation artifacts live at `skills/<skill-name>/workspace/` and `skills/<skill-name>/evals/` and are gitignored — do not commit them. See [`AGENTS.md`](AGENTS.md) for authoring rules.

## Distribution model

CC Switch is the primary manager. Register this public GitHub repository as a custom skill repository, then let CC Switch install selected skills into its single source-of-truth directory and synchronize them to Codex and Claude Code using symlinks or copies.

The Codex and Claude Code plugin manifests both point to the same `skills/` directory. They exist as direct-install fallbacks and do not introduce hooks, MCP servers, marketplaces, or client-specific copies of skills.

## Skills

<!-- skills:start -->

| Skill | Description |
| --- | --- |
| [apple-design](skills/apple-design/SKILL.md) | Apple's approach to interface design and fluid, physical motion, translated for the web. Use when building or reviewing gesture-driven UI, spring animations, drag/swipe/sheet interactions, momentum and interruptible transitions, translucent materials and depth, typography (optical sizing, tracking, leading), reduced-motion, or the design foundations (feedback, spatial consistency, restraint) behind Apple-style interfaces. |
| [frontend-file-structure](skills/frontend-file-structure/SKILL.md) | Use for React TypeScript file-structure work involving ownership or folders for new or moved files, multi-file components with narrow public entries, page and route separation, mirrored tests, path naming, import aliases, or directory-tree review. Trigger only when placement is unresolved or structure must change. Do not use for UI, logic, performance, security, upgrades, or debugging, or for code and tests whose path and structure are already established. |
| [generate-commit-message](skills/generate-commit-message/SKILL.md) | Generate, revise, or validate English Conventional Commit messages from Git repository changes, diffs, patches, file lists, or user-provided change summaries. Use when asked to draft a commit message, choose a commit type or scope, describe staged or unstaged work, add a breaking-change or issue footer, or split mixed changes into atomic commits. Inspect all uncommitted changes by default, but never stage files or create the commit. |
| [grill-me](skills/grill-me/SKILL.md) | A relentless interview to sharpen a plan, decision, or design. Use when the user wants to stress-test their thinking or uses any "grill" trigger phrase such as "grill me", "grill my plan", or "poke holes in this". |

<!-- skills:end -->

This catalog is generated from skill frontmatter. Run `python3 scripts/validate_skills.py --fix` after adding, modifying, renaming, or removing a skill. Continuous integration runs the validator without `--fix` and rejects stale catalog entries.

## Skill lifecycle

When using `skill-creator` to create or improve a skill:

1. Store the skill under `skills/<skill-name>/` and keep `SKILL.md` as its entry point.
2. Prefer shared `name` and `description` metadata that works in both Codex and Claude Code.
3. Add platform-specific metadata only when the skill genuinely requires it.
4. Keep `skill-creator` eval workspaces and `evals/` specs under the skill directory; both paths are gitignored and must not be committed. Do not use sibling `*-workspace/` directories.
5. Update this catalog with the repository validator.
6. Bump both fallback plugin manifests to the same version when the distributed skill set changes.
7. Run the validator and its tests before considering the skill complete.

Version fallback plugins consistently:

- Patch: backward-compatible fixes or improvements.
- Minor: a new skill or backward-compatible capability.
- Major: a removal, rename, or other breaking change.

## Validation contract

The repository validator is dependency-free and checks:

- kebab-case skill directory names;
- required and matching `name` and `description` frontmatter;
- duplicate skill names;
- portable shared frontmatter fields;
- missing local files referenced by a skill;
- agreement between the skill catalog and filesystem;
- matching Codex and Claude Code plugin versions.

An empty `skills/` directory is valid during repository initialization.
