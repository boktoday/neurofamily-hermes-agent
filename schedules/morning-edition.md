# Morning Edition

**Skill:** morning-edition
**Default:** every morning at 07:15, family's timezone. Print on weekdays, family edition at weekends.
**Purpose:** one calm A4 page on the kitchen table before the day starts. What is on, what anchors the day, one question worth asking, and one rotating feature.

## The prompt

> Load the morning-edition skill. Build today's paper: read the family folder's paper.json and family-calendar.md, and any brief filed in the news folder, then run scripts/build_paper.py --family <family folder>. Print it only if paper.json says print is true. Report one line: the edition date, which feature printed, and whether the printer accepted it. If a section is empty, print the page anyway and say what was missing. Never pad the paper to fill space.

## Notes

- Days with no feature are correct and expected. A thin page is the point: the family chose which day carries which feature in paper.json.
- The paper is black and white only, so it prints cheaply on any home printer. Do not add colour.
- The one question changes daily and is chosen by date, not at random, so the same day always gives the same question if the paper is rebuilt.
- News prints only what has been filed in the family folder's news folder. A news brief is a separate job (the NDIS watch, or a news prompt), never generated inside the paper build.
- If the printer is offline, still save the PDF and tell the family where it is. Never claim paper came out of a printer without checking the queue.

## Install

```bash
hermes cron add --name "Morning Edition" --schedule "15 7 * * *" \
  --prompt "Load the morning-edition skill. Build and print today's Morning Edition from the family folder."
```

On Windows, add a printer check twenty minutes before, so a sleeping printer is woken before press time rather than after:

```bash
hermes cron add --name "Printer awake check" --schedule "55 6 * * *" \
  --script scripts/printer_check.py --no-agent
```
