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
- A page opens on its own file's board. A browser save from a different source
  revision is never loaded over it. If that save holds edits, it is kept aside
  in the browser (with its soundtrack) and a notice offers to open, download or
  clear it, so edits are never silently lost. Attaching or clearing a
  soundtrack counts as an edit. Each kept copy has its own key, so later edits
  never replace earlier ones. An untouched copy of an older file is discarded.
  Opening kept edits restores their soundtrack and makes them this page's own
  save, so a reload keeps them; edits made since the page opened are kept
  aside first.
- **Clear old browser copies** downloads a JSON backup, then removes this film's
  saves under other storage keys and the kept edits. It never touches the
  current key, a complete-project file's own save, another file's kept edits,
  another film's saves or any file on disk.
- `build --label` records numbered versions in `versions.json` beside the
  manifest and archives the replaced output with a readable name. Rebuilding an
  unchanged board keeps the same version and still archives the replaced HTML
  under a dated name. `--output` review builds to a different destination are
  not versions. The page embeds the list with links to earlier files.
- `save` imports a browser export and builds it as a named version.
- `open` starts a local app server (standard library, `127.0.0.1:4318`, in the
  background) and opens the browser. Projects are chosen with the native
  Finder dialog or from a recent list; the browser never supplies a path.
  Writes need a custom header and a matching project revision, so other sites
  cannot write and a stale window gets a conflict instead of overwriting.
- In the app, edits save to `board.json` (replacement images become
  content-named files), music to `audio/imported/`. Before the first change in
  any ten-minute window, the board, audio and asset references are copied to
  `<earlier>/autosave/` (30 kept). Older board-only snapshots remain readable
  and retain the current music and atlases. Save version calls `build --label`.
  Restore validates its target before keeping the current complete state and
  pruning old snapshots, then loads the named version's board, music and
  images or the automatic save. Invalid media references leave source intact.
  Version saving and Restore pause editing, wait for soundtrack persistence
  and stop on failure. In-progress imports and the video-export dialog must
  finish or close first.
- Project branding and legacy browser storage identifiers are configuration.

## Observe

Run the README checks and build a real external project. Verify panel count,
runtime and media hashes against its source. Open a separate browser test
project, edit/reload/export, then import that export and rebuild it. Check that
the engagement's current-file block agrees with the installed working folder.

## Per-panel sound effects (16 November 2026)

Goal: hear spot effects (a door, footsteps) against the timed board without touching the soundtrack. One optional effect per panel: `sfxPath` on disk, embedded as `sfx` in a page, with `sfxName`, `sfxLevel` (0 to 1), and `sfxIn` and `sfxOut` (start and stop points in seconds into the file; an older `sfxSeconds` length is still read). It starts at the panel's start in the presentation preview, the exporter preview and the exported video. The soundtrack, its offset and its mix settings are unchanged. Verification: `test_panel_sound_effect_round_trips_between_page_and_project`, plus attaching, playing and exporting an effect in a browser.
