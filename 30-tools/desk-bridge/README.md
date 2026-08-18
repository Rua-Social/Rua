# desk-bridge

Telegram seat for the Rua desk. Phone in, same repo and same Grok
conductor out. Not a new org chart. How the phone behaves:
`EXPERIENCE.md`.

## Goal

You DM `@Rua_desk_bot`. A launchd process on this Mac runs `grok` in
`~/Rua` and texts you back. A voice note is transcribed first, then
takes the same path.

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
match the dashboard.

Set `DESK_ENGINE=claude` in `desk-bridge.env` to run the phone
on Claude Code instead of Grok. `/status` shows which engine.

Voice notes also need `~/.grok/secrets/elevenlabs.env`:

```
export ELEVENLABS_API_KEY=
```

## Run

```bash
python3 30-tools/desk-bridge/bridge.py --check
python3 30-tools/desk-bridge/bridge.py --install
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
| `/new` | Fresh Grok session |
| `/status` | Owner, effort, queue, pending, last timing, last error, next keep/reset |
| `/brief` | Walking brief from the lists and client records |
| `/park` | Instant line on Founder → Ideas |
| `/idea` | Instant thought. Long ones land in `20-studio/ideas/` |

Anything else, including a voice note, is handed to the desk.

The phone run enforces medium effort and drops a fat, stale, or
wrong-effort session so a pricing job does not ride into the next
hello. Studio Grok stays on whatever effort you set there.

Grok has 60 seconds to produce its first meaningful event. Each accepted
phone ask, including voice preprocessing, has five minutes total.
Completed work is written to a local outbox before Telegram delivery,
so a transient send failure does not rerun the work. A dedicated sender
retries without blocking message pickup or the sole Grok worker. One Grok
ask runs at a time; later messages are acknowledged and queued.

The installed job holds a `caffeinate` idle-sleep assertion, so this
Mac Studio stays up while the bot is loaded. The display can still
sleep. `--uninstall` drops the assertion. This is a local poll, not
a cloud bot.
