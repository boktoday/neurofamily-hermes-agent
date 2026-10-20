# Installing the NeuroFamily Support Ecosystem - step by step

This guide walks you through installing the ecosystem into Hermes Agent and getting the family's support team running. The Family Navigator runs the family onboarding interactively; this document is the reference for getting there.

---

## Step 0: What you need

| You need | Check with | Get it at |
|---|---|---|
| Hermes Agent | `hermes --version` | https://hermes-agent.nousresearch.com/docs |
| Python 3.10+ | `python --version` | https://www.python.org/downloads/ |
| A model provider key | - | Free options below, or fully local (Step 5) |
| A chat app (optional but recommended) | - | https://t.me/BotFather for a Telegram bot |

Any laptop from the last several years works. Everything runs on your own machine.

---

## Step 1: Get the ecosystem

Option A - git:

```bash
git clone https://github.com/boktoday/neurofamily-hermes-agent.git
```

Option B - download the zip from the GitHub page (`Code` button, then `Download ZIP`) and extract it.

Put the folder somewhere sensible, for example `~/neurofamily-hermes-agent`.

---

## Step 2: Install Hermes Agent

Follow the official quick start: https://hermes-agent.nousresearch.com/docs

One-line install: run the installer from the docs page for your operating system. When `hermes --version` prints a version, you are done with this step.

---

## Step 3: Create the family's profile

The cleanest setup is a dedicated Hermes profile for the family:

```bash
hermes profile create neurofamily
```

Then copy the ecosystem into it:

```bash
# Skills (the support team)
cp -r ~/neurofamily-hermes-agent/skills/* <profiles-dir>/neurofamily/skills/

# Shared-brain templates
mkdir -p ~/neurofamily
cp ~/neurofamily-hermes-agent/shared/*.template.md ~/neurofamily/

# Configuration (optional example; review before use)
cp ~/neurofamily-hermes-agent/config.yaml <profiles-dir>/neurofamily/config.yaml
```

