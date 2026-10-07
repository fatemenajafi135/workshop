IMAGE = mini-agent-sandbox
CONTAINER = mini-agent

.PHONY: setup reset test

# Build the sandbox image, then start a fresh container.
setup:
	docker build -t $(IMAGE) .
	$(MAKE) reset

# Throw the container away and start a fresh one, with no network.
# /work gets a new git history, so `git diff` shows only what the agent changed.
reset:
	docker rm -f $(CONTAINER) > /dev/null 2>&1 || true
	docker run -d --name $(CONTAINER) --network none --memory 512m --pids-limit 256 $(IMAGE) > /dev/null
	docker exec $(CONTAINER) sh -c "git init -q && git add -A && git commit -q -m baseline"

# Run the test suite inside the container.
test:
	docker exec $(CONTAINER) python -m pytest -q
