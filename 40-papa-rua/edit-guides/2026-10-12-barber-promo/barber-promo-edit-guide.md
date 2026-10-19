# EDIT GUIDE: Papa Rua × Barber Promo Reel (37s)

**For:** tonight's showcase at the National Concert Hall (12 Oct 2026)
**Source:** `IMG_1467.MOV`, 22:58, one locked-off 4K vertical shot from the counter. Timecodes below match the `barber promo` project in the `papa rua NCH` library, where the timeline is the raw clip from 00:00:00:00.
**Rendered cut:** `papa-rua-barber-promo.mp4` in this folder (1080×1920, dialogue only, burned-in captions in Poppins SemiBold, the closest free match to Instagram's own caption font, which isn't publicly available). `papa-rua-barber-promo-clean.mp4` is the same cut with no text, for using Instagram's auto-captions and text tool so everything's in the real Instagram font.

**Runtime note:** this cut runs 37s, under the usual 60–75s reel target on purpose. It's a same-day "come tonight" promo, so shorter keeps people watching through to the ending. The 60s version would add the artist development programme detail (01:49–01:57) and the photo-shoot/tag story (03:20–03:32).

**Framing:** there's no B-roll, so every cut changes framing. **W** = wide (about 1.1× crop, tidies the scarf on the left), **M** = medium (1.5×), **T** = tight (2× on your face, still full 1080 detail from the 4K). Jump cuts that change framing read as deliberate. Cuts that keep the same framing look like mistakes.

**Transcript warning:** FCP's auto-transcript picked up the TV football commentary (00:00–00:24, 11:57–12:30, 14:24+ and other stretches). Lines below were re-checked with a second speech model. Where a line couldn't be pinned down (the barber's question at 00:41), it's cut instead of captioned with a guess. Lowest-confidence captions still in: "The Concert Hall?" (00:37) and "It's part of, like, a showcase gig" (01:38).

---

## HOOK (0:00–0:02.5)

`00:00:24:11 – 00:00:26:22` · **T**
*"I'm playing a gig tonight, actually, so I need to look fresh."*
→ Opens straight on the reason you're there: the stakes and the setting in one line. It needs no context and it explains why you're in a barber's chair.

---

## NARRATIVE BODY (0:02.5–0:32)

`00:00:34:13 – 00:00:38:23` · **W**
*"We're doing the National Concert Hall tonight, so..." / "The Concert Hall?" / "Yeah, yeah. Believe it or not."*
→ Names the venue, and the barber's double-take does the bragging for you. The wide shot gets both of you in for the reaction.

*[CUT: skip 00:39–00:45, the barber's follow-up question. Every transcription heard it differently, so it's cut instead of captioned with a guess]*

`00:00:45:23 – 00:00:48:06` · **T**
*"Last time I was there was with Phil Coulter, actually."*
→ The flex, delivered casually. It follows "believe it or not" without needing the question.

*[CUT: skip 00:48–01:38, IMRO talk / football / venue chat, tangent]*

`00:01:38:12 – 00:01:42:09` · **W**
*"It's part of, like, a showcase gig."*
`00:01:45:15 – 00:01:47:08` · **T**
*"Artist development programme."*
→ Tells people what tonight actually is. The jump cut drops the "I've been doing this..." ramble in between.

*[CUT: skip 01:47–02:50, programme detail and Jafaris. Good for a 60s version, too slow here]*

`00:02:50:13 – 00:02:54:22` · **M**
*"We're all the same hopeless people trying to make our dreams come true."*
`00:02:54:22 – 00:02:57:05` · **W**
*"Not hopeless. It's actually the opposite."*
→ **Money line.** Self-deprecating, then the barber flips it. The cut to wide lands on his reply. The out point stops before he starts his next sentence (~02:57:07).

*[CUT: skip 02:57–03:45, football career talk, photo-shoot tag story (alt for longer cut)]*

`00:03:45:18 – 00:03:49:10` · **M**
*"Would you let me do a little gig in here?" / "Absolutely."*
→ Charm beat. The barber's reply is faint, but two transcription passes agree on "absolutely".

*[CUT: skip 03:49–10:09, IMRO/royalties, venue history, football]*

`00:10:09:14 – 00:10:14:11` · **T**
*"It's just gonna be a very different kind of show in the National Concert Hall. Friends and family."*
→ Second venue mention right before the payoff, and it sets the tone of tonight.

*[CUT: skip 10:14–20:54, rest of the cut. Hair progression carries the time jump]*

`00:20:54:10 – 00:20:56:14` · **M**
*"I'm looking forward to tonight now." / "Feeling good."*
→ The reveal: finished cut, ready to go. **Freeze frame on the last frame** for the ending.

---

## CALL TO ACTION (0:32–0:37)

A plain freeze on the last frame (you leaning into the mirror checking the cut), with no zoom, darkening or title card. A single caption-style line sits at the top: *"Tonight at the National Concert Hall"*. The goodbye is captioned in the normal subtitle spot.
Audio under it: `00:22:41:03 – 00:22:46:12` *"Yeah, happy days. See you later, man. Have a good one. Sound."* The video at that point is the camera being picked up, so only the audio is used.

⚠️ **No spoken line gives the time or tickets.** The freeze-frame line only says what's certain. Put doors time and ticket/guest-list details in the IG caption, or change `END_TEXT` in `build.py` and re-run `python3 build.py`. It renders in under a minute.

---

## Lines to avoid

- **22:30–22:36** "6 weeks, 26th November, trying to give myself time to promote it". That's the *headline show*, not tonight. Don't mix them up in this promo.
- **21:18–21:31** "This is a bit of a lazy way out to post something now" / "No, do it again. Go for it." It's funny and self-aware, but it undercuts a same-day promo. Save it as a stinger or for a behind-the-scenes post.

## Alternative hooks

- 03:46 "Would you let me do a little gig in here?" is playful and works as a cold open if you'd rather lead with charm than stakes.
- 02:50 "We're all the same hopeless people trying to make our dreams come true." It's the strongest emotional line, but it lands better after the setup than as a hook.
