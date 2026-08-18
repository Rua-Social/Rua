# Lists

Two lists. Files, not a product and not a new agent.

- **Desk** is the conductor's list: blocked work, what it is moving, what it
  finished.
- **Founder** is his list: what he has to do, what he has planned, what he
  is waiting on.

When the phone hits something it cannot do, write it under Desk → Blocked.
Do not design the fix from Telegram. When something moves or lands, update
the line here and tell him in one sentence.

Opened 17 August 2026 from a messy voice note. Enough structure for now.

## Desk

### Blocked

- 17 Aug — asked to open the last Fitzpatrick call transcript on Drive. Phone cannot. Cross-checked the local 16 Jul Gemini export instead (`Social concepts runthrough #1`).
- 17 Aug — phone `grok -p` still cannot see Gmail, Calendar, or Drive. Dashboard Grok can. Fail-closed is live: one EXPERIENCE sentence, no Mail.app.
- 17 Aug — founder confirmed Mac Mail.app and Calendar.app are unused. Real mail and calendar are Google Workspace only. Locked in `desk.md`.

### Moving

- These two lists, so the next blocked thing has a place to land.
- 18 Aug — Ecoplex still WIP. Month-1 pack and cover note sit in `10-clients/ecoplex/`. Links from Victoria are in. Not sent.

### Done

- 18 Aug — Fitzpatrick Draft 4 is with them. Follow-up sent to Tommy (Alicia CC) on **Fitzpatrick Castle Tuesday 18th August**. Ball is theirs.
- 17 Aug — desk-bridge fail-closed on Google. Bot reloaded. Model roster in `desk.md`: live `haiku`, `sonnet`, `opus`, `gemini-3-flash-preview`, `gpt-5.6-luna`. Not `kimi-code`, not `gemini-2.5-flash`, not `gpt-5.6-sol`.
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

- 18 Aug — chase the Fitzpatrick deposit on a dated thread: the
  mid-September window holds on receipt. Draft 4 is with them; the gate
  now locks dates and production, not concept work.
- 18 Aug — send the Ecoplex month-1 pack. Send order is in
  `10-clients/ecoplex/cover-note.md`; pack reprinted with three amend
  rounds, card matches.

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
