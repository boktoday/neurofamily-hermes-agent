# Starter artifacts

Ready-made tools the Artifacts Generator can personalise and deliver. Family-safe: everything here runs locally or in the family's own accounts.

| Artifact | What it is | Best for |
|---|---|---|
| `food-diary.html` | Fillable local diary: safe-food map, meal entries, stress notes, CSV export, print | Food Support families, ARFID tracking, showing patterns to a dietitian |
| `food-diary-sheets.md` | The same diary as a Google Sheet / Excel workbook (spec + formulas) | Families with connections set up; multi-carer households |
| `lesson-chunks.html` | Local-first lesson planner: paste or dictate a lesson, AI breaks it into small sequential steps + a motivating overview. Text-to-speech, mark-complete, rich-text editor per step, AI feedback, saved Q&A history | Autistic young people and executive-function support: turning schoolwork, therapy material or daily tasks into manageable steps |
| `iep-companion.html` | The school's plan as an interactive companion: goals in plain words, sparks and badges, kid-friendly themes, meeting questions, words to know, attendance check-ins, print view | Every IEP/EHCP family; preparing for reviews; helping the child understand their own plan |

## How to deliver one

1. Open the file, personalise it for the family (names, colours, the child's own words).
2. Send the file into the chat, or paste it as a page if the family uses a sharing space.
3. Explain the three things that matter: how it saves, how to export, when to use it.
4. Offer to review it with them after two weeks. A tool that is not reviewed becomes clutter.

## Instructions: `lesson-chunks.html`

**What it does.** You paste (or dictate, in Chrome/Edge) a lesson plan — one paragraph or a whole page. It uses an LLM (via OpenRouter, your own key) to produce a short encouraging overview and break the material into the smallest sequential steps. The student works through the steps one at a time: mark a step complete, listen to it read aloud, expand any step to write a response in the built-in editor, get AI feedback on the response, and ask follow-up questions that are saved to history.

**Runs locally.** One self-contained file — no install, no account, no cloud storage. Open it with a double-click in any browser (Chrome, Edge, Firefox). All lessons and settings save in the browser's own storage on that computer. To move to another device, open the file there and re-enter content, or use **Copy** in the lesson view to export the overview + steps as Markdown.

**First-time setup (one minute).**

1. Open the file. Go to **Settings** (top right).
2. Optional: add the student's name, bio and learning style — this personalises how the steps are written.
3. Add an **OpenRouter API key** (free account at openrouter.ai/keys; cheap or free models work). This is the only thing that needs the internet — it sends the lesson text to the AI to chunk it, plus your questions.
4. Pick a preferred model if you like (the default works fine). **Save Settings.**

**Daily use.**

1. **Home:** type or dictate the lesson plan (dictation needs Chrome/Edge and a mic). Title is optional.
2. Click **Chunk Lesson**. Wait a few seconds. You get an Overview plus numbered steps.
3. Guide the student through the steps: speaker icon reads a step aloud, check circle marks it done, chevron expands a step for writing + feedback, **Copy** exports the whole lesson as Markdown.
4. Ask questions in **Ask a Question** below the steps — answers are saved.
5. **Lessons** lists everything saved, **History** searches past Q&A by date.

**Privacy note.** The lesson content you paste is sent to the OpenRouter model only when you click Chunk Lesson or ask a question. Everything else — saved lessons, settings, history — stays on the device in the browser. Don't paste anything more sensitive than you would put in a school email.

## Contributing

New artifacts belong here when they are: local or family-account-only, one file wherever possible, printable, and useful to families beyond the one they were built for. First-then boards, feelings ladders and week planners are welcome additions.
