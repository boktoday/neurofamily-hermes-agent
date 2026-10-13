# Schedules

Ready-to-install check-ins for real family life. Each schedule names the skill that runs it and the exact prompt to use. Families opt in; nothing is scheduled automatically.

| Schedule | Default rhythm | Skill |
|---|---|---|
| Daily routine anchors | Weekday mornings, 7:00 | Routine Architect |
| Weekly family check-in | Sunday, 18:00 | Family Navigator |
| Carer wellbeing check-in | Wednesday, 20:00 | Parent Companion |
| Sibling check-in | Fortnightly, Saturday morning | Sibling Support |
| Monthly ecosystem review | First Sunday, 19:00 | Family Navigator |

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
- Skip gracefully: if the family has not engaged in a while, one gentle message, then wait. Schedules serve the family, not the other way around.
- If a message reveals a crisis, the escalation rails in the skill take over immediately.
- Any schedule can be paused by saying "pause the family check-in".
