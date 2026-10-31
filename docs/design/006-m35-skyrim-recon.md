# 006 M35 — Skyrim: behavior-graph reconnaissance

The long-term goal of `projects/skyrim` is a clean-room, modern engine that runs Skyrim Special
Edition's stock data files (ESM/BSA). This first milestone is narrow: measure how big the job of
interpreting Skyrim's Havok Behavior graphs is. Nothing in it needs Windows or a running game.

## Decisions

- **D287** — The game is Skyrim SE, Steam app 489830, Windows depot, fetched by `steamcmd` into
  `~/skyrim-se` on the machine doing the work. The operator logs in once by hand
  (`steamcmd +login <user> +quit`); an agent never sees a Steam credential.
- **D288** — Extracted data, conversions and XML dumps live in `~/skyrim-data-extracted`, outside git.
  The zone holds only our code, aggregate statistics and notes in our own words.
- **D289** — Notes derived from reverse-engineered sources (the community's headers for the game binary,
  Nemesis/Pandora internals) carry a **DIRTY-SIDE** header. A later clean implementation works from a spec, not from them.
- **D290** — Tools run natively on Apple Silicon, built in ephemeral `nix shell`s; no Wine, no global
  installs.

## Invariants

- **I152** — No Bethesda file, or dump of one, is tracked in this zone. Gate: `zone.toml` refuses
  tracked `.hkx/.bsa/.esm/.esp/.nif/.dds`.

## Exit

`REPORT.md` exists with the class census (`census/census.json`), a toolchain verdict
(`TOOLCHAIN.md`), a scope estimate (`SCOPE.md`) and an oracle design (`ORACLE.md`).
