# Storyboard source and project recovery

## Result

Keep editor source in Rua and make each external project rebuildable from
plain JSON and media files. The vault record is the entry point for the named
project, current HTML and historical files. A downloaded complete-project HTML
must be importable back into that source without losing images or music.

## Boundaries

No client data, generated HTML, reference video or audio is committed here.
No hosting, automatic cloud sync or collaborative database is introduced.
Existing browser saves are not claimed as recovered merely because a file
has been migrated. Old files remain available until their state is reconciled.

## Behaviour

- `check` validates source and media dependencies.
- `build` embeds source, config, board, images and optional audio in one HTML.
  Replaced outputs are archived; identical builds leave the current file alone.
- `import` parses literal JSON from a browser export without executing scripts,
  extracts media into the project and retains a complete earlier project copy.
- Browser saves with a different source revision produce a persistent warning.
  They are not silently replaced with disk content.
- Project branding and legacy browser storage identifiers are configuration.

## Observe

Run the README checks and build a real external project. Verify panel count,
runtime and media hashes against its source. Open a separate browser test
project, edit/reload/export, then import that export and rebuild it. Check that
the engagement's current-file block agrees with the installed working folder.
