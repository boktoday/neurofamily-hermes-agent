# Schedules

Ready-to-install check-ins for real family life. Each schedule names the skill that runs it and the exact prompt to use. Families opt in; nothing is scheduled automatically.

| Schedule | Default rhythm | Skill |
|---|---|---|
| Daily routine anchors | Weekday mornings, 7:00 | Routine Architect |
| Weekly family check-in | Sunday, 18:00 | Family Navigator |
| Carer wellbeing check-in | Wednesday, 20:00 | Parent Companion |
| Sibling check-in | Fortnightly, Saturday morning | Sibling Support |
| Monthly ecosystem review | First Sunday, 19:00 | Family Navigator |
| NDIS rules watch | Every 14 days, 06:40, silent when nothing has moved | NDIS Guide |
| Morning Edition | Every morning, 07:15, printed A4 | Morning Edition |

## How to install one

Ask the agent, in plain words:

> "Set up the weekly family check-in from the schedules folder, delivered here Sunday at 6pm."

The agent creates the Hermes cron job itself. Or do it directly:

```bash
hermes cron add --name "Weekly family check-in" --schedule "0 18 * * 0" \
  --prompt "Load the family-navigator skill. Run the weekly family check-in exactly as described in schedules/weekly-family-checkin.md. Read the family folder first. Keep it warm and short."
```

## Rules for every schedule

- Only during waking hours the family chose. Never before 7:00 or after 21:00 unless asked.
- **Check capacity first.** `python scripts/capacity_mode.py get`. On red, skip every non-essential nudge; on yellow, send the shortest version of the message.
- If a message reveals a crisis, the escalation rails in the skill take over immediately. Capacity mode never suppresses that.
- Any schedule can be paused by saying "pause the family check-in".
- Run them on a local model where possible (see `docs/models.md`): the check-ins
  are simple by design, so they cost nothing locally. Ask the agent to pin the
  job's model when it sets it up.

## When nobody answers: the zero-shame rule

A check-in that goes unanswered is information, not a failure. Three in a row is a signal to stop.

1. **Three consecutive unanswered check-ins** and this schedule goes quiet. No fourth attempt, no escalation, no summary of what was missed, no "I haven't heard from you".
2. Send **one** warm sign-off, then nothing more:

   > Going quiet so notifications don't pile up. Whenever you're ready, tomorrow or months from now, just send "reset" and we'll start fresh from today with zero backlog.

3. Record the pause with `python scripts/capacity_mode.py pause 168` so every other schedule sees the same state. Recurring nudges stay off until the family sends "reset" or asks for them again.

When they do come back, run `python scripts/reset_from_today.py`. It archives the old notes into `~/neurofamily/archive/YYYY-MM/` and starts from today. Never list what was missed, never count the days, never ask what happened.

A family that returns after four months is not behind. They are back.
