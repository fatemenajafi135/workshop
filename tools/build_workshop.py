"""Build the attendee branch (`workshop`) from `main`.

    python3 tools/build_workshop.py

What it does: starts a fresh `workshop` branch from the last commit on `main`, moves the finished
files into solutions/, puts the TODO versions from attendee/ in their place, and removes what
attendees don't need (the lab, CLAUDE.md). It then goes back to `main`.
The `workshop` branch is thrown away and rebuilt every time: never edit it by hand.
Change attendee/ on `main`, then run this again.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
SOLUTIONS = ["agent/core.py", "agent/sandbox.py"] + [
    f"agent/missions/{name}.py" for name in ["permission", "stop_check", "budget", "trimming", "caching", "prompt"]
]


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def main() -> None:
    if git("branch", "--show-current") != "main":
        sys.exit("Run this from the main branch.")
    if git("status", "--porcelain"):
        sys.exit("Commit your changes on main first: the workshop branch is built from the last commit.")

    git("checkout", "-q", "-B", "workshop", "main")
    try:
        build()
        git("add", "-A")
        git("commit", "-q", "-m", "Attendee version, built from main by tools/build_workshop.py\n\n"
            "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>")
        print("Built branch `workshop`:", git("log", "--oneline", "-1"))
    finally:
        git("checkout", "-q", "main")


def build() -> None:
    for path in SOLUTIONS:  # the finished files
        target = ROOT / "solutions" / Path(path).relative_to("agent")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / path, target)

    for source in (ROOT / "attendee" / "agent").rglob("*.py"):  # the TODO versions
        shutil.copy(source, ROOT / "agent" / source.relative_to(ROOT / "attendee" / "agent"))
    shutil.copy(ROOT / "attendee" / "README.md", ROOT / "README.md")
    shutil.copy(ROOT / "attendee" / "WORKSHOP.md", ROOT / "WORKSHOP.md")
    shutil.copy(ROOT / "attendee" / "SETUP.md", ROOT / "SETUP.md")

    shutil.rmtree(ROOT / "attendee")
    shutil.rmtree(ROOT / "lab")  # the lab is only for the host's reveal
    for name in ["CLAUDE.md", "tools/build_workshop.py"]:
        (ROOT / name).unlink()

    makefile = (ROOT / "Makefile").read_text()
    makefile = re.sub(r"# Host-only:.*?\nlab:\n\t[^\n]*\n\n", "", makefile, flags=re.DOTALL)
    makefile = makefile.replace(" lab ", " ")
    (ROOT / "Makefile").write_text(makefile)


if __name__ == "__main__":
    main()
