# Delivery and closeout

Stage 8. Two artefacts close a full sprint: the delivery ledger and the
handover. Both are built after the cuts exist.

Cutting is outside this skill. The night-of cut list is `reel-edit-guide`,
and only after Stage 7b has SRTs on disk. Take the human's instruction for
how the cuts were made, then reconcile and hand over. Do not rebuild the
edit guide inside the handover.

Match the handover to what was sold. A light handover is correct when the
finish is files plus captions. A fuller handover is correct when a floor
was sold and the client needs to see planned against landed.

---

## The delivery ledger

Use this when the scope stated a committed quantity or a conservative floor.

Reconcile three numbers:

- **Conservative floor.** What was committed as the planned minimum.
- **Landed.** What the shoot actually produced, counted from the final
  asset list. Do not include optional clips.
- **Upside ceiling.** The higher figure if masters get clipped into
  individual assets. Held as an option pending the client's call. Never
  counted as delivered.

State all three plainly. Do not inflate landed with the upside.

On a full handover cover, the three numbers can run as a hero row (landed
as the large figure), then a ledger table listing each concept with planned
and landed counts and a note.

If no floor was sold, skip the hero arithmetic. List what was delivered.

---

## Handover structure

A working order for a full sprint handover. Drop or merge pages when the
job is smaller.

1. **Cover.** Delivered. The engagement named. Ledger hero row if a floor
   was sold.
2. **The numbers.** Ledger table, concept by concept, when a floor exists.
3. **What we made.** Grouped in whatever categories this work actually
   produced (people, place, product, offer, or other). One block per piece:
   a kicker, a line of description, a pull quote of the strongest real
   line where there is one.
4. **Status.** Assets held pending client input. Each gets a clear reason.
5. **Suggested copy.** Captions ready to lift, grouped. Pulled from real
   lines. Tagged if on hold, a collaboration, or carrying a note.
6. **Where it lives and what is next.** Location of the files, how to use
   them, posting guidance if that was part of the sale.
7. **Sign-off.**

Do not force a people / place / voices chapter plan onto a job that was
not built that way.

---

## Pending items

Anything that cannot ship without the client's word goes on the status
page with a plain reason, never buried. Reasons that qualify:

- Consent or a signed release is missing.
- The client must decide whether to split a master into individual assets
  (this is what moves a count toward the ceiling).
- A collaboration or co-post waits on a third party.
- An editorial or legal hold this client has set.

---

## Suggested copy

Lift captions from the footage. Use this client's voice and any length
rule they actually have. Tag each line so they know its state:

- **hold**, waiting on client review
- **copost**, collaboration asset
- **note**, a production note attached

---

## Delivery-specific component CSS

The handover can use the base recipe in `document-build.md` plus these
components. This is layout, not a requirement to use the navy/purple look
when the client has their own assets.

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

Export to PDF and QA pagination with the same recipe as every other deck
(see `references/document-build.md`).
