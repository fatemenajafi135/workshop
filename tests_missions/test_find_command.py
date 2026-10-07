"""find_command() in agent/core.py: the first command in the model's reply."""

from agent.core import find_command


def test_bash_block():
    assert find_command("Let me look.\n```bash\ncat money.py\n```\nThen more.") == "cat money.py"


def test_the_first_block_wins():
    assert find_command("```bash\nfirst\n```\n```bash\nsecond\n```") == "first"


def test_a_block_cut_off_by_the_stop_word_still_counts():
    assert find_command("Let me look.\n```bash\ncat money.py\n") == "cat money.py"


def test_claudes_own_tool_format():
    reply = '<function_calls>\n<invoke name="bash">\n<parameter name="command">ls</parameter>\n</invoke>'
    assert find_command(reply) == "ls"


def test_multi_line_commands_stay_intact():
    assert find_command("```bash\ncat > a.py <<'EOF'\nx = 1\nEOF\n```") == "cat > a.py <<'EOF'\nx = 1\nEOF"


def test_no_command():
    assert find_command("All tests pass. Done.") is None


def test_other_languages_are_not_commands():
    assert find_command("```python\nprint(1)\n```") is None
