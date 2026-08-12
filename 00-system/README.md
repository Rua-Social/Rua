# 00-system/

Shared operating machinery for Rua.

This directory contains reusable capabilities and scaffolds that support work across Rua. Client-specific work, business operations and standalone software tools live elsewhere.

## Current structure

### `skills/`

Reusable capabilities for recurring work, centred on instructions and procedures.

A skill defines how a task should be performed without requiring the procedure to be re-explained each time. Skills may include supporting references or scripts where these are part of the reusable capability.

Standalone executable software and internal tools with their own purpose or lifecycle belong in `30-tools/`. A skill may use those tools.

### `templates/`

Reusable document or data scaffolds for recurring Rua work.

Templates are not finished client work, brand assets, procedures or standalone executable software.

## Boundaries

- Client-specific work → `10-clients/`
- Rua Social / Rua Studio business operations → `20-studio/`
- Standalone software and internal tools → `30-tools/`

Other top-level directories are described in the root README.

## Adding a skill

Create a skill when a reusable capability is worth standardising.

Keep reusable instructions and supporting resources separate from project/client-specific inputs where practical.

Give each skill its own directory under `skills/` and document its instructions in `SKILL.md`.

## Maintaining this directory

Keep this README focused on the system that exists.

Update it when the responsibilities or structure of `00-system/` materially change, not whenever individual skills or templates are added.

Additional system components should be introduced when a real workflow creates a clear need for them.