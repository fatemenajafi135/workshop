"""Mission 2: the agent may only stop when the whole test suite passes."""

from agent.missions import stop_check


def pytest_says(monkeypatch, output):
    monkeypatch.setattr(stop_check.sandbox, "run", lambda command, container="x": output)


def test_green_tests_let_the_agent_stop(monkeypatch):
    pytest_says(monkeypatch, "39 passed in 0.03s\n[exit code 0]")
    assert stop_check.unfinished("mini-agent") is None


def test_red_tests_send_the_failures_back(monkeypatch):
    pytest_says(monkeypatch, "FAILED tests/test_group.py::test_new_group_has_no_members\n1 failed\n[exit code 1]")
    message = stop_check.unfinished("mini-agent")
    assert message is not None
    assert "test_new_group_has_no_members" in message


def test_it_runs_the_whole_suite_not_one_test(monkeypatch):
    asked = []
    monkeypatch.setattr(stop_check.sandbox, "run", lambda command, container="x": asked.append(command) or "[exit code 0]")
    stop_check.unfinished("mini-agent")
    assert asked and "pytest" in asked[0] and "::" not in asked[0]


def test_it_can_be_switched_off(monkeypatch):
    pytest_says(monkeypatch, "1 failed\n[exit code 1]")
    monkeypatch.setenv("MISSIONS", "none")
    assert stop_check.unfinished("mini-agent") is None
