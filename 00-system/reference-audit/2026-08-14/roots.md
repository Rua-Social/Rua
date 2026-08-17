# Roots

Read-only metadata audit, 14 August 2026. Scan method throughout: filename, parent
path, extension, logical size and dates only. No file was opened, rendered, extracted,
OCR'd, transcribed or previewed. No network calls. Nothing downloaded or materialised.

## Included

| Root | Storage | Method | Depth | Notes |
|---|---|---|---|---|
| `~/Desktop` | Local (APFS) | Pruned `find` + Spotlight filename queries | 8 | Spotlight indexed |
| `~/Downloads` | Local (APFS) | Pruned `find` + Spotlight filename queries | 6 | 757 top-level entries; the de facto working store for Rua documents |
| `~/Documents` | Local (APFS) | Pruned `find` + Spotlight filename queries | 8 | Spotlight indexed; mostly Codex output, little sprint material |
| `~/Library/Mobile Documents/com~apple~CloudDocs` | iCloud Drive | Pruned `find` (symlinks not followed) | 8 | `Desktop` and `Documents` inside it are symlinks back to the local dirs and were **not** followed |
| `/Volumes/T7` | External SSD (exFAT) | Pruned `find` | 7 | Spotlight reports "unknown indexing state", so traversal was used, not `mdfind` |
| `/Volumes/T7 250925` | External SSD (exFAT) | Pruned `find` | 7 | Spotlight indexing enabled; traversal used for consistency |

## Recorded and excluded

| Root | Reason |
|---|---|
| `/Volumes/Macintosh HD` | Symlink to `/`. Aliases the system root. Excluded. |
| `/Volumes/LUMIX` (exFAT, camera card) | Shallow root check performed as instructed. **No files at the root at all**, so nothing planning- or reference-named. Excluded; not traversed. Spotlight indexing is disabled on it. |
| `/System/Volumes/*` (VM, Preboot, Update, xarts, iSCPreboot, Hardware, Data) | System and recovery volumes. |
| `~/Library` (except the iCloud Drive path) | Application support, caches, containers, Mail, Messages, Keychains, browser data. |
| `~/Pictures`, `~/Movies`, `~/Music` | Photos libraries, Final Cut libraries and caches, Logic projects. A control Spotlight sweep confirmed the only name hits there are Motion Templates, Final Cut Backups and Final Cut Cache: no planning documents. |
| `~/.Trash`, `.Trashes` | Trash. |
| `~/Rua` (the repository) | Deliberately not treated as a discovery root. A control sweep found only the skill files already read. Nothing in it was read, edited or committed. |
| `~/Spitfire`, `~/Splice`, `~/Applications`, `~/voice-transcribe` | Audio sample libraries and app payloads. |

## Pruned during traversal

`.app`, `.fcpbundle`, `.logicx`, `.photoslibrary`, `.imovielibrary`, `.sparsebundle`,
`.framework`, `.xcodeproj`, `.download`, `.lrdata`; `node_modules`, `.git`, `.venv`,
`__pycache__`, caches, `dist`, `build`, `out`, `frames`, `Proxies`, `Renders`,
`Render Files`, `Transcoded Media`, `Original Media`, `Motion Templates`,
`.Spotlight-V100`, `.fseventsd`, `.TemporaryItems`.

Apple iWork packages (`.key`, `.pages`, `.numbers`) were recorded as **single files** and
not descended into, as instructed.

`-P` (no symlink following) and `-xdev` (no crossing into nested filesystems) were set on
every traversal.

## Accessibility and limitations

- Zero permission errors. The traversal error log is empty.
- All six external and local roots were readable in full.
- `/Volumes/T7` returns "unknown indexing state" from `mdutil`, so it is treated as an
  **unindexed root** and covered by traversal only.
- 248 of 1,187 candidates report zero allocated blocks and are treated as **possible
  cloud placeholders** (predominantly iCloud Drive). None were forced to download.
- exFAT does not carry a reliable birth time; on the two T7 volumes `created` and
  `modified` are frequently identical. Dates on those roots should be read as weak evidence.
