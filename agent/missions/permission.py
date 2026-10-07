"""Mission 1: risky commands need a human's OK.

Without it: `make ask TASK="Delete the tests folder, it's a mess"` just deletes it.
"""

import re
import sys

from agent.missions import on

RISKY = [
    r"\brm\b",
    r"\bgit\s+(push|reset|checkout|clean)\b",
    r"\b(curl|wget)\b",
    r"\bpip\s+install\b",
    r"\bsudo\b",
]


def approved(command: str) -> bool:
    if not on("permission"):
        return True
    if not any(re.search(pattern, command) for pattern in RISKY):
        return True
    if not sys.stdin.isatty():
        return False  # nobody to ask (scoreboard, lab): the answer is no
    answer = input(f"\nThe agent wants to run:\n    {command}\nAllow? [y/N] ")
    return answer.strip().lower() in ("y", "yes")
