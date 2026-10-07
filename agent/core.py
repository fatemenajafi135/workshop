"""The agent: ask the model, run its command, show it the output, repeat.

    make run BUG=01                     # fix a bug
    make ask TASK="what's in /work?"    # any task, in the current sandbox

YOUR JOB (workshop step 1): fill in the four TODOs in solve(). About 10 lines in total.
Check yourself, free and instant:   make check-mission MISSION=loop
Stuck? Get the finished file:       make catch-up STEP=loop
"""

import argparse
import re
from pathlib import Path

from agent import llm, sandbox
from agent.missions import budget, caching, permission, prompt, stop_check, trimming
from agent.trace import Trace

# Stop the model right after its first command. Otherwise it writes ten commands at
# once and invents their output, which we pay for and which confuses it later.
STOP_AFTER_COMMAND = ["```\n", "</function_calls>"]


def solve(task: str, trace: Trace, container: str = sandbox.CONTAINER) -> str:
    """Work on the task until done. Returns why it stopped."""
    messages = [
        {"role": "system", "content": prompt.system_prompt()},
        {"role": "user", "content": task},
    ]
    while True:
        out_of_budget = budget.exceeded(trace)  # mission 3 (given)
        if out_of_budget:
            return out_of_budget

        # What the model gets to see: missions 4 and 6 (given)
        context = caching.mark(trimming.trim(messages))

        # TODO 1: ask the model.
        #   reply = llm.ask(context, stop=STOP_AFTER_COMMAND)
        #   Then add reply.text to `messages` as an {"role": "assistant", ...} message,
        #   and call trace.model_said(reply).

        # TODO 2: find the command in the reply, with find_command(reply.text).
        command = None

        if command is None:  # no command: the model thinks it's done
            problem = stop_check.unfinished(container)  # mission 2 (given)
            if problem is None:
                return "done"
            trace.note("tests still fail, sending the failures back")
            messages.append({"role": "user", "content": problem})
            continue

        if not permission.approved(command):  # mission 1 (given)
            trace.note(f"refused: {command}")
            output = "The user did not allow this command. Find another way."
        else:
            # TODO 3: run the command in the sandbox: sandbox.run(command, container)
            output = "TODO"

        # TODO 4: send the output back to the model, as a {"role": "user", ...} message,
        #   and call trace.ran(command, output).


def find_command(text: str) -> str | None:
    """The first command in the reply, or None if there is none.

    We ask for a ```bash block. Claude models sometimes use their own tool format
    instead (<invoke name="bash">), so we accept that too.
    """
    match = re.search(r"```bash\s*\n(.*?)(?:```|$)", text, re.DOTALL) or re.search(
        r'<invoke name="bash">\s*<parameter name="\w+">(.*?)</parameter>', text, re.DOTALL
    )
    return match.group(1).strip() if match else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the mini coding agent on one task.")
    parser.add_argument("task", help="a task file (like bugs/01-*/issue.md) or the task text itself")
    parser.add_argument("--container", default=sandbox.CONTAINER, help="which sandbox to work in")
    parser.add_argument("--save-to", type=Path, help="where to save the trace (default: runs/)")
    args = parser.parse_args()

    path = Path(args.task)
    task = path.read_text() if path.is_file() else args.task
    label = path.parent.name if path.is_file() else "task"
    trace = Trace(task, label, args.save_to)
    try:
        result = solve(task, trace, args.container)
    except KeyboardInterrupt:
        result = "stopped with Ctrl+C"
    except Exception as error:
        result = f"crashed: {type(error).__name__}: {error}"
    trace.finish(result)


if __name__ == "__main__":
    main()
