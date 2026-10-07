"""Mission 4: shorten old command outputs so the history doesn't explode."""

from agent.missions import trimming


def conversation(n):
    """system + task + n more messages; every command output is long."""
    messages = [{"role": "system", "content": "system prompt"}, {"role": "user", "content": "the task"}]
    for i in range(n):
        if i % 2 == 0:
            messages.append({"role": "assistant", "content": f"step {i}\n```bash\nls\n```"})
        else:
            messages.append({"role": "user", "content": f"output {i}: " + "x" * 2000})
    return messages


def test_short_conversations_are_left_alone():
    messages = conversation(4)
    assert trimming.trim(messages) == messages


def test_old_outputs_get_shorter():
    messages = conversation(40)
    trimmed = trimming.trim(messages)
    assert sum(len(m["content"]) for m in trimmed) < sum(len(m["content"]) for m in messages) / 2


def test_the_system_prompt_and_the_task_are_never_trimmed():
    messages = conversation(40)
    trimmed = trimming.trim(messages)
    assert trimmed[0] == messages[0]
    assert trimmed[1] == messages[1]


def test_recent_messages_stay_as_they_are():
    messages = conversation(40)
    assert trimming.trim(messages)[-6:] == messages[-6:]


def test_the_model_never_loses_a_message():
    messages = conversation(40)
    assert len(trimming.trim(messages)) == len(messages)


def test_the_real_history_is_not_changed():
    messages = conversation(40)
    before = [dict(m) for m in messages]
    trimming.trim(messages)
    assert messages == before


def test_assistant_messages_are_not_trimmed():
    messages = conversation(40)
    for before, after in zip(messages, trimming.trim(messages)):
        if before["role"] == "assistant":
            assert after == before


def test_the_start_stays_the_same_for_several_steps():
    # Caching (mission 6) only works if the start of the conversation doesn't change.
    first = trimming.trim(conversation(30))
    one_step_later = trimming.trim(conversation(32))
    assert first[:25] == one_step_later[:25]


def test_it_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("MISSIONS", "none")
    messages = conversation(40)
    assert trimming.trim(messages) == messages
