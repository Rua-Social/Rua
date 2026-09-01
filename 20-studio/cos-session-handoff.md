# Desk / CoS session handoff — 18–19 August 2026

For a hostile review in a **separate** `tools` window on
`/model kimi-code`. Full hands. Not `kimi_run`. Not K3.

This file is a session synthesis. It is **not** doctrine, **not**
the todo, **not** the phone contract. If it disagrees with
`30-tools/desk-bridge/EXPERIENCE.md`, `spec.md`,
`00-system/skills/rua-todo/SKILL.md`, or `20-studio/desk.md`,
those files win.

Ask of this review: pressure-test the **logic of the solutions**,
especially what is shipped vs only designed, the contradictions,
and what would be wrong to build next. Do not implement. Do not
add a bot, a folder, or a skill unless the finding is that the
handoff itself is the miss.

---

## 0. What this product is

`@Rua_desk_bot` (`30-tools/desk-bridge/`) is a **Telegram seat**,
not a chief of staff product and not a fifth Grok room.

A launchd process on the Mac takes an owner-locked DM or voice
note, runs one `grok -p` (or Claude if `DESK_ENGINE=claude`) in
`~/Rua`, and texts back one short result.

“Filter like a chief of staff” is a line in `DESK_RULES`. At the
start of the session it had almost no mechanism behind it.

Phone constraints that stayed locked the whole session:

- One human. Groups ignored.
- One Grok ask at a time. Five-minute budget. No subagents.
  No four-seat fan-out. Never Kimi on the phone.
- Voice inbound only (ElevenLabs Scribe). No TTS.
- Google Workspace fail-closed. Dashboard connectors stay on
  grok.com. Not Mail.app / Calendar.app.
- Telegram owns the pixels. Text out. File attachments parked.
- Success (`EXPERIENCE.md`): from a voice note or a text, the
  founder knows the result without opening a laptop.
- Do not optimize: session length, turn count, desktop
  completeness, engagement.

Founder context that changes the answer: owner-operated, small
client load, control of time, not org growth, not automating
himself out of craft. `20-studio/founder-context.md`.

Repo law: skills / tools / agents only when the trigger is real.
No `agents/`, `orchestration/`, `projects/` minted to complete a
diagram. `AGENTS.md`.

---

## 1. How we got here (honest)

The founder asked how to make the Telegram CoS “way better.”

**Conductor’s first take (wrong, overturned).** Unlock Gmail /
Calendar / Drive on the phone. That is the job a CoS does, and
`lists.md` already said the phone was waiting on it.

**Blind panel (same brief, no shared conclusions).**

| Seat | Highest-leverage change |
| --- | --- |
| Grok 4.5 | Rank `/brief` from Git. Instant. No Google. No push. |
| Sonnet | Morning push of the *existing* pocket brief. |
| Gemini | Morning push, plus ping when Blocked clears. |
| Kimi k2.6 | After a desk ask, append real actions back into the list. |
| GPT-5.6 Luna | Codex usage cap. No review. |

All four finished seats said: do **not** put Google on the phone,
do **not** build an agent or a second memory store. The memory
already existed as files. Shared kill risk: **noise**.

**Process miss, 18 Aug.** The conductor ran `kimi_run` + `kimi-k3`
for that short panel. That is the 17 August 240s reader cage,
already written in `desk.md`. It timed out. Cheap `kimi` finished.
Logged in `20-studio/desk.md` (**Kimi: do not repeat 17 August**)
and in `lists.md` Done. For *this* review: `/model kimi-code` in
`tools`. Do not `kimi_run` this file.

**Approved then shipped (slice 1).** Write-back after a real desk
ask, then rank `/brief`. Morning push parked. Google stays
fail-closed.

**Then the founder rejected the list itself.** Todos were leaking
into diary, incidents, `/brief`, client notes, chat. That forced
the split below. It also means the first shipped slice was
pointed at the wrong file (`lists.md`). The mechanism survived.
The home changed.

---

## 2. Solutions that are live

### 2.1 Ranked walking card

`/brief` is not first-bullet order. It ranks a gated Do, and one
live client card retrieved with `rua vault` when that engagement
is the job.

After the split, `/brief` reads **`20-studio/todo.md` only**, plus
that client card. It does **not** read `lists.md`.

`/todo` dumps the open list. Empty: `Nothing open.` Full:
`Todo is full. Close one.`

### 2.2 Append-only write-back (`LIST+`)

After a real desk ask (not park / idea / brief / todo / status /
Google miss), Grok may end with at most two hidden trailers:

```
LIST+ Do | one short action
LIST+ Done | what landed
```

