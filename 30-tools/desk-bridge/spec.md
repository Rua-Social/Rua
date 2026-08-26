# desk-bridge

## Goal

A Telegram DM is a seat at the Rua desk. A process on this Mac hands
each message to the selected engine in `~/Rua` and sends one short phone reply back.
The seat is owner-locked, preserves completed replies across transient
Telegram failures, and fails quickly when Grok has not started responding.

Voice notes are inbound only: download the Telegram file, transcribe
with ElevenLabs Scribe v2, then run the same desk path as text.

How the phone session behaves is `EXPERIENCE.md`. This file does not
restate it. If they conflict, fix the one that is wrong, then the other.

## Out of scope

Slack. Cloud hosting. Spoken replies (TTS). Image ingest. Video notes.
The official Claude/Grok Telegram plugin. A custom agent file.
Opening the bot to anyone else. Changing studio reasoning effort.
Google remote MCP OAuth (`/mcps` `i`). Re-enabling the disabled
local `gmail` / `calendar` / `drive` MCP servers. Claude-for-Google.
Mail.app, Calendar.app, or a browser as a stand-in for Gmail,
Calendar, or Drive.
A custom agent or phone plugin profile. A persistent Grok leader.
Direct model API calls. Cost or quality routing. Retrying a request on
another engine after any tool has run. Cross-engine session history. A
new dependency, host, service, or chat surface. Changing Telegram's look.

## Done

- `python3 30-tools/desk-bridge/bridge.py --check` talks to Telegram
  and finds `grok`.
- Only a private DM from the preconfigured Telegram user is answered.
  Groups are ignored. A blank owner id prevents startup; the first
  person to find the bot can never claim it.
- Secrets stay in `~/.grok/secrets/`, not Git.
- Secret and state directories are owner-only (`0700`); secret,
  state, metric, outbox, and log files are owner-only (`0600`).
- `/park` and `/idea` (and the same words on a voice note) capture
  without Grok. Park is a list bullet. A long idea also writes
  `20-studio/ideas/`.
- `/brief` returns a ranked pocket brief from `20-studio/todo.md`
  plus one live client card from `10-clients/*/README.md`; the same
  brief is appended to a Google miss reply. Do is ranked from all
  open lines. A STALE badge does not demote a gated chase behind a
  fresh sit-down line. They do not read `lists.md`. They do not open
  Mail.app, Calendar.app, or Drive.
- `/todo` returns the open list from `20-studio/todo.md`. Cap 7.
  Prints the action text, not the ISO date. STALE prefix when stale.
  Empty is "Nothing open." Full is "Todo is full. Close one." then
  the list, then "Text the action to close it."
- After a real desk ask (not `/park`, `/idea`, `/brief`, `/todo`,
  or `/status`), at most two `LIST+ Heading | line`
  trailers in the Grok reply are stripped from Telegram. `Do` appends
  once to `todo.md`. `Done` moves a matching open line to
  `todo-done.md`. Moving and Blocked stay on the `lists.md` diary.
  Junk refuses on add and on close, duplicates are skipped, and a full
  list refuses. Every refused `Do` or `Done` adds one plain line to the
  reply: "Already on the list.", "Todo is full. Close one.", or
  "Not a todo line." A voice-originated ask never closes the list: its
  `Done` is refused with "Voice can't close the list. Text it if it
  landed." Grok does not edit those files. No second model call.
- `/new` drops the session and any queued asks. Control commands do
  not wait behind Grok.
- `/engine auto|claude|codex|grok` is owner-only through the existing DM
  pairing, runs locally without a model, and persists the selected mode in
  owner-only state rather than rewriting secrets. A valid switch drops the
  session and queued asks with the same cut-line behavior as `/new`, clears
  engine cooldown state, and replies `Engine set to <engine>. Next message
  starts fresh.` Bare or invalid input returns `Use /engine
  auto|claude|codex|grok` without changing state. `/new` does not change the
  selected mode, and `/status` reports the persisted override.
- A live text from the phone gets a real desk reply.
- A voice note from the paired user is transcribed and answered.
- The phone gets the last assistant text after the last tool, not the
  studio log. Reaction + typing are best effort and never delay Grok.
- The poller remains live while one engine worker handles asks in order.
  A second ask receives the queue sentence in `EXPERIENCE.md`.
