# desk-bridge

Telegram seat for the Rua desk. Phone in, same repo and one configured
conductor out. Not a new org chart. How the phone behaves:
`EXPERIENCE.md`.

## Goal

You DM `@Rua_desk_bot`. A launchd process on this Mac runs the selected
engine in `~/Rua` and texts you back. A voice note is transcribed first,
then takes the same path.

Out of scope: Slack, spoken replies, images, a public webhook,
anyone else's Telegram, the official Claude Telegram plugin.

## Secrets

`~/.grok/secrets/desk-bridge.env` (not in Git):

```
export TELEGRAM_BOT_TOKEN=
export TELEGRAM_USER_ID=
```

Set `TELEGRAM_USER_ID` to the founder's numeric Telegram user id before
installing. The bridge refuses to start when it is blank. It never trusts
the first person who happens to find the bot.

The launchd job does not inherit a login shell. Phone Grok also
loads `~/.grok/secrets/xpoz.env` and `moonshot.env` so MCP keys
match the dashboard, and sets `GROK_MANAGED_MCP_GATEWAY_TOOLS_ENABLED`
plus `GROK_MANAGED_MCPS_ENABLED` so grok.com Gmail / Calendar /
Drive connectors are on the phone process too. `/mcps` `i` on
Google's remote MCP servers does not complete. Not Mail.app.

Set the phone engine in `desk-bridge.env`:

```bash
export DESK_ENGINE=auto
export DESK_ENGINE_ORDER=claude,codex,grok
```

Fixed `grok`, `claude`, and `codex` modes remain available. Auto mode
falls through only when the current engine has done no tool work and is
missing, logged out, at capacity, rate-limited, or out of usage. A working
fallback stays active for an hour before the preferred engine is tried
again. `/status` shows the mode, active engine, and temporary failures.
From the paired Telegram DM, `/engine auto|claude|codex|grok` persists a
local override without rewriting the secrets file. Switching clears the
current engine session, queued asks, and cooldowns; `/new` clears the session
and queue without changing the selected engine.

Voice notes also need `~/.grok/secrets/elevenlabs.env`:

```
export ELEVENLABS_API_KEY=
```

## Run

```bash
python3 30-tools/desk-bridge/bridge.py --check
python3 30-tools/desk-bridge/bridge.py --install
```

Offline boundary suite:

```bash
python3 -m unittest discover -s 30-tools/desk-bridge -p 'test_*.py'
```

`--install` writes `~/Library/LaunchAgents/com.rua.desk-bridge.plist`
and loads it. `--uninstall` removes it. `--run` is the long-poll loop
(what launchd starts).

Install verifies the replacement launchd job and restores the previous
plist if loading fails. A runtime lock prevents a second bridge process;
shutdown stops any active Grok process group before launchd restarts it.

State and logs: `~/.grok/desk-bridge/`.
The bridge enforces owner-only permissions on secrets, state, metrics,
pending replies, and launchd logs at startup.

## Phone commands

| Command | What it does |
| --- |---|
| `/help` | Short usage |
| `/new` | Fresh engine session |
| `/engine auto\|claude\|codex\|grok` | Select engine mode; next message starts fresh |
| `/status` | Owner, effort, queue, pending, last timing, last error, next keep/reset |
| `/brief` | Ranked walking brief from `20-studio/todo.md` and one client card |
| `/todo` | Open actions only |
| `/park` | Instant line on Founder → Ideas |
| `/idea` | Instant thought. Long ones land in `20-studio/ideas/` |

Anything else, including a voice note, is handed to the desk. Voice notes
are first written to owner-only durable state under
`~/.grok/desk-bridge/voice/`, outside Git. The phone receives
`Voice saved. Working from it.` only after the transcript is safe. To hold a
long information dump without running the engine, begin with:
`Save this as intake. No action yet.` It returns a receipt and does not touch
the todo. Voice may add a todo only when it explicitly says
`Add one todo: ...`; voice never closes one.
A real commitment in that reply is appended to `20-studio/todo.md`
and hidden from Telegram. `lists.md` is the desk diary, not the todo.

The phone run enforces medium effort and drops a fat, stale, or
wrong-effort session so a pricing job does not ride into the next
hello. Studio Grok stays on whatever effort you set there.

Grok has 60 seconds to produce its first meaningful event. Each accepted
phone ask has five minutes after voice capture. Voice capture remains
recoverable while queued and is persisted before engine work.
Completed work is written to a local outbox before Telegram delivery,
so a transient send failure does not rerun the work. A dedicated sender
retries without blocking message pickup or the sole engine worker. One
ask runs at a time; later messages are acknowledged and queued.

Voice records move through `queued`, `downloaded`, `transcribing`,
`transcribed`, `engine-running`, and `completed`. A restart never replays a
record after engine work has begun. The record keeps safe metadata and the
transcript, not prompt text in metrics or logs. Source audio is retained
during the pilot for retry and model comparison.

The installed job holds a `caffeinate` idle-sleep assertion, so this
Mac Studio stays up while the bot is loaded. The display can still
sleep. `--uninstall` drops the assertion. This is a local poll, not
a cloud bot.
