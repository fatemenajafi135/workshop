"""The lab: an outer loop around the agent that keeps trying to make one slow function faster.

    make lab                 # runs for 2 hours (LAB_HOURS=0.5 for a shorter run)

Every attempt is a fresh agent with a fixed time budget. A change is kept only if
the tests pass and the benchmark gets faster; every kept change is a git commit.
Everything is logged in lab/output/log.md, the best code is in lab/output/best/.
"""

import json
import os
import random
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console

from agent.llm import load_env

HOURS = float(os.environ.get("LAB_HOURS") or 2)
ATTEMPT_TIME = 300  # seconds per attempt
MIN_GAIN = 0.10  # keep a change only if it's at least 10% faster
CONTAINER = "mini-agent-lab"

ROOT = Path(__file__).parent.parent
LAB = ROOT / "lab"
OUTPUT = LAB / "output"

TASK = """\
In /work/splitter/optimal.py, fewest_transfers() is correct but slow. Make it faster.

Rules:
- It must still return a shortest possible list of transfers. All tests must pass.
- Don't change the tests. Don't remember results between calls, don't special-case inputs.
- The benchmark runs it on groups of 12 to 13 people.
- Measure your change yourself before you finish (time.perf_counter on a few groups).
- When you're done, reply without a bash block, in one sentence: what you changed.

The benchmark now takes {best:.3f}s (it started at {baseline:.3f}s).
{history}"""

console = Console()


def main() -> None:
    load_env()
    OUTPUT.mkdir(exist_ok=True)
    start_sandbox()
    cases = benchmark_cases()
    baseline = measure(cases)
    if not baseline["ok"]:
        sys.exit(f"The benchmark fails before the agent did anything: {baseline['error']}")
    baseline_seconds = best = baseline["seconds"]
    export_best()

    log = OUTPUT / "log.md"
    log.write_text(
        f"# Lab log\n\n"
        f"Started {datetime.now():%Y-%m-%d %H:%M}  ·  model {os.environ.get('MODEL')}  ·  "
        f"baseline {baseline_seconds:.3f}s  ·  keep if ≥{MIN_GAIN:.0%} faster\n\n"
        "| # | time | outcome | benchmark | vs start | what the agent did |\n"
        "|---|------|---------|-----------|----------|--------------------|\n"
    )
    console.print(f"Lab started: baseline {baseline_seconds:.3f}s, running for {HOURS}h")

    history: list[str] = []
    deadline = time.time() + HOURS * 3600
    attempt = 0
    while time.time() < deadline:
        attempt += 1
        summary = run_agent(attempt, TASK.format(
            best=best, baseline=baseline_seconds, history=history_text(history)))
        outcome, seconds = judge(cases, best)
        if outcome == "kept":
            commit(f"attempt {attempt}: {best:.3f}s -> {seconds:.3f}s\n\n{summary}")
            best = seconds
            export_best()
        else:
            rollback()

        shown = f"{seconds:.3f}s" if seconds is not None else "–"
        speedup = f"{baseline_seconds / seconds:.1f}×" if seconds else "–"
        line = summary.replace("|", "/").replace("\n", " ")[:160]
        with log.open("a") as f:
            f.write(f"| {attempt} | {datetime.now():%H:%M} | {outcome} | {shown} | {speedup} | {line} |\n")
        history.append(f"- attempt {attempt}, {outcome} ({shown}): {line}")
        style = "green" if outcome == "kept" else "red"
        console.print(f"[{style}]attempt {attempt}: {outcome}[/] {shown}  best {best:.3f}s  ·  {line}")

    console.print(f"Lab done: {baseline_seconds:.3f}s -> {best:.3f}s. See {log.relative_to(ROOT)}")


def start_sandbox() -> None:
    """A clean sandbox with the slow function and its tests, committed as the starting point."""
    subprocess.run(["make", "-s", "reset", "BUG=none", f"CONTAINER={CONTAINER}"], check=True, cwd=ROOT)
    put_file(LAB / "optimal.py", "splitter/optimal.py")
    put_file(LAB / "test_optimal.py", "tests/test_optimal.py")
    sandbox("git add -A && git commit -q -m 'lab: slow fewest_transfers'")


