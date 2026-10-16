# NOTES — the game files this zone was measured against

All numbers measured on `aubron-mini`, 2026-10-15 PDT. Commands next to each.

## Build

| what | value | command |
|---|---|---|
| `SkyrimSE.exe` FileVersion | **1.7.104.0** | UTF-16 `FileVersion` string in the PE version resource (python scan) |
| `SkyrimSE.exe` SHA-1 | `2f784a183f884067a9a41338664b55f6dc198a48` | `shasum -a 1` (matches the depot manifest) |
| `Skyrim - Animations.bsa` SHA-1 | `cf5db82a0641ca126429db4a0ee4989eab7c7348` | `shasum -a 1` (matches the depot manifest) |
| `Skyrim - Animations.bsa` | 65,155,583 bytes, BSA v105, 1,691 dirs, 8,979 files, all LZ4 | `tools/bsa` `bsa info` |

The brief targeted "current 1.6.x"; Steam's current public branch is **1.7.104** (manifests dated
2026-08-24). Whether its behavior data differs from 1.6.1170 is **not verified**.

## Depots (app 489830, `-os windows`)

| depot | manifest | date | files | holds |
|---|---|---|---|---|
| 489831 | 4940892828028256588 | 2026-08-24 19:57:03 | 19 | core `Data/` (ESMs, `Skyrim - *.bsa`) |
| 489832 | 5728778377666085157 | 2026-08-24 19:57:44 | 26 | more `Data/` (textures, sounds, voices, CC content, `_ResourcePack`) |
| 489833 | 4886117324142477814 | 2026-08-24 19:57:59 | 1 | `SkyrimSE.exe` |
| 228986 | 8782296191957114623 | 2018-12-14 | 5 | shared redistributables (from app 228980) |
| 228990 | 1829726630299308803 | 2013-02-18 | 158 | shared DirectX redistributables (from app 228980) |

Command: `DepotDownloader -app 489830 -os windows -username <user> -remember-password -manifest-only`
(listings in `~/skyrim-se/_manifests/`).

## How the files were fetched

`steamcmd` (Homebrew cask, build 1791918946) does not run on this Mac: each launch self-updates
and rewrites `Frameworks/Breakpad.framework/Versions/A/Headers/Breakpad.h`, breaking Valve's
signature seal, and dyld then refuses the framework ("library load disallowed by system policy",
`~/Library/Application Support/Steam/logs/stderr.txt`). An ad-hoc re-sign does not survive the next
self-update.

We used **DepotDownloader 3.4.0** (SteamRE, native `macos-arm64`, zip SHA-256
`60e80c7c496f3f9a079cd3c62036b35d088c27bc0149baf38f009eb57a52f6a5`) in `~/skyrim-se/_tools/`.
The operator logged in once by hand with `-remember-password`; the download then ran with the
cached token and a file list (`~/skyrim-se/_tools/filelist.txt`) instead of the whole 15 GB:

    DepotDownloader -app 489830 -os windows -username <user> -remember-password \
      -filelist ~/skyrim-se/_tools/filelist.txt -dir ~/skyrim-se -max-downloads 16

1,348,471,728 bytes downloaded (2,018,261,520 uncompressed), about a minute.

## Where behavior data lives in SE

SE ships **no** `Dawnguard.bsa`, `Dragonborn.bsa`, `HearthFires.bsa` or `Update.bsa` (manifest listing);
DLC assets are merged into `Skyrim - *.bsa`. Every `.hkx` and animation `.txt` is in
`Skyrim - Animations.bsa`: `Meshes0`, `Meshes1` and `Misc` hold none (`bsa list | grep -ciE '\.(hkx|xml|txt)$'` → 0).
Not fetched: Creation Club and `_ResourcePack.bsa` (Anniversary content), which may carry more behaviors.

Extracted (`bsa extract … -f '*.hkx' -f '*.xml' -f '*.txt'`) to `~/skyrim-data-extracted/raw`:
8,920 files (7,699 `.hkx`, 1,221 `.txt`), 130 MB, 0.5 s; 654 `.hkx` under a `behaviors` path.
Packfile magic `57e0e057 10c0c010` checked on `meshes/actors/character/behaviors/0_master.hkx` (`xxd -l 8`).
