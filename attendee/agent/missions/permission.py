"""Mission 1: risky commands need a human's OK.

THE HABIT: the agent runs anything, even `rm -rf`.
  See it:  make reset BUG=none
           make ask TASK="Delete the tests folder, it's a mess." MISSIONS=none
  Then:    make test        <- the tests are gone

YOUR JOB: write approved(command). It answers: may this command run?
  - A command with none of the RISKY words below: True, no questions.
  - A risky one: show it to the human and ask. Only "y" or "yes" means True.
  - Nobody is typing (the scoreboard): sys.stdin.isatty() is False. Then the answer is False.
  - Missions can be switched off: if not on("permission"), the answer is always True.

Check yourself (free):  make check-mission MISSION=permission
Stuck?                  make catch-up STEP=permission
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
    # TODO: write this. Hints: re.search(pattern, command), input("..."), .strip().lower()
    return True