`<profiles-dir>` is your Hermes profiles directory (on Windows: `%LOCALAPPDATA%\hermes\profiles\`). If you already have a family Hermes profile you like, you can instead copy the skills into that profile's `skills/` folder.

---

## Step 4: Connect a model provider

The example config defaults to OpenRouter with a fast low-cost model.

```bash
cp .env.example .env
# then edit .env and set OPENROUTER_API_KEY
```

**Free and low-cost options:**

- **OpenRouter** (https://openrouter.ai/) - one key unlocks a huge catalogue, including free-tier models that rotate monthly. Check the live catalogue for what is currently free.
- **OrcaRouter** (https://orcarouter.ai/) - alternative router; model `orcarouter/auto` routes to the cheapest live model.
- Local models - see Step 5. Completely free and completely private.

---

## Step 5: Optional - fully offline with local models

Everything in this ecosystem can run with no cloud at all, so nothing about your family leaves the machine. Two good paths:

**First, check what your machine can actually run.** Open [canirun.ai](https://canirun.ai) in a desktop browser. It reads your processor, memory and graphics directly, ranks the open models that fit, and gives you the exact Ollama or LM Studio command for the one you pick. No account, nothing to install. Two more worth knowing: [localllm-advisor.com](https://localllm-advisor.com) works in both directions, model for your hardware or hardware for a model, and [localllm.run](https://localllm.run) walks goal, hardware, model and setup in order. Five minutes here saves a wasted 5GB download.

**LM Studio (easiest, has a GUI)**

1. Download from https://lmstudio.ai/ and install.
2. Search for and download a small instruction model. Good starting points: a current Qwen instruct model (7B-9B), Gemma (9B class), or Llama (8B class). On a modest laptop choose a 4B class model; on a gaming laptop or Mac with 16GB+ unified memory, an 8B-12B class model runs well.
3. Start the local server (Developer tab, "Start Server"; default port 1234).
4. Point Hermes at it: set `model.default` to your model's name and `model.provider` to the LM Studio OpenAI-compatible endpoint (http://localhost:1234/v1). Consult the Hermes docs for the exact provider entry.

**Ollama (command line)**

1. Install from https://ollama.com/.
2. `ollama pull qwen2.5:7b` (or another small instruct model).
3. Point Hermes at http://localhost:11434/v1 with the model name you pulled.

Local models are less capable than the frontier models, and that is fine for this ecosystem: the work is warm, practical conversation, planning and writing, not heavy reasoning. Choose the largest model your machine runs comfortably.

---

## Step 5b: Optional - connect the family's calendar and mail

With a free Maton account, the team can work with the family's real Google or
Microsoft calendar, mail, tasks and files (read-first; writes always need the
family's yes in the moment). Full details in `docs/connections.md`. Skip this
step entirely if the family prefers everything to stay inside the family folder.

---

## Step 5c: Models and voice - the recommended setup

**Everyday:** the config default is DeepSeek Flash via OpenRouter: fast, inexpensive, and right for most family conversations.

**Complex work:** the same OpenRouter key unlocks frontier models. When a job needs heavier reasoning (an advocacy letter, a tangled support plan), ask the agent to switch, or let it propose the switch.

**Schedules on a local model:** the check-ins are simple by design, so run them on a small local model (LM Studio or Ollama) and the unattended, around-the-clock part costs nothing and stays private. The agent can pin a cron job's model and provider when it creates it.

**Voice both ways, locally:** local `faster-whisper` transcribes incoming voice notes; local **Piper** speaks replies (`pip install piper-tts`). Voice note in, voice note out, no cloud involved, on whichever channel the family uses.

Full detail, including what each tier costs: `docs/models.md`.

---

## Step 6: First conversation (family onboarding)

Start Hermes and say:

> "Hello, we are setting up the NeuroFamily support team. Let's build our family profile."

The Family Navigator walks you through the Profile Builder questions (about 18 minutes, can be done over several sittings), and writes `family-profile.md` and `child-summary.md` into `~/neurofamily/`. You can stop and resume any time. See `PROFILE_BUILDER.md` for what the questions cover.

---

## Step 7: Add the schedules (optional)

The check-ins and nudges live in `schedules/`. Each file has a copy-paste setup command. The common pattern:

```bash
hermes cron add --name "Weekly family check-in" --schedule "0 18 * * 0" --prompt "Load the family-navigator skill and run the weekly family check-in as described in schedules/weekly-family-checkin.md"
```

Or simply tell the agent: "Set up the weekly family check-in from the schedules folder and deliver it here Sunday evening." It can create the job itself.

---

## Step 8: Channels (optional)

**WhatsApp is the primary shared group.** Hermes ships a built-in WhatsApp bridge (it links like a device on WhatsApp Web, via QR pairing). It supports group chats, voice messages, and scheduled messages at any hour with no restrictions, which matters because the team's check-ins must deliver reliably.

Recommendations for a family setup:

| Setting | Recommendation |
|---|---|
| Number | A dedicated SIM or eSIM for the bot (do not link the family's personal number); small account-restriction risk exists with any linked-device bridge |
| The group | One WhatsApp group: the family + the bot number. Everyone can talk to the team there |
| One-to-one | Optional: a young person can also message the bot privately where the family agrees, with the consent rules in AGENTS.md |
| Always-on | The bridge lives on the family's machine; keep it running on whatever schedule the family is comfortable with |
| Setup | `hermes whatsapp` - pick the bot mode, scan the QR from the bot phone, add the numbers that may talk to it |

Telegram also works well (free bots, excellent audio, our own recommended alternative) if the family already lives there. The official WhatsApp Cloud API path exists but currently supports direct messages only in v1 and restricts out-of-window sends, so it is not the right path for a scheduled-check-in family group.




---

## Updating

```bash
cd ~/neurofamily-hermes-agent
git pull
# then re-copy skills/ into your profile as in Step 3
```

`CHANGELOG.md` records what changed.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Skills do not appear | Copied to the wrong profile's `skills/` folder; check the path from Step 3 |
| Model errors on every message | `.env` key missing or config provider name does not match your key |
| Agent forgets the family | `~/neurofamily/` folder not created, or profile not pointed at it |
| Slow or costly responses | Switch to a smaller model, or the local setup in Step 5 |
