from __future__ import annotations

import re
from pathlib import Path


def ensure_repo_path(repo: str) -> Path:
    p = Path(repo).resolve()

    # Create the repo directory if it does not exist.
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)

    if not p.is_dir():
        raise SystemExit(f"Invalid repo path (not a directory): {repo}")

    return p


def strip_code_fences(text: str) -> str:
    if not text:
        return ""

    s = text.strip()
    s = re.sub(r"^\s*Here is the code:\s*", "", s, flags=re.IGNORECASE)
    lines = s.splitlines()

    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].lstrip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


def parse_multi_file_output(text: str) -> dict[str, str]:
    """Parse LLM output containing multiple files delimited by ### FILE: markers.

    Expected format:
        ### FILE: path/to/file.py
        <content>

        ### FILE: another/file.md
        <content>

    Returns dict mapping relative file paths to their contents.
    Returns empty dict if no FILE markers are found.
    """
    if not text:
        return {}

    # Split on ### FILE: <path> lines
    parts = re.split(r"^###\s*FILE:\s*(.+?)\s*$", text, flags=re.MULTILINE)

    # parts[0] is text before the first marker (discard) then alternating by path and content
    if len(parts) < 3:
        return {}

    files: dict[str, str] = {}
    for i in range(1, len(parts), 2):
        path = parts[i].strip()
        content = parts[i + 1] if i + 1 < len(parts) else ""
        content = strip_code_fences(content).rstrip() + "\n"
        if path and content.strip():
            files[path] = content

    return files