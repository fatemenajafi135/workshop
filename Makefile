IMAGE = mini-agent-sandbox
CONTAINER = mini-agent
BUG = 01

# BUG=03 plants bugs/03-*/bug.patch, BUG=all plants every bug.
ifeq ($(BUG),all)
PATCHES = bugs/*/bug.patch
else
PATCHES = bugs/$(BUG)-*/bug.patch
endif

.PHONY: setup reset test verify-bugs

# Build the sandbox image, then start a fresh container.
setup:
	docker build -t $(IMAGE) .
	$(MAKE) reset

# Throw the container away and start a fresh one, with no network, then plant the bug.
# /work gets a new git history, so `git diff` shows only what the agent changed.
reset:
	docker rm -f $(CONTAINER) > /dev/null 2>&1 || true
	docker run -d --name $(CONTAINER) --network none --memory 512m --pids-limit 256 $(IMAGE) > /dev/null
	cat $(PATCHES) | docker exec -i $(CONTAINER) git apply
	docker exec $(CONTAINER) sh -c "git init -q && git add -A && git commit -q -m baseline"

# Run the test suite inside the container.
test:
	docker exec $(CONTAINER) python -m pytest -q

# Maintainer check: each bug turns exactly the tests in its test.txt red.
verify-bugs:
	sh bugs/verify.sh
