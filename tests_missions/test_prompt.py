"""Mission 5: the system prompt. This one is words, not code: the test only checks the basics."""

from agent.missions import prompt


def test_it_still_explains_the_bash_block():
    assert "```bash" in prompt.system_prompt()


def test_switched_off_you_get_the_basic_prompt(monkeypatch):
    monkeypatch.setenv("MISSIONS", "none")
    assert prompt.system_prompt() == prompt.BASIC


def test_your_prompt_adds_to_the_basic_one():
    assert prompt.system_prompt().startswith(prompt.BASIC.strip())
