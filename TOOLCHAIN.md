# TOOLCHAIN — reading Skyrim SE data on macOS arm64

Verdict: **both halves work natively, no Wine, no Windows.** Measured 2026-10-15 on `aubron-mini`
against build 1.7.104 (`NOTES.md`). Details, commands and caveats: `tools/bsa/RESULT.md`,
`tools/hkx/RESULT.md`.

| job | tool | version | verdict | evidence |
|---|---|---|---|---|
| fetch game files | DepotDownloader | 3.4.0 (SteamRE, macos-arm64) | works | 1.35 GB in ~1 min with a file list; operator login once |
| fetch game files | steamcmd | Homebrew cask 1791918946 | **fails** | self-update breaks Breakpad's code-signature seal every launch (`NOTES.md`) |
| BSA v105 → files | `tools/bsa` (ours, Rust over `ba2` 3.0.1) | — | works | 8,920 files from `Skyrim - Animations.bsa`, 0 failed, 0.5 s |
| HKX → XML | serde-hkx `hkxc` | 2.0.0, commit `2b684a3` | works | 1,763/1,763 non-animation files; `hkxc verify` 7,699/7,699 byte-identical |
| HKX → XML | HavokLib (C++) | — | fails for behaviors | no `hkb*` classes in its source (read, not built) |
| HKX → XML | HKX2Library (.NET) | — | not tried | serde-hkx did not fail |

## Rerun from nothing

```sh
# 1. game files (operator logs in once: add -manifest-only on the first, interactive run)
~/skyrim-se/_tools/depotdownloader/DepotDownloader -app 489830 -os windows -username <user> \
  -remember-password -filelist ~/skyrim-se/_tools/filelist.txt -dir ~/skyrim-se
# 2. BSA extractor
(cd tools/bsa && nix shell nixpkgs#cargo nixpkgs#rustc -c cargo build --release)
tools/bsa/target/release/bsa extract "$HOME/skyrim-se/Data/Skyrim - Animations.bsa" \
  ~/skyrim-data-extracted/raw -f '*.hkx' -f '*.xml' -f '*.txt' -q
# 3. hkxc (pinned build into ~/skyrim-data-extracted/_toolsrc) and bulk conversion
tools/hkx/build_serde_hkx.sh
tools/hkx/bulk_convert.sh graph      # -> ~/skyrim-data-extracted/xml/
tools/hkx/bulk_convert.sh anim 200   # -> ~/skyrim-data-extracted/xml-anim-sample/
```

## Traps

- **`hkxc convert` exits 0 when it fails.** Success is a non-empty output file; the scripts check that.
- **Read XML, not JSON.** JSON drops NaN (14 files fail to read back) and the sign of −0.0. XML
  rounds floats to 6 decimals; 1,174/1,763 files round-trip byte-identical through XML, the rest
  differ only in rounding, unused vector lanes, NaN payloads and a leading space in 5 strings.
- **Classify files by root class, not path**: 428 `hkbBehaviorGraph`, 457 `hkbProjectData`,
  353 `hkbCharacterData`, 475 `hkaAnimationContainer`, 50 skeleton/ragdoll files.
- Spline-compressed animation data stays a raw byte array; decompression is a separate job.
