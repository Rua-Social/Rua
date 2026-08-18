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
- 18 Aug — Ecoplex reference links parked in `10-clients/ecoplex/links.md` (9 TikTok, 1 IG reel, 1 IG story). Waiting on what they are for.
- 18 Aug — Fitzpatrick Draft 4 change set written in the instance record, not issued. Waiting on go-ahead to reissue the concepts file. Reply draft still on Tommy's thread. Alicia back week of 24 Aug: roof map, bubbles yes/no, mid-September date, deposit.

### Done

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

- Send the Fitzpatrick reply (Gmail, thread **Fitzpatrick Castle Tuesday 18th August**). Review before send. Do not send the unused recap on Social media references.

### Planned

- Catch-up with Tommy and Alicia early in the week of 24 Aug, once Alicia is back from London. No new deck.

### Waiting on the desk

- Phone still cannot see Gmail, Calendar, or Drive.
- Phone hung and timed out on 17 Aug. Error report is on Desk → Blocked.
- 18 Aug CoS slice on the phone: false Session-reset after MCP success is off; `/status` shows keep/reset; bare `status` and unknown `/` are commands. Live DM to confirm follow-up memory.
- Fitzpatrick: Alicia back from London, then roof map, bubbles for the coffee hatch, mid-September date, deposit. History is in. Pilates is the in-house instructor.
