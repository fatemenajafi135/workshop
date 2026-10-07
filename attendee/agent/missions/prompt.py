"""Mission 5 (optional): the system prompt. Change it, then measure with `make score`.

Compare: make score MISSIONS=permission,stop_check,budget   (basic prompt)
         make score                                         (your prompt)

YOUR JOB (the competition): write BETTER below. It's words, not code.
Check yourself (free):  make check-mission MISSION=prompt
Stuck?                  make catch-up STEP=prompt
"""

from agent.missions import on

BASIC = """\
You are a coding agent. You work on a Python project in /work.

In every reply, think briefly, then give exactly one shell command in a ```bash block.
You will get its output back. Each command runs in a fresh bash shell in /work,
so `cd` does not carry over. There is no internet.

Run tests with `python -m pytest`. Edit files with sed, or rewrite them with
cat > file <<'EOF'. When the task is done, reply without a bash block.
"""

# TODO: this is YOUR prompt. Add what you think the agent needs to know, after BASIC.
# Ideas: reproduce first? read before editing? never touch the tests? check everything at the end?
# Then measure it: make score MISSIONS=permission,stop_check,budget   (basic prompt)
#                  make score                                         (your prompt)
BETTER = BASIC + """
"""


def system_prompt() -> str:
    return BETTER if on("prompt") else BASIC
