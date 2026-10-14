---
name: local-support
description: "Use at onboarding and whenever the family needs local services or crisis lines."
version: 1.0.0
author: NeuroFamily Support Ecosystem contributors
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [local, support, crisis, autism, adhd, onboarding]
    related_skills: [hard-moments, family-navigator, health-appointments]
---

# Local Support

Builds and maintains the family's own short list of local services: autism and ADHD organisations, parent and carer lines, and the crisis numbers for their area. This is the list every other skill reaches for when a hard moment appears.

## When to use

- During onboarding, after the location question is answered.
- Whenever the family says "find us support near us", "who do we call", or the family moves region.
- At each quarterly check-in, to re-verify the list and refresh dead links.

## First: the location question

Ask plainly and explain why: "Which country and state or region are you in? It only loads the right local services, and it stays on your machine like everything else." Save to `profile/family.md` under `location`. Never infer location from a name, a language or a school.

## Then: build the list

1. Load the matching file from `shared/local-support/` (for example `au.md`). A state or province detail narrows it further.
2. **Verify every entry live before presenting it.** Fetch each organisation's page; a link that fails, or a page that no longer carries the listed number, gets flagged and either replaced or marked "check directly". Never present an unverified number as current.
3. Trim to what fits this family: young children or older, diagnosis stage or post-diagnosis, autism-first or ADHD-first or both. Keep the crisis section intact regardless.
4. Present it warmly, not as a wall: crisis lines first, then the two or three services most relevant this month, then "the rest are saved for when you need them".
5. Save the working list to `profile/local-support.md` with today's verification date. Add the crisis lines to the family's **crisis card** artifact.
6. Offer to draft the first contact: Autism Connect asks good questions; a GP letter is one paragraph the agent can write.

## If the family's country is not covered

Say so plainly, then: build the bridge list instead: **findahelpline.com** for verified crisis and support lines by country, plus the family's GP or paediatrician as the route to local services. Offer to add the country to `shared/local-support/` over time, and never invent a local service.

## Guardrails

- Never invent, guess or "probably" a phone number. Verified sources only, with dates.
- Keep the distinction loud: 24/7 crisis services versus information lines with office hours versus volunteer-run charities.
- The list lives in the family folder. Location and services never leave the machine unless the family shares them.
- This skill finds and organises support. It does not give medical advice, and it does not assess anyone.

## Quarterly refresh

At the quarterly check-in: re-fetch each listed link, note changes, update the verification date, and tell the family what changed in one short line. A paged practice while things are calm beats a dead number in a hard moment.
