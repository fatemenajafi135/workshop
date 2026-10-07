# Build a mini coding agent: the guide

You will build the heart of a coding agent in about 10 lines, then see why real agents are much bigger.

> **The idea:** the loop is easy. The problems are around it.

**You write about 20 lines of code today. Everything else is ready.**
Stuck at any point? `make catch-up STEP=...` gives you the finished file (see the end).

---

## Before the workshop (do this at home, 15 to 20 min)

**Follow [SETUP.md](SETUP.md).** It has every step, what you should see, and what to do when something fails.
The short version:

```bash
git clone <repo-url> mini_coding_agent
cd mini_coding_agent
make setup        # downloads a few hundred MB: do it on good wifi, before the day!
```

`make setup` also creates a file called `.env`. Open it and:
1. Pick your provider (Vercel, OpenRouter, OpenAI, Anthropic, Google, or Ollama on your own computer). Remove the `#` in front of its `BASE_URL` and `MODEL` lines. If two providers are on, the one lower in the file is used, so put a `#` in front of the one you don't want.
2. Put your key in `API_KEY=`.

```bash
make check        # every line must show ✓. This is your ticket to the workshop.
```

**If `make check` shows ✗**, it says how to fix it. Two common ones:
- *"ALL_PROXY is a socks:// proxy"* → run `unset ALL_PROXY all_proxy`.
- *"Docker is installed but not running"* → start Docker Desktop (macOS) or `sudo systemctl start docker` (Linux).

**Cost:** one bug costs a few cents with a small model. The whole workshop should cost around $1 or less. Your provider's dashboard shows the real number.

---

## The picture

```
 your computer (host)                          Docker sandbox: no internet
 ────────────────────                          ───────────────────────────
 agent/core.py   the loop  ──── command ────►  /work: a small app with ONE bug
   │  ▲                     ◄─── output ─────  (a bad command can only break this box)
   ▼  │
 agent/llm.py    talks to the AI model
```

The AI can only write text. So we ask it for **one command**, run that command in the sandbox,
and give the result back. Again and again, until the AI says it's done.

---

## Step 1: the loop (everyone, live with the host)

**First, meet the app and its bug:**

```bash
make reset BUG=01     # a fresh sandbox, with bug 01 planted
make demo             # use the app like a user. Look at the amounts: something is wrong!
make test             # 4 tests fail
```

**Now write the loop.** Open `agent/core.py` and find `solve()`. There are four `TODO`s. Fill them in:

**TODO 1:** ask the model, and remember its answer
```python
        reply = llm.ask(context, stop=STOP_AFTER_COMMAND)
        messages.append({"role": "assistant", "content": reply.text})
        trace.model_said(reply)
```

**TODO 2:** find the command in the answer (replace the line `command = None`)
```python
        command = find_command(reply.text)
```

**TODO 3:** run the command in the sandbox (replace the line `output = "TODO"`)
```python
            output = sandbox.run(command, container)
```

**TODO 4:** give the result back to the model
```python
        messages.append({"role": "user", "content": output})
        trace.ran(command, output)
```

**Check your code (free, instant, no AI):**
```bash
make check-mission MISSION=loop        # 5 passed? 
```

**Now run it, for real:**
```bash
make run BUG=01
make test             # green!
```

You have a coding agent. 🎉 Look at the output: every *step* is one trip around your loop.

---

## Step 2: the agent has bad habits (watch the host)

Your loop works, but is it a good agent? The host shows three bad habits. Each one has a fix waiting in `agent/missions/`.

| Bad habit | What you'll see |
|---|---|
| 1. **Does anything**, even `rm -rf` | The agent deletes the tests because we asked it to |
| 2. **Says "done" too early** | It runs ONE test, sees green, stops. The other tests still fail |
| 3. **Never gives up** | It keeps going, and keeps spending |

Three more, for later: 4. **Old text piles up** (every step re-sends the whole history, so it costs more and more), 5. **Vague instructions**, 6. **Pays full price** for text the AI has already seen.

---

## Step 3: fix one habit (in pairs)

**Pick one mission and write it.** Each file in `agent/missions/` starts with a comment that tells you the habit, how to see it, and exactly what to write. Each is 5 to 15 lines.

| Mission | File | Your job in one line | Check (free) |
|---|---|---|---|
| 1. Permission gate | `permission.py` | Risky commands need a human's "yes" | `make check-mission MISSION=permission` |
| 2. Real stop | `stop_check.py` | Only stop when ALL tests pass | `make check-mission MISSION=stop_check` |
| 3. Budget | `budget.py` | Stop at 30 steps or $0.50 | `make check-mission MISSION=budget` |
| 4. Trimming | `trimming.py` | Shorten old outputs | `make check-mission MISSION=trimming` |
| 6. Caching | `caching.py` | Ask the provider to remember the start | `make check-mission MISSION=caching` |

Missions 1 to 3 are the best place to start. 4 and 6 are for fast pairs.

**The way to work:**
1. See the bad habit: `make run BUG=04 MISSIONS=none` (`MISSIONS=none` switches all fixes off).
2. Write your mission. Run the free check until it says `passed`.
3. See the habit disappear: `make run BUG=04`.

