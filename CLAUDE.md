# CLAUDE.md

## What this repo is

Material for a hands-on workshop: **"Build a mini coding agent"**.
Audience: developers who know Python, all with GitHub and Docker installed.

Story of the session:
> "We build a coding agent in ~10 lines, then spend an hour finding out why real ones aren't 10 lines."

Attendees build a tiny agent that fixes bugs in a demo project, improve its harness in pairs,
compete on a bug set, and finally see the host's long-running "lab" demo (an outer loop that
optimizes code by itself for the whole session).

## Session flow (the repo must support each step)

1. **Setup (5 min)**: clone, `make setup`, put the key in `.env`, `make check`
2. **Core loop, live-coded (15 min)**: attendees type the agent loop along with the host
3. **First run (10 min)**: agent fixes one bug, tests turn green in the terminal
4. **Missions in pairs (30 min)**: fix the agent's bad habits (see Missions)
5. **Competition (20 min)**: same bug set for everyone, `make score` prints a table
6. **Lab reveal (20 min)**: host shows what the outer loop did during the session

## Architecture

- The **agent runs on the host** (`agent/`). Every command the model asks for runs **inside a Docker container** via `docker exec` with a timeout. Nothing the model runs touches the host.
- The demo project is **copied into the image, not bind-mounted**. A bad command can only break the container; `make reset` recreates it.
- The model replies in plain text with one ```bash``` block per step. No native tool-calling: keeps the loop model-agnostic and easy to explain on a slide. No bash block = the agent thinks it's done.
- Model and API key come from `.env` (`MODEL=`, `API_KEY=`, optional `BASE_URL=`). One small wrapper, `agent/llm.py`, using the `openai` SDK against any OpenAI-compatible endpoint; default is **Vercel AI Gateway** (one key, most providers). The only model name in the repo is the default in `.env.example`.

## Planned layout

```
agent/
  core.py        # the ~10-line loop (TODO version on `start`, full on solution branches)
  llm.py         # model wrapper, returns text + token usage
  sandbox.py     # run(cmd) -> output, via docker exec, with timeout and output truncation
  trace.py       # colored step-by-step terminal output + saves runs/<id>.json
  missions/      # one file per mission, with TODOs
demo_project/    # clean `splitter` package + pytest tests (all green)
bugs/<id>/       # issue.md (what a user would write), bug.patch, test.txt
scoreboard.py    # runs the agent on every bug in a fresh container, prints a table
check.py         # verifies Python, Docker, sandbox, test runner, model call (stops at first problem)
lab/             # host-only outer-loop demo (built last)
Dockerfile
Makefile         # setup, reset, run, test, check, verify-bugs (later: score)
requirements.txt # host packages: openai, rich
.env.example     # BASE_URL, API_KEY, MODEL
README.md        # attendee-facing instructions
```

## Missions (step 4)

Each mission starts with a failure attendees can see, then a small fix (10–30 lines):

1. **Permission gate**: risky commands (`rm`, `git push`, `curl`, ...) need human approval
2. **Real stop condition**: before finishing, the harness runs the tests and sends failures back
3. **Budget**: max steps and max cost, graceful exit
4. *(optional)* **Context trimming**: shorten old command outputs so history doesn't explode
5. *(optional)* **System prompt**: change it, measure the effect with the scoreboard

## Demo project and bugs

- Domain: **expense splitter** ("Splitwise-lite"): friends on a trip, who paid, who owes whom. All amounts are integer cents.
- `demo_project/` is **clean**. Each bug is a patch in `bugs/<id>/`, applied when the container starts: **one bug per container**, so the full suite has exactly that bug's red tests. `BUG=all` applies every patch.
- After applying the patch, the container's `/work` gets a fresh `git init` + commit, so history doesn't reveal the fix and `git diff` shows only the agent's changes.
- 6 bugs, independent of each other, mixed difficulty (one trivial, one that needs reading two files, one the agent often gets wrong).
- Fixed = the full suite is green.

## Platforms

Ubuntu and macOS; Windows only via WSL2. The Makefile must work with GNU make 3.81 (macOS default) and plain POSIX `sh`. Keep each target to a few visible commands, so they can be copied by hand.

## Scoreboard

For each bug: fresh container, run the agent, run the tests, record fixed (yes/no), steps, tokens/cost, time. Print one table. Pairs run it on their own version of the agent.

## Lab demo (host only, built last)

Autoresearch-style outer loop: an agent tries to make a slow function faster. Each attempt has a fixed time budget. A change is kept only if tests pass and runtime improves; every kept change is a git commit. Must run unattended for ~2 hours and leave a readable log for the reveal.

## Git branches

- `start`: what attendees clone (core loop is TODO)
- `step-1-loop`: working core loop
- `mission-N-solution`: one per mission, so anyone stuck can catch up with one command
- `final`: everything

## Code principles

- **This is teaching code shown on a projector.** Readability beats cleverness. Short files, short functions, obvious names.
- No agent frameworks. Minimal dependencies: `openai` SDK, `rich` for output, `pytest`. Ask before adding anything else.
- No hidden magic: if something matters to how the agent behaves, it should be visible in `agent/`.
- Python 3.12, type hints where they help reading, not everywhere.

## How to work with me in this repo

- Plan before code. Propose the approach for a step and wait for my go-ahead.
- One step at a time, small reviewable diffs. Commit at working checkpoints.
- Don't generate code I didn't ask for. Don't refactor beyond the current step.
- Point out problems and simpler alternatives directly. Be critical, not encouraging.

## Build order

1. Dockerfile + demo project + failing tests + `make setup/reset`
2. `llm.py` + `check.py`
3. `sandbox.py` + core loop (full version first, then derive the TODO version)
4. `trace.py` (colored output + saved trajectories)
5. Missions: TODO files + solution branches
6. `scoreboard.py`
7. `lab/` outer-loop demo
8. Attendee `README.md`, then a full timed dry run

## Open decisions

- Which model for the session (default in `.env.example`: `anthropic/claude-haiku-4.5`), and a shared gateway key with a hard spending cap
- How cost is shown on the scoreboard (tokens only, or estimated money)
- The lab demo's target function and metric
