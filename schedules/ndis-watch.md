# NDIS rules watch

**Skill:** ndis-guide
**Default:** every 14 days, 06:40, delivered only when something has moved.
**Purpose:** the NDIS changes its laws, price limits and guidelines on its own timetable. An agent that quotes a superseded rule is worse than one that admits it does not know, so this schedule keeps the shipped library honest.

## The prompt

> Run `python scripts/ndis_watch.py`. If it reports no change, say nothing and stop: silence is the correct answer on a quiet fortnight. If it reports a change, read `shared/ndis/changes/<date>.md`, then run `python scripts/fetch-ndis-docs.py` to pull the latest library, and then tell me in plain words which sources moved and what the change appears to mean for a family using this agent. Quote the changed text, do not paraphrase from memory. Where a change touches a rule the ndis-guide skill states (eligibility, reasonable and necessary, price limits, early childhood, plan management), update `skills/ndis-guide/SKILL.md` in the same pass and say which lines you changed. Never invent a new rule to fill a gap: if the page is blocked or unreadable, say that plainly and leave the previous source in place.

## Notes

- The watch covers ten official sources: the consolidated NDIS Act 2013, pricing arrangements and price limits, the pricing page, eligibility, what the NDIS is, reasonable and necessary, would we fund it, the early childhood approach guide and partner page, and the news feed.
- Silence is the default on purpose. A fortnightly "nothing changed" message trains people to ignore the one that matters.
- A blocked page (bot wall, 403) is not a change. The watcher keeps the previous hash and reports `blocked`, so a scrape failure cannot overwrite a good source with an error page.
- Run it by hand before a family meeting or a plan review, even if the schedule is not due: `python scripts/ndis_watch.py --verbose`.
