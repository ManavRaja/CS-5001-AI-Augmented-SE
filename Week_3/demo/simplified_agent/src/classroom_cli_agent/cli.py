from __future__ import annotations

import argparse
import os
import sys

from .agent import Agent
from .types import AgentConfig
from .utils import ensure_repo_path

DEFAULT_MODEL = "devstral-small-2:24b-cloud"
DEFAULT_HOST = "http://localhost:11434"
VERSION = "0.2.0"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cca", description="Classroom CLI agent")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    p.add_argument("--repo", required=True, help="Repository path")
    p.add_argument(
        "--model",
        default=os.environ.get("OLLAMA_MODEL", DEFAULT_MODEL),
        help=f"Ollama model (default: {DEFAULT_MODEL})",
    )
    p.add_argument(
        "--host",
        default=os.environ.get("OLLAMA_HOST", DEFAULT_HOST),
        help=f"Ollama host (default: {DEFAULT_HOST})",
    )
    p.add_argument(
        "--temperature",
        type=float,
        default=float(os.environ.get("OLLAMA_TEMPERATURE", "0.0")),
        help="Sampling temperature (default: 0.0)",
    )
    p.add_argument("--verbose", action="store_true", help="Verbose output")

    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Create or update a single Python module from a description")
    c.add_argument("--desc", required=True, help="Natural language description or spec")
    c.add_argument("--module", required=True, help="Relative path to module file, e.g., src/program.py")

    cm = sub.add_parser("commit", help="Commit and optionally push changes")
    cm.add_argument("--message", required=True, help="Commit message")
    cm.add_argument("--push", action="store_true", help="Also run git push")

    return p


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    ensure_repo_path(args.repo)

    cfg = AgentConfig(
        repo=args.repo,
        model=args.model,
        host=args.host,
        temperature=args.temperature,
        verbose=args.verbose,
    )
    agent = Agent(cfg)

    try:
        if args.cmd == "create":
            r = agent.create_program(args.desc, args.module)
        else:  # commit
            r = agent.commit_and_push(args.message, args.push)

        stream = sys.stdout if r.ok else sys.stderr
        print(r.details, file=stream)
        return 0 if r.ok else 1
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as e:
        print(str(e) or e.__class__.__name__, file=sys.stderr)
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
