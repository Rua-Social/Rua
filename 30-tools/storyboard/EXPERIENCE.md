# Storyboard session

A director opens the **Storyboard** app, picks a project and edits the board.
The project on disk is the record, the way a Final Cut library is.

## Working in the app

The board leads to panel editing, presentation, director's notes and next steps.
Every change saves to the project within a second; the status reads
"Saved to project · time". There is no Save button to remember. Cmd+S, or
**Save version…** under **Versions**, names a version and updates the
shareable HTML. **Versions** lists named versions and automatic saves (every
ten minutes while editing) with **Restore**; restoring keeps the board, music
and frames you had first. Editing pauses during Save version and Restore.
If music has not saved, either operation stops and explains how to keep it.

If a save fails, a message above the board says why and the page keeps the
work. A second window on the same project stops saving and asks for a reload
rather than overwriting newer work. If the app has been quit, the page says
so and points to Export → Editable backup.

Success: the director never thinks about saving, can always step back to an
earlier state, and the shareable HTML matches the last named version.

## Standalone files

A built HTML opened from Finder still works for clients and reviewers. Its
edits save only in that browser. Opening a rebuilt file always shows that
file's board. Edits made in this browser on an earlier version are kept aside,
and one notice offers to open, download or clear them. Only a complete-project
export carries the soundtrack with the board; `rua storyboard save` brings it
back into the project as a named version.

The command line reports panel count, duration, soundtrack status and backup
locations. Invalid source or missing media stops the operation.
