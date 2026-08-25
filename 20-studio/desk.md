# The Rua desk

How the founder sits down and works with more than one model.
This is a studio operating note, not doctrine and not a product.

You were not dreaming. You do not need a new orchestration layer.
You already have the pieces. The hub is this repo.

## Two layers people mix up

**Model** is the brain. Grok 4.6, Kimi, Gemini, Claude, GPT.

**Harness** is the hands. Grok Build, Claude Code, Gemini CLI, Codex,
Kimi Code. Each harness has its own tools, memory, login, and bill.
(Kimi Code was missing from this list while it ran the 18 Aug hostile
review. Fixed in that sitting.)

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
| `desk` | Read `20-studio/desk.md`. You are the conductor. Wait for a class. Do not invent work. | Sit-down, founder, systems, `/desk-brief`, board |
| `sales` | Read `20-studio/sales/README.md` and `00-system/templates/scope-of-work.md`. Do not start a delivery skill. | Scope, proposal, invoice, payment gate |
| `job` | Name the engagement. Read only `10-clients/<slug>/` for that engagement. | The one live client job |
| `tools` | Read `00-system/skills/rua-ship-gate/SKILL.md`. Software only. Code, session, and look. | Anything under `30-tools/` |
| `papa` | Read `40-papa-rua/README.md`. Do not invent a release. | Papa Rua |

One live `job` room. If there is no live engagement, leave it idle.
If two paid engagements are live at once, do not add a second
job room. Rename and reseed this one to the slug you are sitting
on. Park the other in Git. Do not keep a room per old client.

## Kimi: do not repeat 17 August

`kimi_run` is a 240-second reader cage. The 17 August timeout was
that cage, not the weights.

- Short extract, first read, or a parallel review: `kimi_run` + `kimi`.
- Do not put `kimi-code` through `kimi_run`.
- Do not put `kimi-k3` through `kimi_run` for a short review. K3
  is `/model kimi-k3` in a look room. A child K3 is only for a
  1M-context read that can afford the cage.

Repeated 18 August on the Telegram CoS panel: conductor called
`kimi_run` + `kimi-k3` for a short blind review. It timed out.
The cheap `kimi` pass finished. Do not do this a third time.

## Which lever

| Need | Lever | Not |
| --- | --- | --- |
| Talk through one class of work | The matching room | Four chats for the same job |
| Independent lookup while you keep talking | A subagent under that room | A new top-level session |
| Cheap extract on Moonshot | `kimi` MCP tool `kimi_run` (or `/model kimi`) | `spawn_subagent` / workflow `model=kimi` — Grok rejects those slugs. Fake `kimi` agent types just run grok-4.6 |
| Coding review or Moonshot write | `/model kimi-code` in `tools` (full Grok hands) | `kimi_run` with `kimi-code` (reader cage, 240s). Grok calling Claude Code pointed at Moonshot |
| Architecture review, hostile or 1M read | `/model kimi-k3` in a named look room. Not `kimi_run` + K3 for a short review (17 Aug cage; repeated 18 Aug) | Making K3 the default conductor; `kimi_run` + `kimi-k3` as a courtesy child |
| Should we do this | The board, in this room. Owner, hostile, class. | A `boardroom` room, named advisors, `/desk-brief` |
| Same parallel pass every sit-down | `/desk-brief` from a session in `~/Rua` | Launching it from `$HOME` |
| Second opinion from Claude / Gemini / Codex | `ai-cli` with the slugs that worked, below | Opening a second terminal for a one-line review |
| Repeated method | A skill | A custom agent file |
| Another model's full harness | Another seat (`rua-desk claude` etc.) | A `/model` stub |

### Board

A founder decision, not a sit-down scan. `/desk-brief` is "what is
on." The board is "should we do this."

Three seats. Roles, not characters. Do not pin a `boardroom` room.

| Seat | Who | What they must do |
| --- | --- | --- |
| Owner | This room, `20-studio/founder-context.md` | Time, economics, craft overlap, small load. What you are actually optimising for. |
| Hostile | `/model kimi-k3` in a look room, or `ai-cli` `opus` | Attack the plan. One concrete risk. Not cheerleading. |
| Class | The room that would have to change: `tools`, `sales`, `job`, or `papa` | What the files actually say. What would have to land in Git. |

They must disagree. Unanimous is a failed session. Each seat cites a
file. Output is the path, what you are not doing, and GO / NO-GO /
CONDITIONAL. You hold the pen.

In this room:

```
Convene the board on: [one sentence].
Owner from founder-context.md. Hostile as K3. Class is [tools / sales / job / papa].
They must disagree. Cite files. I decide.
```

If that handoff starts happening every week, add a `/board` workflow
next to `/desk-brief`. Not before.

A custom agent file is earned when a role needs its own tools or
prompt, not when you want a job title.

