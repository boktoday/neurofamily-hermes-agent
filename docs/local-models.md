# Choosing a local model

Part of the ecosystem runs best on your own machine: the scheduled check-ins, the quiet background jobs, and everything, for families who want nothing leaving the house. This guide helps you pick a model your computer can actually run.

**First stop: [canirun.ai](https://canirun.ai).** It reads your GPU or Mac straight from the browser, ranks the open models that fit your machine, and hands you the exact Ollama or LM Studio command to run the one you choose. No account, no install.

Two more worth knowing:

- [localllm-advisor.com](https://localllm-advisor.com) works both directions: best models for your hardware, or best hardware for a model you have your eye on. Fully client-side and private.
- [localllm.run](https://localllm.run) walks you through goal, hardware, model and setup in order, with guides for agent use.

## What agent work asks of a model

Our agents run tools: they read files, write artifacts, draft messages, keep schedules. That puts three demands on a local model:

1. **Tool calling.** The model must support function calling, or the agent cannot do its job. This matters more than raw size: a 14B model with solid tool calling beats a 32B model without it.
2. **Instruction following.** The profile rules (declarative language, no-pressure food support, the never lists) only hold if the model actually follows instructions.
3. **Enough context.** The agent reads the family folder. Look for 32k context or more.

The picks below all support tool calling. Newer models arrive constantly, so treat this as a starting shortlist and let the checkers above rank whatever is current.

## The tiers

| Your machine | Start with (Ollama tag) | Also good |
|---|---|---|
| Modest laptop, 8 to 16 GB RAM, no dedicated GPU | `qwen3:8b` | `llama3.2:3b` on 8 GB machines |
| Capable machine, 16 to 32 GB RAM or 8 to 12 GB VRAM | `qwen3:14b` | `phi4:14b` |
| Strong machine, 32 GB+ RAM or 16 to 24 GB VRAM | `gpt-oss:20b` | `qwen3:30b-a3b` |
| Workstation, 64 GB+ RAM or 24 GB+ VRAM | `llama3.3:70b` | `gpt-oss:120b` |

Every tag above runs in both Ollama and LM Studio (they are GGUF models under the hood). Mixture-of-experts models like `gpt-oss:20b` are fast for their size but still load all their weights, so trust the checkers on memory, not the parameter count.

## Getting one running

1. **Install the engine.** [Ollama](https://ollama.com) (one installer, one command per model) or [LM Studio](https://lmstudio.ai) (graphical, good for browsing). Pull or download a tag from the table.
2. **Point the agent at it.** Both engines serve an OpenAI-compatible endpoint on the same machine: Ollama at `http://localhost:11434/v1`, LM Studio at `http://localhost:1234/v1`. Set the provider in `hermes setup` or the profile's config, and check the [Hermes docs](https://hermes-agent.nousresearch.com/docs) for the exact keys in your version.
3. **Try it on one job.** Run a single scheduled check-in or a short conversation on the local model first. Keep the everyday conversations on the default model if you like, and mix freely: Hermes can run each scheduled job on its own model.

## Which jobs suit a local model

- **Great fit, and the place to start: the repetitive work.** Cron jobs, scheduled check-ins, daily anchors, short warm replies, folder reading and note taking. Small, frequent and the same every day, which is exactly what a local model is for.
- **Better on a bigger model:** advocacy letters, tangled support plans, big monthly reviews. A frontier model reached for occasionally is the pragmatic mix.
- **The all-local setup:** a capable machine plus a good local model plus local voice (Piper and faster-whisper, see [models.md](models.md)) means the whole loop runs with nothing leaving the house.

## Power tools, for the technically curious

- **whichllm** (`uvx whichllm`) ranks models from live Hugging Face data, weighted by real benchmarks rather than size. [github.com/Andyyyy64/whichllm](https://github.com/Andyyyy64/whichllm)
- **llm-checker** (`npx llm-checker hw-detect`) detects hardware, scores models, and can even test a model's tool-calling compatibility. [github.com/rumplestilzken/llm-checker](https://github.com/rumplestilzken/llm-checker)
- **llmfit** detects your specs and recommends fits with quantisation and speed estimates. [github.com/AlexsJones/llmfit](https://github.com/AlexsJones/llmfit)
