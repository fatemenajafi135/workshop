"""Level 5 (at home): sandbox.run() and sandbox.shorten(). run() needs the sandbox: make reset."""

import subprocess

import pytest

from agent import sandbox


def sandbox_is_running():
    result = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", sandbox.CONTAINER],
                            capture_output=True, text=True)
    return result.stdout.strip() == "true"


needs_sandbox = pytest.mark.skipif(not sandbox_is_running(), reason="start the sandbox first: make reset")


def test_short_output_is_left_alone():
    assert sandbox.shorten("hello") == "hello"


def test_long_output_keeps_the_start_and_the_end():
    output = "START" + "x" * 10000 + "END"
    short = sandbox.shorten(output)
    assert len(short) < len(output) / 2
    assert short.startswith("START") and short.endswith("END")
    assert "cut" in short


@needs_sandbox
def test_it_runs_commands_in_the_project_folder():
    assert "splitter" in sandbox.run("ls")


@needs_sandbox
def test_it_reports_the_exit_code():
    assert sandbox.run("exit 3").strip().endswith("[exit code 3]")


@needs_sandbox
def test_errors_are_included():
    assert "oops" in sandbox.run("echo oops >&2")


@needs_sandbox
def test_a_stuck_command_is_killed(monkeypatch):
    monkeypatch.setattr(sandbox, "TIMEOUT", 2)
    assert "killed" in sandbox.run("sleep 30")


@needs_sandbox
def test_commands_cannot_reach_the_internet():
    output = sandbox.run("python -c \"import urllib.request; urllib.request.urlopen('https://pypi.org', timeout=3)\" 2>&1 | tail -1")
    assert "Error" in output
