from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, Tuple


def clamp(s: str, max_chars: int = 14000) -> str:
    if len(s) <= max_chars:
        return s
    return s[:max_chars] + "\n\n[TRUNCATED]"


def ensure_repo_path(repo: str) -> Path:
    p = Path(repo).resolve()
    if not p.exists() or not p.is_dir():
        raise SystemExit(f"Invalid repo path: {repo}")
    return p


def ensure_ollama_available() -> None:
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
    except Exception:
        raise SystemExit("Ollama CLI not found. Install Ollama and ensure `ollama` is on PATH.")


def ensure_model_available(model: str) -> None:
    try:
        out = subprocess.check_output(["ollama", "list"], text=True)
    except Exception:
        raise SystemExit("Unable to run `ollama list`. Ensure Ollama is installed and running.")

    # Typical output includes a header and rows like:
    # NAME                ID              SIZE      MODIFIED
    # llama3:latest       ...             ...
    # We match the NAME column precisely to reduce false positives.
    names: set[str] = set()
    for line in (out or "").splitlines():
        line = line.strip()
        if not line or line.lower().startswith("name "):
            continue
        name = line.split()[0]
        if name:
            names.add(name)

    if model not in names:
        raise SystemExit(f"Ollama model '{model}' not found locally. Run: ollama pull {model}")


def parse_coverage_total(json_path: Path) -> Tuple[float, Dict[str, Any]]:
    data = json.loads(json_path.read_text(encoding="utf-8"))
    total = float(data["totals"]["percent_covered"])
    return total, data


def strip_code_fences(text: str) -> str:
    """
    Remove Markdown code fences and language tags from LLM output.
    Also trims common wrappers like '[CODE]' or leading prose lines.
    """
    if not text:
        return ""

    s = text.strip()

    # Remove simple wrappers often seen in model outputs
    s = re.sub(r"^\s*\[CODE\]\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^\s*Here is the code:\s*", "", s, flags=re.IGNORECASE)

    lines = s.splitlines()

    # Drop opening fence: ``` or ```python
    if lines and lines[0].lstrip().startswith("```"):
        lines = lines[1:]

    # Drop closing fence
    if lines and lines[-1].lstrip().startswith("```"):
        lines = lines[:-1]

    return "\n".join(lines).strip()


_WORD_TENS = {
    "zero": 0,
    "ten": 10,
    "twenty": 20,
    "thirty": 30,
    "forty": 40,
    "fifty": 50,
    "sixty": 60,
    "seventy": 70,
    "eighty": 80,
    "ninety": 90,
}

_WORD_UNITS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


def parse_coverage_target(text: str) -> float:
    """
    Parse natural language into a numeric coverage percentage.

    Supported examples:
    - "100%"
    - "one hundred percent"
    - "at least ninety five percent"
    - "ninety percent"
    - "95 percent"
    """
    if not text:
        raise ValueError("Coverage target is empty.")

    t = text.lower().strip()

    # Numeric percent like 95% or 95 percent
    m = re.search(r"(\d+(?:\.\d+)?)\s*(%|percent)\b", t)
    if m:
        val = float(m.group(1))
        if val < 0 or val > 100:
            raise ValueError(f"Coverage target out of range: {val}")
        return val

    # Word-based: handle "one hundred"
    if "hundred" in t:
        return 100.0

    # Word-based: tens + optional units, e.g. "ninety five"
    tens = 0
    for w, v in _WORD_TENS.items():
        if re.search(rf"\b{w}\b", t):
            tens = v
            break

    units = 0
    for w, v in _WORD_UNITS.items():
        if re.search(rf"\b{w}\b", t):
            units = v
            break

    if tens > 0:
        val = float(tens + units)
        if val > 100:
            val = 100.0
        return val

    raise ValueError(f"Cannot parse coverage target: '{text}'")
