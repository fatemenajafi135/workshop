"""Mission 2: the agent may only stop when the whole test suite passes.

THE HABIT: the agent runs ONE test, sees green, and says "done". The rest still fails.
  See it:  make run BUG=04 MISSIONS=none
           make test        <- still red!

YOUR JOB: write unfinished(container). It's called when the model says it's done.
  - Run the WHOLE suite in the sandbox: sandbox.run("python -m pytest -q --tb=short", container)
    The output ends with "[exit code 0]" when every test passed.
  - All green: return None (the agent may stop).
  - Otherwise: return a message for the model with the test output, telling it to keep going.
  - Missions can be switched off: if not on("stop_check"), return None.

Check yourself (free):  make check-mission MISSION=stop_check
Stuck?                  make catch-up STEP=stop_check
"""

from agent import sandbox
from agent.missions import on


def unfinished(container: str) -> str | None:
    """None if the agent may stop. Otherwise a message telling it what still fails."""
    # TODO: write this.
    return None
