"""Get a finished solution when you're stuck.

    make catch-up STEP=loop          # the loop in agent/core.py
    make catch-up STEP=permission    # or: stop_check, budget, trimming, caching, prompt
    make catch-up STEP=missions      # every mission you haven't finished yet (not the prompt)
    make catch-up STEP=all           # the loop and every mission you haven't finished yet

Your own version is kept next to it as <file>.mine, so nothing is lost.
With missions and all, a part whose free test already passes is left alone: it's yours.
Without make, it's just a copy:  cp solutions/missions/permission.py agent/missions/permission.py
"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
MISSIONS = ["permission", "stop_check", "budget", "trimming", "caching", "prompt"]
STEPS = {"loop": ("core.py", "agent/core.py"), "sandbox": ("sandbox.py", "agent/sandbox.py")}
STEPS |= {name: (f"missions/{name}.py", f"agent/missions/{name}.py") for name in MISSIONS}


def main() -> None:
    wanted = sys.argv[1] if len(sys.argv) > 1 else ""
    bulk = wanted in ("missions", "all")
    if wanted == "all":
        names = [name for name in STEPS if name not in ("prompt", "sandbox")]
    elif wanted == "missions":
        names = [name for name in MISSIONS if name != "prompt"]
    elif wanted in STEPS:
        names = [wanted]
    else:
        sys.exit(f"Which step? make catch-up STEP=<one of: {', '.join(STEPS)}, missions, all>")

    if not (ROOT / "solutions").is_dir():
        sys.exit("There is no solutions/ folder here: this is the full version, nothing to catch up on.")

    for name in names:
        if bulk and passes_its_test(name):
            print(f"  = {STEPS[name][1]} already works: kept yours")
            continue
        source, target = (ROOT / "solutions" / STEPS[name][0]), ROOT / STEPS[name][1]
        if target.read_text() == source.read_text():
            print(f"  = {STEPS[name][1]} is already the finished version")
            continue
        if target.exists():
            shutil.copy(target, target.with_name(target.name + ".mine"))
        shutil.copy(source, target)
        print(f"  ✓ {STEPS[name][1]}  (yours is saved as {target.name}.mine)")


def passes_its_test(name: str) -> bool:
    test = ROOT / "tests_missions" / f"test_{name}.py"
    command = [sys.executable, "-m", "pytest", str(test), "-q", "-p", "no:cacheprovider"]
    return subprocess.run(command, capture_output=True, cwd=ROOT).returncode == 0


if __name__ == "__main__":
    main()
