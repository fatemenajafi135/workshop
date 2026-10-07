"""Is this machine ready for the workshop? Run: make check

Stops at the first problem and says how to fix it.
"""

import os
import platform
import shutil
import subprocess
import sys
from urllib.parse import urlparse

IMAGE = "mini-agent-sandbox"
CONTAINER = "mini-agent"


class Problem(Exception):
    """A check failed. The message says how to fix it."""


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=120)


def check_python() -> str:
    if platform.system() == "Windows":
        raise Problem("native Windows isn't supported: open a WSL2 terminal and run everything there")
    if sys.version_info < (3, 12):
        raise Problem(f"Python {platform.python_version()} found, need 3.12 or newer")
    return f"Python {platform.python_version()}"


def check_docker() -> str:
    if shutil.which("docker") is None:
        raise Problem("docker not found: install Docker Desktop (macOS) or Docker Engine (Linux)")
    if run(["docker", "info"]).returncode != 0:
        raise Problem("Docker is installed but not running (or needs sudo): start Docker and try again")
    return "Docker is running"


def check_sandbox() -> str:
    if run(["docker", "image", "inspect", IMAGE]).returncode != 0:
        raise Problem("sandbox image is missing: run `make setup`")
    state = run(["docker", "inspect", "-f", "{{.State.Running}}", CONTAINER]).stdout.strip()
    if state != "true":
        raise Problem("sandbox container isn't running: run `make reset`")
    return f"container {CONTAINER} is running"


def check_tests() -> str:
    result = run(["docker", "exec", CONTAINER, "python", "-m", "pytest", "-q", "--tb=no"])
    last_line = (result.stdout.strip().splitlines() or [""])[-1]
    # pytest exit codes: 0 = all passed, 1 = some failed. Anything else means it couldn't run.
    if result.returncode not in (0, 1):
        raise Problem(f"pytest couldn't run in the sandbox ({last_line}): run `make reset`")
    return f"pytest runs in the sandbox: {last_line}"


def check_model() -> str:
    try:
        from openai import AuthenticationError

        from agent import llm
    except ImportError:
        raise Problem("Python packages are missing: run `make setup`, then `make check`")
    for name in ("API_KEY", "MODEL"):
        if not os.environ.get(name):
            raise Problem(f"{name} is not set: add it to .env (see .env.example)")
    for name in ("ALL_PROXY", "all_proxy"):
        if os.environ.get(name, "").startswith("socks://"):
            raise Problem(
                f"{name} is a socks:// proxy, which Python can't use: run `unset ALL_PROXY all_proxy` "
                "(an http:// HTTPS_PROXY keeps working)"
            )
    try:
        reply = llm.ask([{"role": "user", "content": "Reply with just the word: ready"}])
    except AuthenticationError:
        raise Problem("the API key was rejected: check API_KEY in .env")
    except Exception as error:
        raise Problem(f"the model call failed: {type(error).__name__}: {str(error)[:300]}")
    tokens = f"{reply.input_tokens} tokens in, {reply.output_tokens} out"
    host = urlparse(os.environ.get("BASE_URL") or llm.GATEWAY_URL).hostname
    return f"{os.environ['MODEL']} via {host} replied {reply.text.strip()!r} ({tokens})"


CHECKS = [
    ("Python", check_python),
    ("Docker", check_docker),
    ("Sandbox", check_sandbox),
    ("Tests", check_tests),
    ("Model", check_model),
]


def main() -> None:
    for name, check in CHECKS:
        try:
            print(f"  ✓ {name}: {check()}")
        except Problem as problem:
            print(f"  ✗ {name}: {problem}")
            sys.exit(1)
    print("\nAll good, you're ready for the workshop.")


if __name__ == "__main__":
    main()
