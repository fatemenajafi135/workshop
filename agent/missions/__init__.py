"""Fixes for the agent's bad habits, one file per mission.

Every mission can be switched off, to show the habit it fixes:
    make run BUG=04 MISSIONS=none
    make run BUG=04 MISSIONS=budget,stop_check
"""

import os

ALL = ["permission", "stop_check", "budget", "trimming", "prompt"]


def on(name: str) -> bool:
    chosen = os.environ.get("MISSIONS") or "all"
    return chosen == "all" or name in chosen.split(",")
