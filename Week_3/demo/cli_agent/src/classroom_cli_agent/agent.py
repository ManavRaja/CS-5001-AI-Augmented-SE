from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple

from .llm import OllamaLLM
from .prompts import improve_tests_prompt, program_prompt, tests_prompt
from .tools import Tools
from .types import AgentConfig, RunResult
from .utils import parse_coverage_total, strip_code_fences


def _missing_lines_summary(cov_json: Dict, module_rel: str) -> str:
    files = cov_json.get("files", {})
    target = module_rel.replace("\\", "/")
    matches = [k for k in files.keys() if k.replace("\\", "/").endswith(target)]
    if not matches:
        return "[No per-file coverage details found for target module.]"
    entry = files[matches[0]]
    missing = entry.get("missing_lines", []) or []
    if not missing:
        return "[none]"
    return "Missing lines: " + ", ".join(str(x) for x in missing)


class Agent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.repo = Path(cfg.repo).resolve()
        self.tools = Tools(self.repo)
        self.llm = OllamaLLM(model=cfg.model, host=cfg.host, temperature=cfg.temperature)

    def create_program(self, desc: str, module_path: str) -> RunResult:
        existing = self.tools.read(module_path)
        raw = self.llm.generate(program_prompt(desc, existing))
        content = strip_code_fences(raw)
        print(content)
        if not content:
            return RunResult(False, "Model returned empty module after sanitization.")
        self.tools.write(module_path, content + "\n")
        return RunResult(True, f"Wrote module: {module_path}")

    def create_tests(self, desc: str, module_path: str, tests_path: str) -> RunResult:
        module_code = self.tools.read(module_path)
        existing_tests = self.tools.read(tests_path)

        raw = self.llm.generate(tests_prompt(desc, module_path, module_code, existing_tests))
        content = strip_code_fences(raw)
        print(content)
        if not content:
            return RunResult(False, "Model returned empty tests after sanitization.")
        self.tools.write(tests_path, content + "\n")
        return RunResult(True, f"Wrote tests: {tests_path}")

    def _run_tests_with_coverage(self) -> Tuple[bool, str, float, Dict]:
        cov_json_path = self.repo / ".coverage.json"
        cmd = f"coverage run -m pytest -q && coverage json -o {cov_json_path.name}"
        ok, out = self.tools.run(cmd)
        print(ok, out)
        if cov_json_path.exists():
            total, data = parse_coverage_total(cov_json_path)
        else:
            total, data = 0.0, {}
        return ok, out, total, data

    def improve_tests_to_target(
        self,
        desc: str,
        module_path: str,
        tests_path: str,
        max_iters: int,
        target_coverage: float,
    ) -> RunResult:
        for i in range(1, max_iters + 1):
            ok, out, total, cov_data = self._run_tests_with_coverage()
            missing = _missing_lines_summary(cov_data, module_path)
            print(ok, out, total, cov_data)
            if ok and total >= target_coverage:
                return RunResult(
                    True,
                    f"Tests passed and coverage reached {total:.1f}%, target was {target_coverage:.1f}%. Iterations used: {i}.",
                    coverage=total,
                )

            module_code = self.tools.read(module_path)
            current_tests = self.tools.read(tests_path)
            prompt = improve_tests_prompt(desc, module_path, module_code, current_tests, out, missing)

            raw = self.llm.generate(prompt)
            content = strip_code_fences(raw)

            if not content:
                return RunResult(
                    False,
                    f"Iteration {i}: model returned empty tests after sanitization. Coverage={total:.1f}%.",
                    coverage=total,
                )

            self.tools.write(tests_path, content + "\n")

        ok, out, total, _ = self._run_tests_with_coverage()
        status = "passed" if ok else "failed"
        return RunResult(
            False,
            f"Stopped at max iterations. Final tests {status}. Coverage={total:.1f}%, target was {target_coverage:.1f}%.\nLast output:\n{out}",
            coverage=total,
        )

    def commit_and_push(self, message: str, push: bool) -> RunResult:
        ok, out = self.tools.git_commit(message)
        if not ok:
            return RunResult(False, out)
        if push:
            ok2, out2 = self.tools.git_push()
            if not ok2:
                return RunResult(False, "Commit succeeded, but push failed:\n" + out2)
            return RunResult(True, "Commit and push succeeded.")
        return RunResult(True, "Commit succeeded.")
