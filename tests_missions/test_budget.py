"""Mission 3: stop when a run gets too long or too expensive."""

from types import SimpleNamespace

from agent.missions import budget


def trace(steps=0, cost=0.0):
    return SimpleNamespace(steps=steps, cost=cost)


def test_plenty_of_budget_left():
    assert budget.exceeded(trace(steps=3, cost=0.02)) is None


def test_too_many_steps():
    assert budget.exceeded(trace(steps=budget.MAX_STEPS)) is not None


def test_too_expensive():
    assert budget.exceeded(trace(steps=3, cost=budget.MAX_COST)) is not None


def test_unknown_cost_is_not_a_reason_to_stop():
    assert budget.exceeded(trace(steps=3, cost=None)) is None


def test_the_reason_says_what_ran_out():
    assert "step" in budget.exceeded(trace(steps=budget.MAX_STEPS)).lower()
    assert "$" in budget.exceeded(trace(cost=budget.MAX_COST + 1))


def test_it_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("MISSIONS", "none")
    assert budget.exceeded(trace(steps=999, cost=99.0)) is None
