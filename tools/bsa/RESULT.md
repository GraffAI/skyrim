# `bsa` — BSA list/extract tool: result

Status (2026-10-15 22:30 PDT): **builds and passes unit tests on synthetic archives; NOT tested on real
Skyrim SE data** — `~/skyrim-se/Data/` did not exist when the build finished
(`ls ~/skyrim-se/Data` → `No such file or directory`).

## What and why

A ~250-line Rust CLI (`src/main.rs`) over the `ba2` crate (Ryan McKenzie's bsa-rs, 0BSD).
`ba2::tes4` reads BSA v103/v104/v105, handles per-file compression toggles, embedded file names,
zlib (v104) and LZ4 frame (v105) — so the format work is the crate's, not ours. Chosen because it
was the preferred candidate and it built first try on Apple Silicon with no extra system deps
(`directxtex`, a C++ dep used by the fo4 module, compiles with nixpkgs' toolchain).

What the CLI adds:
- `info`, `list [-l]`, `extract` with repeatable `-f GLOB` filters (globset, case-insensitive;
  a glob with no `/` like `*.hkx` matches at any depth; `*` does not cross `/`, `**` does).
- Paths lowercased, `\` → `/`, sorted; nameless entries (hash-only archives) shown as `#<hash hex>`.
- Path-traversal guard: an entry with `..` or an absolute path aborts extraction (archive data is
  untrusted).
- Per-file decompression errors are reported and counted; exit status 1 if any failed.

## Versions (Cargo.lock)

ba2 3.0.1, lzzzz 1.1.0 (LZ4), flate2 1.1.10 + libz-sys 1.1.30 (zlib), memmap2 0.9.11,
directxtex 1.3.0, globset 0.4.20, anyhow 1.0.104.
Toolchain (ephemeral, `nix shell nixpkgs#cargo nixpkgs#rustc`): rustc 1.98.1, cargo 1.98.0.

## Build / run

```sh
cd projects/skyrim/tools/bsa
nix shell nixpkgs#cargo nixpkgs#rustc -c cargo build --release
nix shell nixpkgs#cargo nixpkgs#rustc -c cargo test --release

B=./target/release/bsa
$B info    ~/skyrim-se/Data/"Skyrim - Animations.bsa"
$B list    ~/skyrim-se/Data/"Skyrim - Animations.bsa" -l -f '*.hkx'
# what we need: behaviors, characters, project files, skeletons under meshes/
$B extract ~/skyrim-se/Data/"Skyrim - Animations.bsa" ~/skyrim-data-extracted/raw \
   -f 'meshes/**/*.hkx' -f 'meshes/**/*.xml' -f 'meshes/**/*.txt' -q
# everything:
$B extract ~/skyrim-se/Data/"Skyrim - Animations.bsa" ~/skyrim-data-extracted/raw -q
# -n / --dry-run prints destinations without writing
```

Binary: `target/release/bsa`, Mach-O 64-bit arm64, 1.9 MB (`file`, `ls -la`); links only system
libc++, libz, libiconv, libSystem (`otool -L`) — so it runs outside the nix shell.

## Tested (measured)

`cargo test --release` → `5 passed; 0 failed`:
- `sse_v105_lz4`: builds a v105 archive with `ba2`'s writer (compressed flag, dir+file strings,
  nested `meshes\actors\character\behaviors` dir, mixed-case name), asserts each payload starts with
  the LZ4 frame magic `04 22 4D 18`, then lists (lowercase `/` paths) and extracts with
  `-f *.hkx -f *.xml` (byte-exact, `.txt` excluded), then extracts all.
- `sse_v105_uncompressed`, `le_v104_zlib` (payload starts with zlib `0x78`): same round trip.
- `rejects_traversal`, `glob_semantics`.
- CLI smoke: `bsa --help`; `bsa info /nonexistent.bsa` → error message, exit 1.

## Not verified

- **Any real Bethesda archive.** The round trips use archives written by the same crate that reads
  them, so they prove the CLI plumbing and codec selection, not compatibility with Bethesda's
  writer. First real check: `bsa info` + `bsa extract` on `Skyrim - Animations.bsa`, then compare
  file count against `bsa list | wc -l` and spot-check that `.hkx` files start with the Havok
  packfile magic `57 E0 E0 57 10 C0 C0 10`.
- Embedded-file-name archives, Xbox archives, hash-only archives (no strings) — handled by the
  crate per its source, not exercised here.
- Performance on multi-GB archives (whole archive is memory-mapped; each file is decompressed into
  memory then written).
- Non-UTF-8 names are converted lossily.

## Real-data test (orchestrator, 2026-10-15 22:35 PDT)

Against the 1.7.104 archives (see `../../NOTES.md`): `bsa info` reads all four v105 archives
(Animations, Meshes0, Meshes1, Misc). `bsa extract "Skyrim - Animations.bsa" ~/skyrim-data-extracted/raw
-f '*.hkx' -f '*.xml' -f '*.txt' -q` → 8,920 files, 115,724,036 bytes, 0 failed, 0.51 s real. Extracted
`.hkx` begin with the packfile magic `57 E0 E0 57 10 C0 C0 10` (`xxd -l 8`).