The bridge strips them from Telegram. `Do` appends once to
`todo.md`. `Done` moves a matching open line to `todo-done.md`.
Duplicates skipped. Junk skipped. Cap 7. Grok must not edit those
files itself. No second model call.

Moving / Blocked trailers still go to the `lists.md` diary.

### 2.3 One todo, self-regulating

| File | Job |
| --- | --- |
| `20-studio/todo.md` | Open actions only |
| `20-studio/todo-done.md` | Closed log. Not briefed. |
| `20-studio/lists.md` | Desk diary + ideas + planned notes. Not the todo. |

Rules (skill `00-system/skills/rua-todo/`, also enforced in
`bridge.py`):

- Line: `- YYYY-MM-DD One concrete action.`
- Cap 7 open.
- After 7 days: `STALE`.
- Refuse: duplicates, niceties, system notes (phone/gmail/kimi/
  launchd/desk-bridge…).
- Any seat that needs the list reads `todo.md`. Nobody writes
  todos into `lists.md`, `desk.md`, client READMEs, or chat.

Treat current `todo.md` as source of truth. Named-client actions
are not stored in Git.

`AGENTS.md` start-of-chat now has a **Founder todo** class.

### 2.4 Instant capture, still on the same bot

`/park` and `/idea` do not run Grok. Short idea → Founder → Ideas
on `lists.md`. Long idea → `20-studio/ideas/<stamp>.md` (directory
created on first write; it may not exist yet). `/brainstorm` is a
short Grok think, not a deck.

### 2.5 Tests and install

`python3 30-tools/desk-bridge/test_bridge.py` was green (107 after
the todo split). `--check` and `--install` reloaded the live job.

---

## 3. Solutions designed, not built

These are the answers the session converged on. They are **not**
in the bridge yet unless a file above already says so.

### 3.1 Promotion tree (breadth for the CoS)

Four kinds of thought were sharing one file. That was the leak.

```
spark          street capture, no commitment     /park /idea
held thought   long enough to keep               20-studio/ideas/
project        named, one next move, or it dies  a sentence, not a folder
commitment     founder owns doing it             todo.md only
paid job       client, scope, money              rua vault
```

**Project is a class decision** (“this is sales”), not
`20-studio/projects/`. A Project Shepherd / PM seat is a **role
you pull** after that sentence exists. It is not a second
Telegram personality and not an `agents/` directory.

Three shapes considered:

1. Status headers on idea files — cheap, folder will rot.
2. One index `20-studio/projects.md` (live projects only, cap/
   stale like the todo). Ideas stay wild. `/brief` never reads
   it. **Recommended if an index is ever earned.**
3. Full `projects/` tree + standing PM — how `lists.md` happened.
   Do not.

Not built. Do not mint the index until the hole after “idea” is
a weekly friction, not a diagram gap.

### 3.2 Unclear voice / ramble (phone UX)

**Today:** transcribe → `Voice note:` → one `grok -p`. No
classify. A ramble can still emit `LIST+` and become a walking-list
lie. Session `--resume` already exists.

**Blind swarm on this** (Kimi k2.6, Sonnet, Gemini, Grok 4.5,
plus CoS / UX / workflow as general-purpose). Named specialist
types failed on the wire; same prompts ran as general-purpose.

Agreed: do **not** guess onto `todo.md`. Do **not** put agents
on Telegram. Trail is a **file**, then a **dashboard room** at
sit-down.

Split (this is an open fork — see §5):

| Seat | When the note is unclear |
| --- | --- |
| UX | No interview. Frozen lines only: `Heard. No line.` / `Not a line yet. Say the action.` / `Already on the list.` |
| Sonnet | The one short result *is* one clarifying question. Next note resumes the session. |
| Kimi / Grok 4.5 / CoS | One paraphrase + tiny menu: act / park / say more. Write nothing until he answers. |

Conductor recommendation to lock: **UX refuse**, plus a **bridge
hard-refuse** on `LIST+ Do` unless the speech already contains one
founder-owned action and a name already on `todo.md` or in
the vault. Grok will keep writing tidy trailers because a
clean line looks like handling the ask. Doctrine alone will not
stop that. The tell: `/todo` grows things he cannot do from the
street.

If he wanted it held, `/park` and `/idea` already exist. Do **not**
auto-park rambles. Venting is not an idea.

Not built.

### 3.3 How a ramble becomes a brief or a goal

Phone never fans out.

```
ramble  →  refuse, or /idea file
        →  desk names the class          (sales / job / tools / papa)
        →  that room reads the file
        →  todo.md only if he owns a next action
        →  rua vault only if it is a real named job
```

