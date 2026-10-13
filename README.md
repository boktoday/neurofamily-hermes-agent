# NeuroFamily Support Ecosystem (Hermes edition)

A multi-agent support ecosystem for families raising neurodiverse children. Built with love for families who deserve support that actually supports them.

![Ecosystem overview](https://scarlet-mill-55mb.here.now/file_129---a834002a-916d-41ae-b7c7-e876187e1c17.jpg)

---

## What this is

Twelve specialist support skills that run on **[Hermes Agent](https://hermes-agent.nousresearch.com/docs)**, your own personal AI assistant. Install it once, and the family has a complete support team through the chat app you already use (Telegram recommended).

Think of it as a multidisciplinary team in your pocket: a family coordinator, a school advocate, an OT for sensory and routines, a coach for emotional regulation, a feeding specialist, a carer wellbeing companion, and more, all working together and all sharing one picture of your family.

**Private by design.** Everything runs on your own machine. Your family's information stays with you.

**The Family Navigator** is the front door. It gets to know your family, routes each need to the right specialist, and holds the big picture across everyone.

---

## The support team

| Skill | Focus |
|---|---|
| Family Navigator | Whole-family hub, triage, coordination |
| Emotional Coach | Regulation, anxiety, meltdown recovery, emotional literacy |
| Sensory Guide | Sensory profiles, sensory diets, environment, fine motor |
| Communication Specialist | AAC, speech and language support, social scripts |
| Education Advocate | IEPs, EHCPs, 504s, ILPs, accommodations, school rights |
| Behaviour Advisor | Behaviour patterns, functions, proactive support plans |
| Routine Architect | Visual schedules, transitions, executive function |
| Young Person Coach | Self-advocacy, identity, independence, transition planning |
| Food Support | ARFID, safe foods, food diaries, low-stress mealtimes |
| Sibling Support | Siblings' feelings, identity, fair attention |
| Parent Companion | Carer burnout, grief, respite, wellbeing |
| Artifacts Generator | Visual schedules, trackers, dashboards, family mini-apps |

Every skill is neurodiversity-affirming, strengths-based and trauma-informed. See `SOUL.md` for the principles and `AGENTS.md` for how the team works together.

---

## How it works

1. **One shared brain.** All skills read and update a shared family folder (`family-profile.md`, `child-summary.md`, `active-concerns.md`, and more). When one specialist learns something important, the others know.
2. **One front door.** The Family Navigator handles first conversations, profiles your family, and routes to specialists.
3. **Schedules for real family life.** Optional check-ins and nudges through Hermes cron jobs: morning routine anchors, a weekly family check-in, carer wellbeing prompts, and a monthly review. See `schedules/`.
4. **Escalation rails.** The team supports; it never diagnoses, treats or replaces professional care. Crises route to humans immediately. See the rails in every skill.
5. **Optional connections.** With a free Maton account, the team can read the family's Google or Microsoft calendar and mail (real appointments in the weekly check-in, school emails summarised before meetings). Read-first, writes need a yes in the moment. See `docs/connections.md`.
6. **A model for every job.** DeepSeek Flash via OpenRouter by default, frontier models on demand for complex work, and local models encouraged for the scheduled check-ins. Voice is local too: Piper speaks, faster-whisper listens. See `docs/models.md`.

---

## Install

See `INSTALL.md`. Short version:

1. Install Hermes Agent (one command, any laptop).
2. Add this profile from the install sheet, or copy `skills/` into your Hermes profile and copy the templates from `shared/`.
3. Have your first conversation with the Family Navigator to build your family profile.
4. Optionally add the schedules from `schedules/`.

---

## Schedules

| Schedule | Rhythm | What it does |
|---|---|---|
| Daily routine anchors | Weekday mornings | Gentle nudge for the morning routine, tied to the visual schedule |
| Weekly family check-in | Sunday evening | Navigator-led: the week ahead, wins, one thing to make easier |
| Carer wellbeing check-in | Wednesday evening | Parent Companion: energy, support, one act of respite planning |
| Sibling check-in | Fortnightly | Sibling Support: a moment that belongs to the sibling |
| Monthly ecosystem review | Monthly | Look back across the team: what worked, what changes |

Setup commands are in `schedules/README.md`.

---

## What changed in the Hermes edition (v2.0.0)

- The twelve OpenClaw agents are now twelve Hermes **skills** (`skills/<name>/SKILL.md`), with the same souls and tools, plus shared-context and escalation sections.
- **Schedules added** (the OpenClaw edition had none).
- **LICENSE added** (PolyForm Noncommercial 1.0.0 with Required Notice). The previous repo had no license.
- **Local models guide** added to `INSTALL.md` (offline setup via LM Studio or Ollama).
- Shared-context **file templates** added (`shared/`), plus the missing regional template.
- Language standardised on "young people" throughout.
- All OpenClaw references replaced with Hermes equivalents.

Full history: `CHANGELOG.md`. What's next: `ROADMAP.md`.

---

## What it is not

- Not therapy, not medical or legal advice.
- Not a replacement for your child's professionals. It helps you get more out of them: better questions, better records, better advocacy.
- Not a companion or a friend substitute for any child. It is a support tool that works for the family.

## Repository layout

```
skills/            12 specialist skills (each SKILL.md)
shared/            the shared brain: family folder templates + regional resources
schedules/         ready-to-install check-ins and nudges
SOUL.md            the principles every skill lives by
AGENTS.md          how the team works together
INSTALL.md         full setup guide (including fully-offline local models)
PROFILE_BUILDER.md the guided family onboarding
config.yaml        example Hermes configuration
docs/              design document + connections and models guides
```

---

## License

PolyForm Noncommercial License 1.0.0. Free to use, change and share for any noncommercial purpose, with credit. See `LICENSE`.

Required Notice: Copyright 2026 Brendan O'Keefe (https://onetoeight.org)

Original OpenClaw edition designed March 2026. Hermes edition rebuilt October 2026.
