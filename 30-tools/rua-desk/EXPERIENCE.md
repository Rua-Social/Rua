# Rua Desk terminal experience

How the founder enters the Rua desk from a terminal.

## Foundation

Terminal CLI on the founder's Mac. The terminal owns the visual chrome.
The founder is holding it. Rua owns the words and command behaviour, not
the terminal's pixels.

## Information architecture

| Surface | Reached from | Purpose |
| --- | --- | --- |
| Seat chooser | Bare `rua-desk` in a terminal | Choose which installed harness holds this sitting |
| Direct launch | `rua-desk <seat>` | Open a known seat without the chooser |
| Status | `rua-desk status` or `s` in the chooser | See which seats are installed |
| Operator card | `rua-desk card` or `c` in the chooser | Read `20-studio/desk.md` |
| Seat proof | `rua-desk ping` | Ask each installed harness for one identifying line |

## Voice and tone

| Do | Don't |
| --- | --- |
| Name the seat and repo being opened | Call one harness the desk or default conductor |
| State a missing command and how to fix it | Print a shell stack or silently return |
| Keep the chooser compact | Explain model-routing theory at launch |

## State patterns

| State | What they see or hear | Gap |
| --- | --- | --- |
| Ready | Four numbered seats plus status, card, and quit | None |
| Launching | `Opening <seat> at <repo>` | None |
| Missing harness | `<seat> is not installed or not on PATH.` | Installation itself stays with that vendor |
| Missing repo | `Rua repo not found at <path>. Set RUA_REPO to the checkout.` | None |
| Invalid chooser input | `Choose 1-4, a seat name, s, c, or q.` and the prompt returns | None |
| Unknown direct command | `Unknown Rua desk command: <command>` followed by help | None |
| Non-interactive bare call | Seat status; it never waits for input | None |
| End of input or quit | `Desk closed.` | None |

## Interaction primitives

Allowed: one menu selection, a direct command, or the existing utility
commands. The launcher may inspect installed commands and versions.

Banned: choosing an engine automatically for an interactive sitting,
altering harness credentials, or pretending sessions transfer between
harnesses.

## Accessibility floor

Every choice has a number and a word. Colour and cursor-only interaction
are not required. Every failure the founder can act on is a plain sentence.

## Rejected

- Remembering the last seat — bare `rua-desk` should make the choice visible.
- Interactive `auto` routing — the founder is choosing a full harness, not
  delegating an unattended phone request.
- A graphical launcher — the terminal already supplies the host.

## Success and what not to optimize

Success: the founder chooses any installed seat and sees that harness open
from the Rua repository.

Do not optimize: feature parity between harnesses.

## Key flows

### Flow 1 — Choose a seat (founder, starting work)

1. Run `rua-desk`.
2. Read the four seats and choose by number or name.
3. **Worked:** see `Opening <seat> at <repo>`, then the selected harness.
4. Failure: a missing harness is named plainly and the founder returns to
   the terminal.

### Flow 2 — Open a known seat (founder, resuming work)

1. Run `rua-desk claude`, `codex`, `grok`, or `gemini`.
2. **Worked:** the named harness opens directly in the Rua repository.
3. Failure: an unknown command prints help; a missing executable names the
   missing seat.
