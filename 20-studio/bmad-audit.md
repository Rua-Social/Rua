# BMAD claim ledger

Research only. Not doctrine. Not a room seed. Do not copy
names, agents, or file trees from this note into operating
files. If a later chat needs the research, open this file
on purpose. Do not load it for a shoot, a sale, or a ship.

Started 17 August 2026 after a first-pass read of BMAD-METHOD
and a request to go deeper into https://github.com/bmad-code-org
without biasing Rua's own files to match what we wanted to hear.

Overturn a line here when a primary source contradicts it.
Do not treat this file as a reason to change `AGENTS.md`,
the rewrite contract, or `rua-ship-gate` until that change is
its own job.

Sources used this pass: BMAD docs site, `CHANGELOG.md` on main,
skill/template files on main, GitHub org (15 public repos),
installer `bmad-modules.yaml` and `platform-codes.yaml`,
selected issues/discussions, Rua files as of this tree.
Stable npm at time of read: `bmad-method@6.11.0` (9–10 Aug 2026).
Main is ahead of that tag.

## Claim ledger (first pass, 17 Aug)

| # | What we said | Verdict | Why |
| --- | --- | --- | --- |
| 1 | Grok is not a BMAD install target | Stale | True of `@latest` 6.11.0 and the install docs. False of `main` after [PR #2732](https://github.com/bmad-code-org/BMAD-METHOD/pull/2732) (14 Aug): `--tools grok` writes `.agents/skills` and `~/.grok/skills`. Use `@next` to get it. |
| 2 | Rewrite contract forbids `_bmad/` at Rua root | Confirmed | `00-system/rewrite-contract.md`: does not authorise "a third-party method (agent roster, `_bmad/`, or equivalent) at the repository root." Root-scoped. Does not by itself ban a sidecar tree. |
| 3 | Generated repo-overview docs make agents worse | Confirmed as *their* claim | [Project context theory](https://docs.bmad-method.org/explanation/project-context-theory/). Studies on that page are unnamed. Their opposite result: a short always-loaded index of *non-derivable* facts helped. |
| 4 | `bmad-document-project` is deprecated; replaced by a small `AGENTS.md` block | Confirmed, flattened | Replacement is `bmad-project-context`: setup / adopt / refresh / record / audit, marked region `<!-- bmad:context -->`. Not a paragraph you type once. |
| 5 | Spec kernel is Why, Capabilities, Constraints, Non-goals, Success signal | Confirmed *now* | Current `spec-template.md` and workflow map. Changelog v6.8.0 still says **Problem**. They renamed it; they did not changelog the rename. |
| 6 | Named agents Mary, John, Sally, Winston, Amelia; Paige on hiatus | Confirmed for BMM defaults | v6.3.0 folded Barry / Quinn / Bob into Amelia. TEA (Murat) and party-mode casts sit outside that five. |
| 7 | Planning artefacts should be deleted after work ships | Overclaimed | Cleanup is for *completed* PRD epics/stories on a brownfield on-ramp. Mid-flight, `_bmad-output/` *is* the store. README still sells durable context. |
| 8 | Fresh chat per build is required | Overclaimed | Quick-fixes: reuse *can* conflict; iterate in the same session after review. Hygiene, not law. |
| 9 | Rua already has most of BMAD in thinner language | Overclaimed | `rua-ship-gate` paraphrases **one** loop: `bmad-build`. It is not the method. See "What Rua does not have." |
| 10 | Rooms already replace named agents | Overclaimed | Rooms are Grok dashboard sessions. Named agents are installed skills with hardcoded identity, menus, and TOML merge. Different objects. |
| 11 | Installing at Rua root would fight `AGENTS.md` and rooms | Overclaimed | The real veto is the rewrite contract plus extra trees. BMad claims it only edits the marked `AGENTS.md` region. Rooms are not deleted by the installer. |
| 12 | desk-bridge is ~875 lines; hugeness is vision not code | Sloppy | About 830 Python lines plus README/spec. Real launchd / Telegram / Scribe seat. "Vision" does not erase that surface. |

## Bias we caught in ourselves

`rua-ship-gate` landed today in commit `2423b02` ("Add a software ship gate and the rewrite contract it depends on"), in the same commit that bans `_bmad/` at root.

Its headings match [Build](https://docs.bmad-method.org/explanation/build/) almost phrase for phrase: compress intent, smallest safe path, one-shot vs plan, diagnose at intent / spec / implementation, park incidental findings.

That is not independent discovery. It is a same-day thin fork of Phase 4, plus a ban on the rest of the church. Saying "Rua already has this" flatters the fork and hides the missing machinery.

## What BMAD actually is (this pass)

Four phases. Implementation always converges on `bmad-build`. Planning is a context factory, not a second ship skill.

- **Analysis (optional):** brainstorm, forge-idea, deep-recon, product-brief, PRFAQ.
- **Planning:** PRD (create/update/validate), UX (`DESIGN.md` + `EXPERIENCE.md`), spec (five-field kernel + companions).
- **Solutioning (scale-dependent):** architecture spine, epics/stories, sprint-planning readiness gate (PASS / CONCERNS / FAIL).
- **Implementation (required if shipping code):** `bmad-build`. Around it: code-review, correct-course, retrospective. Unattended sibling: `bmad-build-auto` / **bmad-loop**.

They have not reconciled two catalogs. `bmad-help` still hard-gates PRD → architecture → epics → sprint-planning → build. Build docs say a clear change enters `bmad-build` directly. Follow the help skill and the build skill and you will be told opposite things.

### Spec Law (current template)

1. Each capability has both `intent` and `success`.
2. Intents are WHAT, not HOW.
3. A constraint that rules nothing out does not belong.
4. At least one non-goal.
5. Success signal is concrete enough to test or demonstrate.
6. Capability IDs are stable. Never reused.
7. Every load-bearing source claim lands in `SPEC.md` or a companion.
8. Lean prose.

`.memlog.md` is canonical. `SPEC.md` is derived and overwritten. Hand-edits die on the next derive.

Architecture is a different artifact: `ARCHITECTURE-SPINE.md` locks only cross-unit invariants. Their own docs disagree on whether the spine derives the spec or the spec adopts the spine.

### Disk they write

```
_bmad/            # method, config, scripts, render snapshots
_bmad-output/     # planning + implementation artefacts
AGENTS.md         # only the marked bmad:context region
.agents/skills    # Grok / Cursor / several CLIs
~/.grok/skills    # Grok global, main / @next only
```

Official default: commit `_bmad/`. Gitignore `*.user.toml`. Personal rules go in home agent config, not the repo.

### What they unlearned (v6, especially 6.11.0)

Generated brownfield docs. `project-context.md`. Story-then-dev-story pair. Quick-dev name. Separate review/editorial skills. Research trio. Readiness as its own skill. Shard/index docs. Distillator. Investigate. Automator (replaced by Loop). Paige, Bob, Quinn, Barry. Cynical reviewer persona (A/B: no lift). Filename-glob artefact discovery (missed `SPEC.md` and `DESIGN.md`).

v6.11.0 deleted more lines than it added. That is their own evidence the earlier catalog was too fat.

## Org map (15 public repos, 17 Aug)

In the installer picker (`bmad-modules.yaml`):

| Code | Repo | Role |
| --- | --- | --- |
| core + bmm | BMAD-METHOD | Bundled. The method. |
| bmb | bmad-builder | Build your own modules. Optional. |
| cis | bmad-module-creative-intelligence-suite | Front-end creativity. Optional. |
| tea | bmad-method-test-architecture-enterprise | Test Architect (Murat). Optional. |
| gds | bmad-module-game-dev-studio | Games. Optional. |
| bmad-loop | bmad-loop | Unattended ship loop. Optional. Early beta. |
| automator | bmad-automator | Archived. Hidden unless already installed. |
| wds | bmad-method-wds-expansion | Deprecated. Hidden unless already installed. |

Not in the picker:

| Repo | Role |
| --- | --- |
| bmad-manticore | Video pipeline (Manny). `--custom-source` only. Closest to Rua's craft. Not evaluated this pass. |
| bmad-plugins-marketplace | Registry. Lags the installer file. |
| bmad-module-template | Starter. |
| bmad-utility-skills | Maintainer toolkit. |
| bmad-method-sample-data | Test corpus. |
| bmad-method-ui | VS Code / web dashboard. Quiet since May. |
| .github | Org chrome. |

Official tables disagree: org profile omits Loop and Manticore; docs install checkbox list omits Loop; marketplace `official.yaml` still lists Automator as experimental.

## What Rua does not have

Do not re-say "we already have this" without naming the missing piece.

- The installer, `_bmad/`, `_bmad-output/`, four-layer TOML, `uv` skill renderer
- Named agents, party-mode, `bmad-help`
- Forge, PRFAQ, deep-recon, product-brief, PRD create/update/validate
- UX two-spine, architecture spine, epics/stories, sprint-status
- Executable `bmad-build` (on-disk spec, review fan-out, local commit)
- Build-auto / Loop
- Review lenses (adversarial, edge-case, verification-gap)
- Project-context skill (verify / prune / record mistakes)
- Correct-course, evidence retro
- Sample-data corpus, CIS, TEA, Manticore

What actually rhymes: one-shot vs spec, park incidentals, always-loaded `AGENTS.md`, skills as procedures. Slogan overlap is not method overlap.

## How they tell people to install (and where that breaks)

Official: install **per project**, commit `_bmad/`. No shipped `--global`, `bmad-link`, or `{bmad-root}`.

If you refuse to put the meta layer in the product repo, the founder (bmadcode) named two workarounds, not a product:

1. Git submodule for `_bmad/`
2. Parent workspace folder, product repos cloned underneath, launch the agent from the workspace; optional separate git for `_bmad-output/`

Issues asking for an external meta repo (#1666) or a global framework token (#1852) were closed with those workarounds. `bmad-link` (#1728) is still open. Nested installs are refused (ancestor-skill collision). Multi-repo / monorepo spanning services has **no official answer** (#1429, #1425).

A knowledge monorepo with a small `30-tools/` folder is exactly the layout they do not support as a first-class install.

Community critiques exist and are individual, not a vote. Recurring complaint: full pipeline is 10–15× for a small MVP; generated docs soaked context and were wrong. Maintainers closed the philosophical version as not a bug. v6.11.0 is their own move toward less dump.

## Contradictions inside their docs (do not flatten)

1. Help catalog requires PRD + architecture + epics + sprint-planning. Build says skip for a clear change.
2. Kernel field 1: Why (live) vs Problem (changelog).
3. `bmad-spec` was core (6.8), then moved into BMM (6.11). Core-only installs no longer get it.
4. Architecture changelog: spine derives SPEC.md. Spec skill: spec derives from memlog; spine is an adopted companion.
5. Correct-course halts without PRD + Epics. Build-direct projects have no documented mid-sprint owner except another Build.
6. `deferred-work.md` removed from the auto contract; quick-fixes page still points at the file.
7. `project-context.md` is dead except where named-agents and spec still mention it.
8. `uv` is a hard halt for `bmad-build`; the installer still never blocks on a missing `uv`.
9. Grok: on main, not in 6.11.0, not in install docs.
10. Roadmap still lists shipped 6.9–6.11 work as in progress.

## Not read yet

- `bmad-prd`, `bmad-ux`, `bmad-create-epics-and-stories` skill bodies
- `bmad-project-context` skill + `references/best-practices.md`
- `bmad-build` steps 2–5 (plan / implement / review / present)
- TEA, CIS, Builder, Loop, Manticore in any depth
- `bmad-method-sample-data` (what a good spec looks like when they write one)
- Customize / expand-for-org how-tos beyond the install-topology quotes
- Discord, YouTube, web-bundles as used artefacts
- Whether ship-gate was written from the Build explanation page, the skill source, or both

## Rules for the next pass

- Quote a URL or a file. If we cannot, mark the line `needs-source`.
- When a Rua file and a BMAD file rhyme, say which was written first if git can tell.
- Do not "improve" `rua-ship-gate` to look more like BMAD in the same breath as reading BMAD.
- Do not install `_bmad/` at the Rua root unless the rewrite contract is rewritten first.
- Manticore is adjacent to Rua's craft. Reading it is a separate job, not a sneaked install.

## Pass 2 — product, UX, design (17 Aug, later)

Open-minded pass. Question: what do they know about software people want to use that a thin ship gate cannot see? Game Dev skipped.

### Compute this pass

- Claude Sonnet (ai-cli, high effort): UX/product judgment. Completed.
- Gemini 2.5 Flash (ai-cli) ×2: volume extract of UX/PRD files, and CIS/WDS/samples/web-bundles. **Both failed** (exit 1, empty final message after fetch). Do not treat Flash as having voted.
- Grok readers in parallel: UX spine (all `bmad-ux` files), PRD/brief/PRFAQ/spec quality, sample-data corpus + Build step-02 + project-context + architecture UX line, hostile-to-cherry-pick org adoption.

### New claims

| # | Claim | Verdict | Source |
| --- | --- | --- | --- |
| 13 | Rua has no UX method for software people *use* | Confirmed as a gap | Ship-gate spec = goal / out of scope / done / observe (command, page, file). No experience layer. Client decks already have tokens in `document-build.md`. Software sessions do not. |
| 14 | BMAD UX is two peer spines, not a mock | Confirmed | `bmad-ux/SKILL.md`: DESIGN.md looks, EXPERIENCE.md behaves. Both win on conflict with mocks. |
| 15 | Named-protagonist journeys are load-bearing for consumer/UX products | Confirmed | PRD skill: "Mary, mom of three — not 'the user'." Validate requires climax beat + failure path. Internal single-operator tools may skip UJ density. |
| 16 | Their sample corpus has no DESIGN/EXPERIENCE files | Confirmed | `bmad-method-sample-data` tree. UX is something skills produce from PRDs. Gold UX-adjacent pattern is UJs *inside* PRDs (Heart Rate Portal, Plantsona). |
| 17 | CIS is ideation, not UX contract | Confirmed | `module-help.csv`: innovation, problem-solving, design-thinking, brainstorming, storytelling. No DESIGN.md writer. |
| 18 | Google DESIGN.md is independent of BMAD | Confirmed | https://github.com/google-labs-code/design.md Apache 2.0. `npx @google/design.md lint`. |
| 19 | A UX file nobody reads is dead output | Confirmed as *their* failure | Issue #1849 (epics ignored UX spec). Later changelog claims #2446 fixed discovery. The failure mode remains the lesson. |
| 20 | desk-bridge already has unofficial EXPERIENCE fragments | Overclaim risk | Phone rules live in `desk.md` + `DESK_RULES`. Not a product contract. Do not promote them this week just because we noticed. |

### What the UX method actually is

Facilitation, not authoring. "Elicit and capture the user's vision, never impose yours. Never volunteer colors, patterns, or directions."

Three Discovery modes: Fast (batch gaps, `[ASSUMPTION]` tags, skip creative tools), Coaching (walk decisions, tools woven in), Design handoff (user runs Stitch / v0 / Figma, save outputs, EXPERIENCE can follow via Update).

Always-on EXPERIENCE sections: Foundation, IA, Voice and Tone (microcopy only), Component Patterns (behavior), State Patterns, Interaction Primitives, Accessibility Floor (behavior), Key Flows.

DESIGN.md is the Google Labs spec: YAML tokens + order-locked prose (Brand & Style → Colors → Typography → Layout & Spacing → Elevation & Depth → Shapes → Components → Do's and Don'ts). Per-color story: why it exists, where used, where *not* used.

**Surface closure:** IA is done when every stated need has a surface, and every surface has a journey that lands there. Probe. Never invent the missing piece.

**Form-factor before IA.** Journeys often derive it.

**Reviewer gate is opt-in.** Hobby may skip. Validate walk: flow coverage, token hex, component on *both* spines, state walk, visual-reference links, bloat, inheritance, shape fit. Verdicts: strong / adequate / thin / broken. No headline grade on UX.

**When they skip UX entirely:** not "has a UI" but "are we changing UX / need new patterns?" Simple updates to screens you are happy with: skip. No UI stories + no UX file: fine.

Examples that show taste, not ceremony:

- Drift (shadcn SaaS): inherit the library; brand is the delta. Banned: infinite scroll, hover-only on small screens, modal stacks > 1. Rejected: streaks, AI-suggested next tasks. Keyboard-first. Named flows (Sarah; Devon and Mara) with climax + failure.
- Quill (native mobile): anti-habit-app. No streaks. Platform type via `note:` fields, not fake px.
- Linen & Logic (editorial, unpaired): Stitch-shaped DESIGN.md only. "Slow Design." EXPERIENCE can arrive later.

There is **no** dedicated UX how-to on docs.bmad-method.org. Method lives in the skill.

### Product quality before code

Analysis is optional but "skipping it means your PRD is built on assumptions." Two doors: brief (gentle) vs PRFAQ (gauntlet). Spec distills; it does not coach. Thin input ("an app for hikers") → stop, send to PRD.

PRD Essential Spine: Vision, Target User (JTBD + UJs), Glossary (no synonyms), Features with testable FR consequences, Non-Goals, MVP, Success Metrics **plus counter-metrics**, Open Questions, Assumptions Index.

PRD rubric judges whether the PRD is *good*, not whether it has headers. Red flags: persona theater, NFR theater, vision theater, activity metrics, "user-friendly" as done-ness. "Be unforgiving" on done-ness.

PRFAQ: no weasel words, mom test, so-what test, no softball FAQs. Verdict: forged / needs heat / cracked.

Sample corpus (~110 artefacts) trains that taste. Planted violations: "users love it," UI-as-capability, vendor soup, mixed concerns. Clean kernels name a behavior, a constraint that *bites*, a non-goal that holds, a success you can fail.

Build's *implementation* spec is a different altitude: frozen Intent + Boundaries + I/O matrix, ~900–1300 tokens, Code Map. Not another PRD.

Architecture does not design UX. It routes to `bmad-ux` if that is the real ask. Spine = invariants so two builders cannot drift.

### CIS (optional module)

| Skill | Code | Job |
| --- | --- | --- |
| Innovation Strategy | IS | Disruption / business model |
| Problem Solving | PS | Systematic problem methods |
| Design Thinking | DT | Empathy-driven HCD |
| Brainstorming | BS | Facilitated techniques |
| Storytelling | ST | Narrative frameworks |

Useful as front-end thinking. Not a substitute for spines. Skip rule they publish: pure technical problems without user interaction, or no time for user validation. Owner-operated tools with one user sit at the edge of that skip.

WDS (Whiteport) is installer-deprecated. Do not adopt a dying module. Its UX instincts are being folded into `bmad-ux`.

Web bundles exist (Gemini Gem / ChatGPT GPT): UX Coach (Norman), PRD Coach (Cagan), PRFAQ (Bezos). Grok is not a bundle target. Plan in a web seat, drop the artefact into `30-tools/<tool>/`. Lowest-commitment way to *run* elicit-don't-author once.

### What a thin engineering culture would reject too quickly

Sonnet's five, kept because they match the primary sources:

1. State Patterns table (cold load, empty, offline, permission-denied, stale) as a pre-ship walk, not a document cult.
2. Counter-metrics ("do not optimize").
3. Written "Rejected — X, because Y" so the next session does not re-litigate.
4. One named-protagonist paragraph with a climax (how they *know* value landed) instead of a persona deck or nothing.
5. Voice Do/Don't table. Cheap insurance against 11pm tone drift.

Also stay curious about: surface closure as a gate question; "elicit, don't author"; stakes-calibrated length; Google DESIGN.md lint *if* we ever own pixels.

### Transferable vs only-if-you-run-the-skill

Portable as plain templates or a chat walk: two-spine split, state table, surface-closure question, UJ shape, non-goals, counter-metrics, glossary discipline, anti-pattern list, Google DESIGN.md.

Only pays inside their machine: memlog.py, Create/Update/Validate resume folders, parallel reviewer HTML, `uv` customization merge, Stitch registry, Sally activation, CIS output under `_bmad-output/`, epics that actually consume UX-DRs.

### Cherry-pick risks (pass 2)

We already stole Build headings into ship-gate. Doing it again with UX headings would be the same mistake with prettier titles.

- Tokens without the "why / where not used" prose become a Tailwind dump.
- State table with no revisit trigger goes stale.
- Journeys without FR/SM cross-refs become fiction.
- Filling section headings solo is cargo-cult elicit-don't-author.
- "WCAG AA" with no contrast target is NFR theater.
- IDs with no downstream reader = #1849 again.
- Copying Drift's Linear look into Rua tools. Rewrite contract already forbids transferring visual devices.
- Improving ship-gate *this week* so it looks like we learned UX.

### Incorporation options that do not touch Rua root

Still not a decision. Options the sources support:

1. Hostile walk of desk-bridge against their UX rubric, in chat, no files.
2. Web-bundle UX Coach on the Gemini seat, once, throw the Gem away after.
3. Hand-write one two-page EXPERIENCE.md for a tool that already has a human session, *if* the walk changes the product. Template earned by a second surface, not by BMAD having one.
4. Parent-workspace sidecar if we ever want to *run* `bmad-ux` for real. Official default still installs into the project.
5. Sally as four lines in the existing `tools` room seed, not a fifth room and not an agent file.

Do not install CIS for this. Do not install at Rua root.

### What pass 2 still did not read

- Manticore (still a separate job)
- TEA Test Architect
- Full `bmad-build` steps 3–5
- CIS skill bodies (only catalog + README)
- Live web-bundle contents
- Google Stitch as a used tool
- Gemini Flash extracts (runs failed)

### Pass 2 rule additions

- A human session is a different failure layer than Intent / Spec / Implementation. Name it if we ever extend the gate. Do not extend the gate in the same breath as reading this.
- desk-bridge is the only current Rua tool whose UX thinness is a product fact, not a missing religion.
- html-to-pdf and animation-renderer do not earn a UX spine. Their own skip rule agrees.

## Pass 3 — CLI map and what we actually made (17 Aug)

### Challenge

The user asked to take every recommendation. Four were rejected this pass:

| Recommendation | Why not |
| --- | --- |
| Parent-workspace BMAD sidecar | Still an install. No first-class support for this monorepo. Parked. |
| UX Coach Gem on Gemini web | A Gem is a user install in another product. We ran the *protocol* on Gemini CLI instead. |
| Org-wide `00-system/templates/experience.md` | One surface does not earn a template. |
| DESIGN.md / ship-gate rewrite / Sally room | Telegram owns pixels. Gate change was the last-pass bias. Rooms stay four plus papa. |

### CLI map (what we ran)

| Job | CLI | Why |
| --- | --- | --- |
| Code and silent-state inventory | Grok explore, this repo | Only seat with the files and ship-gate. |
| Hostile state / surface-closure walk | Claude Sonnet via ai-cli | Adversarial product judgment. |
| Voice table, climax journey, counter-metrics, rejected list | Gemini 3 Flash via ai-cli | The UX-Coach seat without a Gem. Flash 2.5 died last pass; 3 Flash completed. |
| Sidecar / Gem / template | Nobody | Challenged. |

### Concrete artefact

`30-tools/desk-bridge/EXPERIENCE.md`

Bound so it is not dead output (their #1849):

- `spec.md` points at it and says session changes must update it
- `README.md` points at it
- `20-studio/desk.md` phone section points at it

Parked product fixes stay in EXPERIENCE.md. Not built this pass.

Gemini invented a pairing-silent "Do" and an "I see the PRD in the chat" line. Those were dropped. Sonnet's silent-drop journey was kept because the code confirms it.

## Pass 4 — founder overturn (17 Aug)

The founder rejected the pass-3 veto of a ship-gate rewrite,
DESIGN.md, and a Sally room. Research was enough.

What changed in Rua (still no `_bmad/` at root, still no
named-agent file):

- `rua-ship-gate` now trips EXPERIENCE.md when a human holds
  the thing, DESIGN.md when Rua owns the pixels, and diagnoses
  an **Experience** layer.
- `00-system/templates/experience.md` and `design.md`.
- Desk room `sally` was added, then removed the same day.
  The founder did not know what the name was for. The work
  stays in the ship gate and the `tools` room. No extra room.

## Pass 5 — residue audit (17 Aug)

What is allowed to stay in *operating* files (gate, desk,
templates, tools):

| Took | Rua name | Where |
| --- | --- | --- |
| Human session as a contract | `EXPERIENCE.md` | ship-gate, templates, desk-bridge |
| Look when we draw pixels | `DESIGN.md` | ship-gate, templates (no desk-bridge file) |
| Who is holding it, states, what not to optimize | plain sentences | ship-gate, experience template |
| Diagnose session separately from code | Experience layer | ship-gate |

Those two filenames are the only borrowed nouns still in
doctrine. They mean session and look. Rename later if they
get in the way. They are not people.

What must not appear in operating files (research note only):

Sally, Mary, John, Winston, Amelia, Paige, party-mode,
`_bmad/`, installer, Gem, Stitch, memlog, named agents,
climax, protagonist, elicit, spines.

Stripped from gate, templates, and desk-bridge in this pass.
`20-studio/bmad-audit.md` keeps the research words on
purpose. Rooms do not load it.

What stayed challenged: sidecar install, Gem install, copying
Drift's look, navy/purple as brand law.

## Pass 6 — Gemini sense-check taken (17 Aug, later)

The founder accepted Gemini 3 Flash's sense-check of the
review wall and told us to make it live. That is decided.
Operating files already hold it (`fc2883f`). This pass
records the calls so the next chat does not re-litigate.

Kept from that sense-check, in `desk-bridge` and
`EXPERIENCE.md`:

- Private DMs only (`chat.type == "private"`). Groups silent.
- First private DM: "Paired. This desk answers you."
- Fat or gone session: first line is "Session reset. The last
  one was too big or gone."
- Offset written after handle, in `finally`.

Left as product, not a bug:

- `--yolo` on the phone Grok.
- Pairing lock is one Telegram account id, not one Grok window.

Live on this Mac: launchd `com.rua.desk-bridge` runs
`30-tools/desk-bridge/bridge.py --run` from this tree.
`--check` paired to Telegram `2147356885`.

Pairing bug the same day (other session
`01a0115d-626b-7c31-8694-e9deef7a3758`): a test helper bound
`path=SECRETS` at def time and wrote `TELEGRAM_USER_ID=7`
into the real secrets file. Leftover `7` made the live bot
say it was paired to someone else. Cleared. Re-paired as
`2147356885`. Tests pass the path in at the call.

Parked, still not this change:

1. Mark chunked replies (1/2).
2. Ack a message that arrives while an ask is in flight.
3. Split the three voice-fail causes.
4. Bot cannot send files. `DESK_RULES` still mentions one.

Codex slugs from the same day live in `20-studio/desk.md`.
Do not use `gpt-5.6-sol` for this review. Luna at low is
the fast 5.6 pass.

This file is the decision record. Do not reopen install,
named agents, a fifth room, or a ship-gate rewrite unless
the founder starts that job.
