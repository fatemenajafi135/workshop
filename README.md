# Build a mini coding agent

A coding agent in ~15 lines, plus everything that shows why real ones are longer:
a sandbox, a permission gate, a stop check, a budget, context trimming, a
scoreboard, and a lab where the agent optimizes code on its own for hours.

> This README is the presenter's version (branch `main`). Attendees get the `workshop` branch: see `workshop_files/WORKSHOP.md`.

## Setup

You need Ubuntu or macOS (Windows: use WSL2), Docker, Python 3.12+, `make`,
and an API key for [Vercel AI Gateway](https://vercel.com/ai-gateway)
(or any OpenAI-compatible endpoint).

```bash
make setup     # .venv with the agent's packages, the sandbox image, a fresh sandbox
               # then put your key in .env: API_KEY=...
make check     # every line should be ✓
```

If `make check` complains about `ALL_PROXY ... socks://`, run `unset ALL_PROXY all_proxy`
(Python can't use `socks://` proxies; an `http://` `HTTPS_PROXY` keeps working).

## Commands

| Command | What it does |
|---|---|
| `make demo` | Use the app like a user, in the sandbox: shows the bug before, and the fix after |
| `make run BUG=01` | Fresh sandbox with bug 01 planted, then the agent works on its issue |
| `make ask TASK="..."` | Any task, in the sandbox as it is now |
| `make test` | Run the test suite in the sandbox |
| `make reset BUG=03` | Fresh sandbox with bug 03. Also `BUG=all`, `BUG=none` |
| `make score` | The exam: bugs 01, 04, 05 in their own sandboxes, in parallel, one table. `BUGS=all` for every bug, `BUGS=02,03` to choose. What the agent changed: `runs/score-<time>/<bug>.diff` |
| `make lab` | The outer loop, for 2 hours. `LAB_HOURS=0.5` for less |
| `make fake` | A free fake model for testing the harness (see below) |
| `make check-mission MISSION=x` | Free tests for a mission (63 in total, no AI) |
| `python3 tools/build_workshop.py` | Rebuild the attendee branch `workshop` from `main` (see `workshop_files/HOW_THIS_WORKS.md`) |
| `make verify-bugs` | Check that each bug breaks exactly its tests (after changing the demo project) |

Add `MISSIONS=none` (or a list like `MISSIONS=budget,stop_check`) to `run`, `ask` or
`score` to switch the agent's fixes off and show the habit each one fixes.

## How it fits together

```
host                                         Docker sandbox (no network)
────                                         ───────────────────────────
agent/core.py   the loop: ask → run → repeat
agent/llm.py    talks to the model (.env)
agent/sandbox.py ── docker exec, 30s timeout ──▶  /work: the splitter project,
agent/trace.py  terminal output + runs/*.json      one bug planted, fresh git history
agent/missions/ fixes for bad habits
```

- The model replies in plain text with one ```` ```bash ```` block per step.
  No bash block = it thinks it's done.
- We stop the model right after its first command (the API's `stop` option).
  Without that, Claude models wrote up to 39 commands per reply, in their own
  `<invoke name="bash">` format, and invented the results. We accept that format too.
- Every command runs in the container. The project is copied in, not mounted:
  the worst a command can do is break the container, and `make reset` replaces it.

## The demo project and its bugs

`demo_project/` is a small expense splitter ("Splitwise-lite"), clean, all tests green.
Each bug in `bugs/` is a patch applied when the sandbox starts, plus the issue a user
would write and the list of tests it turns red.

| Bug | The user's complaint |
|---|---|
| 01 | Amounts in the summary look wrong (€60.0) |
| 02 | Summary crashes for a group with no expenses |
| 03 | Summary says the person who paid owes money |
| 04 | New groups sometimes already have people in them |
| 05 | Summary crashes after splitting €10 three ways |
| 06 | I wasn't at the dinner but I'm still paying for it |

## Missions

Each one lives in `agent/missions/` and is one visible call in `solve()`.

| Mission | File | The bad habit | See it with |
|---|---|---|---|
| 1. Permission gate | `permission.py` | Runs `rm -rf` without asking | `make reset BUG=none` then `make ask TASK="Delete the tests folder, it's a mess" MISSIONS=none` |
| 2. Stop check | `stop_check.py` | Runs one test, sees green, stops | `make run BUG=04 MISSIONS=none`, then `make test` |
| 3. Budget | `budget.py` | Never gives up, never stops spending | `make run BUG=04 MISSIONS=stop_check` (stop with Ctrl+C) |
| 4. Trimming *(optional)* | `trimming.py` | Re-sends every old output, tokens explode | Compare token counts in the trace with `MISSIONS=stop_check,budget`. Trims in batches of 10 messages, so caching keeps working |
| 5. System prompt *(optional)* | `prompt.py` | A vague prompt | `make score MISSIONS=permission,stop_check,budget` vs `make score` |
| 6. Caching *(optional)* | `caching.py` | Pays full price to re-send the same old text every step | Long runs only (4,096+ tokens): the step header shows `(N cached)` and the cost drops ~9× |

## Testing without paying

`make fake` starts a fake model: free, instant, always the same scripted answers.
Use it when you change the harness, not when you want to know how good the AI is.

```bash
make fake                                                       # terminal 1
make score MODEL=fake/model BASE_URL=http://127.0.0.1:8765/v1  # terminal 2
```

## The lab

`make lab` gives the agent `lab/optimal.py`: `fewest_transfers()`, exact but slow.
Each attempt is a fresh agent with 5 minutes. A change is kept only if the tests pass
(untouched) and a hidden benchmark is at least 10% faster with correct answers.
Kept changes are git commits.

For the reveal:

```bash
cat lab/output/log.md                       # every attempt, kept or not, and why
git -C lab/output/best log --oneline        # the kept changes
git -C lab/output/best show HEAD            # the latest one
```

## Before the session

- [ ] Gateway key with a hard spending limit in `.env`; `make check` all ✓
- [ ] `make score` once with the session's model: how many bugs does it fix, what does it cost?
- [ ] Start `make lab` when the session starts (it runs for 2 hours)
- [ ] Rehearse: `run BUG=01`, `run BUG=04 MISSIONS=none`, the permission demo, `make score`
