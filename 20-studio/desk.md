# The Rua desk

How the founder sits down and works with more than one model.
This is a studio operating note, not doctrine and not a product.

You were not dreaming. You do not need a new orchestration layer.
You already have the pieces. The hub is this repo.

## Two layers people mix up

**Model** is the brain. Grok 4.6, Kimi, Gemini, Claude, GPT.

**Harness** is the hands. Grok Build, Claude Code, Gemini CLI, Codex.
Each harness has its own tools, memory, login, and bill.

VS Code can host a chat panel or a terminal. It does not become the
coordinator just because four models are installed. The coordinator is
the repository: `AGENTS.md`, the right skill, and files on disk.

## What is actually live

No OpenRouter account. No OpenRouter key. So there is no way to put
Gemini, Claude, or Kimi *inside* Grok. Those names in the Grok picker
were stubs. They are gone.

What works is four separate seats you already logged into:

| Seat | What it is | Bill / login | Open it |
| --- | --- | --- | --- |
| Grok | Default conductor. Rua skills. Brains: `grok-4.6`, `grok-4.5`. | grok.com | `rua-desk grok` |
| Claude Code | Claude's own harness. Plugins, Claude memory. | Anthropic | `rua-desk claude` |
| Gemini CLI | Google's own harness. Drive / multimodal if you use them. | Google | `rua-desk gemini` |
| Codex | OpenAI harness in ChatGPT.app. Computer use. GPT-5.6. | ChatGPT | `rua-desk codex` |

That is multi-model work. It is four harnesses on one repo, not one
chat window routing four APIs.

## Sit down

1. Open this repo.
2. Name the class before loading doctrine. See `AGENTS.md`.
3. Pick **one** harness. Do not open four chats for the same job.
4. Change seats only when you need different hands, or when a thread
   is already in flight on another seat.

```
rua-desk           # see what is installed
rua-desk grok      # default seat
```

## Which seat for which Rua class

| Class | Seat | Why |
| --- | --- | --- |
| Founder / direction | Grok | Reads `20-studio/founder-context.md`. This note lives here. |
| Sales / scope | Grok or Claude Code | Shared rules. Stay in the harness you opened. |
| Defined sprint | Grok | `rua-shoot-plan` is wired here. |
| Pickup / execution | Grok or Codex | Scope of work only. Do not load the sprint skill. |
| Tool / software | Grok | `rua-ship-gate`. Approval before files. |
| Claude-only memory or Claude plugins | Claude Code | Different hands, not a Grok `/model` switch. |
| Gemini-only account, Drive, multimodal CLI | Gemini CLI | Different hands. |
| Computer use / a Codex thread already in flight | Codex | Finish it there. Resume with the resume-codex skill. |

## Handoff

The bus is Git and files, not a chat export.

- One job, one working tree. Do not let two harnesses edit the same
  files at the same time.
- When you change seats, say what class the job is and point at the
  files that matter. The next harness will read `AGENTS.md` itself.
- To continue a foreign session from Grok: `resume-claude`,
  `resume-codex`, `resume-cursor`.
- Claude and Gemini both load `AGENTS.md`. Claude also has `CLAUDE.md`.
  Gemini also has `GEMINI.md`. Those two files are adapters, not a
  second rulebook.

## OpenRouter is optional and not set up

OpenRouter is a paid gateway. One key, many brains, so Grok could
`/model` to Kimi, Gemini, or Claude without leaving the TUI.

That is not free and it is not configured. Do not add those models
back until there is an OpenRouter account, a key in
`OPENROUTER_API_KEY`, and a reason the separate CLIs are not enough.

Until then, ignore any advice that says "switch to Kimi inside Grok."

## What we are not building

No `agents/`, `orchestration/`, `models/`, or `pipelines/` directory.
No router service. No third-party method at the repository root.

If the same handoff starts repeating every week, that is when a skill
or a small tool is earned. Until then this note is the desk.

## Optional: VS Code as the file surface

VS Code is not installed on this machine. It is a good editor. It is
not required for multi-model work.

If you want the GUI later:

```
brew install --cask visual-studio-code
```

Then open this repo and use the integrated terminal as extra seats
(`rua-desk grok`, `rua-desk claude`, and so on). A community Grok
Build extension exists for in-editor chat. That is a skin on the same
CLI, not a new coordinator.
