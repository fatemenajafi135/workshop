import pytest


@pytest.fixture(autouse=True)
def all_missions_on(monkeypatch):
    monkeypatch.delenv("MISSIONS", raising=False)
