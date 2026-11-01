# Storyboard session

A director uses one local HTML in a browser to review, time and edit a board.
A code editor and `rua storyboard` maintain its disk source between sessions.

The board leads to panel editing, presentation, director's notes and next steps.
Export offers a complete editable project, review HTML, JSON, print and video.
Only a complete project carries the soundtrack with the board.

Browser autosave success means the current browser holds a copy. It does not
mean a disk file has changed. Storage failure asks for an export. A different
source revision warns that saved browser edits may hide rebuilt disk content;
the user saves a complete copy before restoring the rebuilt board.

The command line reports panel count, duration, soundtrack status and backup
locations. Invalid source or missing media stops the operation. A successful
import still needs a build before the current HTML is updated.

Success is an editable disk project and a matching current HTML, discoverable
through the vault record, with earlier versions available for recovery.
