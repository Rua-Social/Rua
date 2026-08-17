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

## One window, four seats

The personal OS is one Grok window looking at this repo.

- **Window:** the Grok dashboard. Several named sessions, one screen.
- **State:** Git. If it is not a file, it is not the org.
- **Procedure:** a skill, when the work is a repeated method.
- **Parallel pass:** a workflow, when several independent readers
  should run at once and hand back one result.

That is multi-agent work *inside* Grok. It is not four APIs in one
chat.

Other models stay other seats. No OpenRouter. No routing service.

## What is actually live

No OpenRouter account. No OpenRouter key. So there is no way to put
Gemini, Claude, or Kimi *inside* Grok. Those names in the Grok picker
were stubs. They are gone.

What works is four separate seats you already logged into:

| Seat | What it is | Bill / login | Open it |
| --- | --- | --- | --- |
| Grok | Default conductor. Dashboard. Rua skills. Brains: `grok-4.6`, `grok-4.5`. | grok.com | `rua-desk grok` |
| Claude Code | Claude's own harness. Plugins, Claude memory. | Anthropic | `rua-desk claude` |
| Gemini CLI | Google's own harness. Drive / multimodal if you use them. | Google | `rua-desk gemini` |
| Codex | OpenAI harness in ChatGPT.app. Computer use. GPT-5.6. | ChatGPT | `rua-desk codex` |

`rua-desk grok` opens the dashboard. `rua-desk grok-one` opens a
single session if you want a quiet thread.

## Sit down

1. `rua-desk grok`
2. If the roster is empty, boot the rooms below once. Pin them.
3. Name the class before loading doctrine. See `AGENTS.md`.
4. Stay in Grok unless you need different hands, or a thread is
   already in flight on another seat.

```
rua-desk           # see what is installed
rua-desk grok      # one window
rua-desk grok-one  # one session
```

Keys in that window:

| Key | What it is |
| --- | --- |
| `Ctrl+\` | Dashboard roster. Peek, reply, dispatch, pin. |
| `Ctrl+G` | Tasks pane. Subagents under the session you are in. |
| `Ctrl+T` | Pin the selected room. |
| `Ctrl+R` | Rename the selected room. |
| `/desk-brief` | Parallel scan of the four repo rooms, then one brief. Studio and clients on grok-4.5; tools, Papa Rua, and the brief on grok-4.6. |
| `/workflows` | Watch a running workflow. |

## Rooms

These are named dashboard sessions, not an `agents/` directory.
Create them the first time by dispatching the seed, then rename and
pin. Reuse them. Do not open a fifth room because a new idea showed
up.

| Room | Seed on first boot | Use for |
| --- | --- | --- |
| `desk` | Read `20-studio/desk.md`. You are the conductor. Wait for a class. Do not invent work. | Sit-down, founder, systems, `/desk-brief` |
| `sales` | Read `20-studio/sales/README.md` and `00-system/templates/scope-of-work.md`. Do not start a delivery skill. | Scope, proposal, invoice, payment gate |
| `job` | Name the engagement. Read only `10-clients/<slug>/` for that engagement. | The one live client job |
| `tools` | Read `00-system/skills/rua-ship-gate/SKILL.md`. Software only. | Anything under `30-tools/` |
| `papa` | Read `40-papa-rua/README.md`. Do not invent a release. | Papa Rua |

One live `job` room. If there is no live engagement, leave it idle.
Do not keep a room per old client.

## Which lever

| Need | Lever | Not |
| --- | --- | --- |
| Talk through one class of work | The matching room | Four chats for the same job |
| Independent lookup while you keep talking | A subagent under that room | A new top-level session |
| Same parallel pass every sit-down | `/desk-brief` | A human reading four folders |
| Repeated method | A skill | A custom agent file |
| Another model's hands | Another seat | A `/model` stub |

A custom agent file is earned when a role needs its own tools or
prompt, not when you want a job title.

## Which seat for which Rua class

| Class | Seat | Why |
| --- | --- | --- |
| Founder / direction | Grok, `desk` room | Reads `20-studio/founder-context.md`. This note lives here. |
| Sales / scope | Grok `sales`, or Claude Code | Shared rules. Stay in the harness you opened. |
| Defined sprint | Grok `job` | `rua-shoot-plan` is wired here. |
| Pickup / execution | Grok `job`, or Codex | Scope of work only. Do not load the sprint skill. |
| Tool / software | Grok `tools` | `rua-ship-gate`. Approval before files. |
| Papa Rua | Grok `papa` | Separate from client delivery. |
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

No `agents/`, `orchestration/`, `models/`, or `pipelines/` directory
in this repo. No router service. No third-party method at the
repository root.

Grok workflows live under `.grok/workflows/`. That is the harness
adapter for a repeated parallel pass, not an org chart. The first
one is `desk-brief`. Add another when the same multi-agent handoff
is happening every week.

Until then this note is the desk.

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
