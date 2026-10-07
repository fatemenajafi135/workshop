# The sandbox: every command the agent asks for runs in here, never on the host.
FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==9.1.1

# Not root: a bad command can break /work, not the container itself.
RUN useradd --create-home agent
USER agent
RUN git config --global user.name "sandbox" \
 && git config --global user.email "sandbox@localhost" \
 && git config --global init.defaultBranch main

# Copied, not mounted: nothing the agent does reaches the host's files.
COPY --chown=agent:agent demo_project /work
WORKDIR /work

CMD ["sleep", "infinity"]
