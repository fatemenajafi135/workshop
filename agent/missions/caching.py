"""Mission 6 (optional): prompt caching.

Every step sends the whole conversation again. With caching, the provider keeps the
start of the conversation, and sending it again costs 10x less (Claude Haiku:
$0.10 instead of $1 per million tokens). It only starts with long conversations
(Claude Haiku: 4,096+ tokens), and only if nothing in the start has changed.

Without it: long runs pay full price for the same old text, step after step.
"""

from agent.missions import on


def mark(messages: list[dict]) -> list[dict]:
    """Ask the provider to remember everything up to the last message."""
    if not on("caching"):
        return messages
    last = messages[-1]
    part = {"type": "text", "text": last["content"], "cache_control": {"type": "ephemeral"}}
    return messages[:-1] + [{"role": last["role"], "content": [part]}]
