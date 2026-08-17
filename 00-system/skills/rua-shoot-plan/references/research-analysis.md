# Research analysis

How to read a client's social history at Stage 1, and how to turn it into a
concept long-list.

Research is generative, not background. Come out with a clear picture of what
lands with this audience, what does not, and what is missing, and a rough set
of concepts that picture has generated.

Do not import another client's baseline, pillars, or outliers.

---

## What to ingest

When the client has a posting history, pull a recent window of their own
channel (date, format, caption, likes, any saved or shared counts available)
plus a visual scroll of the feed. Numbers tell you what performed. The scroll
tells you why it looks the way it does.

Six months is a working default, not a sacred number. If the useful history is
shorter or longer, say so.

For thin or missing history, flag the gap openly and supplement: competitor
or analogue accounts, the wider category, and any brief material. Do not skip
the read and jump to ideas. Where the read is thin, say that judgement is
carrying more of the direction.

Use the channels they actually use. Do not assume one platform.

## The channel pull (required when a handle exists)

The pull is a file in the instance, not a vibe from a scroll in chat.

Path: `10-clients/<slug>/01-research/channel-pull.json`

Write it before findings. Instagram is the first automated source. A later
TikTok or other pull uses the same shape. The handle lives on the instance,
never in this skill.

Pull the last six months with xpoz (`xpoz__getInstagramPostsByUser`, by
username). Write what came back. Do not wait for a manual export. If xpoz
is missing or the fetch fails, still write the file, mark `gap`, and say
why. Firecrawl cannot read Instagram.

Each item in the pull is one post the machine actually retrieved:

- `id`
- `posted_at`
- `channel` (`instagram`, `tiktok`, or the name of the channel)
- `format` (`reel`, `carousel`, `static`, `story`, `other`)
- `caption` (verbatim, or empty)
- `like_count`, `comment_count`, `view_count` when the source gives them
- `permalink` when the source gives one
- `sponsored` when the source marks it, or when the visual scroll shows it

The pull also records `pulled_at`, `window_start`, `window_end`, `source`
(which tool or API), and `gap` if the window is short or the fetch failed.

### Guardrails

- **No pull, no claimed read.** If the handle exists and the file is missing,
  Stage 1 is incomplete. Run the pull or mark `gap` as thin-history and say
  why. Do not write a format split, baseline, or caption-tone law from memory.
- **Cite the pull.** Findings name posts by `id` and `posted_at`. A pillar
  that cannot point at items in the file is not a pillar.
- **Copy voice comes from captions in the file.** Quote them. Do not invent
  a house style and attribute it to the account.
- **Baseline from the file.** Counts come from the pull. A number that is
  not in the file does not go in Week 0.
- **Sponsored stays separate.** If `sponsored` is true, keep that post out
  of the organic baseline. If the source does not mark paid posts, the
  visual scroll can. Do not count unmarked paid posts as organic proof.
- **Visual scroll still happens.** The file is numbers and text. You still
  look at the feed so you can say why it looks the way it does. The scroll
  does not replace the file.
- **Failed fetch is a gap, not a story.** Do not scrape around a failed
  xpoz pull and pretend it is a read.
- **Do not invent posts.** If the pull is empty, the history is thin. Say so.

This skill does not contain a client handle or an API key.

---

## What to look for

**Format split.** Video versus static, short-form versus in-feed. Establish
which format the account actually rewards, separate from which it posts most.

**Content category.** People, product, place, offer, or whatever recur here.
Which subjects repeat, and which ones outperform.

**Baseline, not peaks.** Find the average of a normal good post once outliers
are stripped. That baseline is the number later concepts are measured against.
Do not let a viral post set the bar.

**Outliers, named as outliers.** Identify what spiked and decide whether it is
a repeatable pillar or a one-off. Calling an outlier an outlier is part of
the job. Do not manufacture a one-off into a category.

**Sponsored and assisted content, flagged separately.** Brand-assisted or paid
posts come out of the organic read so they do not skew the baseline. Note
them. Do not count them as organic proof.

**Caption and tone.** What voice lands. Match what is good and lift what is
flat. The copy voice in the concepts deck comes from here, not from a
previous client.

**Frequency and consistency.** How often they post and how steady it is. This
sets expectations for how output gets dripped out afterward.

---

## The output of this stage

1. A findings summary, structured around the lenses above. This becomes the
   Week 0 deck at Stage 2.
2. A rough concept long-list. Hold it loosely. It is raw material for the
   greenlight call. Do not present it as fixed.

There is no case-study library to read alongside this. Use this client's
material. If the human wants a historical comparison, ask which source to
open. Do not reach for another client's file unprompted.
