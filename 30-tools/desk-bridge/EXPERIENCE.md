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
| Help | `/help` or `/start` | Commands, pairing, and that `/new` does not restart the Mac. |
| New session | `/new` | Drop the Grok session and any queued asks. Next message starts fresh. Cuts the line. |
| Status | `/status`, `/statua`, or the word status | Owner, engine, session, effort, queue, pending, last run, last error, whether the next ask will keep or reset. Last run is timing, not JSON. |
| Brief | `/brief` or the word brief | Ranked walking card from `20-studio/todo.md` plus one live client card. Not `lists.md`. Not live Google. |
| Todo | `/todo` or the word todo | Open actions only. Full and STALE lines if those apply. |
| Park | `/park …`, `park …`, `backlog …`, or a voice note that starts that way | Instant. Lands on Founder → Ideas. No Grok. |
| Idea | `/idea …` or `idea …` | Instant. Short stays on the list. Longer goes to `20-studio/ideas/`. |
| Brainstorm | `/brainstorm …` or `brainstorm …` | Eyes + typing. A short think comes back. Not a deck. |
| Desk ask | Other text from the paired user | One short result from the desk. A real commitment lands on `todo.md`. A done moves to `todo-done.md`. A refused write says so in one line. Machine `LIST+` lines never show. |
| Voice ask | A voice note from the paired user | Transcribe, then the same path as text, except it never closes the todo. |
| Working | After an ask is accepted | Eyes reaction plus typing. |
| Queue | A second ask while one is running | "Hold that. Still on the last one." |
| Setup | `--check` or `--install` with no owner id | "Set TELEGRAM_USER_ID before starting the desk." |
| Foreign | Anyone else in a DM | "This desk is paired to another Telegram account." |
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
| "On the list." / "Sent to the desk." | "Got it!" "Love this idea!" "I'll brainstorm that for you" |
| A commitment becomes one todo line; the reply stays the result | `LIST+` on the phone, a todo in `lists.md`, niceties on the open list |
| The instance or todo answer first | Lead with the Google sentence when the card already has it |
| "Google isn't on this phone seat. Parked on the desk list." only if the files are silent | Mail.app, Calendar.app, Chrome, "wire it at the Mac" |
| Filter: escalate what blindsides, handle the ask, park niceties | A studio essay, a second org, "on it" |
| Client-facing files: written for the person who sits with them, and the person they are for | Internal paths, steal-language, process notes, names that are not in the room |
| Links they send are the thing: a still they recognise, then a click | A table of URLs the founder has to talk through |

The bot does not rewrite Grok. Final text is sent as-is after the
last tool. The bridge gives Grok the minimum matching phone rules;
Grok does not reread this file on every ask. `DESK_RULES` must match
this table.

## State patterns

| State | What the phone says |
| --- | --- |
| Missing configured owner | On the Mac: "Set TELEGRAM_USER_ID before starting the desk." The bridge does not start. |
| Foreign DM | "This desk is paired to another Telegram account." |
| Group or channel | Nothing. |
| Working | Eyes + typing every 4s. |
| Queued behind one ask | "Hold that. Still on the last one." |
| No first Grok event (60s) | "Grok is busy. Try again in a minute." |
| Timeout (5 min) | "The desk timed out. Send it again or try a smaller ask." |
| Grok missing | "grok is not installed on this Mac." |
| Other desk fail | "Desk hit an error. /status" |
| Empty Grok text | "(no text)" |
| Voice, no key | "Voice is wired. ElevenLabs key is missing." |
| Voice, no file | "That voice note had no file." |
| Voice fail | "Couldn't transcribe that. Try again or type it." |
| Fat or stale session | "Session reset. The last one was too big or gone." then the new reply. Only when the history file is missing, over the byte cap, or at the wrong effort. A normal success does not reset the next ask. |
| Session restored at the wrong effort | "Session reset. The last one was too big or gone." then the new reply. |
| Wrong inbound type | "Text or a voice note." |
| Long reply | Extra Telegram messages, no "1/2". |
| Google not on this seat | Only when `todo.md` and `10-clients/` do not have the fact. "Google isn't on this phone seat. Parked on the desk list." Then the pocket brief. A named send ("what did I send Tommy") is a desk ask, not this state. |
| Park, nothing after the word | "Say what to park." |
| Parked | "On the list." |
| Idea, nothing after the word | "Say the idea." |
| Idea sent | "Sent to the desk." Name the file if one was written. |
| Desk ask named a real commitment | The result, with no `LIST+`. The line is on `todo.md`. |
| Same commitment already open | The result, then: Already on the list. |
| Refused todo write | One line after the result: "Todo is full. Close one." or "Not a todo line." |
| Voice note reported a done | Voice never closes the list. "Voice can't close the list. Text it if it landed." |
| Todo empty | "Nothing open." |
| Todo at seven open | "Todo is full. Close one." then the list. |
| Open line older than seven days | Marked `STALE` on `/todo` and `/brief`. |
| Reply completed but Telegram is unavailable | The result is held locally and delivered without rerunning Grok when Telegram returns. `/status` shows a pending delivery. |

