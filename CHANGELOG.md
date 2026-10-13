# Changelog

All notable changes to the NeuroFamily Support Ecosystem are documented here.

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
