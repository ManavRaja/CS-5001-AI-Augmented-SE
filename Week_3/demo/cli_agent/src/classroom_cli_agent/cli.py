from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict
from typing import Any

from .agent import Agent
from .types import AgentConfig, RunResult
from .utils import (
    ensure_model_available,
    ensure_ollama_available,
    ensure_repo_path,
)

DEFAULT_MODEL = "devstral-small-2:24b-cloud"
DEFAULT_HOST = "http://localhost:11434"
VERSION = "0.2.0"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cca",
        description=(
            "Classroom CLI agent (Ollama-based). Generates code and tests with an Ollama model. "
            "Suggested workflow: create or scaffold, generate tests, then run a test report."
        ),
        epilog=(
            "Examples:\n"
            "  cca --repo . create --module src/program.py --desc \"spec text\"\n"
            "  cca --repo . gen-tests --module src/program.py --tests tests/test_program.py --desc \"spec text\"\n"
            "  cca --repo . report --fail-on-coverage 95% --report-md reports/test_report.md\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

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
    # Kept for backward compatibility with existing configs; not used by the two-step flow.
    p.add_argument("--max-iters", type=int, default=3, help="Max iterations for test improvement")
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    p.add_argument("--json", action="store_true", help="Print a JSON summary to stdout (useful for CI tooling)")

    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("create", help="Create or update a single Python module from a description")
    c.add_argument("--desc", required=True, help="Natural language description or spec")
    c.add_argument("--module", required=True, help="Relative path to module file, e.g., src/program.py")

    sc = sub.add_parser(
        "scaffold",
        help=(
            "Create or update a multi-file scaffold from a description (writes multiple files). "
            "Useful for frameworks like Flask with routes, services, templates."
        ),
    )
    sc.add_argument("--desc", required=True, help="Natural language description or spec")
    sc.add_argument("--out-dir", default=".", help="Relative output directory root (default: .)")
    sc.add_argument("--overwrite", action="store_true", help="Overwrite existing files when scaffolding")

    gt = sub.add_parser("gen-tests", help="Generate or update pytest tests for a module (no execution)")
    gt.add_argument("--desc", required=True, help="Natural language description or spec")
    gt.add_argument("--module", required=True, help="Relative path to module file, e.g., src/program.py")
    gt.add_argument("--tests", required=True, help="Relative path to tests file, e.g., tests/test_program.py")
    gt.add_argument("--overwrite", action="store_true", help="Overwrite tests file if it already exists")

    rp = sub.add_parser("report", help="Run pytest with coverage and write a structured report")
    rp.add_argument("--module", default=None, help="Relative module path to include per-file coverage details (optional)")
    rp.add_argument(
        "--report-out",
        default="reports/test_report.json",
        help="Relative path for JSON report output (default: reports/test_report.json)",
    )
    rp.add_argument("--report-md", default=None, help="Optional relative path for a Markdown report")
    rp.add_argument("--fail-on-coverage", default=None, help="Exit non-zero if coverage is below target (e.g., '95%')")
    rp.add_argument("--fail-on-tests", action="store_true", help="Exit non-zero when pytest fails")

    cm = sub.add_parser("commit", help="Commit and optionally push changes")
    cm.add_argument("--message", required=True, help="Commit message")
    cm.add_argument("--push", action="store_true", help="Also run git push")

    return p


def build_agent(args: argparse.Namespace) -> Agent:
    ensure_repo_path(args.repo)
    ensure_ollama_available()
    ensure_model_available(args.model)

    cfg = AgentConfig(
        repo=args.repo,
        model=args.model,
        host=args.host,
        temperature=args.temperature,
        max_iters=args.max_iters,
        verbose=args.verbose,
    )
    return Agent(cfg)


def json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, indent=2, sort_keys=True)


def emit(args: argparse.Namespace, cfg: AgentConfig, result: RunResult) -> None:
    if args.json:
        payload: dict[str, Any] = {
            "ok": result.ok,
            "details": result.details,
            "cmd": args.cmd,
            "coverage": result.coverage,
            "config": asdict(cfg),
        }
        print(json_dumps(payload))
        return

    stream = sys.stdout if result.ok else sys.stderr
    print(result.details, file=stream)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        agent = build_agent(args)
        cfg = agent.cfg

        if args.cmd == "create":
            r = agent.create_program(args.desc, args.module)

        elif args.cmd == "scaffold":
            r = agent.scaffold_project(args.desc, out_dir=args.out_dir, overwrite=args.overwrite)

        elif args.cmd == "gen-tests":
            if (not args.overwrite) and agent.tests_exist(args.tests):
                r = RunResult(False, f"Tests file already exists: {args.tests}. Use --overwrite to replace it.")
            else:
                r = agent.create_tests(args.desc, args.module, args.tests)

        elif args.cmd == "report":
            cov_target = agent.parse_coverage_target(args.fail_on_coverage) if args.fail_on_coverage else None
            r = agent.generate_test_report(
                module_path=args.module,
                report_out_path=args.report_out,
                report_md_path=args.report_md,
                fail_on_tests=args.fail_on_tests,
                fail_on_coverage=cov_target,
            )

        else:  # commit
            r = agent.commit_and_push(args.message, args.push)

        emit(args, cfg, r)
        return 0 if r.ok else 1

    except KeyboardInterrupt:
        stream = sys.stderr
        print("Interrupted.", file=stream)
        return 130
    except Exception as e:
        stream = sys.stderr
        print(str(e) or e.__class__.__name__, file=stream)
        return 1


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()