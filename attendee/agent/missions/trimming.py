"""Mission 4 (optional): shorten old command outputs so the history doesn't explode.

THE HABIT: every step re-sends every old output. The token count in the trace keeps growing.
  See it:  make run BUG=06 MISSIONS=stop_check,budget      (watch the tokens in each step header)

YOUR JOB: write trim(messages). It returns what the model gets to see. The real history
(`messages` in core.py) is never changed: return a new list.
  - messages[0] is the system prompt, messages[1] is the task: never trim those.
  - The last KEEP_LAST messages stay as they are.
  - Older messages from the "user" role are command outputs: cut those longer than SHORT
    characters to SHORT characters, plus a note like "[... 1700 characters trimmed]".
  - Assistant messages (the model's own words) stay as they are.
  - To keep caching (mission 6) working, trim in batches, not one by one: cut at
    (len(messages) - KEEP_LAST) // BATCH * BATCH, so the start only changes every few steps.
  - Missions can be switched off: if not on("trimming"), return messages.

Check yourself (free):  make check-mission MISSION=trimming
Stuck?                  make catch-up STEP=trimming
"""

from agent.missions import on

KEEP_LAST = 6  # the most recent messages always stay as they are
BATCH = 10  # trim 10 messages at a time, not one by one
SHORT = 300  # older command outputs are cut to this many characters


def trim(messages: list[dict]) -> list[dict]:
    """What the model gets to see. The full history itself is never changed."""
    # TODO: write this.
    return messages
