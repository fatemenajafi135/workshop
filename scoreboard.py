"""Runs the agent on every bug, each in its own fresh sandbox, and prints one table.

    make score                    # the small exam: bugs 01, 04, 05
    make score BUGS=all           # every bug
    make score BUGS=02,03         # the bugs you choose
    make score MISSIONS=none      # the agent without its missions, to compare

Fixed = the whole test suite passes and the agent didn't touch the tests.
What the agent changed is saved as runs/score-<time>/<bug>.diff.
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.table import Table

from agent.llm import load_env

TIME_LIMIT = 300  # seconds per bug; a stuck agent is killed
ROOT = Path(__file__).parent

console = Console()


def main() -> None:
    load_env()
    bugs = sorted(path.parent for path in ROOT.glob("bugs/*/issue.md"))
    chosen = os.environ.get("BUGS") or "all"
    if chosen != "all":
        bugs = [bug for bug in bugs if bug.name.split("-")[0] in chosen.split(",")]
    out_dir = ROOT / "runs" / f"score-{datetime.now():%Y%m%d-%H%M%S}"
    out_dir.mkdir(parents=True)

    model = os.environ.get("MODEL") or "(MODEL from .env)"
    missions = os.environ.get("MISSIONS") or "all"
    console.print(f"Scoring {len(bugs)} bugs  ·  model {model}  ·  missions {missions}\n")
    started = time.time()
    with ThreadPoolExecutor(max_workers=len(bugs)) as pool:
        results = list(pool.map(lambda bug: score(bug, out_dir), bugs))

    print_table(results, time.time() - started)
    (out_dir / "scores.json").write_text(json.dumps(results, indent=2))
    console.print(f"\nTraces and scores saved in {out_dir.relative_to(ROOT)}/")


def score(bug: Path, out_dir: Path) -> dict:
    """Fresh sandbox with this bug, let the agent work, then check the result."""
    bug_id = bug.name.split("-")[0]
    container = f"mini-agent-score-{bug_id}"
    trace_file = out_dir / f"{bug.name}.json"
    make("reset", f"BUG={bug_id}", f"CONTAINER={container}")

    started = time.time()
    agent = [sys.executable, "-m", "agent.core", str(bug / "issue.md"),
             "--container", container, "--save-to", str(trace_file)]
    try:
        # No stdin: the permission gate has nobody to ask, so risky commands are refused.
        subprocess.run(agent, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=TIME_LIMIT, cwd=ROOT)
    except subprocess.TimeoutExpired:
        pass
    seconds = time.time() - started

    tests_pass = docker_exec(container, "python", "-m", "pytest", "-q") == 0
    tests_changed = run_in(container, "git status --porcelain -- tests")
    tests_untouched = tests_changed.strip() == ""
    # Save what the agent changed (new files too) before the container is deleted.
    (out_dir / f"{bug.name}.diff").write_text(run_in(container, "git add -A && git diff --cached"))
    subprocess.run(["docker", "rm", "-f", container], capture_output=True)

    trace = json.loads(trace_file.read_text()) if trace_file.exists() else {}
    result = {
        "bug": bug.name,
        "fixed": tests_pass and tests_untouched,
        "verdict": verdict(tests_pass, tests_untouched),
        "steps": trace.get("steps", 0),
        "tokens": trace.get("input_tokens", 0) + trace.get("output_tokens", 0),
        "cost": trace.get("cost"),
        "seconds": round(seconds),
        "stopped": trace.get("result") or f"killed: no answer after {TIME_LIMIT}s",
    }
    mark = "[green]✓[/]" if result["fixed"] else "[red]✗[/]"
    console.print(f"  {mark} {bug.name}  ({result['verdict']}, {result['steps']} steps)")
    return result


def verdict(tests_pass: bool, tests_untouched: bool) -> str:
    if not tests_untouched:
        return "edited tests"
    return "fixed" if tests_pass else "tests fail"


def print_table(results: list[dict], seconds: float) -> None:
    table = Table(title="Scoreboard")
    table.add_column("bug")
    table.add_column("result", no_wrap=True)
    for column in ["steps", "tokens", "cost", "time"]:
        table.add_column(column, justify="right", no_wrap=True)
    table.add_column("stopped", no_wrap=True)
    for r in results:
        style = "green" if r["fixed"] else "red"
        table.add_row(r["bug"], f"[{style}]{r['verdict']}[/]", str(r["steps"]), f"{r['tokens']:,}",
                      money(r["cost"]), f"{r['seconds']}s", r["stopped"].split(":")[0])

    fixed = sum(r["fixed"] for r in results)
    costs = [r["cost"] for r in results]
    total_cost = None if None in costs else sum(costs)
    table.add_section()
    table.add_row(f"[bold]{fixed}/{len(results)} fixed", "", str(sum(r["steps"] for r in results)),
                  f"{sum(r['tokens'] for r in results):,}", money(total_cost), f"{seconds:.0f}s", "")
    console.print()
    console.print(table)


def money(cost: float | None) -> str:
    return "$?" if cost is None else f"${cost:.3f}"


def make(*args: str) -> None:
    subprocess.run(["make", "-s", *args], check=True, capture_output=True, cwd=ROOT)


def docker_exec(container: str, *command: str) -> int:
    return subprocess.run(["docker", "exec", container, *command], capture_output=True).returncode


def run_in(container: str, shell_command: str) -> str:
    """Run a shell command in the container, return what it printed."""
    command = ["docker", "exec", container, "sh", "-c", shell_command]
    return subprocess.run(command, capture_output=True, text=True).stdout


if __name__ == "__main__":
    main()
