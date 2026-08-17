# desk-bridge — Experience

How the phone behaves. `spec.md` owns build and observe.
This is for the founder, on the phone. Telegram owns the pixels.

## Foundation

Telegram DM with `@Rua_desk_bot`. One preconfigured human.
Groups are ignored. The Mac runs Grok in `~/Rua` and texts back.

If a need cannot land as a short Telegram message, it is
not this seat.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| Help | `/help` or `/start` | The three commands. Text or a voice note. |
| New session | `/new` | Drop the Grok session. Next message starts fresh. |
| Status | `/status` | Owner, session, effective effort, queue, pending delivery, last run, last error. |
| Desk ask | Other text from the paired user | One short result from the desk. |
| Voice ask | A voice note from the paired user | Transcribe, then the same path as text. |
| Working | After an ask is accepted | Eyes reaction plus typing. |
| Queue | A second ask while one is running | "Queued. One ask is already running." |
| Setup | `--check` or `--install` with no owner id | "Set TELEGRAM_USER_ID before starting the desk." |
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
| "Grok is busy. Try again in a minute." | Wait silently for an upstream first response |
| "The desk timed out. Send it again or try a smaller ask." | A stack trace or a fifteen-minute wait |
| "Couldn't transcribe that. Try again or type it." | Guess at a garbled note |
| Name the repo path when work creates a file | Claim the text-only bridge attached it |
| "Google isn't on this phone seat. Parked on the desk list." | Mail.app, Calendar.app, Chrome, "wire it at the Mac" |

The bot does not rewrite Grok. Final text is sent as-is after the
last tool. The bridge gives Grok the minimum matching phone rules;
Grok does not reread this file on every ask. `DESK_RULES` must match
this table.

## State patterns

| State | What the phone says |
| --- | --- |
| Missing configured owner | On the Mac: "Set TELEGRAM_USER_ID before starting the desk." The bridge does not start. |
| Foreign DM | "This desk is paired to someone else." |
| Group or channel | Nothing. |
| Working | Eyes + typing every 4s. |
| Queued behind one ask | "Queued. One ask is already running." |
| No first Grok event (60s) | "Grok is busy. Try again in a minute." |
| Timeout (5 min) | "The desk timed out. Send it again or try a smaller ask." |
| Grok missing | "grok is not installed on this Mac." |
| Other desk fail | "Desk hit an error. /status" |
| Empty Grok text | "(no text)" |
| Voice, no key | "Voice is wired. ElevenLabs key is missing." |
| Voice, no file | "That voice note had no file." |
| Voice fail | "Couldn't transcribe that. Try again or type it." |
| Fat or stale session | "Session reset. The last one was too big or gone." then the new reply. |
| Session restored at the wrong effort | "Session reset. The last one was too big or gone." then the new reply. |
| Wrong inbound type | "Text or a voice note." |
| Long reply | Extra Telegram messages, no "1/2". |
| Google not on this seat | "Google isn't on this phone seat. Parked on the desk list." |
| Reply completed but Telegram is unavailable | The result is held locally and delivered without rerunning Grok when Telegram returns. `/status` shows a pending delivery. |

## What you can send

Text, voice note, `/help`, `/start`, `/new`, `/status`.

Not this seat: Slack, TTS, images, video notes, the official
Telegram plugin, anyone else's Telegram, a fifth Grok room.

One Grok ask at a time. The poller stays awake. A second DM is
acknowledged as queued; its own five-minute budget keeps running while it
waits behind the first ask.

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
2. Eyes and typing throughout transcription and desk work. Phone stays in a pocket.
3. **Worked:** the notification is the punchline.
4. Failure: no first Grok event → "Grok is busy…"; five-minute total timeout → "The desk timed out…"

### Flow 2 — The desk forgot (founder, same footpath)

1. Texts something that needed the last chat.
2. History is gone, over the byte fallback, or over the prompt-token budget. Session is dropped.
3. **Worked:** first line is "Session reset. The last one was too big or gone." then a fresh answer.
4. He can restate the ask. `/status` will not say "none" as if nothing happened.

### Flow 3 — Tomorrow brief (founder, on the street)

1. Asks what's on the calendar tomorrow, last doc on Drive, last mail.
2. Eyes and typing.
3. **Worked:** the meeting, the last file, the last thread. Or, if
   Google is missing from this seat: "Google isn't on this phone
   seat. Parked on the desk list."
4. Failure: Mail.app, Calendar.app, or a two-minute hunt. Do not.

## Parked

1. Mark chunked replies (1/2).
2. Split the three voice-fail causes.
3. Telegram file attachments. This bridge sends text and repo paths.
4. Space connectors on the phone `grok -p` process.
5. Claude-for-Google. Drive and Gmail worked on Haiku; Calendar
   auth failed. A second Google path. Not this seat.
6. Alternate-model fallback. It needs a controlled quality result first.
