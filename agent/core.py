"""The agent: ask the model, run its command, show it the output, repeat.

Run it with: make run BUG=01
"""

import re
import sys
from pathlib import Path

from agent import llm, sandbox

SYSTEM_PROMPT = """\
You are a coding agent. You fix bugs in a Python project in /work.

In every reply, think briefly, then give exactly one shell command in a ```bash block.
You will get its output back. Each command runs in a fresh bash shell in /work,
so `cd` does not carry over. There is no internet.

Run tests with `python -m pytest`. Edit files with sed, or rewrite them with
cat > file <<'EOF'. When the task is done, reply without a bash block.
"""


def solve(task: str) -> None:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]
    while True:
        reply = llm.ask(messages)
        messages.append({"role": "assistant", "content": reply.text})
        print(reply.text)

        command = find_command(reply.text)
        if command is None:
            return  # no command: the model thinks it's done

        output = sandbox.run(command)
        messages.append({"role": "user", "content": output})
        print(output)


def find_command(text: str) -> str | None:
    """The first ```bash block in the model's reply, or None if there is none."""
    match = re.search(r"```bash\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else None


if __name__ == "__main__":
    solve(Path(sys.argv[1]).read_text())
