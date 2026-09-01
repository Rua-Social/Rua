# 00-system/

Shared operating machinery for Rua.

This directory contains reusable capabilities and scaffolds that support
work across Rua. Client-specific work, business operations and standalone
software tools live elsewhere.

## Current structure

### `rewrite-contract.md`

How doctrine is written. Binding on every model. Read it before adding a
rule, an example, or a name to a skill.

### `skills/`

Reusable capabilities for recurring work, centred on instructions and
procedures. A skill defines how a task should be performed without
requiring the procedure to be re-explained each time.

Skills are doctrine. No living client names, fees, people, venues, or
proof points. See the rewrite contract.

Standalone executable software belongs in `30-tools/`. A skill may use
those tools.

### `templates/`

Reusable document or data scaffolds for recurring Rua work.

Templates are not finished client work, brand assets, or standalone
software.

### `reference-map.md`

A pointer to the library. Named artefacts are retrieved with `rua vault`.
Consulted on purpose. Never default context for a production chat.

## Boundaries

- Client-specific work → `rua vault`. `10-clients/` is a marker, not a record.
- Rua Social / Rua Studio business operations → `20-studio/`
- Standalone software and internal tools → `30-tools/`

## Adding a skill

Create a skill when a reusable capability is worth standardising.

Keep reusable instructions separate from project and client-specific
inputs.

Give each skill its own directory under `skills/` and document it in
`SKILL.md`. Write new text against the rewrite contract. Do not
search-replace names out of an old memoir.

## Maintaining this directory

Keep this README focused on the system that exists.

Update it when the responsibilities or structure of `00-system/`
materially change, not whenever individual skills or templates are added.

Additional system components should be introduced when a real workflow
creates a clear need for them.
