from __future__ import annotations


def program_prompt(desc: str, existing: str) -> str:
    return (
        "You are a software engineer. Write a single Python module that satisfies the description.\n"
        "Return ONLY the full module content.\n"
        "- Output raw Python only\n"
        "- No Markdown\n"
        "- No code fences\n"
        "- No explanations\n\n"
        f"DESCRIPTION:\n{desc}\n\n"
        "EXISTING MODULE (may be empty):\n"
        f"{existing}\n"
    )
