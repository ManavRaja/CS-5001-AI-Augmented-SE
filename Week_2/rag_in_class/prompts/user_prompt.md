You are an expert software engineer refactoring Python code.

## Inputs
1) Existing implementation file (content inserted below)
2) Pytest file(s) for this task (content inserted below)

## Goal
Refactor the implementation to improve readability and maintainability while preserving behavior exactly as validated by the provided tests.

Ensure the refactored code returns exactly the same types as the original, including None values.
If the original returns None for empty cases, the refactored version must do the same.
Preserve the exact input-output behavior, including edge cases and error handling.
Explicitly handle all edge cases mentioned in the original code (e.g., n ≤ 2)
Preserve all checks and conditions from the original, even if they seem redundant.
Keep function names the same when refactoring.

## Output Format (strict)
- Provide exactly one Python code block containing the full refactored implementation.
- After the code block, provide the checklist in 5 to 10 bullets.
- Do NOT include any additional text.

---

## Implementation file content
<<<IMPLEMENTATION>>>
