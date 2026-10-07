"""Mission 4 (optional): shorten old command outputs so the history doesn't explode.

Without it: every step re-sends every output so far; watch the token count in the trace.
"""

from agent.missions import on

KEEP_LAST = 6  # the most recent messages always stay as they are
BATCH = 10  # trim 10 messages at a time, not one by one: see below
SHORT = 300  # older command outputs are cut to this many characters


def trim(messages: list[dict]) -> list[dict]:
    """What the model gets to see. The full history itself is never changed.

    Trimming in batches keeps the start of the conversation the same for several
    steps. Caching (mission 6) only works if the start doesn't change.
    """
    if not on("trimming"):
        return messages
    cut = (len(messages) - KEEP_LAST) // BATCH * BATCH
    if cut <= 2:
        return messages
    old, recent = messages[:cut], messages[cut:]
    # old[0] is the system prompt and old[1] the task: never trim those
    return old[:2] + [shorten(message) for message in old[2:]] + recent


def shorten(message: dict) -> dict:
    content = message["content"]
    if message["role"] != "user" or len(content) <= SHORT:
        return message
    cut = len(content) - SHORT
    return {"role": "user", "content": content[:SHORT] + f"\n[... {cut} characters trimmed]"}
