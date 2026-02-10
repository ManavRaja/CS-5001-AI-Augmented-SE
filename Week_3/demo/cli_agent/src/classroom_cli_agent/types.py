from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AgentConfig:
    repo: str
    model: str
    host: str
    temperature: float
    max_iters: int
    verbose: bool


@dataclass(frozen=True)
class RunResult:
    ok: bool
    details: str
    coverage: Optional[float] = None
