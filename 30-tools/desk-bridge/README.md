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

Leave `TELEGRAM_USER_ID` blank. The first person who DMs the bot is
paired and the id is written back.

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

State and logs: `~/.grok/desk-bridge/`.

## Phone commands

| Command | What it does |
| --- |---|
| `/help` | Short usage |
| `/new` | Fresh Grok session |
| `/status` | Paired user, session id, last error |

Anything else, including a voice note, is handed to the desk.

The phone run uses medium effort and drops a fat session so a
pricing job does not ride into the next hello. Studio Grok stays
on whatever effort you set there.

The installed job holds a `caffeinate` idle-sleep assertion, so this
Mac Studio stays up while the bot is loaded. The display can still
sleep. `--uninstall` drops the assertion. This is a local poll, not
a cloud bot.
