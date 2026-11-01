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

Open the current HTML named in the record. Select a panel to edit it, use
**Present board** for timed playback, and **Export → Video with music** for the
animatic. Browser saves belong to that browser and file address. They do not
rewrite files, update this repository or back up an attached soundtrack.

Before moving a file, changing browsers or finishing a session:

1. Choose **Export → Save complete project**. This includes edited panels,
   replacement images, attached music and video settings.
2. Save the exported HTML back to the external source project:

   ```sh
   rua storyboard import /path/to/saved-project.html --project /path/to/project.json
   rua storyboard check /path/to/project.json
   rua storyboard build /path/to/project.json
   rua vault current <record-ref>
   ```

3. Open the current HTML again. If a warning says the browser save belongs to a
   different file version, keep a complete-project export, then use **Restore
   original board** to load the rebuilt disk board and soundtrack. This action
   also exports a complete backup first. A failed soundtrack save stops the
   restore and keeps the prior board, with a visible warning. A fresh browser
   can open the complete built file.

`import` makes a complete timestamped copy of the prior source project in its
parent's `earlier/` directory before replacing it. `build` archives an existing
changed output before replacing it. Failed validation leaves the current
project and output intact. Existing music is retained when importing JSON or a
review HTML without music; use `--clear-audio` for deliberate removal.
`--expected-panels N` can reject an accidentally selected test board.

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
Keep legacy `storageKey` and `databaseName` values when migrating a project;
changing the browser or address still requires a complete-project export.

The four original contact sheets use eight panels each (`imageIndex` 0–31).
Additional panels can use replacement images or no image (`imageIndex: -1`).
Video export uses the browser's available encoders and runs in real time.
It is a review animatic, with browser-dependent codec support.

## Verify

```sh
python3 -m unittest discover -s 30-tools/storyboard -p 'test_*.py'
node 30-tools/storyboard/test_reset.js
node --check 30-tools/storyboard/src/app.js
node --check 30-tools/storyboard/src/video-engine.js
node --check 30-tools/storyboard/src/video-export.js
```

Tests cover portable builds, recoverable imports, media preservation, invalid
input and restoring the disk soundtrack after backing up browser edits. For
changes to the editor, also check opening, panel editing, reload and
complete-project export in a browser using a disposable project.
See [spec.md](spec.md), [EXPERIENCE.md](EXPERIENCE.md) and [DESIGN.md](DESIGN.md).
