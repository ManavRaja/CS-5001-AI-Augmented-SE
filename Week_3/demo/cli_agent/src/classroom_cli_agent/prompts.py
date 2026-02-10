from __future__ import annotations


def program_prompt(desc: str, existing: str) -> str:
    return (
        "You are a software engineer. Write a single Python module that satisfies the description.\n"
        "Return ONLY the full module content.\n"
        "IMPORTANT:\n"
        "- Output raw Python only\n"
        "- Do NOT use Markdown\n"
        "- Do NOT use ``` fences\n"
        "- Do NOT include explanations\n"
        "Constraints:\n"
        "- Python standard library only\n"
        "- Include docstrings\n"
        "- Keep the design minimal\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "EXISTING MODULE (may be empty):\n"
        f"{existing}\n"
    )


def tests_prompt(desc: str, module_path: str, module_code: str, existing_tests: str) -> str:
    return (
        "You are a QA engineer. Write pytest tests for the described module.\n"
        "Return ONLY the full test file content.\n"
        "IMPORTANT:\n"
        "- Output raw Python only\n"
        "- Do NOT use Markdown\n"
        "- Do NOT use ``` fences\n"
        "- Do NOT include explanations\n"
        "Constraints:\n"
        "- Use pytest\n"
        "- Aim for high line coverage of the target module\n"
        "- Do not modify production code in this step\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        f"TARGET MODULE PATH: {module_path}\n\n"
        "TARGET MODULE CODE:\n"
        f"{module_code}\n\n"
        "EXISTING TESTS (may be empty):\n"
        f"{existing_tests}\n"
    )


def scaffold_prompt(desc: str, out_dir: str, existing_tree: str) -> str:
    return (
        "You are a software engineer. Create a multi-file project scaffold that satisfies the description.\n"
        "Return ONLY valid JSON.\n"
        "IMPORTANT:\n"
        "- Output JSON only (no Markdown, no explanations)\n"
        "- Do NOT wrap in ``` fences\n"
        "- Paths must be relative, use forward slashes\n"
        "- Do NOT use absolute paths\n"
        "- Do NOT include '..' in paths\n"
        "\n"
        "JSON schema (required):\n"
        "{\n"
        "  \"files\": [\n"
        "    {\"path\": \"relative/path.ext\", \"content\": \"file contents...\"}\n"
        "  ]\n"
        "}\n"
        "\n"
        "Guidance:\n"
        "- Include an entrypoint module in src/ (for Flask prefer src/app.py with create_app())\n"
        "- Put routes in src/routes/, services in src/services/, templates in src/templates/ when relevant\n"
        "- Keep dependencies minimal; use common project layout\n"
        "\n"
        f"OUTPUT ROOT (all files must be under this directory): {out_dir}\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "EXISTING TREE (paths under output root, may be empty):\n"
        f"{existing_tree}\n"
    )


def coverage_target_prompt(user_text: str) -> str:
    """Build a prompt to parse a numeric coverage percentage from natural language."""

    return (
        "You are an expert at extracting structured data from natural language.\n"
        "Parse a code coverage target from the user's text.\n\n"
        "Output requirements:\n"
        "- Return ONLY valid JSON\n"
        "- Do NOT use Markdown\n"
        "- Do NOT include explanations\n"
        "- The JSON must match this schema exactly:\n"
        "  {\"coverage_percent\": <number 0..100>}\n\n"
        "Rules:\n"
        "- Interpret the user's intent as a percentage target for total test coverage.\n"
        "- Accept inputs like '95%', 'at least ninety five percent', '>= 90', 'coverage 87.5', '100 percent'.\n"
        "- If the user specifies a number above 100, clamp to 100.\n"
        "- If the user specifies a negative number, clamp to 0.\n"
        "- If multiple numbers appear, pick the one most likely to be the coverage target.\n\n"
        f"USER TEXT:\n{user_text}\n"
    )
