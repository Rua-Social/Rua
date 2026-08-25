# Session handover: France tape edit guide

**Archived 24 August 2026.** Not a run order. Do not paste this as a session opener. Do not drop it in as `CLAUDE.md`.
Release was 21 August, not 28. Cut from `40-papa-rua/EDIT-DAY.md`. Post from `40-papa-rua/POSTING.md`.

The body below is the 20 August 2026 chat. It still says 28 August and that v2 is the source of truth. Both are wrong.

---

## 1. Who and what

**Artist:** Papa Rua. Independent Irish artist, based Meath. Real name Darragh Hoare. Big-voiced emotional performer, underdog independent grind narrative. North star reference is Teddy Swims.

**Producer and collaborator:** Blanka. French producer based in the south of France. Extensive creative relationship spanning several years, roughly two visits a year since 2021. Blanka's own album is out 27 November 2026.

**The asset in question:** a 3h 38m raw recording of the July 2026 sessions at Blanka's place in the south of France. Three brand new songs tracked, all post-album material. Plus an origin story monologue, interviews, and a lot of banter.

**The job:** turn that tape into short-form content for Instagram Reels across a release campaign.

---

## 2. Files you need locally

| File | What it is |
|---|---|
| `raw_files_for_transcript_-_balnkas_recording_sessions__iTT_English__United_States_.itt` | Auto-generated caption file, 2,502 cues. Timestamps reliable, wording rough |
| `france-tape-master-edit-guide.md` | v1 of the guide, 6 July 2026, 20 cuts across 4 batches |
| `france-tape-master-edit-guide-v2.md` | v2, 20 August 2026, output of this session. Supersedes v1 |
| `PAPA_RUA_BRAND_x_CONTENT.pdf` | Brand and content pillars |
| `Papa_Ruaaudiencetimeline_2.csv` | Spotify audience data, 916 rows |
| Lyric PDFs, 10 tracks | Album lyrics |

**To parse the .itt in terminal:**

```python
import re
raw = open('transcript.itt', encoding='utf-8').read()
rows = re.findall(r'<p begin="([\d:]+)" end="([\d:]+)"[^>]*>(.*?)</p>', raw, re.S)
for b, e, t in rows:
    t = re.sub(r'<[^>]+>', '', t).replace('&amp;','&').replace('&#39;',"'").strip()
    print(b.rsplit(':',1)[0], ' '.join(t.split()))
```

Timestamps are `HH:MM:SS:FF` at 25fps. Strip the frame field. Condensing into 20-second blocks brings 2,502 cues down to 471 readable lines, which is the practical way to read the whole thing.

---

## 3. What happened in this session

Darragh asked for a humour and top of funnel pass on the master edit guide. v1 was strong but entirely deep: doubt, grind, origin, craft, collaboration.

**The diagnosis:** all twenty v1 cuts ask a stranger to care about Papa Rua before they have decided they do. That is conversion material aimed at people who already follow. Nothing on the plan earned the first follow from a cold viewer.

**The output:** v2 of the master guide with a light layer of eleven new cuts (A to K) built from banter, mistakes and studio comedy already on the tape, plus a clean alt of the vlog cut.

**Three arguments that carried the recommendation:**

1. Light cuts need no context. The nope supercut works for someone who has never heard a Papa Rua song.
2. Light cuts are dialogue, not music. Standing rule 2 caps intelligible unreleased hook exposure at 15 seconds per cut, which has been throttling post volume. Eleven cuts that barely touch the songs means eleven more posts without burning new material.
3. Nine of the eleven are clean. Before v2 the paid-safe list was effectively three cuts, because most of the strongest v1 material carries f-bombs.

**Standing cadence recommendation:** two light cuts per deep cut. Light runs first in the week, deep runs second. Light earns the profile visit, deep converts it.

---

## 4. The two comedy seams v1 missed

Both were mapped as vocal tracking in v1's segment map and skipped past.

- `[02:16:00 to 02:19:30]` the "nope" run. Blanka rejecting the word "come" roughly eleven times in three and a half minutes. Best comedy edit on the tape.
- `[01:14:00 to 01:34:20]` water breaks, talkback failures, the burp, the producer being right, the "twisted twisted wow wow" harmony stack.

---

## 5. Corrections found in v1 (still outstanding)

- **"Lubricate the system" is at `[01:24:16 to 01:24:36]`, not 02:24:24.** v1 had it in the wrong place entirely.
- **`[01:23:36]` captions read "Listen, perfect bitch?"** Almost certainly "perfect pitch". Affects Cut 12 and Cut K. Do not caption until verified.
- **`[02:16:30]` captions read "Careful of the cum."** It is a producer note about the plosive on the word "come" in the lyric "Come with me". Audio is probably fine, the caption must never go on screen. It sits inside the best comedy run on the tape, so handle it rather than avoiding the whole section.
- `[02:25:36]` "that was hired" is likely "that was hard". Verify.
- `[03:16:24]` "cards in my fingers" is likely "chords". Verify.
- `[01:53:20]` a name garble in Cut 14 that reads like André 3000. If real it becomes the hook of that cut.

