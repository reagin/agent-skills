#!/usr/bin/env python3
"""Validate portable Agent Skills and synchronize the README catalog."""

import argparse
import ast
from dataclasses import dataclass
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import unquote


PORTABLE_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_PATTERN = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)
TOP_LEVEL_FIELD_PATTERN = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):(?:[ \t]*(.*))?$")
MARKDOWN_LINK_PATTERN = re.compile(
    r"!?\[[^\]]*\]\((?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\)"
)
CATALOG_START = "<!-- skills:start -->"
CATALOG_END = "<!-- skills:end -->"


@dataclass(frozen=True)
class Issue:
    path: Path
    message: str


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    directory: Path


def _decode_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        try:
            decoded = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value[1:-1]
        return str(decoded)
    return value


def _block_scalar(lines: Sequence[str], start: int, folded: bool) -> Tuple[str, int]:
    values: List[str] = []
    index = start
    while index < len(lines):
        line = lines[index]
        if line and not line[0].isspace():
            break
        values.append(line.strip())
        index += 1

    if folded:
        value = " ".join(part for part in values if part)
    else:
        value = "\n".join(values).strip()
    return value, index


def _parse_frontmatter(path: Path) -> Tuple[Dict[str, Optional[str]], str, List[Issue]]:
    issues: List[Issue] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return {}, "", [Issue(path, f"cannot read UTF-8 SKILL.md: {error}")]

    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "", [Issue(path, "SKILL.md must start with YAML frontmatter")]

    try:
        closing_index = next(
            index for index in range(1, len(lines)) if lines[index].strip() == "---"
        )
    except StopIteration:
        return {}, "", [Issue(path, "YAML frontmatter is missing its closing delimiter")]

    frontmatter_lines = lines[1:closing_index]
    fields: Dict[str, Optional[str]] = {}
    index = 0
    while index < len(frontmatter_lines):
        line = frontmatter_lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[0].isspace():
            issues.append(Issue(path, f"unexpected indented frontmatter content: {line.strip()}"))
            index += 1
            continue

        match = TOP_LEVEL_FIELD_PATTERN.match(line)
        if not match:
            issues.append(Issue(path, f"invalid top-level frontmatter line: {line}"))
            index += 1
            continue

        key, raw_value = match.group(1), (match.group(2) or "")
        if key in fields:
            issues.append(Issue(path, f"duplicate frontmatter field: {key}"))

        if raw_value in {"|", "|-", "|+", ">", ">-", ">+"}:
            value, index = _block_scalar(
                frontmatter_lines, index + 1, raw_value.startswith(">")
            )
            fields[key] = value
            continue

        fields[key] = _decode_scalar(raw_value) if raw_value else None
        index += 1

        if key == "metadata":
            while index < len(frontmatter_lines):
                nested = frontmatter_lines[index]
                if nested and not nested[0].isspace():
                    break
                index += 1

    body = "\n".join(lines[closing_index + 1 :]).strip()
    return fields, body, issues


def _validate_local_links(skill_dir: Path, skill_md: Path, body: str) -> List[Issue]:
    issues: List[Issue] = []
    root = skill_dir.resolve()
    for match in MARKDOWN_LINK_PATTERN.finditer(body):
        raw_target = match.group(1) or match.group(2) or ""
        target = unquote(raw_target).split("#", 1)[0].split("?", 1)[0]
        if not target or target.startswith(("#", "/", "//")):
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
            continue

        resolved = (skill_dir / target).resolve()
        try:
            resolved.relative_to(root)
        except ValueError:
            issues.append(Issue(skill_md, f"local reference escapes the skill directory: {raw_target}"))
            continue
        if not resolved.exists():
            issues.append(Issue(skill_md, f"referenced file does not exist: {raw_target}"))
    return issues


def _validate_skill(skill_dir: Path) -> Tuple[Optional[Skill], List[Issue]]:
    skill_md = skill_dir / "SKILL.md"
    issues: List[Issue] = []
    directory_name = skill_dir.name

    if not NAME_PATTERN.fullmatch(directory_name) or len(directory_name) > 64:
        issues.append(
            Issue(
                skill_dir,
                "skill directory must be 1-64 characters of lowercase letters, numbers, and single hyphens",
            )
        )
    if not skill_md.is_file():
        issues.append(Issue(skill_dir, "skill directory must contain SKILL.md"))
        return None, issues

    fields, body, parse_issues = _parse_frontmatter(skill_md)
    issues.extend(parse_issues)

    for field in sorted(set(fields) - PORTABLE_FIELDS):
        issues.append(Issue(skill_md, f"non-portable frontmatter field: {field}"))

    name = fields.get("name") or ""
    description = fields.get("description") or ""
    compatibility = fields.get("compatibility")

    if not name:
        issues.append(Issue(skill_md, "required frontmatter field is missing or empty: name"))
    elif not NAME_PATTERN.fullmatch(name) or len(name) > 64:
        issues.append(Issue(skill_md, "name must satisfy the Agent Skills naming rules"))
    elif name != directory_name:
        issues.append(Issue(skill_md, f"name '{name}' must match directory '{directory_name}'"))

    if not description:
        issues.append(
            Issue(skill_md, "required frontmatter field is missing or empty: description")
        )
    elif len(description) > 1024:
        issues.append(Issue(skill_md, "description must not exceed 1024 characters"))

    if compatibility is not None and not 1 <= len(compatibility) <= 500:
        issues.append(Issue(skill_md, "compatibility must contain 1-500 characters"))

    if not body:
        issues.append(Issue(skill_md, "SKILL.md must contain instructions after frontmatter"))
    else:
        issues.extend(_validate_local_links(skill_dir, skill_md, body))

    if not name or not description:
        return None, issues
    return Skill(name=name, description=" ".join(description.split()), directory=skill_dir), issues


