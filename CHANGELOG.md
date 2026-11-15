# Changelog

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