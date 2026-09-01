# DESIGN.md

How it looks when Rua owns the pixels. Not the session.
Not a client deck. Not Telegram or CLI chrome we inherit.

Copy into `30-tools/<tool>/DESIGN.md` when the ship gate
says we own the look. YAML tokens at the top. Prose says
why each token exists and where it is not used.

Do not promote client-deck navy, purple, or any living
job's palette into this file.

```yaml
---
name: {product}
description: {one line}
colors: {}
typography: {}
rounded: {}
spacing: {}
components: {}
---
```

## Brand & Style

What kind of thing this is.

## Colors

Per colour: why it exists, where it is used, where it is
not used. Hex in the frontmatter. A colour without a hex
is not a token.

## Typography

Roles, not a font moodboard.

## Layout & Spacing

## Elevation & Depth

## Shapes

Radii with the reason, not an arbitrary number.

## Components

Visual spec only. Behaviour lives in EXPERIENCE.md.

## Do's and Don'ts

Hard visual rules.

Omit any section that does not apply. Keep this order
when a section is present. Reference tokens as
`{colors.primary}`, not restated hex in prose.
