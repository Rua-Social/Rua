# Delivery and closeout

Stage 8. Two artifacts close the sprint: the delivery ledger and the handover document. Both are built
here, after the cuts exist. The per-asset edit guides and the master transcript cut that feed this stage
are produced with the reel-edit-guide skill, not this one.

The Skehans handover is the worked example: a nine-page document that reconciles what was planned
against what landed, walks the client through every piece, flags what is still waiting on them, hands
over ready-to-lift copy, and says where it lives and what happens next.

---

## The delivery ledger

The ledger reconciles three numbers:

- **Conservative floor.** What the shot list committed to as a planned minimum. On Skehans this was the
  floor count carried in the shot list capture summary.
- **Landed.** What the shoot actually produced, counted from the final asset list. On Skehans this came
  in above floor.
- **Upside ceiling.** The higher figure if masters get clipped into individual assets. On Skehans the
  food master is the clearest case: cut into individual dish videos it lifts the count toward the
  ceiling. This is held as an option pending the client's call, not counted as delivered.

State all three plainly so the client sees the floor they were promised, the number they got, and the
headroom still available. Do not inflate the landed figure with the upside. Keep the upside as a clearly
marked "if we clip the masters" line.

On the handover cover, the three numbers run as a hero row (the landed figure carried as the large
hero), then a full ledger table inside lists each concept with its planned and landed counts and a note.

---

## Handover structure

Page order, following the Skehans handover:

1. **Cover.** "Delivered." The sprint named, with the ledger hero row (floor, landed, ceiling).
2. **The numbers.** What the sprint produced. The full ledger table, concept by concept.
3. **What we made / 01, the people.** The interview and portrait pieces (on Skehans: the View pieces,
   Douglas, Chai, Julius, the regulars). One block per piece with a kicker, a line of description, and
   a pull quote of the strongest line where there is one.
4. **What we made / 02, the pub's character.** The place and atmosphere pieces (memorabilia, exteriors,
   the comment-bait formats).
5. **What we made / 03, the voices and the views.** The vox pop and view pieces.
6. **Status, ready now and one word from you.** The short list of assets held pending client input.
   Each gets a clear reason. On Skehans: Grant (held on the no-religion rule and consent), the dishes
   (the clip-the-master decision), and the Blindboy co-post (a planned collaboration to co-post, not a
   licensing issue).
7. **Suggested copy.** Captions ready to lift, two columns, grouped. Each caption is six words or fewer
   and pulled from a real line in the footage. Tag anything that is on hold, a co-post, or carries a
   note.
8. **Handover, where it lives and what is next.** Where the assets sit (on Skehans, Frame, with the
   Frame instructions), the posting guidance (drip the assets out over time, do not dump them all at
   once), and a pointer to the copy.
9. **Sign-off.** A closing line in the house serif, with Rua Social contact details.

---

## Pending items

Anything that cannot ship without the client's word goes on the status page with a plain reason, never
buried. The three Skehans holds are the template for the kinds of reasons that qualify:

- An editorial-rule or consent hold (Grant: the no-religion rule plus consent, held for client review).
- A production decision the client owns (the dishes: whether to clip the food master into individual
  videos, which is what moves the count toward the ceiling).
- A collaboration to coordinate (the Blindboy co-post: agreed as a co-post, so it waits on the
  co-posting partner rather than on a rights problem).

---

## Suggested copy

Lift captions straight from the footage. Six words or fewer, in the client's voice, no formula. Tag
each one so the client knows its state. The Skehans tags are the set to reuse:

- **hold**, for a caption attached to an asset waiting on client review.
- **copost**, for a caption on a collaboration asset.
- **note**, for anything carrying a production note.

---

## Delivery-specific component CSS

The handover uses the base CSS from `references/document-build.md` plus these components.

```css
/* HERO NUMBER ROW (on the cover) */
.prog { display: flex; align-items: center; gap: 20px; padding-top: 34px; border-top: 1px solid rgba(255,255,255,0.12); margin-bottom: 20px; }
.prog-item { min-width: 96px; }
.prog-num { font-family: var(--serif); font-style: italic; font-size: 46px; line-height: 1; color: rgba(255,255,255,0.5); }
.prog-num.is-hero { font-size: 62px; color: #ffffff; }
.prog-label { font-size: 10px; font-weight: 500; letter-spacing: 0.16em; text-transform: uppercase; color: rgba(255,255,255,0.42); margin-top: 9px; }
.prog-num.is-hero + .prog-label { color: rgba(255,255,255,0.7); }
.prog-arrow { font-size: 22px; color: rgba(124,58,237,0.9); padding-bottom: 16px; }

/* LEDGER TABLE */
.ledger { width: 100%; border-collapse: collapse; font-size: 12px; margin: 6px 0 18px; }
.ledger th { text-align: left; padding: 8px 12px; font-size: 9px; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; color: white; background: var(--night); }
.ledger th.num, .ledger td.num { text-align: center; width: 64px; }
.ledger td { padding: 8px 12px; border-bottom: 1px solid var(--border); vertical-align: middle; line-height: 1.4; }
.ledger tr:last-child td { border-bottom: none; font-weight: 500; background: var(--bg); }
.lg-title { font-weight: 500; color: var(--night); }
.lg-num { font-size: 10px; color: var(--muted); margin-right: 7px; }
.lg-note { font-size: 11px; color: var(--muted); }
.lg-land { font-weight: 500; color: var(--purple); }

/* PIECE BLOCKS (what we made) */
.lead { font-size: 14.5px; color: var(--stone); line-height: 1.6; margin-bottom: 22px; max-width: 560px; }
.piece { padding: 15px 0; border-top: 1px solid var(--border); }
.piece:first-of-type { border-top: none; padding-top: 2px; }
.piece-kicker { font-size: 9px; font-weight: 500; letter-spacing: 0.13em; text-transform: uppercase; color: var(--purple); margin-bottom: 4px; }
.piece p { font-size: 13px; line-height: 1.6; color: var(--body); margin-bottom: 0; }
.pull { font-family: var(--serif); font-style: italic; font-size: 16px; color: var(--night); margin-top: 8px; line-height: 1.35; }

/* SUGGESTED COPY */
.copy-cols { display: grid; grid-template-columns: 1fr 1fr; gap: 0 36px; }
.copy-group { margin-bottom: 18px; }
.copy-group-label { font-size: 9px; font-weight: 500; letter-spacing: 0.14em; text-transform: uppercase; color: var(--stone); margin: 0 0 8px; padding-bottom: 6px; border-bottom: 1px solid var(--border); }
.cap { margin-bottom: 9px; }
.cap-name { font-size: 10px; font-weight: 500; color: var(--muted); display: block; margin-bottom: 1px; }
.cap-line { font-size: 12.5px; color: var(--night); line-height: 1.35; display: block; }
.cap-tag { display: inline-block; font-size: 8px; font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase; padding: 1px 5px; border-radius: 2px; margin-left: 5px; vertical-align: 1px; }
.cap-tag.hold { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.cap-tag.copost { background: var(--purple-light); color: #5b21b6; border: 1px solid #c4b5fd; }
.cap-tag.note { background: var(--bg); color: var(--stone); border: 1px solid var(--border); }

/* SIGN-OFF */
.signoff { margin-top: 26px; padding-top: 22px; border-top: 2px solid var(--night); }
.signoff p { font-family: var(--serif); font-style: italic; font-size: 19px; color: var(--night); line-height: 1.4; }
```

Export to PDF and QA pagination with the same recipe as every other deck (see
`references/document-build.md`).
