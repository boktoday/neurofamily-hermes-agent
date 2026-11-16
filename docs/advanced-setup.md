# Advanced setup

Everything that used to make `INSTALL.md` long. You do not need any of it to get
the family team running: `python scripts/quickstart.py` covers the two choices
most families actually make.

Read this when you want a different provider, a local model, a scheduled job, or
WhatsApp instead of Telegram.

---

## Contents

- [Choosing a model provider properly](#choosing-a-model-provider-properly)
- [Zero data retention, exactly](#zero-data-retention-exactly)
- [Local models: what your machine can run](#local-models-what-your-machine-can-run)
- [Models and voice: the recommended mix](#models-and-voice-the-recommended-mix)
- [Schedules and cron](#schedules-and-cron)
- [WhatsApp: the dedicated number](#whatsapp-the-dedicated-number)
- [Calendar, mail and files](#calendar-mail-and-files)
- [Redaction, in more detail](#redaction-in-more-detail)

---

## Choosing a model provider properly

`quickstart.py` offers two paths: OpenRouter, or a model on your own computer.
Both are the right answer for most families. The rest of this section is for
anyone who wants something else.

**OpenRouter** (https://openrouter.ai/)
One key unlocks a huge catalogue, including free-tier models that rotate monthly.
Check the live catalogue for what is currently free. This is the default for a
reason: one key, one place to top up, no per-vendor accounts.

**Cheaper Inference** (https://cheaperinference.com/)
A discounted marketplace across many labs, typically 35-55% below list price and
never above it, with no separate routing surcharge. OpenAI-compatible at
`https://api.cheaperinference.com/v1` with `ci_live_` keys.

There is **no free tier and no subscription**: it is a prepaid wallet, funded
from $25, paid per token. A free-model flag exists (`GET /v1/models?free=true`)
but it is usually a single model and it changes.

**OrcaRouter** (https://orcarouter.ai/)
Alternative router. The model `orcarouter/auto` routes to the cheapest live
model. Metadata-only storage by default.

**A model on this computer**
Completely free and completely private. See
[Local models](#local-models-what-your-machine-can-run) below.

### What each one keeps

This matters more than the discount for a folder full of names, schools and
diagnoses. Both paid routers offer zero data retention, but they do not default
to it equally.

| Provider | Out of the box | Zero data retention |
|---|---|---|
| OpenRouter | Check its own current terms; terms and default retention vary by upstream provider | Enforced per model group in the account privacy settings, per guardrail, or per request. Your own logging is separate and off unless you opt in. |
| Cheaper Inference | **Retains a copy of request content** (prompts, instructions, files, images, audio and outputs) to operate, secure, troubleshoot and improve the service | A self-serve toggle in the dashboard Data Protection page, or a `zdr` field on a request. Routes only to zero-retention providers and disables caching. May limit which models you get and change the price. Metadata is kept either way. Turning it on does not delete anything already retained. |
| OrcaRouter | Stores only request metadata (time, model, token counts, cost, latency, status). Bodies are stored only if a workspace owner switches on request logging, which is off by default | A per-workspace grant against a signed DPA, available on every plan. Once active it cannot be overridden: no logging, zero-retention upstreams only, no fallback, `X-Orca-ZDR: active` on every response. Metadata is still kept. It stops new content being stored; erase what came before from the console. |
| Local model | Nothing leaves the machine | Not applicable |

Two honest cautions. Cheaper Inference does not make a universal zero-retention
claim on its enterprise page and says to confirm route and provider coverage
before sending production data, so treat the toggle as a strong reduction rather
than an absolute guarantee. And zero retention stops the provider storing your
words; it does not stop the model seeing them, so the de-identification
convention still does the other half of the work.

---

## Zero data retention, exactly

### OpenRouter

It is **not** a single switch. ZDR is enforced per model group in your account
privacy settings at <https://openrouter.ai/settings/privacy>:

| Model group | Effect when switched on |
|---|---|
| Anthropic | Removes first-party Anthropic endpoints (Bedrock and Vertex remain) |
| OpenAI | Removes first-party OpenAI endpoints (Azure remains) |
| Google | Removes AI Studio endpoints |
| SpaceXAI | Removes non-ZDR SpaceXAI endpoints |
| All other models | Removes all other non-ZDR endpoints |

Turn on the groups you will actually use. "All other models" covers most of the
catalogue; add Anthropic, OpenAI or Google if you pick their models.

OpenRouter also separates **Safety Retention** (an endpoint may keep prompts
only to detect abuse) from true ZDR, and lets you allow or exclude those
endpoints per group. If you have not chosen, self-serve accounts allow Safety
Retention and enterprise accounts use ZDR only.

Per-request control exists as `provider.zdr = true`, which can only add
enforcement, never loosen an account setting. Because `zdr` ORs with the account
setting, you cannot switch it off from a request.

### Cheaper Inference

Sign in, open **Data Protection** (`/dashboard/data-protection`), and switch zero
data retention on. Do it *before* the first request that carries anything real:
it applies from the moment you enable it and does not delete what was already
kept.

An individual request can also carry `zdr: true`, which adds to the account
setting and cannot switch it off. Expect a narrower model list and a higher
price; `GET /v1/models?zdr=true` returns the zero-retention price view, and
`GET /v1/models` reports each model's `zero_data_retention_route` as
`discounted`, `rail_only` or `none`. A model with no zero-retention provider
currently serving it fails with `503 zdr_capacity_unavailable` before it is sent
upstream.

### The part that is worth remembering

Cheaper Inference says it themselves, in their own documentation:

> ZDR does not detect, mask, or anonymize PII; there is no automatic
> pre-provider PII redaction. Remove sensitive data in your application before
> sending it, including tool results and attachments.

Zero retention stops them keeping it. It cannot stop you sending it. That is why
`scripts/redact_doc.py` exists, and why it runs before the file is attached.

---

## Local models: what your machine can run

**First, check what your machine can actually run.** Open
[canirun.ai](https://canirun.ai) in a desktop browser. It reads your processor,
memory and graphics directly, ranks the open models that fit, and gives you the
exact Ollama or LM Studio command for the one you pick. No account, nothing to
install. Two more worth knowing:
[localllm-advisor.com](https://localllm-advisor.com) works in both directions,
model for your hardware or hardware for a model, and
[localllm.run](https://localllm.run) walks goal, hardware, model and setup in
order. Five minutes here saves a wasted 5GB download.

### LM Studio (easiest, has a GUI)

1. Download from <https://lmstudio.ai/> and install.
2. Search for and download a small instruction model. Good starting points: a
   current Qwen instruct model (7B-9B), Gemma (9B class), or Llama (8B class).
   On a modest laptop choose a 4B class model; on a gaming laptop or Mac with
   16GB+ unified memory, an 8B-12B class model runs well.
3. Start the local server (Developer tab, "Start Server"; default port 1234).
4. Point Hermes at it. `quickstart.py` detects a running server on port 1234
   automatically. By hand, set `model.default` to the model's name and add a
   `custom_providers` entry with `base_url: http://localhost:1234/v1`.

### Ollama (command line)

1. Install from <https://ollama.com/>.
2. `ollama pull qwen2.5:7b` (or another small instruct model).
3. `quickstart.py` detects a running server on port 11434. By hand, point the
   profile at `http://localhost:11434/v1` with the model name you pulled.

Local models are less capable than the frontier models, and that is fine for
this ecosystem: the work is warm, practical conversation, planning and writing,
not heavy reasoning. Choose the largest model your machine runs comfortably.

The config `quickstart.py` writes looks like this:

```yaml
model:
  default: llama3.1
  provider: local-ollama

custom_providers:
  - name: local-ollama
    base_url: http://localhost:11434/v1
    api_key: local
    model: llama3.1
```

---

## Models and voice: the recommended mix

**Everyday:** DeepSeek Flash via OpenRouter is fast, inexpensive, and right for
most family conversations. Cheaper Inference serves the same DeepSeek family at
a lower per-token rate if you would rather fund there instead.

**Complex work:** the same OpenRouter key unlocks frontier models. When a job
needs heavier reasoning (an advocacy letter, a tangled support plan), ask the
agent to switch, or let it propose the switch.

**Schedules on a local model:** the check-ins are simple by design, so run them
on a small local model and the unattended, around-the-clock part costs nothing
and stays private. The agent can pin a cron job's model and provider when it
creates it.

**Voice both ways, locally:** local `faster-whisper` transcribes incoming voice
notes; local **Piper** speaks replies (`pip install piper-tts`). Voice note in,
voice note out, no cloud involved, on whichever channel the family uses.

Full detail, including what each tier costs: `docs/models.md`.

---

## Schedules and cron

The check-ins and nudges live in `schedules/`. Each file has a copy-paste setup
command. The common pattern:

```bash
hermes -p neurofamily cron add --name "Weekly family check-in" \
  --schedule "0 18 * * 0" \
  --prompt "Load the family-navigator skill and run the weekly family check-in as described in schedules/weekly-family-checkin.md"
```

Or simply tell the agent:

> "Set up the weekly family check-in from the schedules folder and deliver it
> here Sunday evening."

It can create the job itself. A few things worth knowing once you have more than
one:

- **Pin the model per job.** A morning paper does not need a frontier model. Set
  it once per job and the running cost of the whole rhythm drops.
- **Timezone is the family's, not the server's.** Pass `--timezone` if the
  machine is set to UTC or a different zone than the household.
- **Continuity and catch-up.** Turn them on for anything the family would notice
  missing. A check-in that silently skipped a day is worse than one that arrives
  late.
- **Delivery target matters.** A job set to deliver "origin" follows the
  conversation it was created in. If you move from terminal to Telegram, re-check
  the target.
- **Verify by running it once.** `hermes -p neurofamily cron run <name>` executes
  without waiting for the schedule.
- **Two jobs writing one file will collide.** The Morning Edition reads; the
  evening check-in writes. Keep them on different files unless you have decided
  otherwise.

On a laptop that sleeps, scheduled work simply does not happen while it is
asleep. That is not a fault; it is the machine being off. If the rhythm matters,
run it on a machine that stays awake, or accept that a missed morning is a
missed morning and read it when you open the lid.

---

## WhatsApp: the dedicated number

WhatsApp is the best channel for a whole-family group where several people
reply, and the repo supports it through a built-in bridge. It is not the default
for one reason: **a WhatsApp account is tied to one phone number**, so the bot
needs its own SIM or eSIM. That is a real cost and a real afternoon, which is why
`quickstart.py` leads with Telegram.

Telegram gives you the same conversation today, free, with no extra number. Add
WhatsApp later without starting again.

If you do want it:

Hermes ships a built-in WhatsApp bridge (it links like a device on WhatsApp Web,
via QR pairing). It supports group chats, voice messages, and scheduled messages
at any hour with no restrictions, which matters because the team's check-ins must
deliver reliably.

| Setting | Recommendation |
|---|---|
| Number | A dedicated SIM or eSIM for the bot (do not link the family's personal number); a small account-restriction risk exists with any linked-device bridge |
| The group | One WhatsApp group: the family + the bot number. Everyone can talk to the team there |
| One-to-one | Optional: a young person can also message the bot privately where the family agrees, with the consent rules in `AGENTS.md` |
| Always-on | The bridge lives on the family's machine; keep it running on whatever schedule the family is comfortable with |
| Setup | `hermes whatsapp` - pick the bot mode, scan the QR from the bot phone, add the numbers that may talk to it |

Then in the profile's `.env`:

```
WHATSAPP_ENABLED=true
WHATSAPP_MODE=bot
WHATSAPP_ALLOWED_USERS=61400000000
```

The official WhatsApp Cloud API path exists but currently supports direct
messages only in v1 and restricts out-of-window sends, so it is not the right
path for a scheduled-check-in family group.

---

## Calendar, mail and files

With a free Maton account, the team can work with the family's real Google or
Microsoft calendar, mail, tasks and files (read-first; writes always need the
family's yes in the moment). Full details in `docs/connections.md`. Skip this
entirely if the family prefers everything to stay inside the family folder.

---

## Redaction, in more detail

`scripts/redact_doc.py` is covered in `INSTALL.md` and in the workbook, page 12.
Three things that only matter once you are using it regularly:

- **Batch it.** It takes one file at a time. A shell loop over a folder is fine;
  check the counts on each output rather than assuming.
- **Keep the names list somewhere.** The `--names` values are the same short
  forms as `~/neurofamily/deidentification.md`. If you find yourself retyping
  them, put them in a small shell script beside the family folder.
- **Re-run it if the document changes.** A redacted file is a snapshot. If the
  plan is reissued, redact the new one rather than editing the old `.md` by hand:
  hand edits are where real values creep back in.

Its tests live in `tests/test_redact_doc.py` and run with
`python -m unittest tests/test_redact_doc.py`.
