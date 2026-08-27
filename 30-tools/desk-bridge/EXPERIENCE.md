# desk-bridge — Experience

How the phone behaves. `spec.md` owns build and observe.
This is for the founder, on the phone. Telegram owns the pixels.

## Foundation

Telegram DM with `@Rua_desk_bot`. One preconfigured human.
Groups are ignored. The Mac runs the selected engine in `~/Rua` and texts back.

If a need cannot land as a short Telegram message, it is
not this seat.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| Help | `/help` or `/start` | Commands, pairing, and that `/new` does not restart the Mac. |
| New session | `/new` | Drop the engine session and any queued asks. Next message starts fresh. Cuts the line. |
| Engine | `/engine auto`, `/engine claude`, `/engine codex`, or `/engine grok` | Persist the selected engine mode locally, clear the engine session and queued asks, clear engine cooldowns, and start the next message fresh. `/engine` alone or an invalid value returns the usage line. |
| Status | `/status`, `/statua`, or the word status | Owner, engine mode, active engine, unavailable engines, session, effort, queue, pending, last run, last error, whether the next ask will keep or reset. Last run is timing, not JSON. |
| Brief | `/brief` or the word brief | Ranked walking card from `20-studio/todo.md` plus one live client card. Do can be a STALE gated line. Not `lists.md`. Not live Google. |
| Todo | `/todo` or the word todo | Walking open actions. Action text, not the date. Full and STALE if those apply. Last line: Text the action to close it. |
| Park | `/park …`, `park …`, `backlog …`, or a voice note that starts that way | Instant. Lands on Founder → Ideas. No Grok. |
| Idea | `/idea …` or `idea …` | Instant. Short stays on the list. Longer goes to `20-studio/ideas/`. |
| Brainstorm | `/brainstorm …` or `brainstorm …` | Eyes + typing. A short think comes back. Not a deck. |
| Desk ask | Other text from the paired user | One short result from the desk. A real commitment lands on `todo.md`. A done moves to `todo-done.md`. A refused write says so in one line. Machine `LIST+` lines never show. |
| File | Ask for the file: "send me the Ecoplex month-1 PDF", or have a doc made and sent | The text answer, then the document. Repo, Downloads, or Desktop only. One file per ask. A raw `FILE+` line never shows. |
| Voice ask | A voice note from the paired user | Transcribe, then the same path as text, except it never closes the todo. |
| Voice intake | A voice note beginning “Save this as intake. No action yet.” | Save the information without running the desk or changing todos; return a receipt. |
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
| "Engine set to claude. Next message starts fresh." | Rewrite the secrets file or keep the old engine session. |
| "Session reset. The last one was too big or gone." | Pretend the old chat is still there |
| "Claude is busy. Try again in a minute." | Wait silently for an upstream first response. The engine name follows fixed mode. |
| "The desk timed out. Send it again or try a smaller ask." | A stack trace or a fifteen-minute wait |
| "Couldn't transcribe that. Try again or type it." | Guess at a garbled note |
| An asked-for file arrives as a document; the path is named either way | A raw `FILE+` line on the phone, or claiming a file was attached when it wasn't |
| "On the list." / "Sent to the desk." | "Got it!" "Love this idea!" "I'll brainstorm that for you" |
| A commitment becomes one todo line; the reply stays the result | `LIST+` on the phone, a todo in `lists.md`, niceties on the open list |
| The instance or todo answer first | Lead with a Google miss when the card already has it |
| Current-data asks: the record answers when it covers the ask, else the parked sentence in seconds | Hanging on Google, a three-engine failure run, Mail.app, Calendar.app, Chrome |
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
| No first engine event (60s), fixed mode | "Claude is busy. Try again in a minute." The engine name follows the configured engine. |
| Timeout (5 min) | "The desk timed out. Send it again or try a smaller ask." |
| Fixed engine missing | "Claude is busy. Try again in a minute." The engine name follows the configured engine. |
| Other desk fail | "Desk hit an error. /status" |
| Empty engine reply | "The desk came back with nothing. Send it again." |
| Voice, no key | "Voice is saved, but the ElevenLabs key is missing." |
| Voice, no file | "That voice note had no file." |
| Voice fail | "Couldn't transcribe that. Try again or type it." |
| Voice saved | "Voice saved. Working from it." The transcript is already owner-only and durable. |
| Voice held | "Voice saved. No actions added." The receipt identifies the saved intake. |
| Voice saved, desk timeout | "Voice saved. The desk timed out. Your intake is safe." |
| Voice interrupted after capture | "Voice saved. Desk stopped after work began. Check before retrying." |
| Voice held for retry | "Voice note held. Try again or check the bridge." |
| Fat or stale session | "Session reset. The last one was too big or gone." then the new reply. Only when the history file is missing, over the byte cap, or at the wrong effort. A normal success does not reset the next ask. |
| Session restored at the wrong effort | "Session reset. The last one was too big or gone." then the new reply. |
| Wrong inbound type | "Text or a voice note." |
| Long reply | Extra Telegram messages, no "1/2". |
| Google tools missing (live mode) | "Google tools are not on this process." The bridge, not the desk prompt, detects this after a live lookup is attempted. Not the parked-Google sentence. Not `/mcps`. |
| Current mail/calendar/Drive ask, Google off | The record answer when it genuinely covers the ask. Otherwise "Google isn't on this phone seat. Parked on the desk list." plus the pocket brief. Seconds, not a three-engine wait. |
| File asked for | The text answer, then the document. |
| File refused | "Can't send that file from the phone seat. It's at …" |
| File send failed | Three tries, then: "That file didn't send. It's on the Mac: …" |
| Park, nothing after the word | "Say what to park." |
| Parked | "On the list." |
| Idea, nothing after the word | "Say the idea." |
| Idea sent | "Sent to the desk." Name the file if one was written. |
| Desk ask named a real commitment | The result, with no `LIST+`. The line is on `todo.md`. |
| Same commitment already open | The result, then: Already on the list. |
| Refused todo write | One line after the result: "Todo is full. Close one." or "Not a todo line." |
| Voice note reported a done | Voice never closes the list. "Voice can't close the list. Text it if it landed." |
| Voice note inferred a Do | Voice does not add it. "Voice did not add a todo. Say \"Add one todo: ...\" if you want that." |
| Todo empty | "Nothing open." |
| Todo at seven open | "Todo is full. Close one." then the list, then "Text the action to close it." |
| Open todo | Action text, `STALE` prefix if stale, then "Text the action to close it." |
| Open line older than seven days | Marked `STALE` on `/todo` and `/brief`. |
| Reply completed but Telegram is unavailable | The result is held locally and delivered without rerunning Grok when Telegram returns. `/status` shows a pending delivery. |
| Preferred engine is out of usage before any tool runs | `Using Codex — Claude hit its limit.` then the result. The named engines follow the configured order. |
| Every configured engine is unavailable | `All desk engines are unavailable. /status` |
| Engine fails after a tool runs | `Desk hit an error. /status` No second engine runs the ask. |
| Valid engine switch | `Engine set to <engine>. Next message starts fresh.` The selection is `auto`, `claude`, `codex`, or `grok`; the current session, queued asks, and cooldowns are cleared. |
| Bare or invalid engine switch | `Use /engine auto|claude|codex|grok` Nothing changes. |

