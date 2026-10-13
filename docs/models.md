# Models and voice

The ecosystem runs on whatever model the family points it at. This is the recommended setup: fast and cheap by default, local where it makes sense, and voice that works fully offline.

## The recommended tiering

| Tier | What runs there | Model | Why |
|---|---|---|---|
| Everyday | Family conversations, check-in replies, notes, planning | DeepSeek Flash via OpenRouter (the config default) | Fast, inexpensive, more than capable for warm practical support work |
| Complex | The occasional heavy job: an advocacy letter, a tangled support plan, a big monthly review | A frontier model via the same OpenRouter key (the agent can propose the switch; check the live catalogue for what is current) | Better reasoning for the jobs where it shows |
| Local | The scheduled check-ins, and everything, for families who want zero cloud | A small instruct model in LM Studio or Ollama | The check-ins are simple by design; they cost nothing and nothing leaves the machine |

## Running the schedules on a local model

The scheduled check-ins (daily anchors, weekly family check-in, and so on) are deliberately formulaic: read the family folder, write a short warm message. They are the perfect fit for a small local model.

- In Hermes, a cron job can carry its own model and provider. When a schedule is set up, pin it to the local model and leave conversations on the default.
- The agent can do this when creating the job, or the family can ask: "run the weekly check-in on the local model".
- Result: the part that runs unattended, around the clock, is private and free; the family's live conversations use the cloud model with full capability.

## Voice: local, in both directions

Voice matters for hands-full parents. Both directions can run entirely on the family's machine:

- **Listening (STT):** local `faster-whisper` transcribes incoming voice notes. A parent can send a rambling voice note at 7am; the team reads it faithfully.
- **Speaking (TTS):** local **Piper** (`pip install piper-tts`) renders spoken replies. Piper is free, private, runs on modest hardware, and Hermes can attach the audio straight into the chat: WhatsApp voice bubbles, Telegram audio, wherever the family lives.
- **Fully offline voice:** Piper plus faster-whisper plus a local model means the whole loop (hear, think, speak) can happen with no internet at all.

Setup pointers: enable voice in the profile's platform config and Hermes picks the STT/TTS providers above. The Hermes voice docs cover the exact switches; `hermes setup` walks through the provider choices.

## What this costs

- Everyday tier: fractions of a cent per message with DeepSeek Flash class models.
- Complex tier: pay per use, only when the family or the agent reaches for it.
- Local tier: free forever.
- Voice: free. Piper and faster-whisper are open source.

## Privacy line

Local model plus local voice plus no external connections means nothing about the family leaves the machine except what the family explicitly chooses to share. That is a legitimate, fully supported way to run the whole ecosystem.
