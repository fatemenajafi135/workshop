"""The only file that talks to the model.

Works with any OpenAI-compatible endpoint. The default is Vercel AI Gateway,
which serves models from most providers behind one key.
Settings come from .env: MODEL, API_KEY, and optionally BASE_URL.
"""

import functools
import os
from dataclasses import dataclass
from pathlib import Path

from openai import BadRequestError, OpenAI

GATEWAY_URL = "https://ai-gateway.vercel.sh/v1"
ENV_FILE = Path(__file__).parent.parent / ".env"


@dataclass
class Reply:
    text: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int  # part of input_tokens the provider remembered (cheaper)
    cost: float | None  # dollars, None if unknown


def ask(messages: list[dict], stop: list[str] | None = None) -> Reply:
    """Send the conversation so far, get the model's next message back.

    `stop`: the model stops writing as soon as it writes one of these.
    """
    model = setting("MODEL")
    try:
        response = client().chat.completions.create(model=model, messages=messages, stop=stop)
        text = response.choices[0].message.content or ""
    except BadRequestError:
        # Some providers reject `stop` or the caching mark. Try again without them,
        # and cut the reply at the first stop word ourselves.
        response = client().chat.completions.create(model=model, messages=plain(messages))
        text = cut_at(response.choices[0].message.content or "", stop or [])
    usage = response.usage
    input_tokens = usage.prompt_tokens if usage else 0
    output_tokens = usage.completion_tokens if usage else 0
    details = getattr(usage, "prompt_tokens_details", None)
    cached_tokens = (details.cached_tokens or 0) if details else 0
    # Vercel AI Gateway reports the real cost of each call (cache discounts included).
    real_cost = (usage.model_extra or {}).get("cost") if usage else None
    return Reply(
        text=text,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cached_tokens=cached_tokens,
        cost=real_cost if real_cost is not None else estimated_cost(model, input_tokens, output_tokens),
    )


def cut_at(text: str, stop: list[str]) -> str:
    """The text up to the first stop word (what `stop` would have given us)."""
    ends = [text.find(word) for word in stop if word in text]
    return text[: min(ends)] if ends else text


def plain(messages: list[dict]) -> list[dict]:
    """The same messages, with caching marks turned back into plain text."""
    return [{"role": m["role"], "content": text_of(m["content"])} for m in messages]


def text_of(content: str | list[dict]) -> str:
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content)


def estimated_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """For endpoints that don't report the cost: tokens times the price.

    The price comes from .env (PRICE_IN, PRICE_OUT: dollars per million tokens),
    or from the endpoint's model list if it has one (Vercel AI Gateway does).
    """
    if os.environ.get("PRICE_IN") and os.environ.get("PRICE_OUT"):
        return (input_tokens * float(os.environ["PRICE_IN"]) + output_tokens * float(os.environ["PRICE_OUT"])) / 1e6
    price = prices(model)
    if price is None:
        return None
    return input_tokens * price[0] + output_tokens * price[1]


@functools.cache
def prices(model: str) -> tuple[float, float] | None:
    """Dollars per input and output token, if the endpoint lists them (Vercel AI Gateway does)."""
    try:
        for listed in client().models.list():
            if listed.id == model:
                pricing = getattr(listed, "pricing", None) or {}
                return float(pricing["input"]), float(pricing["output"])
    except Exception:  # prices are nice to have, never worth crashing for
        pass
    return None


@functools.cache
def client() -> OpenAI:
    return OpenAI(
        api_key=setting("API_KEY"),
        base_url=os.environ.get("BASE_URL") or GATEWAY_URL,
        timeout=120,
    )


def setting(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set: add it to .env (see .env.example)")
    return value


def load_env(path: Path = ENV_FILE) -> None:
    """Copy KEY=value lines from .env into the environment.

    Real environment variables win. If a key appears twice in the file, the last one wins
    (so uncommenting a second provider's lines works, even if the first is still on).
    """
    if not path.exists():
        return
    values = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip().strip("\"'")
    for key, value in values.items():
        os.environ.setdefault(key, value)


load_env()
