# Setup guide

Do this **before the workshop**. It takes 15 to 20 minutes, mostly waiting for downloads.
At the end, one command (`make check`) must show all ✓. That is your ticket.

> Not ready when the workshop starts? Start at **Step 4** and let the download run while the host talks. Details at the end.

You need about **1 GB of free disk space** and a **few hundred MB of download** (do it on good wifi).

---

## Step 0: What do you already have?

Open a terminal and run these four commands. (On Windows, see Step 1: use WSL2.)

| Run | You should see | What it is for |
|---|---|---|
| `docker --version` | `Docker version 2x...` | The **sandbox**: the AI's commands run inside a Docker container, never on your computer |
| `python3 --version` | `Python 3.12` or newer | Runs the agent |
| `git --version` | `git version 2...` | Gets the code |
| `make --version` | `GNU Make 3...` or `4...` | Short commands like `make check` |

Anything missing? Go to Step 1. Everything there? Go to Step 2.

---

## Step 1: Install what's missing

### Ubuntu / Debian
```bash
sudo apt update
sudo apt install -y git make python3 python3-venv
```
`python3-venv` is easy to forget, and `make setup` fails without it.

**Docker:** follow the official steps: <https://docs.docker.com/engine/install/ubuntu/>
Then let your user use Docker without `sudo`, and **log out and back in**:
```bash
sudo usermod -aG docker $USER
```
Test it: `docker run --rm hello-world` must print "Hello from Docker!".

**Python older than 3.12?** (Ubuntu 22.04 has 3.10.) Install 3.12 from the deadsnakes repository:
```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv
```
Later you run `make setup PYTHON=python3.12` instead of `make setup`.

### macOS
```bash
xcode-select --install        # gives you git and make. A window opens: click Install.
brew install python@3.12      # only if python3 --version shows less than 3.12
```
**Docker:** install Docker Desktop: <https://docs.docker.com/desktop/setup/install/mac-install/>
Open the app once and wait until it says Docker is running (the whale icon stops moving).
If you installed Python with brew, you may need `make setup PYTHON=python3.12`.

### Windows
Native Windows does **not** work. Use **WSL2**, which gives you Ubuntu inside Windows:
1. Open PowerShell **as administrator** and run `wsl --install`. Restart the computer.
2. Open **Ubuntu** from the Start menu. From now on, **every command in this guide runs in that Ubuntu window.**
3. Install Docker Desktop for Windows: <https://docs.docker.com/desktop/setup/install/windows-install/>
   In its settings, turn on "Use the WSL 2 based engine", and under Resources → WSL integration, turn on Ubuntu.
4. In Ubuntu, follow the Ubuntu steps above (skip the Docker engine part: Docker Desktop provides it).
5. Keep the project in your Ubuntu home folder (`cd ~`), **not** in `/mnt/c/...`. It's much faster.

---

## Step 2: Get the code

```bash
git clone https://github.com/fatemenajafi135/workshop.git mini_coding_agent
cd mini_coding_agent
ls
```
You should see `Makefile`, `WORKSHOP.md` and `agent`. Stay in this folder for everything else.

---

## Step 3: Get an API key

The agent needs an AI model. Any provider that works like OpenAI's API is fine. Pick one:

| Provider | How | Cost |
|---|---|---|
| **Vercel AI Gateway** (easiest, many models, one key) | Make an account at vercel.com. Open the dashboard → **AI Gateway** → **API Keys** → **Create key**. Copy it | Free $5 credit every 30 days |
| OpenRouter, OpenAI, Anthropic, Google | Their website → API keys → create a key | Pay as you go |
| **Ollama** (a model on your own computer) | Install Ollama, then `ollama pull qwen3-coder` | Free, but needs a strong computer and is slower |

A small, cheap model is enough. Set a **spending limit** if your provider offers one.

🔒 **The key is a password.** Never post it in chat, in a screenshot or on GitHub. The file where you'll put it, `.env`, is never uploaded: git ignores it.

---

## Step 4: `make setup`

```bash
make setup
```
(Python 3.12 installed under another name? `make setup PYTHON=python3.12`)

**What it does, in 4 parts:**
1. Creates a private Python environment in `.venv` and installs the agent's packages (about 75 MB).
2. Copies `.env.example` to `.env`. This is where your key goes (Step 5).
3. Builds the **sandbox**: a small Linux box with Python and our demo app inside.
4. Starts the sandbox, and plants **bug 01** in the demo app.

**What you should see:** a lot of text. The last lines mention `git init`, `baseline` and `Leaving directory`. **No red error text** means it worked.
**How long:** a few minutes. The download is the slow part.

