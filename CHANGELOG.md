# Changelog

## The Morning Edition no longer prints someone else's name

Found by running the real agent end to end rather than reading the code.

`shared/paper.template.json` shipped with `"family_name": "The O'Keefe family"`. A family who never edited `paper.json` would get a kitchen-table paper headed with the author's surname. `build_paper.py` falls back to the template whenever `paper.json` is missing, so a family who skipped `setup-family-folder.py` hit it every time.

- The template default is now `"The family"`, which matches the fallback already in `build_paper.py` (`cfg.get("family_name") or "The family"`).
- Verified by building a paper against a folder with no `paper.json` at all: the heading reads "The family", not a stranger's surname.

---

## canirun.ai/models reaches the two places people look

Local models were offered in three places and explained in `docs/`, but the question a family actually asks first - *will this run on my laptop?* - was only answered in a document they had no reason to open yet.

- **README**, feature 6 ("A model for every job"), now points at [canirun.ai/models](https://canirun.ai/models/) with what it is for: grading 146 open models against your real graphics card or Mac, with the memory each needs.
- **The workbook, page 27** ("Running it on your own machine") carries the same pointer inside the existing speed-table warning, where the reader is already choosing between Qwen3.6 35B and the 800B models that will not fit. The page was full to within 3pt of the body floor, so the addition was paid for by trimming the Screenshot 14 placeholder caption rather than shrinking type.
- **`docs/advanced-setup.md`** now names the catalogue path alongside the landing page: the root detects your hardware, `/models/` lets you check a specific model before a multi-gigabyte download.
- Verified: the URL returns 200 and `/models` redirects to `/models/`, so the trailing slash is the canonical form. The page is titled "Local AI models you can run" and lists 146 models. Workbook still 31 pages, overflow gate `PASS`, page 27 body text ends at 803.0pt against the 806.0pt floor.

---

## The sketch replaces the old hero image

- `docs/ecosystem-overview.jpg` is gone; `docs/family-agent-sketch.png` takes its place as the README's opening image, with alt text that describes what the sketch actually shows rather than "Ecosystem overview".
- The new image is the source file from `neurodivergeagent.com/assets/family-agent-sketch.png`, byte-identical, 2560x1440, 431 KB.
- **Two labels in the sketch do not match the repo, and the image was committed as supplied.** It reads "14 specialists + Navigator" and "5 reality-proof schedules". The repo has **fifteen** specialists plus the Navigator (sixteen skills), and **seven** schedules. `morning-edition` is not in the sketch at all, despite being one of the headline features and a full page in the workbook. Regenerating the sketch with those corrected would keep the image and the repo telling the same story.

---

## One command, two questions, three minutes

The setup was correct and complete, and it assumed the reader was comfortable in a terminal. Cloning, creating a profile by hand, editing a hidden `.env`, comparing three inference routers and buying a SIM card for WhatsApp is a lot to ask of a parent doing this at 11pm after a hard day. `scripts/quickstart.py` replaces all of it with one command and two questions.

- **`scripts/quickstart.py`**, standard library only, Python 3.10+. Five steps: check Python and the Hermes CLI; copy the sixteen skills, `shared/`, `templates/` and the config into a `neurofamily` profile; build the family folder with its private partitions; ask which brain; ask how you want to talk to it.
- **The profile location is derived the way Hermes derives it**, not guessed: `HERMES_HOME` if set (and unwound correctly when it points at a profile rather than the root), otherwise `LOCALAPPDATA/hermes` on Windows and `~/.hermes` elsewhere, honouring `HERMES_DATA_DIR_SUFFIX`. `--profiles-dir` overrides it.
- **Two choices, not four.** Cloud means OpenRouter with a key written straight to `.env`; local means Ollama or LM Studio, auto-detected on ports 11434 and 1234 and configured through `custom_providers` with no key at all. If a local engine is already running, it becomes the suggested default and the script says why.
- **Never destructive.** A first run copies; a second run finds everything identical and copies nothing. `--update` keeps every file the family has edited and writes the repository's version beside it with `.new` on the end. Existing `.env` files are merged, not replaced, and the previous one is kept as `.env.bak`.
- **`--dry-run` writes nothing, prompts for nothing and makes no network call.** It resolves both paths, plans all 110 file copies, and prints each one with its action, so the copy logic is verifiable on any machine without creating a profile.
- **`docs/advanced-setup.md`** now carries what used to make `INSTALL.md` long: the full provider comparison and retention table, zero-retention instructions for both OpenRouter and Cheaper Inference, local-model hardware guidance, the models-and-voice mix, cron detail, and the WhatsApp dedicated-number explanation.
- **`INSTALL.md` rewritten** from 241 lines to a three-minute path for a non-technical parent: get the folder, run one command, say hello. It keeps the two troubleshooting answers people actually hit, and points at `docs/advanced-setup.md` for everything else.
- **OpenRouter's zero-retention wording was corrected while writing it.** It is not a single toggle, which is how it is usually described: ZDR is enforced per model group in the account privacy settings, with a separate Safety Retention choice, and it is not on by default for self-serve accounts. The wizard and the docs now say that rather than sending someone looking for a switch that does not exist.
- **Stale step references fixed.** `AGENTS.md`, `README.md`, `skills/ndis-guide/SKILL.md` and `shared/deidentification.template.md` all pointed at `INSTALL.md` Step 4 and Step 5, which no longer exist after the rewrite. All now point at `docs/advanced-setup.md`.
- Verified: `python scripts/quickstart.py --dry-run` exits 0 and reports 110 planned copies; a real run against a sandbox writes the profile, the family folder, `.env` and `config.yaml` correctly; `--update` preserves an edited `SOUL.md` and saves `SOUL.md.new`; the Telegram and local-engine paths both produce working config; the 30 redaction tests still pass.

---

## Privacy, written down for the family rather than only for the machine

The de-identification gate, the private partitions and the redaction script were all in place but scattered across `AGENTS.md`, four skills and a script's docstring. A family reading the README would not have found them, and the workbook said nothing about any of it.

- **`README.md` gained a "Privacy first" section** with the four layers in the order they apply: the de-identification gate, the private partitions, local redaction, and the provider's retention setting. Each layer says what it does, what it deliberately does not do, and where the code that enforces it lives. The closing subsection, "What this does not claim", states the honest position: it lowers exposure, it does not make anyone anonymous.
- **The zero-retention instructions are now specific.** The section gives the dashboard route (Data Protection), the timing that actually matters (before the first request, because enabling it later does not delete what was already kept), and the trade (narrower model list, possible price change). It also quotes Cheaper Inference's own documentation: *"ZDR does not detect, mask, or anonymize PII; there is no automatic pre-provider PII redaction."* That sentence is the argument for why local redaction exists at all, and it comes better from the provider than from us.
- **`INSTALL.md` Step 4** gained the same dashboard path, the `zdr: true` per-request note, the `/v1/models?zdr=true` price view, and a pointer to Step 5d for the machine-side half.
- **The workbook gained page 12, "Before you attach anything"**, framed as two gates the reader closes: one on their own machine (the redaction script, when to run it, what it removes, what it misses) and one in the provider's dashboard. It carries the same quotation, an "if it has already gone" note for the family who attaches the original by mistake, and a tick box.
- **A stale cross-reference bug was found and fixed while doing it.** Six references pointed at "page 15" for the crisis lines, which had been right before two pages were inserted ahead of it and had been wrong ever since: page 15 is "What we never ask it to do", and the crisis lines are page 22. One reference to the key sheet pointed at page 15 instead of page 11. All were corrected, and `verify_pages.py` now re-derives the page map from the rendered markup and checks that every reference resolves to a real page.
- **The recap page counted wrong.** It said "all ten are ticked" over a checklist that the new page would have made eleven. Privacy is now in the closing checklist as two items, the two gates, giving twelve in a balanced six-row grid.
- **`README.md` said "Fifteen specialist support skills"** while the repo has sixteen and the layout section said sixteen. That was a leftover from the routing unification and is now consistent.
- Workbook is 31 pages, A4, vector, overflow gate `PASS`, every page number 2..31 in sequence.

---

## Local PII redaction before a document is ever attached

The de-identification gate asked whether to de-identify a document *after* it arrived. On a hosted provider that is too late: attaching the file is the moment the bytes leave the machine. `scripts/redact_doc.py` moves that step to the family's own computer.

- **`scripts/redact_doc.py`**, standard library only. Reads `.txt`, `.md`, `.csv` and `.html` natively; `.pdf` through `pypdf`/`PyPDF2` or the `pdftotext` binary, and says so plainly and stops if neither is present rather than pretending it redacted something it never read.
- **A scanned PDF is not the same problem as a missing reader**, so it no longer gets the same advice. Telling a family to `pip install pypdf` when pypdf is present and the file is a photo of a letter wastes their time and makes the tool look broken; that case now says the PDF had no text layer and points at OCR. pypdf's own recovered-file chatter is silenced too, because this script's stdout is meant to carry counts and nothing else.
- **Redacts** NDIS participant numbers (keyword-anchored, plus bare 9-digit runs), Medicare numbers, Centrelink CRNs, labelled dates of birth, email addresses, Australian mobile and landline numbers, Australian street addresses and state postcodes, and any name passed with `--names`. Names become stable pseudonyms: `[SCHOOL_A]`, `[CHILD_A]`, `[PERSON_A]` for a titled adult.
- **Deliberately leaves alone** ordinary dates, because review dates are the substance of a plan, and 1300 / 1800 / 13 service numbers, because one of them is the NDIS line.
- **Three leaks closed during development**, each caught by a test that now guards it:
  - Name substitution ran first and chewed emails into `[CHILD_A].[CHILD_A]@example.com`. Structured patterns now run before names.
  - Bare-token name expansion turned the suburb `Reservoir` into `[SCHOOL_A]` inside an address, because the school was called Reservoir High School. Schools no longer get bare-token expansion.
  - The output file was named after the input, so `Sarah-Whitmore-plan.pdf` produced `Sarah-Whitmore-plan.redacted.md`, and the summary printed the source filename. Both are now scrubbed.
- **Two attribution bugs found by running a real IEP excerpt.** A father written as `Mr Daniel Whitmore` was labelled `[CHILD_B]`, because the family had typed his name without the title; classification now pre-scans the document for a title before it decides, so he becomes `[PERSON_A]`. And a surname shared by two people was being attributed to whichever name was processed first, so a bare `Whitmore` silently meant the daughter; a shared surname now gets `[SURNAME_A]`, which belongs to neither.
- **`tests/test_redact_doc.py`**, 30 tests against a fabricated NDIS plan and a fabricated IEP excerpt, including that no identifier survives, that the plan's own review dates and goals do survive, and that the terminal summary contains no values.
- **`AGENTS.md`** gained "Before a document is attached, not after", **`INSTALL.md`** gained Step 5d, and **`skills/ndis-guide/SKILL.md`** now asks before the attachment rather than after. All three say plainly what to do if a raw file has already been sent: name it, then offer a local model or zero data retention.
- Verified: `python -m unittest tests/test_redact_doc.py` returns 30 tests, OK, exit code 0.

---

## Private partitions, and a paper.json that actually gets created

Two problems with one shape: the family folder had no notion of privacy, and the Morning Edition could not start on a fresh install.

- **`scripts/setup-family-folder.py` now copies `*.template.json` as well as `*.template.md`.** It only globbed markdown, so `shared/paper.template.json` was skipped and `~/neurofamily/paper.json` never existed. `build_paper.py` silently fell back to the repo defaults, which meant a family's choices never took effect. Now `paper.template.json` lands as `paper.json`. Still never overwrites.
- **Three partitions are created with the folder:** `shared/`, `private-parent/` and `private-yp/`. The two private ones are mode `0o700` on POSIX, and each carries a `README.md` stating its boundary. On Windows the chmod is skipped, because ACLs are not expressible that way, and the documentation is the control instead.
- **`scripts/build_paper.py` cannot read a private partition.** Every read goes through a new `guard_shared()` check that exits with a clear message rather than opening the file, and a run prints `private partition present, not read: …` so the skip is visible rather than assumed. Tested three ways: the three reader functions each refuse, pointing `--family` at `private-parent/` refuses, and a normal build prints the skip line and produces its page.
- **`AGENTS.md` gained a "Privacy partitions" section** naming the three rooms, who may see each, and the rule that what travels from a private note into `shared-notes.md` is the operating conclusion, never the disclosure.
- **`parent-companion`** writes carer reflections to `~/neurofamily/private-parent/carer-notes.md` and is told directly never to copy them into `shared-notes.md`. **`young-person-coach`** and **`sibling-support`** write to `~/neurofamily/private-yp/` and need that person's explicit consent, in that conversation, before summarising anything for a parent. All three inherit the `hard-moments` safety override and say so out loud rather than letting someone discover it later.
- **`morning-edition`** now documents its fixed reading list, so a future feature cannot quietly pull private material onto the kitchen table.
- Three more phantom profile paths went with this: `parent-profile.md`, `young person-profile/<name>.md` and `sibling-profile/<sibling-name>.md` were not files the schema defines.
- Verified: `setup-family-folder.py --target <tmp>` writes 11 files plus three partitions, and a second run writes 0 and leaves 11 alone. Both scripts compile. Task 1's phantom-path sweep still returns zero.

---

## Sixteen-skill catalogue unified, license and model drift fixed

`AGENTS.md`, `profile.yaml`, `README.md` and the routing tables disagreed on how many skills exist, and four skills were invisible to the navigator.

- **Count corrected to sixteen** in `AGENTS.md` ("Twelve skills" was the opening line), `profile.yaml` ("twelve specialist support skills") and `README.md`, which already said 16 in the directory map while its migration note said twelve. `profile.yaml` now also names all sixteen slugs so the profile is self-describing.
- **The four missing skills are routable.** `hard-moments`, `local-support`, `ndis-guide` and `morning-edition` were absent from the `AGENTS.md` routing table, the `family-navigator` routing table and its catalogue line, and `morning-edition` was missing from the README skill table. All four now carry a slug, a trigger and what to hand over. The old bare "Crisis or safeguarding" row is replaced by the real `hard-moments` skill.
- **`behaviour-advisor` collaboration points** gained `hard-moments` (crisis handover mid-behaviour-work), `ndis-guide` (behaviour support funding and restrictive-practice rules) and `local-support`.
- **Licenses aligned.** Three skills declared MIT (`hard-moments`, `local-support`, `morning-edition`) against a root PolyForm Noncommercial LICENSE, and `ndis-guide` had no license field at all, nor author, platforms or metadata. All sixteen now read `license: PolyForm Noncommercial 1.0.0`, matching the root LICENSE title. `ndis-guide` also gained its missing author, platforms and tags.
- **Phantom cross-reference removed:** `local-support` listed `health-appointments` in `related_skills`, which is not a skill in this repo. Replaced with `parent-companion`.
- **`config.yaml` model id namespaced** to `deepseek/deepseek-v4-flash` with a comment on how OpenRouter resolves ids. Correction worth recording: the previous bare `deepseek-v4-flash` was **not** returning a 404. Tested against the live API, both forms answer HTTP 200, because OpenRouter resolves the bare name as an alias. The bare form is simply absent from the published catalogue at `/api/v1/models`, so it can be retired without notice. The namespaced id is the durable one, and the comment now says exactly that rather than overstating the risk.
- Verified: all 16 skill directories are named in `README.md`, `AGENTS.md`, `profile.yaml` and `skills/family-navigator/SKILL.md`; `grep -rn "license:" skills/` returns 16 identical values; every `related_skills` entry resolves to a real skill; `config.yaml` and `profile.yaml` parse; the model id is present in the live OpenRouter catalogue.

---

## Legacy OpenClaw paths removed from every skill

Sweep of `skills/**/SKILL.md` for file paths left behind by the OpenClaw-to-Hermes migration. Conflicting paths made the agent spend tool calls looking for files that do not exist.

- **Paths now match the schema in `AGENTS.md` and nothing else.** `USER.md` becomes `~/neurofamily/family-profile.md`. `memory/YYYY-MM-DD.md` becomes `~/neurofamily/shared-notes.md`. `behaviour-profile/<child-name>.md`, `emotional-profile/<child-name>.md` and `child-education-profile.md` all become `~/neurofamily/child-summary.md`, which is where a behaviour or regulation plan now lives. `/workspace/agents/ECOSYSTEM.md` becomes `AGENTS.md` at the repo root.
- **`skills/family-navigator/SKILL.md` consolidated from 283 to 243 lines.** The file carried two merged versions of itself. Removed: a stray `## Who you are` heading stacked directly above `## Who I Am`, two empty headings (`## How you work`, `## Tools and templates`), a duplicate profile-reading section, a duplicate resource list, and a second routing table that disagreed with the first. The two routing tables are now one, with skill slugs, when to route and what to share in a single place.
- **Bugs fixed in the navigator:** the slug `young person-coach` was broken and is now `young-person-coach`; `food-coach` in the routing table was the wrong skill and is now `food-support`; the display names "Young person Coach" and "Food Support Coach" are now "Young Person Coach" and "Food Support"; and the sentence "I check in, not in." now reads "I check in, not up on you."
- **`## Memory Files` renamed to `## Files you keep current`** in every skill. The old heading read like the Hermes `memory` tool, and the split between that tool and the family folder was part of the confusion.
- Australian English and every SOUL.md neurodiversity-affirming rule preserved. No new features.
- Verified: `grep -rnE "USER\.md|/workspace/|ECOSYSTEM\.md|young person-coach|behaviour-profile" skills/ AGENTS.md README.md` returns zero matches, as does a second sweep for `memory/`, `emotional-profile`, `child-education-profile`, `food-coach` and `Memory Files`. Every skill slug in the routing table resolves to a real directory, and every `~/neurofamily/*.md` referenced has a matching template in `shared/`.

---

## Zero data retention compared across providers

- **Docs:** `INSTALL.md` Step 4 gains a "What each one keeps" table after the provider list, because retention matters more than the discount for a family folder full of names, schools and diagnoses. The finding worth acting on: **Cheaper Inference retains a copy of request content by default** and zero data retention is a self-serve dashboard toggle (or a `zdr` request field) that may limit the model list and change the price. **OrcaRouter** stores only metadata by default and grants full zero retention per workspace against a signed DPA, available on every plan, after which it cannot be overridden and every response carries `X-Orca-ZDR: active`.
- **Docs:** `shared/deidentification.template.md` gains "The other half: what the provider keeps", tying the typing convention to provider retention and pointing at local models as the only option that stores nothing anywhere.
- Two cautions are stated rather than glossed: Cheaper Inference makes no universal zero-retention claim on its enterprise page, and zero retention stops storage, not the model seeing the data.

---

## Cheaper Inference added to the provider options

- **Docs:** `INSTALL.md` Step 4 now lists **Cheaper Inference** (https://cheaperinference.com/) alongside OpenRouter, OrcaRouter and local models. It is a discounted marketplace across many labs, typically 35-55% below list price and never above it, OpenAI-compatible at `https://api.cheaperinference.com/v1`. Stated plainly because it differs from OpenRouter in a way that matters to a family budgeting: there is no free tier and no subscription, it is a prepaid wallet funded from $25, paid per token. A free-model flag exists (`GET /v1/models?free=true`) but it is usually a single model and it changes.
- **Docs:** Step 5c notes that Cheaper Inference serves the same DeepSeek family at a lower per-token rate for families who would rather fund there than at OpenRouter.

---

## De-identification gate

- **New:** `shared/deidentification.template.md`, which lands in the family folder as `deidentification.md`. It holds the substitution convention (names to "Miss A, 17", street addresses to suburb plus a landmark, phone and email masked, schools and clinics to "her school" and "our GP", dates of birth to age, plan numbers never typed), plus what to give generously instead, where the real details live, and the honest limit that de-identification lowers exposure without making anyone anonymous.
- **New:** a hard gate in `AGENTS.md` that every skill inherits. The team asks before the profile onboarding begins, and before any personal or medical document is read, uploaded or summarised. Unanswered counts as yes. Asked once per session, never per document, and never twice for a detail a family has already declined.
- **Changed:** `PROFILE_BUILDER.md` gains a Step 0, so the first message of onboarding is the question rather than a question about a person.
- **Changed:** `skills/family-navigator/SKILL.md` opens onboarding with the gate and repeats it before profile updates. `skills/education-advocate/SKILL.md` gates document review, since school paperwork carries a name, date of birth, school and often an address on page one. `skills/ndis-guide/SKILL.md` gates the family's own plan, report or assessment, which carries a client number as well.

---

## Morning Edition paper

- **New:** `scripts/build_paper.py` prints a black-and-white A4 page each morning from the family folder: routine anchors, appointments for the next seven days, one question chosen by date, plus one rotating feature per weekday.
- **New:** `skills/morning-edition/SKILL.md` and `schedules/morning-edition.md`, with `shared/paper.template.json` for settings. Defaults: news on Monday, family edition on Saturday and Sunday, nothing else, because a thin page is the point.
- Features available: `news` (newest brief in the family's news folder), `learn` (strategy bank drawn from the ecosystem's skills), `local` (crisis lines and services for the family's own country and region), `family` (weekend page). The region is the family's own setting, not shipped content.


All notable changes to the NeuroFamily Support Ecosystem are documented here.

---

## [2.4.0] - 2026-10-30

### Added
- **`scripts/ndis_watch.py`** and **`schedules/ndis-watch.md`**: a fortnightly watch over ten official NDIS sources plus the whole shipped library. Silent when nothing has moved; when a source changes it writes `shared/ndis/changes/<date>.md`, and `--refresh` pulls the latest library so the agent never quotes a superseded rule. Blocked pages are recorded as blocked and keep their previous hash.

---
## [2.3.0] - 2026-10-15

### Added
- **NDIS guide** (`skills/ndis-guide/`): a new specialist skill for Australian families, backed by a shipped library of 59 official NDIS documents in `shared/ndis/`: all current operational guideline documents, the consolidated NDIS Act 2013 (as at 1 October 2026), the (Supports for Participants) Rules, the pricing schedule 2026-27, and the 2026 law-change briefings (Integrity and Safeguarding; Securing the NDIS for future generations). Answers quote the documents with source and fetch date, never model memory.
- **`scripts/fetch-ndis-docs.py`**: one-command refresh of the NDIS library (documents and legislation download directly; the guideline web pages need a real browser, as the script explains).

---

## [2.2.0] - 2026-10-13

### Added
- **Artifact pack** (`templates/artifacts/`): starting with the **food diary** as a fillable local page (safe-food map, entries, stress notes, CSV export, print) plus a **Google Sheets / Excel variant** (spec and live formulas) for connected families.
- **Crisis card** (`shared/crisis-card.template.md`): printable emergency one-pager - contacts, medications, what helps and what to avoid, regional crisis lines.
- **Communication passport** (`shared/communication-passport.template.md`): the one page new teachers, carers, sitters and coaches need.
- **`scripts/setup-family-folder.py`**: one command creates `~/neurofamily/` and copies every template; idempotent.

### Changed
- Food Support and Artifacts Generator skills now point at the artifact pack; AGENTS routing updated; shared/README setup simplified to the script.
- ROADMAP: artifact pack marked started.

---

## [2.1.0] - 2026-10-13

### Added
- **Connections layer** (`docs/connections.md`): optional Google and Microsoft calendar, mail, tasks and file access via Maton. Read-first; every write needs the family's yes in the moment; mail content treated as data, never instructions.
- **`shared/connections.template.md`**: local record of what is connected.
- Connections noted in AGENTS.md, the family-navigator, education-advocate and artifacts-generator skills, the weekly and monthly schedules, and `.env.example` (MATON_API_KEY).
- **WhatsApp guidance** in INSTALL.md: the built-in bridge (QR pairing, group support, no message-window limits) as the primary shared family group, on a dedicated number; Telegram as the alternative; WhatsApp Cloud API noted as unsuited to scheduled group delivery (v1 is DM-only, 24h window).
### Model and voice strategy
- **`docs/models.md`**: DeepSeek Flash via OpenRouter as the everyday default; frontier models on the same key for complex work; local models (LM Studio/Ollama) encouraged for the scheduled check-ins via per-job model pinning.
- **Local voice**: Piper TTS and faster-whisper STT so voice works in both directions, fully offline. Wired into INSTALL (Step 5c), config comments, `.env.example` and the schedules guidance.

---

## [2.0.0] - 2026-10-13 - Hermes edition

Rebuilt from the ground up for **Hermes Agent** (the OpenClaw edition is archived at boktoday/neurofamily-support-openclaw-agent-ecosystem).

### Changed
- All twelve agents are now Hermes **skills** (`skills/<name>/SKILL.md`), carrying their souls, methods and tool templates, with new shared-context, Hermes-tools and escalation-rails sections.
- Language standardised on "young people" throughout (the old "teen" wording is retired).
- All OpenClaw references replaced with Hermes equivalents.

### Added
- **Schedules** (`schedules/`): daily routine anchors, weekly family check-in, carer wellbeing check-in, sibling check-in, monthly ecosystem review. The OpenClaw edition had none.
- **LICENSE**: PolyForm Noncommercial 1.0.0 with Required Notice. The previous repository had no licence at all.
- **Shared-context file templates** (`shared/`): the ecosystem's "shared brain" is now real files families can use, not just a description.
- **Local models guide** in INSTALL.md: fully offline operation via LM Studio or Ollama (promised in v1.4.0, never shipped then).
- **Regional template** (`shared/regional/_template.md`) so communities can add their country.
- **ROADMAP.md** and this changelog entry.

### Fixed
- Family onboarding now writes directly into the shared folder (no orphaned USER.md).
- The profile builder, regional files and shared-context docs now describe one coherent install path.

---

## Earlier history (OpenClaw edition, March 2026)

All notable changes to the NeuroFamily Support Ecosystem will be documented in this file.

---

## [1.4.0] - 2026-03-04

### Added
- **Shared Context Layer** - Cross-agent memory system (CHILD_SUMMARY.md, ACTIVE_CONCERNS.md, SHARED_NOTES.md, AGENT_COORDINATION.md, FAMILY_CALENDAR.md)
- **Regional Support** - Country-specific resources (Australia, UK, US)
- **Profile Builder** - Automated onboarding questionnaire for families
- **LMStudio Integration** - Local AI option with Qwen 2.5 9B and other models
- **Local Models Guide** - Complete setup for offline AI

---

## [1.3.0] - 2026-03-04

### Added
- **Telegram setup guide** - Individual bots, group chats, multiple bots for different agents
- **WhatsApp setup guide** - Business API and QR linking options
- **Discord setup** - Best for young people families
- **Channel comparison table** - Telegram vs WhatsApp vs Discord
- **Recommended setups by family type** - Single parent, two-parent, young people-focused, extended family
- **Privacy considerations** - What's visible in each platform

---

## [1.2.0] - 2026-03-03

### Added
- **SETUP_GUIDE.md** - Complete installation and configuration guide

### Updated
- **README.md** - Added setup reference

---

## [1.1.0] - 2026-03-03

### Added
- **Artifacts Generator** - New agent that builds interactive tools, visual dashboards, printable resources, and mini-apps for families
- **USER.md family profile template** - Comprehensive template for families to fill in with detailed information about each family member
- **README.md** - Project documentation and quick start guide

### Updated
- **Family Navigator** - Enhanced to read USER.md first and tailor all responses to the specific family
- **Family Navigator AGENTS.md** - Added critical instructions to read USER.md before every response
- **Family Navigator TOOLS.md** - Added USER.md as the critical tool + routing guidance with context

---

## [1.0.0] - 2026-03-02

### Added
- **Initial ecosystem launch** with 11 core agents:

| Agent | Description |
|-------|-------------|
| 🧭 Family Navigator | Support coordinator, front door to ecosystem |
| 📚 Education Advocate | IEP, EHCP, 504, school advocacy |
| 🗓️ Routine Architect | Visual schedules, transitions, executive function |
| 💚 Emotional Coach | Meltdowns, anxiety, emotional regulation |
| 🧡 Parent Companion | Caregiver burnout, respite, wellbeing |
| 🎨 Sensory Guide | Sensory processing, OT, environment |
| 💬 Communication Specialist | AAC, social scripts, language |
| 🛠️ Behaviour Advisor | PBS, behaviour patterns |
| 🌻 Sibling Support | Sibling needs, family dynamics |
| 🚀 Young people Coach | Independence, transitions, identity |
| 🍎 Food Support Coach | ARFID, safe foods, food diaries |

- **ECOSYSTEM.md** - Overview of the system
- **NEUROFAMILY_ECOSYSTEM_COMPLETE.md** - Comprehensive 1,300-line documentation

---

## Future Ideas

Potential agents to add:
- **Sleep Coach** - Sleep difficulties, insomnia, routine
- **Financial Planner** - Benefits, funding, disability costs
- **Legal Advisor** - Rights, discrimination, education law
- **Social Connector** - Finding community, peer groups, activities

---

*Changelog format based on [Keep a Changelog](https://keepachangelog.com/)*