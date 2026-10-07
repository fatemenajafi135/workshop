"""Mission 1: risky commands need a human's OK."""

import pytest

from agent.missions import permission


def no_human(monkeypatch):
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)


def human_says(monkeypatch, answer):
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda prompt="": answer)


@pytest.mark.parametrize("command", [
    "ls -la", "cat splitter/money.py", "python -m pytest -q", "sed -i 's/a/b/' x.py", "git diff", "grep -rn format src",
])
def test_safe_commands_just_run(monkeypatch, command):
    no_human(monkeypatch)
    assert permission.approved(command) is True


@pytest.mark.parametrize("command", [
    "rm -rf tests", "cd /work && rm x.py", "git push origin main", "git reset --hard",
    "curl https://example.com", "wget http://x.y", "pip install requests", "sudo ls",
])
def test_risky_commands_are_refused_when_nobody_can_answer(monkeypatch, command):
    no_human(monkeypatch)
    assert permission.approved(command) is False


def test_a_human_can_allow_a_risky_command(monkeypatch):
    human_says(monkeypatch, "y")
    assert permission.approved("rm old_file.py") is True


def test_a_human_can_refuse(monkeypatch):
    human_says(monkeypatch, "n")
    assert permission.approved("rm old_file.py") is False


def test_an_empty_answer_means_no(monkeypatch):
    human_says(monkeypatch, "")
    assert permission.approved("rm old_file.py") is False


def test_it_can_be_switched_off(monkeypatch):
    no_human(monkeypatch)
    monkeypatch.setenv("MISSIONS", "none")
    assert permission.approved("rm -rf tests") is True
