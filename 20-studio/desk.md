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

Other models stay other seats unless they have a real API
behind them. No OpenRouter. No routing service.

## What is actually live

Kimi is inside Grok via the Moonshot API. `/model kimi` is
`kimi-k2.6` (cheap). `/model kimi-code` is `kimi-k2.7-code`.
`/model kimi-k3` is the flagship ($3 / $15 per 1M, 1M context,
always thinks). Default stays `grok-4.6`.

Claude, Gemini, and Codex stay on their own logins. From a
new Grok session they can also be called as tools through
the `ai-cli` MCP (one window, no second API bill). Two
agents may work in parallel on different files. They must
not write the same file at the same time. Git is the handoff.

What works:

| Seat | What it is | Bill / login | Open it |
| --- | --- | --- | --- |
| Grok | Default conductor. Dashboard. Rua skills. Brains: `grok-4.6`, `grok-4.5`. Kimi via Moonshot. | grok.com + Moonshot API | `rua-desk grok` |
| Claude Code | Claude's own harness. Plugins, Claude memory. | Anthropic | `rua-desk claude` |
| Gemini CLI | Google's own harness. Multimodal if you use it. | Google | `rua-desk gemini` |
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
rua-desk ping      # each seat answers one line
```

Keys in that window:

| Key | What it is |
| --- | --- |
| `Ctrl+\` | Dashboard roster. Peek, reply, dispatch, pin. |
| `Ctrl+G` | Tasks pane. Subagents under the session you are in. |
| `Ctrl+T` | Pin the selected room. |
| `Ctrl+R` | Rename the selected room. |
| `/desk-brief` | Parallel scan of the four repo rooms, then one brief. Studio and clients on grok-4.5; tools, Papa Rua, and the brief on grok-4.6. Must run from `~/Rua`. Grok children cannot be Kimi. |
| `/workflows` | Watch a running workflow. |

## Rooms

These are named dashboard sessions, not an `agents/` directory.
Create them the first time by dispatching the seed, then rename and
pin. Reuse them. Do not open a room because a new idea showed up.

| Room | Seed on first boot | Use for |
| --- | --- | --- |
| `desk` | Read `20-studio/desk.md`. You are the conductor. Wait for a class. Do not invent work. | Sit-down, founder, systems, `/desk-brief` |
| `sales` | Read `20-studio/sales/README.md` and `00-system/templates/scope-of-work.md`. Do not start a delivery skill. | Scope, proposal, invoice, payment gate |
| `job` | Name the engagement. Read only `10-clients/<slug>/` for that engagement. | The one live client job |
| `tools` | Read `00-system/skills/rua-ship-gate/SKILL.md`. Software only. Code, session, and look. | Anything under `30-tools/` |
| `papa` | Read `40-papa-rua/README.md`. Do not invent a release. | Papa Rua |

One live `job` room. If there is no live engagement, leave it idle.
If two paid engagements are live at once, do not add a second
job room. Rename and reseed this one to the slug you are sitting
on. Park the other in Git. Do not keep a room per old client.

## Which lever

| Need | Lever | Not |
| --- | --- | --- |
| Talk through one class of work | The matching room | Four chats for the same job |
| Independent lookup while you keep talking | A subagent under that room | A new top-level session |
| Cheap extract on Moonshot | `kimi` MCP tool `kimi_run` (or `/model kimi`) | `spawn_subagent` / workflow `model=kimi` — Grok rejects those slugs. Fake `kimi` agent types just run grok-4.6 |
| Hostile / long-context on Moonshot | `kimi_run` with model `kimi-k3` | Making K3 the default |
| Same parallel pass every sit-down | `/desk-brief` from a session in `~/Rua` | Launching it from `$HOME` |
| Second opinion from Claude / Gemini / Codex | `ai-cli` MCP tools. See Codex slugs below. | Opening a second terminal for a one-line review |
| Repeated method | A skill | A custom agent file |
| Another model's full harness | Another seat (`rua-desk claude` etc.) | A `/model` stub |

A custom agent file is earned when a role needs its own tools or
prompt, not when you want a job title.

The conductor stays Grok. The other seats are unused if you never
call them. Pull a seat when the job matches. Do not pull all four
for courtesy, and do not skip them to keep the chat tidy.

- Long extract or first read of a fat file or folder: `kimi_run`
  (`kimi`, or `kimi-code` if the material is `30-tools/`).
- Hostile or 1M-context read: `kimi_run` with `kimi-k3`.
- Second opinion on a ship or a judgement call: `ai-cli` Claude
  or Codex. Do not pass `gpt-5.3-codex`.

Codex via `ai-cli`, tried 17 Aug on desk-bridge (same short
review prompt):

| Slug | Effort | Result |
| --- | --- | --- |
| `gpt-5.4-mini` | low | Finished ~1 min. Thin. `--yolo` + tests only. |
| `gpt-5.5` | medium | Finished ~2 min. Pairing, `--yolo`, silent drop. |
| `gpt-5.6-luna` | low | Finished ~2 min. Same plus group-chat / no `chat.type` check. Use this for a fast 5.6 pass. |
| `gpt-5.6-terra` | low | Finished ~2 min. Same core; missed groups; named spec vs session-file tension. |
| `gpt-5.6-sol` | default | Hung 5+ min after reading. Killed. Do not use Sol for this. |
- Mail, calendar, Drive: Grok built-in connectors. Sign in once at
  grok.com/connectors. Do not use the local Google MCP servers.
- Multimodal: Gemini CLI, or `ai-cli` Gemini for a one-shot.
- Phone: never Kimi, never a four-seat fan-out.

Kimi is a reader. `kimi_run` cannot write files. That is the point.
The false start was routing (OpenRouter, `model=kimi` children),
not the model. Do not rule Kimi out. Do not make K3 the default.

## Which seat for which Rua class

| Class | Seat | Why |
| --- | --- | --- |
| Founder / direction | Grok, `desk` room | Reads `20-studio/founder-context.md`. This note lives here. |
| Sales / scope | Grok `sales`, or Claude Code | Shared rules. Stay in the harness you opened. |
| Defined sprint | Grok `job` | `rua-shoot-plan` is wired here. |
| Pickup / execution | Grok `job`, or Codex | Scope of work only. Do not load the sprint skill. |
| Tool / software | Grok `tools` | `rua-ship-gate`. Approval before files. Session and look live here too. |
| Papa Rua | Grok `papa` | Separate from client delivery. |
| Claude-only memory or Claude plugins | Claude Code | Different hands, not a Grok `/model` switch. |
| Gemini-only account, multimodal CLI | Gemini CLI | Different hands. |
| Computer use / a Codex thread already in flight | Codex | Finish it there. Resume with the resume-codex skill. |

## Handoff

The bus is Git and files, not a chat export.

- One job, one working tree. Parallel work on different files is
  fine. Concurrent writes to the same file are not. Commit or park
  before another agent touches those paths.
- When you change seats, say what class the job is and point at the
  files that matter. The next harness will read `AGENTS.md` itself.
- To continue a foreign session from Grok: `resume-claude`,
  `resume-codex`, `resume-cursor`.
- Claude and Gemini both load `AGENTS.md`. Claude also has `CLAUDE.md`.
  Gemini also has `GEMINI.md`. Those two files are adapters, not a
  second rulebook.

## Kimi is inside Grok. OpenRouter is not set up

Kimi is a Moonshot API model on this machine. `/model kimi` and
`/model kimi-code` are live. The key is `MOONSHOT_API_KEY`, not
in Git.

OpenRouter is still not set up. Do not add Claude or GPT as Grok
`/model` entries unless there is an API key for that vendor and a
reason the official CLI is not enough.

## What we are not building

No `agents/`, `orchestration/`, `models/`, or `pipelines/` directory
in this repo. No router service. No third-party method at the
repository root.

Grok workflows live under `.grok/workflows/`. That is the harness
adapter for a repeated parallel pass, not an org chart. The first
one is `desk-brief`. Add another when the same multi-agent handoff
is happening every week.

Until then this note is the desk.

## On the phone

Telegram bot `@Rua_desk_bot` is the same desk, reached while away.
The process lives on this Mac: `30-tools/desk-bridge/`.
It is a seat, not a fifth room and not a new agent file.

How the phone behaves is `30-tools/desk-bridge/EXPERIENCE.md`.
This chat is a phone, not a studio log.

- Work silently. Class, doctrine, and file-hunting stay off-screen.
- Send one short result: what happened, where it is, what they need.
- Short paragraphs. No markdown tables. No file trees. No "Loading…".
- If you send a file, say it is in the chat. Do not recap the job.
- Voice notes are inbound. They are transcribed, then treated as the ask.
- Phone Grok runs at medium effort. Studio stays on the dashboard setting.
- Do not install the official Telegram plugin. This seat is desk-bridge.
- Lists live in `20-studio/lists.md`. Desk list and founder list. If
  something is blocked, write it there. Do not invent a tracker.

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
