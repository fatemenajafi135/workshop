"""Mission 4 (optional): shorten old command outputs so the history doesn't explode.

Without it: every step re-sends every output so far; watch the token count in the trace.
"""

from agent.missions import on

KEEP_LAST = 6  # the most recent messages stay as they are
SHORT = 300  # older command outputs are cut to this many characters


def trim(messages: list[dict]) -> list[dict]:
    """What the model gets to see. The full history itself is never changed."""
    if not on("trimming"):
        return messages
    old, recent = messages[:-KEEP_LAST], messages[-KEEP_LAST:]
    # old[0] is the system prompt and old[1] the task: never trim those
    return old[:2] + [shorten(message) for message in old[2:]] + recent


def shorten(message: dict) -> dict:
    content = message["content"]
    if message["role"] != "user" or len(content) <= SHORT:
        return message
    cut = len(content) - SHORT
    return {"role": "user", "content": content[:SHORT] + f"\n[... {cut} characters trimmed]"}
