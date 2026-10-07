"""Mission 3: stop when a run gets too long or too expensive.

THE HABIT: an agent that never gives up runs (and spends) forever.
  See it:  make run BUG=06 MISSIONS=none      (stop it with Ctrl+C when you've seen enough)

YOUR JOB: write exceeded(trace). It's called before every step. Return None while there's
budget left, otherwise a short reason (it's shown in the trace and the scoreboard).
  - trace.steps is the number of steps so far. At MAX_STEPS or more: out of budget.
  - trace.cost is the dollars spent so far. At MAX_COST or more: out of budget.
    It can be None (the provider doesn't report prices): then ignore the cost.
  - Missions can be switched off: if not on("budget"), return None.

Check yourself (free):  make check-mission MISSION=budget
Stuck?                  make catch-up STEP=budget
"""

from agent.missions import on

MAX_STEPS = 30
MAX_COST = 0.50  # dollars


def exceeded(trace) -> str | None:
    """None while there's budget left. Otherwise why the run has to stop."""
    # TODO: write this.
    return None