- Phone runs Grok (`grok -p`), Claude Code (`claude -p`), or Codex
  (`codex exec`) from `DESK_ENGINE` in the desk-bridge secrets file.
  `DESK_ENGINE=auto` tries the configured `DESK_ENGINE_ORDER`; default
  order is Claude, Codex, Grok. Claude and Codex use their unattended
  modes because the launchd job cannot click allow.
- Auto mode falls through only when an engine is missing, unauthenticated,
  at capacity, rate-limited, or out of usage before any tool event. It
  never reruns an ask on another engine after a tool event. A working
  fallback stays active for an hour before the preferred engine is probed
  again. Engine state contains no prompt text.
- The switch reply starts with `Using <engine> — <failed engine> hit its
  limit.` If every configured engine is unavailable, the reply is `All
  desk engines are unavailable. /status`. `/status` shows configured mode,
  active engine, and engines cooling down.
- The phone engine runs at effective medium effort. Missing, over the history
  byte cap, or wrong-effort sessions start fresh and say so. A large
  prompt-token total from MCP tools does not reset the next ask.
- Engine output is parsed while it runs. No first meaningful event within 60 seconds
  uses the provider-busy sentence. Idle work and the whole ask have
  separate deadlines; the total phone budget is five minutes and ten turns.
- Completed replies enter an owner-only outbox before Telegram delivery.
  Delivery retries never rerun Grok or duplicate its side effects.
  Delivery itself is at-least-once: a process death in Telegram's narrow
  send/checkpoint gap can repeat a reply chunk. A dedicated sender keeps
  Telegram delivery latency off the poller and sole engine worker.
- Privacy-safe JSONL metrics cover pickup, acknowledgement, voice,
  engine first event and finish, effective model/effort, usage, delivery,
  and failure stage without storing the prompt.
- While installed, the job prevents idle system sleep.
- Install verifies the replacement launchd job and restores the prior plist
  on failure. A singleton runtime lock prevents concurrent bridges, and
  shutdown terminates the active Grok process group.
- Phone `grok -p` sets `GROK_MANAGED_MCP_GATEWAY_TOOLS_ENABLED=1`
  and `GROK_MANAGED_MCPS_ENABLED=1` so it has the same grok.com
  Gmail, Calendar, and Drive tools as the dashboard TUI. Google's
  remote MCP servers (`gmailmcp.googleapis.com` and kin) are not
  this seat's login: `/mcps` `i` does not complete their OAuth. It
  also loads `~/.grok/secrets/xpoz.env` and `moonshot.env` so
  dashboard MCP keys exist in the launchd child.
- A Telegram `getUpdates` idle timeout is not written to `last_error`.
  `/status` keeps the last real desk miss. If Grok hits the turn
  limit after producing text, that text is sent.
  An explicit live mail, calendar, or Drive lookup is a desk ask like
  any other: the instance card and `todo.md` answer first. When the
  files are silent, Grok uses the Google tools if this process has
  them, and replies with the short result. It does not emit
  "Google isn't on this phone seat." If the tools are missing it
  replies "Google tools are not on this process." It does not send
  them to `/mcps`. There is no input gate, so named-send and last-doc
  asks always reach the desk. It does not open Mail.app or Calendar.app.

Success on the phone: the founder knows the result without opening
a laptop. Do not optimize session length, turn count, or desktop
completeness. See `EXPERIENCE.md`.

## Observe

```
python3 30-tools/desk-bridge/test_bridge.py
python3 30-tools/desk-bridge/bridge.py --check
python3 30-tools/desk-bridge/bridge.py --install
```

Then DM `@Rua_desk_bot`; send a text, a second text while the first
is running, an obvious Google ask (calendar or last mail), and a
voice note. The Google ask must come back as the live result, not
"Google isn't on this phone seat." `/status` must show effort,
queue depth, pending, and last timing as plain lines, not JSON.
`/brief` and `/todo` must not mention a `lists.md` diary line.
A desk ask that names a commitment must show that line on the next
`/todo` and must not print `LIST+`. A voice note that reports a done
must not close the list; the reply ends with the voice-refusal line.

`EXPERIENCE.md` is the session contract. A later change that
touches pairing, waiting, voice-fail, or session-drop must
update that file in the same change.
