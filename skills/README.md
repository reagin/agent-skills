# Skills

This directory is the canonical source for every published skill in this repository. CC Switch scans the repository recursively for `SKILL.md`, while this project intentionally accepts published skills only at `skills/<skill-name>/SKILL.md`.

## Minimal skill

```text
skills/
└── skill-name/
    └── SKILL.md
```

`skill-name` must use lowercase kebab-case and must match the `name` field in `SKILL.md`.

Use only the portable Agent Skills frontmatter fields by default:

- `name` and `description` (required)
- `license`, `compatibility`, `metadata`, and `allowed-tools` (optional)

Create `scripts/`, `references/`, `assets/`, `agents/openai.yaml`, or evaluation files inside an individual skill only when that skill needs them. Do not create empty resource directories or example skills to reserve future structure.

After any skill lifecycle change, follow the synchronization checklist in [`AGENTS.md`](../AGENTS.md).
