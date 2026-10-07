"""Mission 3: stop when a run gets too long or too expensive.

Without it: an agent that never gives up runs (and spends) forever.
"""

from agent.missions import on

MAX_STEPS = 30
MAX_COST = 0.50  # dollars


def exceeded(trace) -> str | None:
    """None while there's budget left. Otherwise why the run has to stop."""
    if not on("budget"):
        return None
    if trace.steps >= MAX_STEPS:
        return f"out of budget: {MAX_STEPS} steps"
    if trace.cost is not None and trace.cost >= MAX_COST:
        return f"out of budget: ${trace.cost:.2f} spent (limit ${MAX_COST:.2f})"
    return None
