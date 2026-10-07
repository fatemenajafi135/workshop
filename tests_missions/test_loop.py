"""Step 1: solve() in agent/core.py. Free: the model, the sandbox and the trace are fakes."""

from types import SimpleNamespace

from agent import core, llm, sandbox


class FakeTrace:
    steps = 0
    cost = 0.0

    def __init__(self):
        self.notes = []
        self.commands = []

    def model_said(self, reply):
        self.steps += 1

    def ran(self, command, output):
        self.commands.append(command)

    def note(self, text):
        self.notes.append(text)


def run_solve(monkeypatch, replies, output="[exit code 0]"):
    """Run solve() with a model that gives these replies, one per step."""
    seen = []  # what the model was sent at each step
    answers = iter(replies)

    def fake_ask(messages, stop=None):
        seen.append(llm.plain(messages))  # caching marks (mission 6) turned back into text
        return llm.Reply(next(answers), 10, 5, 0, 0.001)

    monkeypatch.setattr(llm, "ask", fake_ask)
    monkeypatch.setattr(sandbox, "run", lambda command, container="x": output)
    trace = FakeTrace()
    return core.solve("fix the bug", trace), trace, seen


def test_a_reply_without_a_command_ends_the_run(monkeypatch):
    result, trace, seen = run_solve(monkeypatch, ["All good, nothing to do."])
    assert result == "done"
    assert len(seen) == 1


def test_the_model_gets_the_task(monkeypatch):
    _, _, seen = run_solve(monkeypatch, ["Done."])
    assert seen[0][-1] == {"role": "user", "content": "fix the bug"}


def test_the_command_is_run_and_traced(monkeypatch):
    _, trace, _ = run_solve(monkeypatch, ["Look.\n```bash\nls -la\n```", "Done."])
    assert trace.commands == ["ls -la"]


def test_the_output_goes_back_to_the_model(monkeypatch):
    _, _, seen = run_solve(
        monkeypatch, ["Look.\n```bash\nls\n```", "Done."], output="file.py\n[exit code 0]"
    )
    last_two = seen[1][-2:]
    assert last_two[0] == {"role": "assistant", "content": "Look.\n```bash\nls\n```"}
    assert last_two[1] == {"role": "user", "content": "file.py\n[exit code 0]"}


def test_it_keeps_going_until_there_is_no_command(monkeypatch):
    replies = ["a\n```bash\none\n```", "b\n```bash\ntwo\n```", "c\n```bash\nthree\n```", "Done."]
    result, trace, seen = run_solve(monkeypatch, replies)
    assert result == "done"
    assert trace.commands == ["one", "two", "three"]
    assert len(seen) == 4
