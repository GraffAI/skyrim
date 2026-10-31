# tools/wall — the wall between the clean side and the plugin (006 M44 I188)

The oracle plugin is GPL-3.0 and lives in its own private repository, outside `world` (006 M44
D355); its build depends on the community's reverse-engineered headers for the game binary.
This zone is mirrored publicly and is what clean-side agents read, so **no clean file here may
name the plugin, its repository, or those headers**. `check` enforces that:

```sh
python3 -I tools/wall/check          # `ok`, exit 0; or exit 1 and the offenders, file:line: token
python3 -I tools/wall/check --list   # every tracked file: dirty, clean, binary or OFFENDS, and counts
```

It reads every file `git ls-files` tracks in the zone (run from anywhere; it finds the zone from
its own path). A file whose first three lines carry the marker `DIRTY-SIDE` (D289) is exempt; a
binary file (a NUL in the first 8 KiB) is skipped; any other file matching the pattern is an
offender. The pattern itself is in `check`, which is therefore marked DIRTY-SIDE: the plugin
repository's name, CommonLib's name for the SSE fork, its C++ namespace prefix, and the SKSE
plugin entry-point prefix. Standard library only, no game data. It is a gate and a hosted gate
of this zone (`zone.toml`).

A file that trips it is fixed one of two ways: it is genuinely informed by reverse-engineered
sources, and gets the marker in its first three lines; or it is clean and named the plugin by
accident, and is reworded. Never the pattern.