def run_agent(attempt: int, task: str) -> str:
    """One attempt by a fresh agent. Returns its last words, or why it stopped."""
    trace_file = OUTPUT / f"attempt-{attempt:02d}.json"
    agent = [sys.executable, "-m", "agent.core", task, "--container", CONTAINER, "--save-to", str(trace_file)]
    try:
        subprocess.run(agent, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL, timeout=ATTEMPT_TIME, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return f"(out of time after {ATTEMPT_TIME}s)"
    if not trace_file.exists():
        return "(the agent didn't start)"
    trace = json.loads(trace_file.read_text())
    if trace["result"] != "done":
        return f"({trace['result']})"
    said = [event["text"] for event in trace["events"] if event["kind"] == "model"]
    return said[-1].strip() if said else "(nothing)"


def judge(cases: list[dict], best: float) -> tuple[str, float | None]:
    """Keep the change only if the tests pass, untouched, and the benchmark got faster."""
    if sandbox("git status --porcelain tests").stdout.strip():
        return "rejected: changed the tests", None
    if sandbox("python -m pytest -q").returncode != 0:
        return "rejected: tests fail", None
    result = measure(cases)
    if not result["ok"]:
        return f"rejected: {result['error']}", None
    if result["seconds"] > best * (1 - MIN_GAIN):
        return "rejected: not faster", result["seconds"]
    return "kept", result["seconds"]


def measure(cases: list[dict]) -> dict:
    """Run the hidden benchmark inside the sandbox."""
    command = ["docker", "exec", "-i", CONTAINER, "timeout", "120", "python", "-", json.dumps(cases)]
    result = subprocess.run(command, input=(LAB / "bench.py").read_text(), capture_output=True, text=True)
    lines = result.stdout.strip().splitlines()
    try:
        return json.loads(lines[-1])
    except (IndexError, json.JSONDecodeError):
        return {"ok": False, "error": "benchmark crashed or took over 120s"}


def benchmark_cases() -> list[dict]:
    """Fixed groups of 12-13 people, made of smaller groups that settle among themselves."""
    cases = []
    for clusters in [(3, 3, 3, 3), (4, 4, 4), (3, 3, 4, 3)]:
        rng = random.Random(sum(clusters))
        amounts = []
        for size in clusters:
            part = [rng.choice([-1, 1]) * rng.randrange(1, 60) * 100 for _ in range(size - 1)]
            if sum(part) == 0:
                part[0] += 100
            amounts += part + [-sum(part)]
        rng.shuffle(amounts)
        balances = {f"p{i}": amount for i, amount in enumerate(amounts)}
        cases.append({"balances": balances, "fewest": fewest_count(amounts)})
    return cases


def fewest_count(amounts: list[int]) -> int:
    """The fewest transfers possible: people minus the most groups that each add up to zero."""
    n = len(amounts)
    totals = [0] * (1 << n)
    most_groups = [0] * (1 << n)
    for mask in range(1, 1 << n):
        lowest = (mask & -mask).bit_length() - 1
        totals[mask] = totals[mask & (mask - 1)] + amounts[lowest]
        most_groups[mask] = max(most_groups[mask & ~(1 << i)] for i in range(n) if mask >> i & 1)
        most_groups[mask] += totals[mask] == 0
    return n - most_groups[(1 << n) - 1]


def history_text(history: list[str]) -> str:
    if not history:
        return "This is the first attempt."
    return "Earlier attempts (most recent last):\n" + "\n".join(history[-10:])


def commit(message: str) -> None:
    sandbox("git add -A")
    subprocess.run(["docker", "exec", CONTAINER, "git", "commit", "-qm", message], check=True)


def rollback() -> None:
    sandbox("git reset -q --hard && git clean -qfd")


def export_best() -> None:
    shutil.rmtree(OUTPUT / "best", ignore_errors=True)
    subprocess.run(["docker", "cp", f"{CONTAINER}:/work", str(OUTPUT / "best")], check=True)


def put_file(source: Path, target: str) -> None:
    command = ["docker", "exec", "-i", CONTAINER, "sh", "-c", f"cat > {target}"]
    subprocess.run(command, input=source.read_text(), text=True, check=True)


def sandbox(command: str) -> subprocess.CompletedProcess:
    return subprocess.run(["docker", "exec", CONTAINER, "sh", "-c", command], capture_output=True, text=True)


if __name__ == "__main__":
    main()