**Stuck for more than 5 minutes?** `make catch-up STEP=permission` (or `stop_check`, `budget`, ...). Your own version is kept as `permission.py.mine`.

---

## Step 4: the competition (this is where you win)

All agents use the **same model** (the host will tell you which). The only thing you change is **your prompt**: the instructions that tell the AI how to work.

1. Get the missions you didn't write: `make catch-up STEP=missions`. (A mission whose free check already passes is left alone: it's yours.)
2. Run the exam once with the basic prompt: `make score-basic`. Write your numbers down: they are the ones to beat.
3. Open `agent/missions/prompt.py`. Write your `BETTER` prompt. It's words, not code.
   Ideas: *Should it reproduce the problem first? Read before editing? Never touch the tests? Check everything at the end?*
4. Run the exam with your prompt: `make score`

`make score` runs 3 bugs at the same time, each in its own sandbox, and prints a table: fixed or not, steps, tokens, cost, time.

**Rules:**
- You only change `BETTER` in `prompt.py`. No hints about a specific bug ("the bug is in settle.py" is cheating).
- Fixing a bug by changing the tests is cheating too: the table says `edited tests`.
- **Winner:** the most bugs fixed. If tied, the lowest cost.
- Want more? `make score BUGS=all` runs all 6 bugs.

---

## At home: level up 🚀

Everything in this repo is yours to take apart. In this order:

1. **Build the other missions** (the ones you didn't write). The free checks tell you when you're done.
2. **Rebuild the parts we gave you.** Copy `agent/sandbox.py` somewhere safe, delete the body of `run()`, write it again, and check: `make check-mission MISSION=sandbox`. Same with `find_command()`: `make check-mission MISSION=find_command`.
3. **Make it yours.** A few ideas: stop the agent when it runs the same command 3 times in a row. Compare two models with `make score`. Add a mission that is not on our list. Write a new bug in `bugs/` and see if your agent can fix it.
4. **Read the real thing.** Real coding agents (Claude Code, Codex, ...) are this loop plus hundreds of missions like the ones you built.

---

## Cheat sheet

| Command | What it does | Costs money? |
|---|---|---|
| `make reset BUG=03` | A fresh sandbox with bug 03 (bugs 01 to 06). `BUG=none` = no bug | no |
| `make demo` | Use the app like a user | no |
| `make test` | Run the app's tests in the sandbox | no |
| `make run BUG=03` | The agent works on bug 03 | a little |
| `make run BUG=03 MISSIONS=none` | Same, with all fixes switched off | a little |
| `make ask TASK="..."` | Give the agent any task | a little |
| `make score` | The exam: bugs 01, 04, 05, with your prompt | a little |
| `make score-basic` | The same exam with the basic prompt (the number to beat) | a little |
| `make check-mission MISSION=x` | Free test for your code | no |
| `make catch-up STEP=x` | Get the finished file | no |
| `make check` | Is everything ready? | a tiny call |

**See what the agent changed** after `make run`: `docker exec mini-agent git diff`
**Test without paying anything:** in one terminal `make fake`, in another `make run BUG=01 MODEL=fake/model BASE_URL=http://127.0.0.1:8765/v1`

### No `make`? Plain commands

| `make ...` | The plain command |
|---|---|
| `setup` | `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cp .env.example .env && docker build -t mini-agent-sandbox .` then the `reset` commands below |
| `reset BUG=03` | `docker rm -f mini-agent` <br> `docker run -d --name mini-agent --network none --memory 512m --pids-limit 256 mini-agent-sandbox` <br> `cat bugs/03-*/bug.patch \| docker exec -i mini-agent git apply` <br> `docker exec mini-agent sh -c "git init -q && git add -A && git commit -q -m baseline"` |
| `test` | `docker exec mini-agent python -m pytest -q` |
| `demo` | `docker exec mini-agent python -m splitter` |
| `run BUG=03` | the `reset` commands, then `.venv/bin/python -m agent.core bugs/03-*/issue.md` |
| `run ... MISSIONS=none` | put `MISSIONS=none` in front: `MISSIONS=none .venv/bin/python -m agent.core ...` |
| `score` | `BUGS=01,04,05 .venv/bin/python scoreboard.py` |
| `check` | `.venv/bin/python check.py` |
| `check-mission MISSION=permission` | `.venv/bin/python -m pytest tests_missions/test_permission.py -q` |
| `catch-up STEP=permission` | `cp solutions/missions/permission.py agent/missions/permission.py` (the loop is `cp solutions/core.py agent/core.py`) |

---

## Something is wrong? 🔧

| What you see | What to do |
|---|---|
| `make check` says ✗ | Read the message: it says how to fix it |
| `No such container: mini-agent` | `make reset` |
| The agent edits files but nothing changes | `make reset`, then run again |
| `crashed: AuthenticationError` | Wrong key in `.env`, or the key doesn't match the `BASE_URL` |
| `crashed: NotFoundError` | The `MODEL` name is wrong for your provider |
| The cost shows `$?` | Your provider doesn't report prices. Add `PRICE_IN` and `PRICE_OUT` to `.env` (see `.env.example`) |
| It's slow or stuck | Press Ctrl+C. The run is saved in `runs/` |
| `make score` is expensive | `make score BUGS=04` runs just one bug |