## What you can send

Text, voice note, `/help`, `/start`, `/new`, `/engine`, `/status`, `/brief`, `/todo`, `/park`, `/idea`.
An unknown `/command` is help, not an engine ask. The words `status`, `brief`, `todo`, `park`, and `idea` are commands.
`/new`, a valid `/engine` switch, and the other commands cut the line. They do not wait behind an engine ask. `/new` does not change the selected engine.
Ask for a file and it arrives as a Telegram document — the repo, Downloads, or Desktop only, one file per ask.

Not this seat: Slack, TTS, images, video notes, the official
Telegram plugin, anyone else's Telegram, a fifth Grok room.

One engine ask at a time. The poller stays awake. A second DM is
acknowledged as queued; its own five-minute budget keeps running while it
waits behind the first ask.

Voice capture is kept safe while it waits behind desk work. A saved voice
record lives in owner-only state outside Git. `/new` and engine switches may
cut off desk work, but never delete a saved voice record. A saved receipt is
proof that the information landed, not proof that the requested work finished.

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
4. Failure: no first engine event in fixed mode → the named engine is busy; five-minute total timeout → "The desk timed out…"

### Flow 1b — Long intake (founder, walking between meetings)

1. Starts the note: “Save this as intake. No action yet.” Then speaks freely.
2. The bridge saves the voice record before any desk work.
3. **Worked:** “Voice saved. No actions added.” plus a receipt.
4. Failure: the desk may stop later, but the saved intake remains available and
   is not replayed automatically after uncertain engine work.

### Flow 2 — The desk forgot (founder, same footpath)

1. Texts something that needed the last chat.
2. History is gone, over the byte fallback, or at the wrong effort. Session is dropped. A big MCP ask does not count as gone.
3. **Worked:** first line is "Session reset. The last one was too big or gone." then a fresh answer.
4. He can restate the ask. `/status` will not say "none" as if nothing happened.

### Flow 3 — Tomorrow brief (founder, on the street)

Live-Google flow. Applies when `DESK_GOOGLE=live`; while Google is off,
a current-data ask gets the record answer or the parked sentence in
seconds, and flows 3–3c do not run.