def discover_skills(root: Path) -> Tuple[List[Skill], List[Issue]]:
    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        return [], [Issue(skills_dir, "canonical skills directory does not exist")]

    skills: List[Skill] = []
    issues: List[Issue] = []
    seen_names: Dict[str, Path] = {}
    for entry in sorted(skills_dir.iterdir(), key=lambda path: path.name):
        if not entry.is_dir() or entry.name.endswith("-workspace"):
            continue
        skill, skill_issues = _validate_skill(entry)
        issues.extend(skill_issues)
        if skill is None:
            continue
        if skill.name in seen_names:
            issues.append(
                Issue(
                    entry,
                    f"duplicate skill name '{skill.name}' also used by {seen_names[skill.name]}",
                )
            )
        else:
            seen_names[skill.name] = entry
            skills.append(skill)
    return skills, issues


def render_catalog(skills: Sequence[Skill]) -> str:
    if not skills:
        return "No skills have been published yet."

    rows = ["| Skill | Description |", "| --- | --- |"]
    for skill in sorted(skills, key=lambda item: item.name):
        description = skill.description.replace("|", "\\|")
        rows.append(
            f"| [{skill.name}](skills/{skill.directory.name}/) | {description} |"
        )
    return "\n".join(rows)


def _validate_catalog(root: Path, skills: Sequence[Skill], fix: bool) -> List[Issue]:
    readme = root / "README.md"
    try:
        content = readme.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [Issue(readme, f"cannot read repository README: {error}")]

    if content.count(CATALOG_START) != 1 or content.count(CATALOG_END) != 1:
        return [Issue(readme, "README must contain one skills catalog marker pair")]

    start = content.index(CATALOG_START) + len(CATALOG_START)
    end = content.index(CATALOG_END, start)
    expected = f"\n\n{render_catalog(skills)}\n\n"
    if content[start:end] == expected:
        return []
    if fix:
        readme.write_text(content[:start] + expected + content[end:], encoding="utf-8")
        return []
    return [Issue(readme, "README skill catalog is stale; run validator with --fix")]


def _load_manifest(path: Path) -> Tuple[Optional[dict], List[Issue]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return None, [Issue(path, f"cannot read plugin manifest: {error}")]
    if not isinstance(payload, dict):
        return None, [Issue(path, "plugin manifest root must be a JSON object")]
    return payload, []


def _validate_manifests(root: Path) -> List[Issue]:
    codex_path = root / ".codex-plugin" / "plugin.json"
    claude_path = root / ".claude-plugin" / "plugin.json"
    if not codex_path.exists() and not claude_path.exists():
        return []
    if not codex_path.is_file() or not claude_path.is_file():
        return [Issue(root, "Codex and Claude Code plugin manifests must both exist")]

    codex, issues = _load_manifest(codex_path)
    claude, claude_issues = _load_manifest(claude_path)
    issues.extend(claude_issues)
    if codex is None or claude is None:
        return issues

    for path, payload in ((codex_path, codex), (claude_path, claude)):
        if payload.get("skills") != "./skills/":
            issues.append(Issue(path, "plugin skills path must be './skills/'"))
        version = payload.get("version")
        if not isinstance(version, str) or not SEMVER_PATTERN.fullmatch(version):
            issues.append(Issue(path, "plugin version must use semantic versioning"))

    if codex.get("version") != claude.get("version"):
        issues.append(Issue(root, "Codex and Claude Code plugin versions must match"))
    return issues


def validate_repository(root: Path, fix: bool = False) -> List[Issue]:
    root = root.resolve()
    skills, issues = discover_skills(root)
    issues.extend(_validate_catalog(root, skills, fix))
    issues.extend(_validate_manifests(root))
    return issues


def _display_path(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the validator's parent repository)",
    )
    parser.add_argument(
        "--fix", action="store_true", help="rewrite the generated README skill catalog"
    )
    args = parser.parse_args(argv)

    issues = validate_repository(args.root, fix=args.fix)
    if issues:
        for issue in issues:
            print(f"{_display_path(issue.path, args.root)}: {issue.message}", file=sys.stderr)
        return 1

    skills, _ = discover_skills(args.root.resolve())
    print(f"Validated {len(skills)} skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
