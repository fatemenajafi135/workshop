"""Mission 2: the agent may only stop when the whole test suite passes.

Without it: on bug 04 the agent runs one test, sees green, and stops.
"""

from agent import sandbox
from agent.missions import on


def unfinished(container: str) -> str | None:
    """None if the agent may stop. Otherwise a message telling it what still fails."""
    if not on("stop_check"):
        return None
    output = sandbox.run("python -m pytest -q --tb=short", container)
    if output.endswith("[exit code 0]"):
        return None
    return (
        "You stopped, but the full test suite still fails:\n\n"
        f"{output}\n\n"
        "Keep going until every test passes."
    )