`kimi_run` + `kimi` for a cheap first extract on the dashboard.
`/model kimi-code` in `tools` for a write. Hostile / 1M:
`/model kimi-k3` in a look room, not as a child for a short
review. `ai-cli` for a second opinion. Git is the bus.

Two finishes, not one pipeline: a closed todo line, or a real
artefact (SOW, spec, deck) in the class’s existing files.

`/desk-brief` is the sit-down org scan. Phone `/brief` is the
pocket card. They are not the same.

### 3.4 More Telegram bots / groups / “agents that ask”

A bot per agent is `lists.md` in Telegram form. Job titles as
chats. Then the CoS has to clean it.

A **second bot is earned only when the session law is different**,
not when the vibe is different.

| Seat | Allowed | Forbidden |
| --- | --- | --- |
| CoS (keep) | `/todo`, `/brief`, close a loop, one punchline | Rambles, interviews, decks |
| Dump (maybe later) | Voice/text in, file out, “Held.” | Todos, questions, doing the job |
| Delivery (maybe later) | Push a file or still *to him* | Conversation |

At most two inbound seats and one outbound pipe. Creative /
marketing / design are **dashboard classes**, not three more
bots. A group where specialists interview him on a footpath is
the walking-interview failure, times N.

**Keep CoS clean on the same bot first** (refuse `LIST+` on
rambles; use `/idea`). A second bot is a new host → spec path,
own `EXPERIENCE.md`, never writes `todo.md`, never asks a
question.

**Content delivery** is a different product: outbound file push.
Attachments on this bridge are already parked. Do not hang
delivery on the CoS thread or a creative group. Clients do not
join.

**Do not build** a creative / marketing / design bot or a
question roster until the same-bot refuse/park path has failed
for a week. Tell: he opens CoS and cannot find the last
punchline because the thread is full of rambles he *wanted* to
keep.

---

## 4. Explicitly not solutions

Left parked or refused on purpose:

- Google / Space connectors on phone `grok -p`
- Morning push of `/brief` (Sonnet/Gemini; parked until the card
  is trusted)
- Automatic engine fallback
- TTS, images, video notes, official Telegram plugin
- Custom agent file, persistent Grok leader, `agents/`
- Phone subagents, Kimi on the phone, four-seat fan-out
- Classifier / pending-question state machine / Telegram
  keyboards
- `20-studio/projects/` or a room per idea
- Opening the bot to anyone else
- Chunked replies `1/2`, split voice-fail causes (older parked
  polish)

---

## 5. Open forks (founder has not locked)

1. **Unclear-note UX:** frozen refuse vs one question vs
   paraphrase menu. Conductor vote: refuse + bridge refuse on
   bad `LIST+`.
2. **Project index:** none vs `projects.md` when the idea→class
   hole is weekly. Conductor vote: none until that friction is
   real.
3. **Second Telegram bot:** not until same-bot cleanliness fails.
4. **“Project manager”:** file-walking role vs second Telegram
   personality. Session answer: role, pulled by class, never a
   bot.

---

## 6. What “done” would look like if the designed slice shipped

Phone:

- A named action he owns still becomes one `todo.md` line, no
  `LIST+` on screen.
- A ramble does **not** become a todo. He sees one frozen
  sentence, or he `/idea`s it.
- `/todo` stays ≤7, no Gmail/Kimi/launchd lines.
- `/brief` stays a pocket card, not a studio log.

Sit-down:

- An idea file plus a named class is enough for `sales` / `job`
  / `tools` / `papa` to start. No new tree required.
- Parallel model work stays in the dashboard, same rules as
  `desk.md`.

---

## 7. Files to read before judging this

- `30-tools/desk-bridge/EXPERIENCE.md`
- `30-tools/desk-bridge/spec.md`
- `30-tools/desk-bridge/bridge.py` (`DESK_RULES`, `LIST+`,
  `todo.md` helpers, `handle_voice`)
- `00-system/skills/rua-todo/SKILL.md`
- `20-studio/todo.md`, `todo-done.md`, `lists.md`, `desk.md`
- `20-studio/founder-context.md`
- `Agents.md` (proportionality + founder-todo class)

---

## 8. What we want from you

1. Where is the logic wrong or two solutions in conflict?
2. Is the live todo split enough, or is the next slice the
   ramble-refuse (3.2) before any tree or second bot?
3. What would you refuse to build that this note still leaves
   tempting?
4. Anything important the session treated as a solution that is
   actually a new leak?

Do not write implementation files. Do not create
`projects/`, a bot, or a skill to complete the picture. Flag
friction. Let the founder decide.
