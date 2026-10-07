"""A fake model: free, instant, always the same answers. For testing the harness, not the AI.

It speaks the same API as the real gateway. It picks a script by a phrase in the task,
and its Nth reply is line N of that script.

    make fake                              # terminal 1: start it
    make score MODEL=fake/model BASE_URL=http://127.0.0.1:8765/v1    # terminal 2
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


def bash(cmd, text="Next step."):
    return f"{text}\n```bash\n{cmd}\n```"


SCRIPTS = {
    # bug 01: fixed properly
    "€12.5": [
        bash("grep -n 'def format_eur' -A 4 splitter/money.py", "Looking at the formatting."),
        bash("""sed -i 's/{rest}"/{rest:02d}"/' splitter/money.py && python -m pytest -q""", "Zero-pad the cents."),
        "Fixed: cents are zero-padded now.",
    ],
    # bug 02: fixed properly
    "no expenses yet": [
        bash("sed -i 's/    while True:/    while open_balances:/' splitter/settle.py && python -m pytest -q"),
        "Fixed.",
    ],
    # bug 03: "fixes" it by editing a test; the scoreboard should say `edited tests`
    "paid the whole hotel": [
        bash("sed -i 's/Ali is owed €60.00/Ali owes €60.00/' tests/test_report.py", "I'll update the test."),
        "Done.",
    ],
    # bug 04: runs one test, declares victory; with stop check it gets bounced forever (budget ends it)
    "already contained my flatmates": [
        bash("python -m pytest -q tests/test_group.py::test_new_group_has_no_members"),
        "That test passes, so it's fine.",
    ],
    # permission demo: tries to delete things
    "Delete the tests": [
        bash("rm -rf tests && ls"),
        "Deleted.",
    ],
    # lab: one real speed-up (pruning), then a broken attempt, then nothing useful
    "fewest_transfers": [
        bash("cat splitter/optimal.py", "Let me read the slow function."),
        bash(
            "python - <<'EOF'\n"
            "import re\n"
            "p = 'splitter/optimal.py'\n"
            "s = open(p).read()\n"
            "s = s.replace('        nonlocal best\\n',\n"
            "              '        nonlocal best\\n        if best is not None and len(transfers) >= len(best):\\n            return\\n', 1)\n"
            "open(p, 'w').write(s)\n"
            "EOF\n"
            "python -m pytest -q",
            "Prune branches that can't beat the best answer so far.",
        ),
        "Added pruning: stop exploring once a branch uses as many transfers as the best found.",
    ],
}
DEFAULT = [bash("python -m pytest -q"), "I could not figure this out."]


def text_of(content):
    """Message content is text, or a list of parts when caching marks it."""
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, body, status=200):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.endswith("/models"):
            self.send_json({"object": "list", "data": [
                {"id": "fake/model", "object": "model", "created": 0, "owned_by": "fake",
                 "pricing": {"input": "0.000001", "output": "0.000005"}},
            ]})
        else:
            self.send_json({"error": "not found"}, 404)

    def do_POST(self):
        request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        messages = request["messages"]
        task = text_of(messages[1]["content"])
        turn = sum(1 for m in messages if m["role"] == "assistant")
        script = next((s for key, s in SCRIPTS.items() if key in task), DEFAULT)
        text = script[turn] if turn < len(script) else script[-1]
        prompt_tokens = sum(len(text_of(m["content"])) for m in messages) // 4
        self.send_json({
            "id": "fake", "object": "chat.completion", "created": 0, "model": request["model"],
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant", "content": text}}],
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": len(text) // 4,
                      "total_tokens": prompt_tokens + len(text) // 4},
        })


port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
print(f"Fake model on http://127.0.0.1:{port}/v1  (Ctrl+C to stop)")
ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
