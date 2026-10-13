# The shared brain

This folder holds the templates for the ecosystem's shared context: the files in the family's own folder (default `~/neurofamily/`) that every skill reads and updates, so the whole team works from one picture of the family.

## Set up

1. Create the family folder: `mkdir -p ~/neurofamily`
2. Run the setup script from the repo root:
   ```bash
   python scripts/setup-family-folder.py
   # or: python scripts/setup-family-folder.py --target /path/to/family/folder
   ```
   It copies every template, dropping the `.template` suffix. Safe to re-run: existing files are left alone.
3. The Family Navigator fills them in during family onboarding.

## The files

| File | What lives there |
|---|---|
| `family-profile.md` | The family: adults, children, needs, priorities |
| `child-summary.md` | The current picture of each child, kept up to date |
| `active-concerns.md` | What is live right now, and the current plan for each |
| `shared-notes.md` | Dated notes any skill adds after a substantive session |
| `family-calendar.md` | Appointments, school meetings, reviews, deadlines |
| `agent-coordination.md` | Which specialist has been working on what |
| `connections.md` | Optional: connected calendar/mail services and their IDs (never keys) |
| `crisis-card.md` | Printable emergency one-pager: contacts, medications, what helps |
| `communication-passport.md` | One page about the child for new teachers, carers and sitters |

## What stays out

Session-private detail (anything a family member marks as private), sensitive financial detail, and anything a young person asks to keep in the room it was said in. Safety concerns are shared with the family's humans, not silently filed.
