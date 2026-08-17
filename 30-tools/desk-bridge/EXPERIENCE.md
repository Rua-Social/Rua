# desk-bridge — Experience

How the phone behaves. `spec.md` owns build and observe.
This is for the founder, on the phone.

## Foundation

Telegram DM with `@Rua_desk_bot`. One paired human. Groups
are ignored. The Mac runs Grok in `~/Rua` and texts back.

If a need cannot land as a short Telegram message, it is
not this seat.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| Help | `/help` or `/start` | The three commands. Text or a voice note. |
| New session | `/new` | Drop the Grok session. Next message starts fresh. |
| Status | `/status` | Pairing, session, effort, last run, last error. |
| Desk ask | Other text from the paired user | One short result from the desk. |
| Voice ask | A voice note from the paired user | Transcribe, then the same path as text. |
| Working | After an ask is accepted | Eyes reaction plus typing. |
| Pairing | First private DM | "Paired. This desk answers you." then the ask. |
| Foreign | Anyone else in a DM | "This desk is paired to someone else." |
| Wrong type | Photo, video note, sticker, document | "Text or a voice note." |
| Group | Any non-private chat | No reply. |

## Voice and tone

| Do | Don't |
| --- | --- |
| Eyes plus typing | "On it." "Loading…" "Thinking…" |
| One short result: what happened, where it is, what they need | Tables, file trees, class labels, studio log |
| "New session. Next message starts fresh." | "How can I help today?" |
| "Session reset. The last one was too big or gone." | Pretend the old chat is still there |
| "The desk timed out. Send it again or try a smaller ask." | A stack trace |
| "Couldn't transcribe that. Try again or type it." | Guess at a garbled note |
| Say a file is in the chat | Recap the job around the file |

The bot does not rewrite Grok. Final text is sent as-is
after the last tool. `DESK_RULES` must match this table.

## State patterns

| State | What the phone says |
| --- | --- |
| First private DM | "Paired. This desk answers you." then the ask. |
| Foreign DM | "This desk is paired to someone else." |
| Group or channel | Nothing. |
| Working | Eyes + typing every 4s. |
| Timeout (15 min) | "The desk timed out. Send it again or try a smaller ask." |
| Grok missing | "grok is not installed on this Mac." |
| Other desk fail | "Desk hit an error. /status" |
| Empty Grok text | "(no text)" |
| Voice, no key | "Voice is wired. ElevenLabs key is missing." |
| Voice, no file | "That voice note had no file." |
| Voice fail | "Couldn't transcribe that. Try again or type it." |
| Fat or stale session | "Session reset. The last one was too big or gone." then the new reply. |
| Wrong inbound type | "Text or a voice note." |
| Long reply | Extra Telegram messages, no "1/2". |

## What you can send

Text, voice note, `/help`, `/start`, `/new`, `/status`.

Not this seat: Slack, TTS, images, video notes, the official
Telegram plugin, anyone else's Telegram, a fifth Grok room.

One ask at a time. A second DM while Grok is running waits
with no ack, up to fifteen minutes.

## If it breaks

Every miss the founder can act on has a plain sentence.
Do not hide a recoverable miss behind `/status` unless the
next step is the Mac itself.

## Success and what not to optimize

Success: from a voice note or a text, the founder knows the
result without opening a laptop.

Do not optimize: session length, turn count, desktop
completeness, engagement.

## Key flows

### Flow 1 — Walk and talk (founder, two minutes from a door)

1. Sends a short voice note.
2. Eyes and typing. Phone stays in a pocket.
3. **Worked:** the notification is the punchline.
4. Failure: fifteen-minute timeout → "The desk timed out…"

### Flow 2 — The desk forgot (founder, same footpath)

1. Texts something that needed the last chat.
2. History is gone or over 400KB. Session is dropped.
3. **Worked:** first line is "Session reset. The last one was too big or gone." then a fresh answer.
4. He can restate the ask. `/status` will not say "none" as if nothing happened.

## Parked

1. Mark chunked replies (1/2).
2. Ack a message that arrives while an ask is in flight.
3. Split the three voice-fail causes.
4. `DESK_RULES` mention a file in the chat. The bot cannot send one.