The conductor stays Grok. The other seats are unused if you never
call them. Pull a seat when the job matches. Do not pull all four
for courtesy, and do not skip them to keep the chat tidy.

- Long extract or first read of a fat file or folder: `kimi_run`
  with `kimi`. `kimi_run` stays a reader (no write). Do not put
  `kimi-code` through `kimi_run` (240s cage, 17 Aug).
- Coding review and Moonshot builds: `/model kimi-code` in `tools`.
  Full hands. That is the job K2.7 Code is for. 18 Aug one-shot
  (`html-to-pdf --print-chrome`) shipped in 142s, 17 tests green.
  `ai-cli` `sonnet` is still the faster writer if you need speed.
- Architecture review: `/model kimi-k3` in a look room, not in
  `desk`. K3 is the long-context / hostile brain. Review first.
  Writes only after the founder keeps a finding.
- A short child review is `kimi_run` + `kimi`. `kimi_run` + K3 is
  only for a 1M-context read that can afford the 240s cage. A
  parallel CoS / desk review is not that. (17 Aug; repeated 18 Aug.)
- Second opinion on a ship or a judgement call: `ai-cli` with the
  slugs that worked, below. Do not pass `gpt-5.3-codex`.
- Never: Grok calling Claude Code with a Moonshot env. That nest
  hijacks `rua-desk claude` or adds a third conductor. Untested
  because both writers already work without it.

Claude and Gemini via `ai-cli`, tried 17 Aug on desk-bridge.
`ai-cli` is a Grok MCP (`npx ai-cli-mcp@latest`, enabled in
`~/.grok/config.toml`, checked 18 Aug), not a shell command. It wraps
the local `claude`, `gemini`, and `codex` CLIs. The slug table below
was last tried 17 Aug: after any CLI update, re-run one cheap slug
before relying on a row. Use the live aliases. There is no current
Haiku 4.6 id.

| Slug | Result |
| --- | --- |
| `haiku` | Live Haiku (4.5). Fast. Keep using this. |
| `sonnet` | Live Sonnet (5). Fast judgement. Keep. |
| `opus` | Live Opus. Same family the founder likes. Keep. |
| `gemini-3-flash-preview` | Fast Gemini that finished. Keep. |
| `gemini-2.5-flash` | Failed twice (empty / exit 1). Do not use. |

Codex via `ai-cli`, tried 17 Aug on desk-bridge (same short
review prompt):

| Slug | Effort | Result |
| --- | --- | --- |
| `gpt-5.4-mini` | low | Finished ~1 min. Thin. `--yolo` + tests only. |
| `gpt-5.5` | medium | Finished ~2 min. Pairing, `--yolo`, silent drop. |
| `gpt-5.6-luna` | low | Finished ~2 min. Same plus group-chat / no `chat.type` check. Use this for a fast 5.6 pass. |
| `gpt-5.6-terra` | low | Finished ~2 min. Same core; missed groups; named spec vs session-file tension. |
| `gpt-5.6-sol` | default | Hung 5+ min after reading. Killed. Do not use Sol for this. |
- Mail, calendar, Drive: Grok built-in connectors on the dashboard
  TUI (grok.com/connectors). Phone `grok -p` gets the same tools via
  managed gateway env. Google's remote MCP servers are not the path:
  `/mcps` `i` hangs. Not Mail.app. Not a local mail CLI.
- Multimodal: Gemini CLI, or `ai-cli` Gemini for a one-shot.
- Phone: never Kimi, never a four-seat fan-out.

`kimi_run` is a reader. That is still the point of the MCP.
`/model kimi-code` can write. The 17 Aug timeout was the cage, not
the weights. Do not rule Kimi out. Do not make K3 the default.
Do not put Kimi inside Claude Code for Grok to call.

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
repository root. No `boardroom` room: the board is three seats in
`desk`, not a sixth pin.

Grok workflows live under `.grok/workflows/`. That is the harness
adapter for a repeated parallel pass, not an org chart. The first
one is `desk-brief`. Add another when the same multi-agent handoff
is happening every week. A `/board` workflow waits for that.

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
- Open actions live in `20-studio/todo.md`. Closed lines in
  `todo-done.md`. Skill: `00-system/skills/rua-todo/`. `/brief` and
  `/todo` read only that file. If the phone is blocked, write it
  under Desk → Blocked in `lists.md`. That file is the diary, not
  the todo.
- Real mail and calendar live in Google Workspace (Gmail, Google
  Calendar), signed in as `darragh@ruasocial.ie`. Mac Mail.app and
  Calendar.app are unused. Do not open them, or icalBuddy, or a
  local mail CLI. Dashboard Grok reaches Workspace via grok.com
  connectors. Phone `grok -p` uses the same connectors (managed
  gateway env). Answer from `10-clients/` and `todo.md` first. If
  those are silent, use the Google tools. Never dump the parked-Google
  sentence. Do not send them to `/mcps`.

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
