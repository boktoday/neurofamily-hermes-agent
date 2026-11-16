# Install

**Goal: from nothing to talking to your family's support team in under three minutes.**

You do not need to edit a hidden file, compare model providers, or buy a SIM card.
One command asks you two questions and does the rest.

---

## Before you start

You need two things:

1. **A computer** - Windows, Mac or Linux. An 8GB Windows laptop is plenty.
2. **Hermes Agent installed.** Get it from
   <https://hermes-agent.nousresearch.com/docs>. There is a one-click desktop
   installer for Windows and Mac, and no administrator rights are needed. When
   `hermes --version` prints a number, you are done with this bit.

If you are installing Hermes for the first time: start it once, then close it.
That creates the folder the next step needs.

---

## Step 1: Get this folder

**On the website:** open <https://github.com/boktoday/neurofamily-hermes-agent>,
click the green **Code** button, then **Download ZIP**. Unzip it somewhere you
will find again, like your Documents folder.

**Or, if you already use a terminal:**

```bash
git clone https://github.com/boktoday/neurofamily-hermes-agent.git
cd neurofamily-hermes-agent
```

---

## Step 2: Run one command

Open a terminal **in that folder** and run:

```bash
python scripts/quickstart.py
```

On a Mac or Linux machine, use `python3` instead of `python`.

It will:

- check your Python and your Hermes install, and tell you exactly what is
  missing if either is;
- copy the sixteen support skills into a `neurofamily` profile;
- build your family folder, with private rooms for the carer and for each young
  person;
- ask you **two** questions, and nothing else.

### The two questions

**"Which brain?"**

| Pick | What it means |
|---|---|
| **1. Cloud (OpenRouter)** | One key, free options to start. Fast and capable. Messages go to that company, so the family folder keeps real names out of them. |
| **2. Local (Ollama / LM Studio)** | Nothing ever leaves your computer. Free forever. Slower, and simpler answers. |

If you already have Ollama or LM Studio running, quickstart finds it and suggests
the local option.

**"How do you want to talk to it?"**

| Pick | What it means |
|---|---|
| **1. This computer** | Zero setup. Type into the Hermes window. |
| **2. Telegram** | Two minutes, free, no extra phone number. Message from anywhere, including at 2am. |

WhatsApp works too, but it needs its own phone number, so it is a later upgrade
rather than a first step. See `docs/advanced-setup.md`.

---

## Step 3: Say hello

```bash
hermes -p neurofamily
```

Then type:

> Hello, we are setting up the NeuroFamily support team. Let's build our family profile.

That is it. You are in. The Family Navigator asks its questions at your pace
(about eighteen minutes in total, and you can stop and resume for weeks), and
writes the answers into your family folder.

**Nothing leaves your computer unless you picked a cloud model.** Even then, the
family folder stays local.

---

## If something goes wrong

**"python is not recognised"**
Python is not installed, or it did not add itself to your PATH. Install the
current version from <https://python.org/downloads> and tick **"Add python.exe to
PATH"** on the first screen of the installer. Close the terminal, open it again.

**"hermes is not recognised"**
Hermes is not installed yet, or the terminal was already open before you
installed it. Install it from <https://hermes-agent.nousresearch.com/docs>, then
open a fresh terminal.

**"That folder does not exist yet"**
Hermes has never been run. Start it once, close it, run quickstart again.

**It stopped half way**
Run it again. It never overwrites your own files. With `--update` it refreshes
the team and keeps everything you have edited, saving the repository's version
beside yours with `.new` on the end.

**You want to see what it would do first**

```bash
python scripts/quickstart.py --dry-run
```

Nothing is written, no key is asked for, no network call is made.

**Skills do not appear in the profile**
They went to the wrong profile, which usually means Hermes was pointed at a
different one. Check with `hermes -p neurofamily skills list`.

**Model errors on every message**
The key in `.env` is missing, or the provider name in `config.yaml` does not match
the key you saved. Run quickstart with `--update` and re-enter the key.

---

## Privacy, in one paragraph

Everything lives on your own machine. Before the agent reads any school or NDIS
document, it asks whether to de-identify, and unanswered means de-identified.
Carer reflections and young-person notes sit in separate private folders that the
Morning Edition is coded never to read.

For a document you are about to attach, scrub it first:

```bash
python scripts/redact_doc.py NDIS-plan.pdf --names "Miss A, our GP, her school"
```

Attach the `.redacted.md`, never the original. The full picture, including what
to switch on at your model provider, is in the **Privacy first** section of
`README.md`.

---

## Updating later

```bash
cd ~/neurofamily-hermes-agent
git pull
python scripts/quickstart.py --update
```

`--update` keeps every file you have edited and writes the repository's version
beside it with `.new` on the end, so you can compare before deciding.
`CHANGELOG.md` records what changed.

---

## Where the rest lives

This file stops here on purpose. Everything else is in one of these:

| You want | Read |
|---|---|
| A different provider, local models, scheduled jobs, WhatsApp | `docs/advanced-setup.md` |
| Which model for which job, and voice | `docs/models.md` |
| Calendar, mail and files | `docs/connections.md` |
| The questions onboarding asks, and why | `PROFILE_BUILDER.md` |
| The book version, page by page | the Windows workbook (page 12 covers redaction) |

---

## What you should have at the end

- a `neurofamily` profile with sixteen skills
- a family folder at `~/neurofamily/` with `shared/`, `private-parent/` and
  `private-yp/`
- a model that answers
- a way to talk to it

If all four are true, you are installed.
