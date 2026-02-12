from __future__ import annotations

from pathlib import Path
from typing import Any

from .llm import OllamaLLM
from .prompts import program_prompt
from .tools import Tools
from .types import AgentConfig, RunResult
from .utils import strip_code_fences


class Agent:
    def __init__(self, cfg: AgentConfig):
        self.cfg = cfg
        self.repo = Path(cfg.repo).resolve()
        self.tools = Tools(self.repo)

    def _log(self, message: Any) -> None:
        if self.cfg.verbose:
            print(message)

    def _llm(self) -> OllamaLLM:
        return OllamaLLM(model=self.cfg.model, host=self.cfg.host, temperature=self.cfg.temperature)

    def create_program(self, desc: str, module_path: str) -> RunResult:
        existing = self.tools.read(module_path)
        prompt = program_prompt(desc, existing)
        self._log(prompt)

        raw = self._llm().generate(prompt)
        self._log(raw)

        content = strip_code_fences(raw)
        if not content:
            return RunResult(False, "Model returned empty module.")

        self.tools.write(module_path, content.rstrip() + "\n")
        return RunResult(True, f"Wrote module: {module_path}")

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
