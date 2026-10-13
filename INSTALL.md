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

Telegram is the recommended channel: easy bots, a good audio player, and it works on every phone in the family. Create a bot with @BotFather, put the token in `.env`, and enable the Telegram platform in your profile config. Other channels (WhatsApp, Signal, Discord and more) are supported by Hermes; see the Hermes docs for current status. A shared family group chat with the assistant can work well, with the rule that the young person can also talk one-to-one where that makes sense.

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
