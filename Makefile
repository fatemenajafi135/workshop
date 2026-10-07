IMAGE = mini-agent-sandbox
CONTAINER = mini-agent
BUG = 01
# Which Python makes the .venv: make setup PYTHON=python3.12 (needs 3.12 or newer)
PYTHON = python3
# Which missions are on: all, none, or a list like budget,stop_check (see agent/missions/).
MISSIONS = all
export MISSIONS
# Which bugs `make score` runs: a small exam by default (easy, stops-too-early, tricky).
# BUGS=all for every bug, or a list like BUGS=02,03.
BUGS = 01,04,05
export BUGS

# BUG=03 plants bugs/03-*/bug.patch, BUG=all plants every bug, BUG=none plants nothing.
ifeq ($(BUG),all)
PATCHES = bugs/*/bug.patch
else
PATCHES = bugs/$(BUG)-*/bug.patch
endif

.PHONY: setup reset demo run ask score score-basic fake test check check-mission catch-up verify-bugs

# Install the agent's packages on the host, build the sandbox image, start a fresh container.
setup:
	$(PYTHON) -m venv .venv
	.venv/bin/pip install -q -r requirements.txt
	[ -f .env ] || cp .env.example .env
	docker build -t $(IMAGE) .
	$(MAKE) reset

# Throw the container away and start a fresh one, with no network, then plant the bug.
# /work gets a new git history, so `git diff` shows only what the agent changed.
reset:
	docker rm -f $(CONTAINER) > /dev/null 2>&1 || true
	docker run -d --name $(CONTAINER) --network none --memory 512m --pids-limit 256 $(IMAGE) > /dev/null
	if [ "$(BUG)" != none ]; then cat $(PATCHES) | docker exec -i $(CONTAINER) git apply; fi
	docker exec $(CONTAINER) sh -c "git init -q && git add -A && git commit -q -m baseline"

# Use the app like a user would, in the sandbox: see the bug before, and the fix after.
demo:
	docker exec $(CONTAINER) python -m splitter

# Fresh sandbox with the bug planted, then let the agent loose on its issue.
run: reset
	.venv/bin/python -m agent.core bugs/$(BUG)-*/issue.md

# Any task, in the sandbox as it is now: make ask TASK="Delete the tests folder"
ask:
	.venv/bin/python -m agent.core "$(TASK)"

# Every bug in its own fresh sandbox, all at once, then one table.
score:
	.venv/bin/python scoreboard.py

# The exam with every mission on except your prompt: the number to beat.
score-basic:
	$(MAKE) score MISSIONS=permission,stop_check,budget,trimming,caching

# A free fake model for testing the harness. Then, in another terminal:
#   make score MODEL=fake/model BASE_URL=http://127.0.0.1:8765/v1
fake:
	.venv/bin/python tools/fake_llm.py

# Run the test suite inside the container.
test:
	docker exec $(CONTAINER) python -m pytest -q

# Is everything ready? Docker, sandbox, tests, model.
check:
	.venv/bin/python check.py

# Free, instant tests for what you wrote (no AI, no cost):
#   make check-mission MISSION=permission   (or loop, stop_check, budget, trimming, caching, prompt)
#   make check-mission                      (all of them)
MISSION =
check-mission:
	.venv/bin/python -m pytest $(if $(MISSION),tests_missions/test_$(MISSION).py,tests_missions) -q -p no:cacheprovider

# Stuck? Get the finished file: make catch-up STEP=loop  (or a mission name, or all)
STEP =
catch-up:
	python3 tools/catch_up.py $(STEP)

# Maintainer check: each bug turns exactly the tests in its test.txt red.
verify-bugs:
	sh bugs/verify.sh
