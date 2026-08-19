# Lists

Desk diary. Not the founder todo.

Open actions live in `20-studio/todo.md`. Closed actions in
`todo-done.md`. Do not put todos here.

- **Desk** is the conductor diary: blocked work, what it is moving, what it
  finished.
- **Founder** here is ideas and planned notes only.

When the phone hits something it cannot do, write it under Desk → Blocked.
Do not design the fix from Telegram.

## Desk

### Blocked

- 17 Aug — asked to open the last Fitzpatrick call transcript on Drive. Phone cannot. Cross-checked the local 16 Jul Gemini export instead (`Social concepts runthrough #1`).
- 17 Aug — phone `grok -p` still cannot see Gmail, Calendar, or Drive. Dashboard Grok can. Fail-closed is live: one EXPERIENCE sentence, no Mail.app.
- 17 Aug — founder confirmed Mac Mail.app and Calendar.app are unused. Real mail and calendar are Google Workspace only. Locked in `desk.md`.

### Moving

- These two lists, so the next blocked thing has a place to land.
- 18 Aug — Ecoplex month-1 pack sent. Waiting on them.

### Done

- 19 Aug — hostile-review fixes on the write-back slice: a Google miss now counts only when the reply *starts* with the sentence (a quoted sentence is not a miss, no false park). `/park …`, `/idea …`, `/backlog …`, `/brainstorm …` with a payload were returning help — fixed and pinned. `pocket_brief` dropped its dead `lists_path` parameter.
- 19 Aug — desk-bridge write-back guards, from the 18–19 Aug hostile review: voice notes never close the todo, junk refuses on close too, every refused `LIST+` gets one phone line. Google input gate removed: instance and todo answer first; a real miss comes back as the EXPERIENCE sentence, then the bridge parks it and adds the pocket card.
- 18 Aug — phone confusion locked: instance and todo first. Google sentence only when those files are silent. Named send is a desk ask. `DESK_RULES` + EXPERIENCE Flow 3b.
- 18 Aug — founder: phone reports what the desk files already know. Google miss is not a reason to withhold the pocket card. Locked.
- 18 Aug — Fitzpatrick Draft 4 is with them. Follow-up sent to Tommy (Alicia CC) on **Fitzpatrick Castle Tuesday 18th August**. Ball is theirs.
- 17 Aug — desk-bridge fail-closed on Google. Bot reloaded. Model roster in `desk.md`: live `haiku`, `sonnet`, `opus`, `gemini-3-flash-preview`, `gpt-5.6-luna`. Not `kimi-code`, not `gemini-2.5-flash`, not `gpt-5.6-sol`.
- 18 Aug — founder todo split out of this file into `20-studio/todo.md`. This file is the desk diary. `/brief` and `/todo` no longer read it.
- 18 Aug — desk-bridge CoS slice: ranked `/brief` and append-only `LIST+` write-back after a desk ask. Morning push still parked. Google still fail-closed.
- 18 Aug — repeated the 17 Aug Kimi cage on the Telegram CoS panel: `kimi_run` + `kimi-k3` for a short review. Timed out. Cheap `kimi` finished. Logged in `20-studio/desk.md`. Do not do it a third time.
- 18 Aug — resolved the phone stall: owner lock, streamed first/idle/total deadlines, durable queue/outbox recovery, and asynchronous delivery are installed and live. The 17 Aug 451.8s timeout remains the incident record; no live ask was run during this deploy.
- 18 Aug — phone Grok `exit 1` / "Desk hit an error": three of six runs (00:23, 00:30, 08:54 voice) hit `--max-turns 10` after xpoz 401s. Launchd did not load `xpoz.env`. `/status` then showed a getUpdates idle timeout. Fix: load xpoz/moonshot secret files, keep last_error, send any text if the turn limit hits.
- 18 Aug — Fitzpatrick catchup happened. Tommy only; Alicia in London from 19 Aug. Biddy killed. Mid-September still the window, no date held, deposit still unpaid. Notes: Drive doc `Rua Social content catchup - shoot date, deposit, concept review`.
- 17 Aug — tomorrow brief recovered in the dashboard window. 18 Aug 12:00–12:30: Rua Social content catchup with Tommy Cox and Alicia Traynor (Fitzpatrick Castle). Last doc sent: `fitzpatrickcastle_concepts_160726.pdf` on 7 Aug. Thread: Social media references. Shoot pointed at the second week of September.
- 17 Aug — Google live in this Grok window via the built-in connectors
  (Gmail & Calendar, Drive) from grok.com/connectors. Signed in as
  `darragh@ruasocial.ie`. That is the path. The local Google MCP
  servers (`gmailmcp` / `drivemcp` / `calendarmcp` in `~/.grok/config.toml`)
  are not the path and stay unsigned. Gemini CLI is still API-key only
  and is not needed for mail, calendar, or Drive.
- 17 Aug — wrote the Google gap into `desk.md`, then moved it here.
- 17 Aug — opened this file after he asked for a desk list, updates, and a
  separate list for him.

## Founder

### Do

Moved 18 Aug to `20-studio/todo.md`. Do not put open actions back here.

### Ideas

Street captures from the phone. Not the walking brief.

### Planned

- 18 Aug — pickup day rate for FW Earghal: €500/day. His number. Move
  it into an engagement record if one opens.

### Waiting on the desk

- Phone still cannot see Gmail, Calendar, or Drive.
- Phone hung and timed out on 17 Aug. Error report is on Desk → Blocked.
- 18 Aug CoS slice 2: `/brief` + Google miss now return the pocket card from the lists; `/new` cuts the queue; pairing is explained on `/help`.
- Fitzpatrick is with them. Alicia back from London week of 24 Aug, then roof map, bubbles for the coffee hatch, mid-September date, deposit. History is in. Pilates is the in-house instructor.
