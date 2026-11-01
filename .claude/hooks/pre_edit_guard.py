#!/usr/bin/env python3
"""Claude Code PreToolUse hook for Write / Edit / MultiEdit / NotebookEdit.

Blocks (exit code 2, reason on stderr so the agent can correct itself):
  - edits to CHANGELOG.md or to files whose header marks them as generated
  - new text that contains an em dash (U+2014)

See AGENTS.md for the rules behind these checks.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

EM_DASH = "\u2014"
GENERATED_MARKER = re.compile(
    r"@generated"
    r"|\bDO NOT EDIT\b"
    r"|(?i:this file (is|was|has been) (auto-?)?generated)"
    r"|(?i:auto-?generated (file|code|by))"
)
HEADER_LINES = 5


def new_text(tool_input: dict) -> str:
    parts = [tool_input.get(k) or "" for k in ("content", "new_string", "new_source")]
    parts += [e.get("new_string") or "" for e in tool_input.get("edits") or [] if isinstance(e, dict)]
    return "\n".join(parts)


def is_generated(path: Path) -> bool:
    if not path.is_file():
        return False
    try:
        with path.open(encoding="utf-8", errors="ignore") as fh:
            header = "".join(fh.readline() for _ in range(HEADER_LINES))
    except OSError:
        return False
    return bool(GENERATED_MARKER.search(header))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    tool_input = payload.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    path = Path(raw_path)

    problems = []
    if path.name.lower().startswith("changelog") and path.suffix.lower() == ".md":
        problems.append(f"{raw_path} is a changelog. Never modify CHANGELOG.md files manually.")
    elif is_generated(path):
        problems.append(
            f"{raw_path} is marked as auto-generated. Do not edit it by hand; "
            "change its source or generator and regenerate."
        )

    text = new_text(tool_input)
    if EM_DASH in text:
        lines = [ln.strip() for ln in text.splitlines() if EM_DASH in ln][:3]
        problems.append(
            "The new text contains an em dash (U+2014). Use a plain dash '-' instead. Offending lines:\n  "
            + "\n  ".join(lines)
        )

    if problems:
        print("\n".join(problems), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
