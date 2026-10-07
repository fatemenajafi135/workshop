"""Shows every step of a run in the terminal, and saves the whole run to runs/<id>.json."""

import json
import os
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

RUNS_DIR = Path(__file__).parent.parent / "runs"
SHOW_LINES = 12  # output lines shown in the terminal (the model gets more)

console = Console()


class Trace:
    def __init__(self, task: str, label: str = "run", save_to: Path | None = None):
        self.started = time.time()
        self.path = save_to or RUNS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}-{label}.json"
        self.steps = 0
        self.input_tokens = 0
        self.output_tokens = 0
        self.cached_tokens = 0
        self.cost: float | None = 0.0  # None once any step had an unknown price
        self.events: list[dict] = []
        self.result: str | None = None
        self.task = task

        console.rule("[bold]task")
        console.print(Text(task.strip()))
        self.save()

    def model_said(self, reply) -> None:
        self.steps += 1
        self.input_tokens += reply.input_tokens
        self.output_tokens += reply.output_tokens
        self.cached_tokens += reply.cached_tokens
        if self.cost is not None and reply.cost is not None:
            self.cost += reply.cost
        else:
            self.cost = None

        cached = f" ({reply.cached_tokens:,} cached)" if reply.cached_tokens else ""
        console.rule(f"[bold]step {self.steps}[/]{cached}  ·  {self.tokens():,} tokens  ·  {self.money()}")
        console.print(Markdown(reply.text))
        self.add("model", text=reply.text, input_tokens=reply.input_tokens,
                 output_tokens=reply.output_tokens, cached_tokens=reply.cached_tokens, cost=reply.cost)

    def ran(self, command: str, output: str) -> None:
        lines = output.splitlines()
        shown = lines[:SHOW_LINES]
        if len(lines) > SHOW_LINES:
            shown.append(f"... {len(lines) - SHOW_LINES} more lines")
        console.print(Text("\n".join(shown)), style="dim")
        self.add("command", command=command, output=output)

    def note(self, text: str) -> None:
        """Something the harness did, not the model: a refusal, a test check, a budget stop."""
        console.print(f"[yellow]▶ harness:[/] {text}")
        self.add("harness", text=text)

    def finish(self, result: str) -> None:
        self.result = result
        style = "green" if result == "done" else "red"
        console.rule(f"[bold {style}]{result}")
        console.print(f"{self.steps} steps  ·  {self.tokens():,} tokens  ·  {self.money()}"
                      f"  ·  {self.seconds():.0f}s  ·  saved to {os.path.relpath(self.path)}")
        self.save()

    def tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def money(self) -> str:
        return "$?" if self.cost is None else f"${self.cost:.3f}"

    def seconds(self) -> float:
        return time.time() - self.started

    def add(self, kind: str, **fields) -> None:
        self.events.append({"kind": kind, "at": round(self.seconds(), 1), **fields})
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({
            "task": self.task,
            "model": os.environ.get("MODEL"),
            "missions": os.environ.get("MISSIONS", "all"),
            "result": self.result,
            "steps": self.steps,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_tokens": self.cached_tokens,
            "cost": self.cost,
            "seconds": round(self.seconds(), 1),
            "events": self.events,
        }, indent=2, ensure_ascii=False))
