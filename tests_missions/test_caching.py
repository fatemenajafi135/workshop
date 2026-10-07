"""Mission 6: ask the provider to remember the start of the conversation."""

from agent.missions import caching


def messages():
    return [
        {"role": "system", "content": "system prompt"},
        {"role": "user", "content": "the task"},
        {"role": "assistant", "content": "I'll look.\n```bash\nls\n```"},
        {"role": "user", "content": "output\n[exit code 0]"},
    ]


def test_the_last_message_is_marked():
    last = caching.mark(messages())[-1]
    assert isinstance(last["content"], list)
    assert last["content"][0]["text"] == "output\n[exit code 0]"
    assert last["content"][0]["cache_control"] == {"type": "ephemeral"}


def test_nothing_else_changes():
    marked = caching.mark(messages())
    assert marked[:-1] == messages()[:-1]
    assert marked[-1]["role"] == "user"


def test_the_original_list_is_not_changed():
    original = messages()
    caching.mark(original)
    assert original == messages()


def test_it_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("MISSIONS", "none")
    assert caching.mark(messages()) == messages()
