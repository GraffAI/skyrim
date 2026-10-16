# AGENTS.md — `projects/skyrim`

A clean-room engine that runs Skyrim Special Edition's stock data (ESM/BSA). The record is
[docs/design/006-m35-skyrim-recon.md](docs/design/006-m35-skyrim-recon.md).

## Rules

- **No Bethesda data in git (I152).** Game install: `~/skyrim-se`. Extracted data and conversions:
  `~/skyrim-data-extracted`. The zone holds code, aggregate statistics and notes in our own words.
- **Clean vs dirty (D289).** Anything informed by reverse-engineered sources (CommonLibSSE,
  Nemesis/Pandora internals) says `DIRTY-SIDE` in its header. Clean code is written from specs.
- **Tools build in `nix shell`**, natively on Apple Silicon; no Wine, no global installs (D290).
- **Steam credentials are the operator's.** An agent never asks for or types them; the operator runs
  `steamcmd +login <user> +quit` once, and agents reuse the cached session.

## Layout

| path | what |
|---|---|
| `tools/bsa` | BSA (v105) extractor |
| `tools/hkx` | HKX → XML conversion recipe and wrappers |
| `tools/census` | the census scripts |
| `census/` | aggregate class/variable/event statistics |
| `semantics/` | per-class notes (DIRTY-SIDE) |
| `NOTES.md`, `TOOLCHAIN.md`, `SCOPE.md`, `ORACLE.md`, `REPORT.md` | the M35 records |
| `ORACLE-HOST.md` | where the oracle runs: host cost and viability (2026-10-16); the host built is `infra/aws/docs/design/006-m38-aws-oracle-host.md` (M38) |
