"""The only file that talks to the model.

Works with any OpenAI-compatible endpoint. The default is Vercel AI Gateway,
which serves models from most providers behind one key.
Settings come from .env: MODEL, API_KEY, and optionally BASE_URL.
"""

import os
from dataclasses import dataclass
from pathlib import Path

from openai import OpenAI

GATEWAY_URL = "https://ai-gateway.vercel.sh/v1"
ENV_FILE = Path(__file__).parent.parent / ".env"


@dataclass
class Reply:
    text: str
    input_tokens: int
    output_tokens: int


def ask(messages: list[dict]) -> Reply:
    """Send the conversation so far, get the model's next message back."""
    client = OpenAI(
        api_key=setting("API_KEY"),
        base_url=os.environ.get("BASE_URL") or GATEWAY_URL,
        timeout=120,
    )
    response = client.chat.completions.create(model=setting("MODEL"), messages=messages)
    usage = response.usage
    return Reply(
        text=response.choices[0].message.content or "",
        input_tokens=usage.prompt_tokens if usage else 0,
        output_tokens=usage.completion_tokens if usage else 0,
    )


def setting(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is not set: add it to .env (see .env.example)")
    return value


def load_env(path: Path = ENV_FILE) -> None:
    """Copy KEY=value lines from .env into the environment. Real env vars win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


load_env()
