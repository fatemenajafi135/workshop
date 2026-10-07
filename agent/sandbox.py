"""Runs the model's commands inside the Docker container, never on the host."""

import subprocess

CONTAINER = "mini-agent"
TIMEOUT = 30  # seconds per command
MAX_OUTPUT = 4000  # characters the model gets to see per command


def run(command: str, container: str = CONTAINER) -> str:
    """Run a bash command in the sandbox. Returns its output and exit code as text."""
    # `timeout` runs inside the container, so a stuck command is really killed there.
    docker_command = ["docker", "exec", container, "timeout", str(TIMEOUT), "bash", "-c", command]
    try:
        result = subprocess.run(
            docker_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            errors="replace",
            timeout=TIMEOUT + 10,
        )
    except subprocess.TimeoutExpired:
        return f"[no answer from the sandbox after {TIMEOUT + 10}s]"

    if result.returncode == 124:
        return shorten(result.stdout) + f"\n[killed: took longer than {TIMEOUT}s]"
    return shorten(result.stdout) + f"\n[exit code {result.returncode}]"


def shorten(output: str) -> str:
    """Keep the start and the end of long output, cut the middle."""
    if len(output) <= MAX_OUTPUT:
        return output
    half = MAX_OUTPUT // 2
    cut = len(output) - MAX_OUTPUT
    return output[:half] + f"\n[... {cut} characters cut ...]\n" + output[-half:]