---

## Step 5: Edit `.env`

Open it in any editor (`nano .env`, or `code .env` for VS Code). It looks like this:

```
BASE_URL=https://ai-gateway.vercel.sh/v1
MODEL=anthropic/claude-haiku-4.5
...
API_KEY=
```

- **Using Vercel?** Only paste your key after `API_KEY=` (no spaces, no quotes). Done.
- **Another provider?** Find its block in the file. Remove the `#` in front of its `BASE_URL` and `MODEL` lines. Then put a `#` in front of the Vercel lines, so only one provider is on. Paste your key after `API_KEY=`.

Example for OpenAI:
```
# BASE_URL=https://ai-gateway.vercel.sh/v1
# MODEL=anthropic/claude-haiku-4.5
BASE_URL=https://api.openai.com/v1
MODEL=gpt-5-mini
API_KEY=sk-...
```
Model names change. If a model name doesn't work, look it up on your provider's model list.

Cost shows `$?`? Only Vercel reports prices. For others, add your provider's prices (dollars per million tokens) at the bottom: `PRICE_IN=...` and `PRICE_OUT=...`. This is optional.

---

## Step 6: `make check`

```bash
make check
```

**You should see:**
```
  ✓ Python: Python 3.12.3
  ✓ Docker: Docker is running
  ✓ Sandbox: container mini-agent is running
  ✓ Tests: pytest runs in the sandbox: 4 failed, 35 passed in 0.04s
  ✓ Model: anthropic/claude-haiku-4.5 via ai-gateway.vercel.sh replied 'ready' (14 tokens in, 4 out)

All good, you're ready for the workshop.
```

- **"4 failed" is correct!** The demo app has a planted bug. Fixing it is the workshop.
- The last line makes one tiny call to the AI (a fraction of a cent) to prove your key works.
- It stops at the first ✗ and tells you what to do. Fix it, run `make check` again.

**All ✓? You're done.** 🎉

---

## When something fails

| What you see | What it means | What to do |
|---|---|---|
| `make: command not found` | `make` is missing | Step 1 (`sudo apt install make` or `xcode-select --install`) |
| `The virtual environment was not created successfully` / `ensurepip is not available` | Ubuntu without `python3-venv` | `sudo apt install python3-venv`, then `rm -rf .venv` and `make setup` |
| `native Windows isn't supported` | You're in PowerShell | Use the Ubuntu (WSL2) window |
| `Python 3.x found, need 3.12 or newer` | Old Python | Install 3.12 (Step 1), then `rm -rf .venv` and `make setup PYTHON=python3.12` |
| `docker not found` | Docker isn't installed | Step 1 |
| `Docker is installed but not running (or needs sudo)` | Docker is off, or you need the docker group | Start Docker Desktop. On Linux: `sudo systemctl start docker`. If you see "permission denied": do the `usermod` command in Step 1, then log out and in |
| `toomanyrequests` while building | Docker Hub limit for anonymous users | `docker login` (a free account), then `make setup` again |
| The download keeps stopping | Wifi | Run `make setup` again: it continues. Or use a phone hotspot |
| `sandbox image is missing` | Setup didn't finish | `make setup` |
| `sandbox container isn't running` | The sandbox stopped (e.g. after a restart) | `make reset` |
| `ALL_PROXY is a socks:// proxy` | Your shell has a proxy Python can't use | `unset ALL_PROXY all_proxy`, then `make check` again |
| `API_KEY is not set` | `.env` has no key | Step 5. Check there is no `#` in front of `API_KEY` |
| `the API key was rejected` | Wrong key, or the key belongs to another provider | Copy the key again. Check that `BASE_URL` matches the provider |
| `the model call failed: NotFoundError` | `MODEL` name is wrong for your provider | Look up the exact name on the provider's model list |
| `... insufficient credits` or `402` | No money on the account | Add credit, or use a different provider |
| Your company laptop / VPN blocks things | Docker Hub or pypi is blocked | Tell the host. Sit with a partner for now |

**Still stuck after 10 minutes?** Stop, and tell the host. It's fine: you'll pair with a neighbour for the first part and fix it at the break.

---

## Late? Setting up during the introduction

While the host talks about the agenda and the picture of the agent:
1. Do Steps 2 and 4 right away (`make setup` keeps downloading while you listen).
2. When it finishes: Step 5 (`.env`), then Step 6 (`make check`).
3. No Docker at all? Don't install it now: it can take a while and may need a restart. Sit with a partner for the first part and install it at the break.
