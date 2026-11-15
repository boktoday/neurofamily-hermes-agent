---
name: morning-edition
description: "Use when the family wants a printed morning paper, asks for the Morning Edition, or wants to change what the paper carries."
version: 1.0.0
author: NeuroFamily Support Ecosystem contributors
license: PolyForm Noncommercial 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [paper, print, routine, news, calendar, morning]
    related_skills: [routine-architect, family-navigator, ndis-guide, local-support]
---

# Morning Edition

One black-and-white A4 page on the table before the day starts. A parent edition on weekdays, a family edition at weekends. The paper is deliberately short: what is on, what anchors the day, one question worth asking, and one rotating feature that the family chooses by weekday.

## When to use

- The family asks for a morning paper, a printed brief, or "something on the fridge each morning".
- They want to change what the paper carries, which day a feature prints, or whether it prints at all.
- A source stops appearing and they ask why the page looks thin.

## What the paper contains

Every day, the Today block: the routine anchors from `paper.json`, appointments and deadlines from `family-calendar.md` for the next seven days, and one question chosen by date (a parent question on weekdays, a family question at weekends).

One feature per day, set in `paper.json` under `weekday_features`:

| Feature | What it prints | Where it comes from |
|---|---|---|
| `news` | News for neurodivergent families | the newest brief in `<family>/news/news-YYYY-MM-DD.md` |
| `learn` | One thing to learn | a 20-item strategy bank inside the builder, drawn from this ecosystem's skills |
| `local` | Crisis lines and who to call | `shared/local-support/<country>.md`, with the family's own region line |
| `family` | One thing to do together, a table question, ten minutes for the sibling | built in, no source needed |
| `none` | nothing extra | a thin page is correct |

Defaults follow what most families want: `news` on Monday, `family` on Saturday and Sunday, nothing on the other weekdays. Change the map, not the code.

## Setup

1. Copy `shared/paper.template.json` into the family folder as `paper.json`.
2. Set the family name, country, and the region line for local services. The region is the family's decision, in their own instance: a suburb or postcode, and how far they will travel.
3. Fill the three anchors if the family has a routine they want printed. Leave them empty and the block is omitted rather than printed blank.
4. File news briefs into `<family>/news/` as `news-YYYY-MM-DD.md`. The paper prints the newest brief filed on or before today, and says plainly when none was filed.

## Running it

```bash
python scripts/build_paper.py --family ~/neurofamily
python scripts/build_paper.py --family ~/neurofamily --no-print
python scripts/build_paper.py --family ~/neurofamily --date 2026-11-09 --no-print
```

It writes `<family>/paper/YYYY-MM-DD.html`, `<family>/paper/editions/YYYY-MM-DD.pdf`, and `last-run.json` with the date, edition, feature, page count and whether the printer accepted the file. The HTML builds with the standard library alone; the PDF step needs Playwright, and printing needs SumatraPDF on Windows. If either is missing the builder says so and still writes the page.

## Rules

- **Black and white only.** Greys, rules and one type family. No colour accents, however tasteful: the paper is printed in ink-saver mode and colour costs the family money.
- **A thin edition is right.** On a day with no feature, one page is the answer. Never pad to look substantial.
- **The question is chosen by date**, not at random, so a rebuild on the same day gives the same paper.
- **Do not generate news inside the paper build.** A brief is filed by its own job or by the agent at the family's request; the paper only prints what exists.
- **Check the queue before claiming paper.** A clean build means a PDF, not a printed page.
- **Nothing clinical.** The footer says the paper is not medical advice and points to the local-support file. Keep it that way.

## Changing it

- New feature: add a branch in `build_paper.py` beside the others, a key in `weekday_features`, and a row in the table above.
- Longer or shorter paper: the layout is one column at 11.4pt. Resist shrinking the type; parents read this while tired. If it needs more room, cut a section instead.
- New country: drop `shared/local-support/<cc>.md` in place and set `country` in `paper.json`.
