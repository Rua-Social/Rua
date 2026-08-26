---
name: reel-edit-guide
description: Generate a structured, timestamped edit guide for Instagram Reels from interview transcripts (.itt or similar caption files). Use this skill whenever the founder uploads a transcript, mentions editing a Reel, asks for edit points, wants to identify a hook or money line, or needs to structure interview footage into a 60-75 second short-form video. Triggers on phrases like "edit guide", "cut this down", "find the hook", "what should I use from this interview", or any time a transcript file is provided alongside a request to produce video content.
---

# Reel Edit Guide

Produces a structured, timestamped edit guide from an interview transcript for a 60–75 second Instagram Reel.

## Inputs

- A transcript file (`.itt`, `.srt`, `.vtt`, or plain text with timestamps)
- Context about the subject/brand (provided in conversation or inferred from transcript)
- Target duration: 60–75 seconds (default), adjustable if specified

## Output Format

Produce a guide with four sections:

---

**EDIT GUIDE — [Subject/Brand] Reel ([target duration])**

---

**HOOK (0:00–0:05)**
`[timestamp]`
*"Quote"*
→ Why this line works as a hook. What emotion or curiosity it creates.
**B-roll suggestion:** Visual that would pair well.

---

**NARRATIVE BODY (0:05–0:50)**

For each included clip:
`[start – end timestamp]`
*"Quote or paraphrase"*
→ Why it's included. What it adds to the story.
**B-roll suggestion:** (if relevant)

For each skipped section:
*[CUT — skip [timestamp range], reason e.g. "tangent", "too technical", "pace killer"]*

---

**CALL TO ACTION (0:50–end)**
`[timestamp]`
*"Quote"*
→ Brief note on delivery or overlay text suggestion.

---

## Process

1. **Read the full transcript first.** Don't start selecting until you've scanned the whole thing.

2. **Identify the money line.** The single most emotionally resonant or surprising quote. This usually anchors the middle-to-end of the body section.

3. **Work backwards to find the hook.** Pick the line most likely to stop a scroll. Should raise a question or make a bold claim. Avoid intros, pleasantries, or anything that requires context to land.

4. **Build the body.** Select 3–5 clips that form a logical arc: problem → craft/process → payoff. Cut anything that is tangential, repetitive, or slows pace.

5. **Find or note a natural CTA.** A line where the subject mentions where to find them, what they make, or a clear next step. If none exists, flag it so the founder can add a caption overlay.

6. **Check total runtime.** Estimate read/spoken duration of selected clips. Aim for 45–55 seconds of interview audio to leave room for B-roll pauses and music. Flag if over or under.

## Principles

- **Cut ruthlessly.** A 90-second answer usually has 8 seconds of gold. Find it.
- **Preserve natural speech rhythm.** Don't cut mid-thought in a way that sounds jarring.
- **Label every cut.** Always explain why something was removed, not just what was kept.
- **B-roll is story.** Suggest specific visuals that reinforce the line, not generic "product shot" notes.
- **One narrative thread.** If the transcript covers multiple topics, pick the strongest one and cut the rest.

## Edge Cases

- **No clear hook in transcript:** Flag this. Suggest the best available option and note that a written caption hook may be needed instead.
- **Interview is under 3 minutes:** May not have enough material. Note this and suggest follow-up questions to fill gaps.
- **Multiple strong money lines:** Pick the most emotional one for the body. Note the others as potential hook alternatives or for a second cut.
- **Subject speaks in long, unbroken paragraphs:** Identify natural breath pauses or sentence ends that could serve as cut points. Note them explicitly.
