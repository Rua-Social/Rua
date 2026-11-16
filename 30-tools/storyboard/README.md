# Storyboard

The timed storyboard editor, presentation view and browser video exporter.
The editable JavaScript, CSS and HTML template live in `src/`. A Python standard
library command builds a single offline HTML from an external project folder.
No package installation or hosted service is required. Python 3.10+ is required.

## Find the current project

```sh
rua vault search <client>
rua vault get <record-ref>
```

The engagement record names its `project.json`, current HTML, source images,
reference video, music status and earlier versions. Client data and media stay
outside Git. Do not use a session output directory or a browser timestamp to
decide which file is current.

## Open, edit and save

Open the **Storyboard** app (Spotlight: Cmd+Space, type "Storyboard"). The
home page lists every storyboard on the connected drives (each drive's
`Rua Projects` folder; earlier copies are left out), most recently opened
first. Click one to open it. **Open one from another folder…** is for a
storyboard kept elsewhere: choose its job folder and the project inside is
found. `STORYBOARD_ROOTS` (folders separated by `:`) changes where it looks.
From a terminal, `rua storyboard open
/path/to/project.json` does the same. The apps are made by
`30-tools/install-apps.sh` (see `30-tools/README.md`).

Opened this way, the project on disk is the record, as in Final Cut:

- **Every edit saves to the project as you work.** The status reads "Saved to
  project · 10:42". Music you attach is copied into the project.
- **Automatic saves.** While you edit, the board is copied aside every ten
  minutes, with its music and frame references (the last 30 are kept, in
  `earlier/autosave/`).
- **Save version… (Cmd+S)** names a version and rebuilds the shareable HTML at
  the project's output path, archiving the previous file.
- **Versions** lists named versions and automatic saves. **Restore** goes back
  to any of them; your board, music and frames are kept first as an automatic
  save. Editing pauses while a version is saved or restored. A failed music
  save stops either operation so it cannot silently use a different track.
- If the same project is open in two windows, the second one stops saving and
  asks you to reload instead of overwriting newer work.

The app runs on this computer only (`127.0.0.1:4318`). **Quit Storyboard** on
the home page stops it; the app starts it again.

### Standalone files

A built HTML opened directly from Finder still works without the app, for
clients and reviewers. Its edits save in that browser only. If this browser
holds edits made on a different version of the file, the page keeps them aside
and says so, with **Open them**, **Download them** and **Clear old copies**.

To bring edits from a standalone file back into the project:

1. Choose **Export → Save complete project**. This includes edited panels,
   replacement images, attached music and video settings.
2. Save it into the project and build it as a named version:

   ```sh
   rua storyboard save /path/to/saved-project.html --project /path/to/project.json --label "what changed"
   rua vault current <record-ref>
   ```

`save` is `import` followed by `build --label`. The separate commands still
work. `import` makes a complete timestamped copy of the prior source project in
its parent's `earlier/` directory before replacing it. Failed validation leaves
the current project and output intact. Existing music is retained when
importing JSON or a review HTML without music; use `--clear-audio` for
deliberate removal. `--expected-panels N` can reject an accidentally selected
test board.

## Versions

Each build of the project's own output that changes the board is a numbered
version. Name it with `--label` (or `save --label`); unnamed builds are
"Untitled". The previous file is archived in the project's `earlier` folder
as `<date>_<prefix>-v<NN>-<label>.html`, and `versions.json` beside
`project.json` records number, date, label, panel count, runtime, music and
file. Rebuilding the same board (an editor update, or `--label` to rename the
current version) keeps the same version number; the replaced HTML is still
copied to `earlier` under a dated name. Builds with `--output` pointing elsewhere
are review copies and are not recorded; the project's own output path still
counts as a version.

The built page lists every version under **Versions**, beside the save status,
with links to the earlier files. From a terminal:

```sh
rua storyboard versions /path/to/project.json
```

**Clear old browser copies** in the footer downloads a backup of this film's
older browser saves and the edits kept aside, then removes them from this
browser. The current file's own save, the saves of complete-project files you
are still working in, other projects' saves and all files on disk are left
alone.

## Change the code or board data

Use Rua's branch and PR workflow for changes to `src/` or `storyboard.py`.
Edit the project's `board.json` for panel content, durations, notes and decisions.
Replace or add image files under its `assets/` directory. Update `project.json`
for branding, source audio and output locations. Build and inspect the result
before treating it as current. Changing source data produces a revision marker
so an older browser save cannot silently masquerade as the new disk version.

```sh
rua storyboard check /path/to/project.json
rua storyboard build /path/to/project.json --output /path/to/review.html
```

An explicit `--output` is useful for checking a draft without replacing the
current output. The default build uses `project.json`'s output path. When the
current filename changes, update the engagement's current block and move the
previous file into its named earlier-versions location.

## Project format

```json
{
  "version": 1,
  "storageKey": "unique-project-id",
  "config": {
    "brand": "Project name",
    "exportPrefix": "Project",
    "databaseName": "rua-storyboard",
    "runtimeMin": 60,
    "runtimeMax": 90
  },
  "board": "board.json",
  "assets": {"board-a": "assets/board-a.png"},
  "audio": null,
  "output": "../../01 Working/Storyboard.html",
  "earlier": "../earlier"
}
```

Board, image and audio paths must stay inside the project folder. Output must be
outside that folder and outside the editor source. Relative output and earlier
paths resolve from `project.json`; `--output` resolves from the command's working
directory. Audio can be `{"path":"audio/track.mp3","name":"track.mp3"}`.
Imported replacement images use `customImagePath` on disk and become embedded
`customImage` values in the built HTML.

Optional display config: `strapline`, `eyebrow`, `footer`, `studio`, `byline`,
`heroTitleLines` (plain text array), `heroDeck`, `arcHeading`, `principles`
(`title`/`detail` objects), and `workflowIntro`. Text is inserted as text, not HTML.
Keep one stable `storageKey` per project; a rebuilt file no longer needs a new
key to show its own board. Keep `databaseName` stable too, so **Clear old
browser copies** can find older saves of the same film. Changing browser still
requires a complete-project export.

The four original contact sheets use eight panels each (`imageIndex` 0–31).
Additional panels can use replacement images or no image (`imageIndex: -1`).
Video export uses the browser's available encoders and runs in real time.
It is a review animatic, with browser-dependent codec support.

## Verify

```sh
python3 -m unittest discover -s 30-tools/storyboard -p 'test_*.py'   # includes the app server
node 30-tools/storyboard/test_reset.js
node 30-tools/storyboard/test_studio_client.js
node --check 30-tools/storyboard/src/app.js
node --check 30-tools/storyboard/src/video-engine.js
node --check 30-tools/storyboard/src/video-export.js
```

Tests cover portable builds, recoverable imports, media preservation, invalid
input, complete version recovery and saves overlapping with browser edits. For
changes to the editor, also check opening, panel editing, reload and
complete-project export in a browser using a disposable project.
See [spec.md](spec.md), [EXPERIENCE.md](EXPERIENCE.md) and [DESIGN.md](DESIGN.md).
