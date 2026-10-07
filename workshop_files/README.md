# Build a mini coding agent

A workshop: you build the heart of a coding agent in about 10 lines, then find out why real ones are much bigger.

**Setup (before the workshop): [SETUP.md](SETUP.md).  The guide for the day: [WORKSHOP.md](WORKSHOP.md)**

The short version of the setup:

```bash
make setup      # then put your API key in .env (any OpenAI-compatible provider works)
make check      # every line must show ✓
```

What's in this repo:

| | |
|---|---|
| `agent/` | The agent. `core.py` is the loop you write. `missions/` has the fixes for its bad habits |
| `demo_project/` | A small app (split expenses between friends). Each bug is a patch in `bugs/` |
| `tests_missions/` | Free tests for the code you write. No AI, no cost |
| `solutions/` | The finished files. `make catch-up STEP=loop` copies one in when you're stuck |
| `scoreboard.py` | `make score`: runs the agent on several bugs and prints a table |
