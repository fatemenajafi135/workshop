"""Mission 6 (optional): prompt caching.

THE HABIT: every step sends the whole conversation again, at full price. With caching the
provider remembers the start of it, and re-sent text costs about 10x less (Claude Haiku:
$0.10 instead of $1 per million tokens). It only starts above ~4,000 tokens, so you will
see it in long runs. The step header then shows "(N cached)".

YOUR JOB: write mark(messages). Mark the LAST message, so everything up to it is remembered.
A normal message looks like   {"role": "user", "content": "some text"}
A marked message looks like   {"role": "user", "content": [
                                  {"type": "text", "text": "some text",
                                   "cache_control": {"type": "ephemeral"}}]}
Return a new list; don't change the one you got.
  - Missions can be switched off: if not on("caching"), return messages.
  - Not every provider supports this. If one doesn't, llm.py quietly tries again without it.

Check yourself (free):  make check-mission MISSION=caching
Stuck?                  make catch-up STEP=caching
"""

from agent.missions import on


def mark(messages: list[dict]) -> list[dict]:
    """Ask the provider to remember everything up to the last message."""
    # TODO: write this.
    return messages
