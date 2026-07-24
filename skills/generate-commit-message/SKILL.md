---
name: generate-commit-message
description: Generate, revise, or validate English Conventional Commit messages from Git repository changes, diffs, patches, file lists, or user-provided change summaries. Use when asked to draft a commit message, choose a commit type or scope, describe staged or unstaged work, add a breaking-change or issue footer, or split mixed changes into atomic commits. Inspect all uncommitted changes by default, but never stage files or create the commit.
---

# Generate Commit Message

Produce evidence-based commit messages that follow Conventional Commits 1.0.0. Treat every message as a recommendation: inspect changes without modifying the repository, and never run `git add`, `git commit`, or another command that changes Git state.

## Gather the Change Evidence

1. Read applicable repository instructions and explicit commit policies.
2. Use a user-provided diff, patch, file list, or change summary when that is the requested source.
3. Otherwise, verify that the current directory is in a Git worktree and inspect all uncommitted changes:
   - Run `git status --short`.
   - Read both `git diff --cached` and `git diff`, including their `--stat` summaries when the patch is large.
   - List untracked paths with `git ls-files --others --exclude-standard`, then inspect relevant text files. Skip binary, generated, vendored, secret-bearing, or excessively large files and disclose any skipped context that could affect the result.
4. Inspect recent commit subjects only when useful for established scope names or trailer style. Do not copy malformed history or change the default message language from English unless an explicit repository policy or the user requires it.
5. If there are no changes and no usable user-provided description, state that there is not enough change evidence to generate a commit message.

Base the message on the observed behavior and intent of the whole change. Do not infer issue numbers, breaking behavior, migration requirements, or business intent from filenames alone.

## Separate Atomic Changes

Group implementation, tests, documentation, and configuration that support the same intent into one atomic change. Treat accompanying tests as part of a feature or fix rather than as a separate `test` commit.

Recommend multiple commits when the working tree contains independently useful or unrelated changes, such as:

- a feature and an unrelated bug fix;
- mechanical refactoring mixed with behavior changes;
- unrelated documentation or dependency maintenance;
- changes that require different commit types or scopes.

For mixed changes, return a numbered split proposal. For each proposed commit, identify the included paths or change group and provide one complete candidate message. Do not stage, move, or commit the groups.

## Choose the Type

Choose the type from the primary intent, not merely from the files changed:

| Type | Use for |
| --- | --- |
| `feat` | Add a new user-facing or developer-facing capability |
| `fix` | Correct incorrect behavior or a defect |
| `perf` | Improve performance without changing intended behavior |
| `refactor` | Restructure code without adding a feature or fixing a defect |
| `docs` | Change documentation or comments only |
| `style` | Change formatting or style without affecting behavior |
| `test` | Add or change tests without a corresponding production change |
| `build` | Change dependencies, packaging, or the build system |
| `ci` | Change continuous-integration or delivery configuration |
| `chore` | Perform maintenance not covered by another type |
| `revert` | Revert one or more earlier commits |

Prefer the most specific supported type. Use `chore` only as a fallback.

## Compose the Message

Use this structure:

```text
<type>[optional scope][optional !]: <description>

[optional body]

[optional footer(s)]
```

Apply these rules:

- Use a lowercase type.
- Add a short noun scope in parentheses only when one coherent codebase area is clear, such as `api`, `auth`, or `parser`. Omit the scope when it would be guessed, overly broad, or misleading.
- Write the description in concise imperative English. Start with a lowercase verb, describe the resulting change, and omit the final period.
- Keep a simple change to the header alone.
- Add a body only when it materially explains motivation, important behavior, or a non-obvious before/after distinction. Separate it from the header with one blank line and do not repeat the header.
- Add footers only when supported by the change evidence or user-provided context. Use Git-trailer-compatible forms such as `Refs: #123` or `Closes #123`.
- Mark a breaking change with `!` immediately before the colon. Add a `BREAKING CHANGE: <description>` footer when migration impact or replacement behavior needs explanation. Never label an internal refactor as breaking without evidence of an incompatible public contract.

Example of a simple message:

```text
fix(parser): prevent duplicate option parsing
```

Example with a body and footers:

```text
feat(api)!: require scoped access tokens

Reject legacy unscoped tokens during authentication.

BREAKING CHANGE: Existing clients must request a scoped token.
Refs: #123
```

## Return the Result

For one atomic change, return exactly one fenced text block containing the final commit message and no preamble or explanation.

For a proposed split, return only the numbered groups, their included paths or change descriptions, and one fenced text block per group. Keep supporting prose minimal.

When revising or validating an existing message, preserve its supported intent, correct any structural or wording problems, and return the corrected message in the same output format. Ask one concise question only when missing context would materially change the type, breaking-change marker, or footer; otherwise produce the best evidence-based result.

The message rules are based on [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and the practical type and wording guidance in [Git 提交规范指南](https://www.liuvv.com/p/b728a06f.html).
