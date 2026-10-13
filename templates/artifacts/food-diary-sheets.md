# Food diary: the Google Sheets / Excel version

For families with connections set up (`docs/connections.md`), the Artifacts Generator can build the diary as a spreadsheet the whole family can fill from their phones.

## Sheet spec

Name: "Food Diary" (one per child if needed). Tab 1 "Log":

| Column | Type | Notes |
|---|---|---|
| A Date | date | One row per meal or snack |
| B Meal | text | Breakfast / Lunch / Dinner / Snack / Drink |
| C Foods | text | What was eaten or offered |
| D Amount | text | "most of it", "few bites", "none" |
| E Status | text | Safe / New / Refused |
| F Stress | 1-10 | Mealtime stress |
| G Context | text | Who was there, where, anything unusual |

Tab 2 "Summary" (formulas, so it updates itself):

- Count of New foods per week: `=COUNTIFS(Log!E:E,"New",Log!A:A,">="&TODAY()-7)`
- Refusals this week: `=COUNTIFS(Log!E:E,"Refused",Log!A:A,">="&TODAY()-7)`
- Average stress this week: `=IFERROR(AVERAGEIFS(Log!F:F,Log!A:A,">="&TODAY()-7),"")`
- A safe-foods list pasted in below, maintained by the family.

## Creating it

The Artifacts Generator creates the sheet with the family's approval (creating a file is a write; see the connections rules). It then shares the link with the family and notes the file in `~/neurofamily/connections.md`.

## Weekly summary flow

The Food Support skill reads the log when the family asks for the weekly summary, and drafts it in the format already in that skill. Sharing with a dietitian or GP: export CSV or print from the summary tab, and offer the family the wording for what to say ("these are patterns we have noticed, not a diagnosis").

## Offline alternative

No connections? Use `food-diary.html` beside this file: same fields, saves in the browser, exports CSV and prints.
