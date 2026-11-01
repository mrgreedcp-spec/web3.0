# Agent guidelines

These rules apply to every coding agent working in this repository (Claude Code, Codex, Cursor, and others).
Where a rule can be checked mechanically, it is also enforced by a hook, listed at the end of this file.

## Writing style

- Never use the em dash (U+2014).
  Use a plain dash "-" instead.
  This applies to code, comments, user-facing output, docs, commit messages, and PR descriptions.
- When writing or substantially editing long Markdown files, put each full sentence on its own line.
  Preserve normal Markdown structure (headings, lists, tables, code blocks), but never wrap multiple sentences onto one physical line.

## Git and generated files

- When writing commit messages, never add your agent name as a co-author.
  No `Co-Authored-By:` trailer naming an agent, model, or tool.
- Never manually modify `CHANGELOG.md` or any file marked as auto-generated (for example a header saying "auto-generated", "@generated", or "DO NOT EDIT").
  Change the source or the generator instead, then regenerate.

## Technical decisions

- Do not give much weight to development cost when choosing an approach.
- Prefer quality, simplicity, robustness, scalability, and long-term maintainability.
- A larger change that leaves the code simpler and correct beats a quick patch that leaves a trap for later.

## Bug fixes

- Always start by reproducing the bug end to end, as closely aligned with how an end user hits it as possible.
  For the CLI tools here, that means running the real script against realistic input, not just calling one function.
- Only then write the fix, and rerun the same reproduction to show it is gone.
- This makes sure you find the real problem, so the fix actually solves it.

## End-to-end testing and polish

- When testing a product end to end, be picky about the UI and output you see, and aim for pixel perfection.
  For this repository that includes the generated Markdown reports, tables, CSV exports, and notifications.
- If something clearly looks off, even if it is unrelated to your task, fix it along the way.

## Engineering excellence

- Apply the same high standard to lint errors, test failures, and test flakiness.
- If you see one, even if it was not caused by your current change, still get it fixed.
- Never silence a check, skip a test, or loosen a lint rule to get to green.

## Checks

Run before every commit:

```bash
bash scripts/check.sh
```

It runs `ruff` (config in `ruff.toml`), shell syntax checks, and a repository-wide em dash scan.

## Enforcement

- `.githooks/commit-msg` rejects commit messages that contain a `Co-Authored-By:` trailer or an em dash.
  Enable it once per clone with `git config core.hooksPath .githooks` (Claude Code does this automatically at session start).
- `.claude/hooks/pre_edit_guard.py` blocks Claude Code edits that introduce an em dash or that touch `CHANGELOG.md` or auto-generated files.
- `.claude/settings.json` turns off Claude Code's default commit co-author attribution.
