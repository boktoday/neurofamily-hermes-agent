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
- **Cheaper Inference** (https://cheaperinference.com/) - a discounted marketplace across many labs, typically 35-55% below list price and never above it, with no separate routing surcharge. OpenAI-compatible at `https://api.cheaperinference.com/v1` with `ci_live_` keys. Note there is **no free tier and no subscription**: it is a prepaid wallet, fund from $25, paid per token. A free-model flag exists (`GET /v1/models?free=true`) but it is usually a single model and it changes.
- **OrcaRouter** (https://orcarouter.ai/) - alternative router; model `orcarouter/auto` routes to the cheapest live model.
- Local models - see Step 5. Completely free and completely private.

**What each one keeps.** This matters more than the discount for a family folder full of names, schools and diagnoses. Both paid routers offer zero data retention, but they do not default to it equally.

| Provider | Out of the box | Zero data retention |
|---|---|---|
| OpenRouter | Check its own current terms; terms and default retention vary by upstream provider | Per-request or account-level where supported |
| Cheaper Inference | **Retains a copy of request content** (prompts, instructions, files, images, audio and outputs) to operate, secure, troubleshoot and improve the service | A self-serve toggle in the dashboard Data Protection page, or a `zdr` field on a request. Routes only to zero-retention providers and disables caching. May limit which models you get and change the price. Metadata is kept either way. Turning it on does not delete anything already retained. |
| OrcaRouter | Stores only request metadata (time, model, token counts, cost, latency, status). Bodies are stored only if a workspace owner switches on request logging, which is off by default | A per-workspace grant against a signed DPA, available on every plan. Once active it cannot be overridden: no logging, zero-retention upstreams only, no fallback, `X-Orca-ZDR: active` on every response. Metadata is still kept. It stops new content being stored; erase what came before from the console. |
| Local model | Nothing leaves the machine | Not applicable |

Two honest cautions. Cheaper Inference does not make a universal zero-retention claim on its enterprise page and says to confirm route and provider coverage before sending production data, so treat the toggle as a strong reduction rather than an absolute guarantee. And zero retention stops the provider storing your words; it does not stop the model seeing them, so the de-identification convention still does the other half of the work.

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

**Everyday:** the config default is DeepSeek Flash via OpenRouter: fast, inexpensive, and right for most family conversations. Cheaper Inference serves the same DeepSeek family at a lower per-token rate if you would rather fund there instead (see the options in Step 4).

**Complex work:** the same OpenRouter key unlocks frontier models. When a job needs heavier reasoning (an advocacy letter, a tangled support plan), ask the agent to switch, or let it propose the switch.

**Schedules on a local model:** the check-ins are simple by design, so run them on a small local model (LM Studio or Ollama) and the unattended, around-the-clock part costs nothing and stays private. The agent can pin a cron job's model and provider when it creates it.

**Voice both ways, locally:** local `faster-whisper` transcribes incoming voice notes; local **Piper** speaks replies (`pip install piper-tts`). Voice note in, voice note out, no cloud involved, on whichever channel the family uses.

Full detail, including what each tier costs: `docs/models.md`.

---

## Step 5d: Redact a document before it leaves the house

Attaching an NDIS plan, an IEP or a paediatrician's letter to a chat with a hosted provider
sends the raw file, including the full name, date of birth, participant number and address. A
small local script scrubs it first.

```bash
python scripts/redact_doc.py NDIS-plan.pdf --names "Sarah Whitmore, Amelia, Reservoir High School"
```

It writes `NDIS-plan.redacted.md` beside the original and prints only counts, so the terminal
is safe to screenshot. Attach the `.redacted.md`, never the original.

- **Inputs:** `.txt`, `.md`, `.csv`, `.html`. For `.pdf`, install `pypdf`
  (`pip install pypdf`) or the `pdftotext` binary; without either the script says so and stops
  rather than pretending it redacted something it never read.
- **Redacts:** NDIS participant numbers, Medicare numbers, Centrelink CRNs, dates of birth,
  email addresses, Australian phone numbers, Australian street addresses and state postcodes,
  plus every name you pass in `--names`.
- **Leaves alone:** ordinary dates, because review dates are the useful part of a plan, and
  service numbers like 1300, 1800 and 13, because one of them is the NDIS line.
- **Names:** a school becomes `[SCHOOL_A]`, a plain name becomes `[CHILD_A]`, and a titled
  adult such as `Dr Whitmore` becomes `[PERSON_A]`. Each is consistent across the document.

It is a pattern matcher, not a guarantee. Read the output before you send it, and treat
"0 items matched" on a real plan as a warning rather than a clean bill of health.

If the family would rather nothing left the machine at all, use Step 5 (local models) instead
of redacting.

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