---

## 6. Standing rules (apply to every cut, carried from v1)

1. Verify every quote against audio before overlay. Timestamps reliable, wording is not.
2. No clean chorus of unreleased material ever airs. Cap intelligible hook exposure at roughly 15 seconds per cut. Process is the product.
3. Every cut ends on a CTA overlay. Session footage has no natural spoken CTAs. Pre-announce: follow. Post-announce: pre-save Turtle Soup. November batch: Blanka's album link.
4. **Two hard embargoes.** Cut 18 names the album's opening tracks, waits for announce day. Cut 20 is the Tokyo collab reveal, waits for that release. No exceptions.
5. Language flag per cut. F-bombs are fine organic, not for paid.

---

## 7. Release calendar (context for scheduling)

| Date | What |
|---|---|
| 17 April 2026 | *Overthinkin* released, first release back after a multi-year absence |
| **28 August 2026** | ***Turtle Soup***, **eight days out as of this session** |
| October 2026 | *Set in Stone* ft. Sara Lugo |
| 27 November 2026 | Blanka's album |
| 4 December 2026 | Fifth single TBC, paired with headline acoustic gig Dublin 11 Dec |
| 29 January 2027 | *Lovechild* with video, plus album announce |
| 16 April 2027 | Album *Love, Fear: Guilt, Greed*, headline band show 17 April |

Album tracklist: U Got Me, Look Out Below, Lovechild, Overthinkin, Reach Out, No Wrong, Out of My Head, Set in Stone, Travelling, Turtle Soup.

Release sequencing is deliberately staggered around Blanka's own campaign to avoid clashes and support cross-promotion.

---

## 8. Strategic context behind all of this

- **The core problem:** every release creates a listener spike that decays back to a floor. No follow CTAs, no sustain content beyond release week. Campaigns create moments rather than compounding growth.
- **What has actually worked:** roughly 20 organic acoustic performance clips posted since January 2026 drove the most recent upward trend. Acoustic-first content is the proven engine. The France tape is a different pillar (process and behind the scenes), and the light layer is the reach layer on top of it.
- **Best save rates in the whole Spotify history** came from the July 2024 spike, a feature on Blanka's "Take Off". Emotional resonance beats algorithmic reach.
- Tools: Ditto (distribution), Laylo (email capture and pre-save for own audience), Ditto smart link (neutral link for curators and press), Groover and SubmitHub (playlist and blog pitching), Spotify for Artists (editorial pitching).

---

## 9. Working preferences

- British English, Irish voice
- **No em dashes**
- Direct recommendations, not decisions repackaged as further choices
- Checkbox task lists grouped by category
- **One master document, not multiple versions or nested sub-guides.** This is why v2 is a full rewrite of the guide rather than a separate addendum file
- Fan-facing copy: warm, direct, unguarded, specific over polished, avoids AI-sounding language
- Press and industry copy: brief, sensory, context-forward
- Do not reference Rua Social (the agency) in artist-facing materials
- PRINCE2 trained, likes systems and process, not dogmatic about it

There is a project skill at `reel-edit-guide` that defines the output format for edit guides: hook, narrative body with labelled cuts, CTA, with every skipped section labelled and a reason given. Core principles: cut ruthlessly, preserve natural speech rhythm, label every cut, B-roll is story, one narrative thread.

---

## 10. Immediate next actions

**Verify on audio before anything goes on screen**
- [ ] `[02:16:30]` the plosive note
- [ ] `[01:23:36]` the "perfect bitch" garble
- [ ] `[00:00:43]` and `[00:01:09]` the Biarritz mishearing, real or caption artefact
- [ ] `[02:25:36]`, `[03:16:24]`, `[01:53:20]`

**Build this week (pre-release)**
- [ ] Cut A, Nope supercut. Priority, build first
- [ ] Cut F, I'm cooking
- [ ] Clean vlog alt

**Release week**
- [ ] Cut C, I can't hear you
- [ ] Cut E, Japan is in Europe
- [ ] Cut 2, A song born from nothing

**Fortnight after release**
- [ ] Cut B, Water
- [ ] Cut D, So close
- [ ] Cut G, The producer was right
- [ ] Cut 3, Origin part one

**Bank as filler, no deadline**
- [ ] Cuts H, I, J, K

**Still needs shooting, not on this tape**
- [ ] Turtle Soup acoustic vignettes and lyric content. Book the shoot day
- [ ] Full band footage from last summer, referenced on camera at `[02:06:23]`. Locate and audit
- [ ] Sara Lugo and Set in Stone content, comes entirely from elsewhere

---

## 11. If you are picking this up in terminal

Read `france-tape-master-edit-guide-v2.md` first. It is the single source of truth and it contains all twenty v1 cuts plus the eleven new ones with full timestamps, hooks, bodies, payoffs, B-roll notes, language flags and the running order to 28 August.

This handover exists so you understand why v2 looks the way it does. Do not create a v3 as a separate document. Edit v2 in place.
