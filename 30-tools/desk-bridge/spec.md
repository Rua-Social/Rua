# desk-bridge

## Goal

A Telegram DM is a seat at the Rua desk. A process on this Mac hands
each message to Grok in `~/Rua` and sends one short phone reply back.

Voice notes are inbound only: download the Telegram file, transcribe
with ElevenLabs Scribe v2, then run the same desk path as text.

How the phone session behaves is `EXPERIENCE.md`. This file does not
restate it. If they conflict, fix the one that is wrong, then the other.

## Out of scope

Slack. Cloud hosting. Spoken replies (TTS). Image ingest. Video notes.
The official Claude/Grok Telegram plugin. A custom agent file.
Opening the bot to anyone else. Changing studio reasoning effort.

## Done

- `python3 30-tools/desk-bridge/bridge.py --check` talks to Telegram
  and finds `grok`.
- Only a private DM from the paired Telegram user is answered.
  Groups are ignored. The first private DM pairs and says so.
- Secrets stay in `~/.grok/secrets/`, not Git.
- A live text from the phone gets a real desk reply.
- A voice note from the paired user is transcribed and answered.
- The phone gets the last assistant text after the last tool, not
  the studio log. Reaction + typing, not "On it."
- Phone Grok runs at medium effort. Fat or missing sessions
  start fresh and say so on the phone.
- While installed, the job prevents idle system sleep.

Success on the phone: the founder knows the result without opening
a laptop. Do not optimize session length, turn count, or desktop
completeness. See `EXPERIENCE.md`.

## Observe

```
python3 30-tools/desk-bridge/test_bridge.py
python3 30-tools/desk-bridge/bridge.py --check
python3 30-tools/desk-bridge/bridge.py --install
```

Then DM `@Rua_desk_bot`, or send a voice note.

`EXPERIENCE.md` is the session contract. A later change that
touches pairing, waiting, voice-fail, or session-drop must
update that file in the same change.