1. Asks what's on the calendar tomorrow, last doc on Drive, last mail.
2. Eyes and typing.
3. **Worked:** current/recent mail, calendar, or Drive asks use live
   Gmail, Calendar, or Drive via `search_tool` then `use_tool`, even
   when the instance has related context. One short verified result.
   Not `lists.md`. Not Mail.app.
4. Failure: "Google isn't on this phone seat." `/mcps`. Mail.app,
   Calendar.app, or briefing a card they have already marked wrong.
   Tools missing: "Google tools are not on this process."

### Flow 3b — What did I send (founder, after a meeting)

1. Asks what went to one or more named people or organisations today.
2. Eyes and typing. The live Gmail tool inspects individual messages.
3. **Worked:** one labelled result per entity, using Europe/Dublin time.
   "To/for" includes To, CC, replies, aliases, and relevant threads; the
   reply says the actual recipient role. "Directly to" requires the named
   entity in To, but a reply still counts. Latest means the individual sent
   timestamp, not thread order. Founder correction beats stale local context.
4. Failure: collapsing several entities into one answer; presenting CC as
   direct To; treating a reply as ineligible; or briefing a local "not sent"
   line as current evidence.
5. If the founder says a newer message exists or supplies evidence, the desk
   does not repeat the older connector result as "latest." It says the
   connected source did not return the item and briefly names what it searched.

### Flow 3c — Lookup versus action

1. Asks about current Workspace state, or asks to follow up.
2. A lookup reads only. "Follow up" drafts only.
3. **Worked:** the lookup returns evidence without mutation. Send, schedule,
   share, or update runs only when the founder explicitly names that action
   and its target is unambiguous.
4. Failure: sending from a lookup, or treating "follow up" as permission to
   send.

### Flow 4 — Links from the street (founder, after a meeting)

1. Texts Instagram or TikTok links, usually with a short ask.
2. Eyes and typing.
3. **Worked:** the links are treated as intake. The reply names what landed, where the file is, and what they need. If they asked for a client document, that file can be sat with without the founder talking. References show as the clip itself, not a URL list.
4. Failure: a photo of a link ("Text or a voice note."); a research dump; a file that still needs a talk-track to make sense.

### Flow 5 — Capture on the street (founder, idea mid-walk)

1. Voice or text: `park …` or `idea …`. `brainstorm …` is a short Grok think, not this path.
2. Park and idea: No Grok. No queue wait. Brainstorm: eyes + typing. Not a deck.
3. **Worked:** park/idea: "On the list." or "Sent to the desk." Brainstorm: the short think comes back. He keeps walking.
4. Failure: only the word, no payload → "Say what to park." / "Say the idea."

### Flow 6 — Commitment on the street (founder, after a call)

1. Texts a desk ask that names a real next action, or that one landed.
2. Eyes and typing. Same one engine turn.
3. **Worked:** the notification is the punchline. `/todo` now shows
   that line. No `LIST+`. No second ask to "put it on the list."
4. Failure: niceties on `todo.md`; the same line twice; the line
   landing in `lists.md`; a voice note closing the list.

### Flow 7 — Explicit voice todo (founder, after a call)

1. Says: “Add one todo: send the deposit follow-up.”
2. The desk may return one validated `Do` line; cap and duplicate rules still apply.
3. **Worked:** the result is returned and the line appears on `/todo`.
4. Any inferred action without that phrase is not added.

### Flow 8 — File to the phone (founder, away from the Mac)

1. Asks for a file — "send me the Ecoplex month-1 PDF" — or asks for a doc to be made and sent.
2. Eyes and typing. The desk works; the text answer lands, then the document.
3. **Worked:** the file opens on the phone.
4. Failure: a path outside the repo, Downloads, or Desktop → "Can't send that file from the phone seat. It's at …"; a failed send → three quiet retries, then "That file didn't send. It's on the Mac: …".

## Parked

1. Mark chunked replies (1/2).
2. Split the three voice-fail causes.
3. Live Google on the phone seat. Suspended 27 Aug: it never returned an
   answer the founder trusted and hung on failure. The machinery stays,
   gated behind `DESK_GOOGLE=live`.
4. Google's remote MCP servers (`/mcps` `i`). Phone `grok -p` gets
   grok.com Gmail / Calendar / Drive via managed gateway env, the
   same connectors as the dashboard TUI. Not a second Google login.
5. Claude-for-Google. Drive and Gmail worked on Haiku; Calendar
   auth failed. Not a second Claude path.
6. Cross-engine session history. Auto fallback starts fresh on the next
   engine. It does not translate or replay the previous engine's chat.
7. Morning push of `/brief`. Only after the ranked card is trusted.
