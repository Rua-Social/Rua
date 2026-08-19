# desk-bridge

## Goal

A Telegram DM is a seat at the Rua desk. A process on this Mac hands
each message to Grok in `~/Rua` and sends one short phone reply back.
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
Giving the phone Grok Space connectors. Claude-for-Google.
Mail.app, Calendar.app, or a browser as a stand-in for Gmail,
Calendar, or Drive.
A custom agent or phone plugin profile. A persistent Grok leader.
Direct xAI API calls. Automatic model routing or fallback. A new
dependency, host, service, or chat surface. Changing Telegram's look.

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
  brief is appended to a Google miss reply. They do not read
  `lists.md`. They do not open Mail.app, Calendar.app, or Drive.
- `/todo` returns the open list from `20-studio/todo.md`. Cap 7.
  Lines older than 7 days are marked STALE on read. Empty is
  "Nothing open." Full is "Todo is full. Close one."
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
- A live text from the phone gets a real desk reply.
- A voice note from the paired user is transcribed and answered.
- The phone gets the last assistant text after the last tool, not the
  studio log. Reaction + typing are best effort and never delay Grok.
- The poller remains live while one Grok worker handles asks in order.
  A second ask receives the queue sentence in `EXPERIENCE.md`.
- Phone runs Grok (`grok -p`) or Claude Code (`claude -p`) from
  `DESK_ENGINE` in the desk-bridge secrets file. Default is grok.
  Claude uses `--dangerously-skip-permissions` because the launchd
  job cannot click allow.
- Phone Grok runs at effective medium effort. Missing, over the history
  byte cap, or wrong-effort sessions start fresh and say so. A large
  prompt-token total from MCP tools does not reset the next ask.
- Grok output is parsed while it runs. No first meaningful event within 60 seconds
  uses the provider-busy sentence. Idle work and the whole ask have
  separate deadlines; the total phone budget is five minutes and ten turns.
- Completed replies enter an owner-only outbox before Telegram delivery.
  Delivery retries never rerun Grok or duplicate its side effects.
  Delivery itself is at-least-once: a process death in Telegram's narrow
  send/checkpoint gap can repeat a reply chunk. A dedicated sender keeps
  Telegram delivery latency off the poller and sole Grok worker.
- Privacy-safe JSONL metrics cover pickup, acknowledgement, voice,
  Grok first event and finish, effective model/effort, usage, delivery,
  and failure stage without storing the prompt.
- While installed, the job prevents idle system sleep.
- Install verifies the replacement launchd job and restores the prior plist
  on failure. A singleton runtime lock prevents concurrent bridges, and
  shutdown terminates the active Grok process group.
- Phone `grok -p` does not inherit grok.com Space connectors
  (Gmail, Calendar, Drive). Those stay on the dashboard session.
  It does load `~/.grok/secrets/xpoz.env` and `moonshot.env` so
  dashboard MCP keys exist in the launchd child.
- A Telegram `getUpdates` idle timeout is not written to `last_error`.
  `/status` keeps the last real desk miss. If Grok hits the turn
  limit after producing text, that text is sent.
  An explicit live mail, calendar, or Drive lookup is a desk ask like
  any other: the instance card and `todo.md` answer first. When the
  files are silent, Grok replies with exactly the `EXPERIENCE.md`
  sentence and nothing else; the bridge then parks the miss once on
  the desk list and appends the pocket brief. There is no input gate,
  so named-send and last-doc asks always reach the desk. It does not
  open Mail.app or Calendar.app.

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
is running, an obvious Google ask, and a voice note. `/status` must
show effort, queue depth, pending, and last timing as plain lines, not JSON.
`/brief` and `/todo` must not mention a `lists.md` diary line.
A desk ask that names a commitment must show that line on the next
`/todo` and must not print `LIST+`. A voice note that reports a done
must not close the list; the reply ends with the voice-refusal line.

`EXPERIENCE.md` is the session contract. A later change that
touches pairing, waiting, voice-fail, or session-drop must
update that file in the same change.