## What you can send

Text, voice note, `/help`, `/start`, `/new`, `/status`, `/brief`, `/todo`, `/park`, `/idea`.
An unknown `/command` is help, not a Grok ask. The words `status`, `brief`, `todo`, `park`, and `idea` are commands.
`/new` and the other commands cut the line. They do not wait behind a Grok ask.

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
2. History is gone, over the byte fallback, or at the wrong effort. Session is dropped. A big MCP ask does not count as gone.
3. **Worked:** first line is "Session reset. The last one was too big or gone." then a fresh answer.
4. He can restate the ask. `/status` will not say "none" as if nothing happened.

### Flow 3 — Tomorrow brief (founder, on the street)

1. Asks what's on the calendar tomorrow, last doc on Drive, last mail.
2. Eyes and typing.
3. **Worked:** if the instance or todo already has the fact, that
   answer only. If the files are silent: "Google isn't on this phone
   seat. Parked on the desk list." Then the ranked pocket brief from
   `todo.md` plus one live client card. Not `lists.md`. Not a live
   calendar lookup.
4. Failure: leading with the Google sentence when the card already
   answers. Mail.app, Calendar.app, or a two-minute hunt. Do not.

### Flow 3b — What did I send (founder, after a meeting)

1. Asks what went to a named person today.
2. Eyes and typing. Grok reads `10-clients/<slug>/`.
3. **Worked:** the send from the instance card. Thread name and file
   if the card has them. Founder correction beats a stale diary line.
4. Failure: the Google sentence. Hunting Gmail. Briefing "not sent"
   from `lists.md` after they said it went.

### Flow 4 — Links from the street (founder, after a meeting)

1. Texts Instagram or TikTok links, usually with a short ask.
2. Eyes and typing.
3. **Worked:** the links are treated as intake. The reply names what landed, where the file is, and what they need. If they asked for a client document, that file can be sat with without the founder talking. References show as the clip itself, not a URL list.
4. Failure: a photo of a link ("Text or a voice note."); a research dump; a file that still needs a talk-track to make sense.

### Flow 5 — Capture on the street (founder, idea mid-walk)

1. Voice or text: `park …` or `idea …` / `brainstorm …`.
2. No Grok. No queue wait.
3. **Worked:** "On the list." or "Sent to the desk." He keeps walking.
4. Failure: only the word, no payload → "Say what to park." / "Say the idea."

### Flow 6 — Commitment on the street (founder, after a call)

1. Texts a desk ask that names a real next action, or that one landed.
2. Eyes and typing. Same one Grok turn.
3. **Worked:** the notification is the punchline. `/todo` now shows
   that line. No `LIST+`. No second ask to "put it on the list."
4. Failure: niceties on `todo.md`; the same line twice; the line
   landing in `lists.md`; a voice note closing the list.

## Parked

1. Mark chunked replies (1/2).
2. Split the three voice-fail causes.
3. Telegram file attachments. This bridge sends text and repo paths.
4. Space connectors on the phone `grok -p` process.
5. Claude-for-Google. Drive and Gmail worked on Haiku; Calendar
   auth failed. A second Google path. Not this seat.
6. Automatic fallback between engines. The phone runs one brain:
   `DESK_ENGINE=grok` or `DESK_ENGINE=claude` in
   `~/.grok/secrets/desk-bridge.env`. Switch is explicit.
7. Morning push of `/brief`. Only after the ranked card is trusted.
