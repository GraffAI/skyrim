# REPORT — 006 M35, night one: Skyrim behavior-graph reconnaissance

Run 2026-10-15 22:26 → 23:14 PDT on `aubron-mini`, orchestrated by one agent with Opus
subagents. Everything below was measured on Skyrim SE **1.7.104.0**'s own files unless it is
marked as an estimate. Each linked file gives the command for its numbers.

## Key numbers

| | | source |
|---|---|---|
| behavior graphs | **428** (plus 353 character, 457 project, 328 skeleton files) | `census/CENSUS.md` |
| node instances / node classes | **33,630 / 47**; 9 classes cover 90%, 25 cover 99% | `CENSUS.md` §5 |
| largest graph / median | 2,711 nodes (`mt_behavior`) / 11 | `CENSUS.md` §2 |
| state-machine nesting | 14 in one file, 21 across 95 behavior references (all resolve) | `CENSUS.md` §2 |
| contract surface | 696 variables, 4,773 events, 75 character properties | `CENSUS.md` §3 |
| engine-written inputs | ≈107 real inputs (264 read-only minus ≈157 constants); 225 graph-written, 61 of them read only by the engine | `semantics/contract.md` §1 |
| events | 1,884 engine-sent only, 742 graph-raised only, 547 both | `contract.md` §2 |
| data-driven share | **89%** (1,677 of 1,884) of engine-sent events are named by data: IDLE/RACE records (4,370 IDLEs, 111 condition functions) and Papyrus (14,026 scripts parsed); ~122 actor events stay hard-coded | `contract.md` §3 |
| animations | 5,936, all `hkaSplineCompressedAnimation`, 4.15 h, 30 fps; 1,857 carry annotations | `CENSUS.md` §4 |
| ragdolls | 48, trees of 3–48 capsule/box bodies, two constraint types (ragdoll 53%, limited hinge 47%) | `semantics/skeleton-physics.md` |
| sound / animated objects | 725 of 751 sound payloads (96.5%) resolve to SNDR editor IDs; 72 of 80 ANIO IDs appear as payloads | `contract.md` §3 |
| modifiers needing only the graph | 2,406 of 2,974 instances | `semantics/modifiers.md` |

## Toolchain verdict

Everything is **native on Apple Silicon, no Wine and no Windows** (`TOOLCHAIN.md`):
- **Download:** DepotDownloader 3.4.0 fetches the game. steamcmd does not run on this Mac (its
  self-update breaks a code signature on every launch; `NOTES.md`).
- **BSA:** our `tools/bsa` (Rust over `ba2` 3.0.1) extracts the archives.
- **HKX:** serde-hkx 2.0.0 converts every behavior, character, project, skeleton and animation file
  to XML. `hkxc verify` round-trips all 7,699 `.hkx` byte for byte. HavokLib has no behavior
  classes.
- **Census:** `tools/census` (Python, deterministic) produces it.
- **Model:** `model/` (strict TypeScript, zero dependencies) loads all 428 graphs in ~0.65 s and
  matches the census exactly.

## Scope estimate (`SCOPE.md`)

**The interpreter is months; vanilla parity is years.** An interpreter that steps all 428 graphs is
roughly 3–5 engineer-months (estimate). The vocabulary is small and the data regular: every
transition is event-driven, there are no chooser states, no generator transition effects and no
additive blender use. Matching Skyrim is roughly 1.5–3 engineer-years (estimate), and most of that
is the engine contract around the graph, not the graph:
- the actor controller's locomotion variables;
- the action/idle system with its 111 condition functions;
- the engine's reactions to ~740 notification events;
- the ragdoll and foot-IK stage after the graph.

An oracle is the biggest lever on that number.

Hardest classes: `hkbStateMachine` (wildcards, nesting, event order), `hkbClipGenerator`,
parametric/synced `hkbBlenderGenerator`, `BSSynchronizedClipGenerator`, the ragdoll Controls
modifiers, `hkbFootIkControlsModifier`, and `BGSGamebryoSequenceGenerator` (603 instances, needs NIF
controller playback).

## Deliverables

All under `projects/skyrim/`:
- **Records:** `NOTES.md`, `TOOLCHAIN.md`, `SCOPE.md`, `ORACLE.md` (DIRTY-SIDE design, not
  built), and the record `docs/design/006-m35-skyrim-recon.md`.
- **Census:** `census/census.json` and `census/CENSUS.md`.
- **Semantics (DIRTY-SIDE):** `semantics/{graph-core,generators,modifiers,skeleton-physics,contract}.md`,
  plus `semantics/INDEX.md` with one row per class, 97 rows.
- **Tools:** `tools/{bsa,hkx,census,contract}`.
- **Model:** `model/`.

Shipped as PR #178 (zone, toolchain, oracle; merged) and the Part 2 PR (everything else).

## Corrections made during the night

Two semantics notes first took their counts from non-vanilla copies: a mod's (SOBA) XML and
Pandora's re-serialised templates, which sit 8 bytes off and which `hkxc` rejects. They were
re-measured on the game's own files. Several claims changed:
- Ragdoll modifiers are in the root list of 37 of 57 actor graphs, not "nearly every creature".
- 737 state machines take their start state from a variable, not 461.
- `hkbDelayedModifier` is mod content: 0 instances in vanilla.

## Open questions

1. Units, smoothing and encoding of the locomotion inputs (`Speed`, `Direction`, `TurnDelta`).
2. The action system's idle-tree walk and fallback when a graph refuses an event.
3. The order of event propagation and wildcard resolution in nested state machines.
4. The post-graph order of ragdoll driver and foot IK, and the ragdoll/get-up hand-off.
5. Whether root motion comes from the text file's motion blocks or the clip, and when it overrides
   the controller.
6. Whether the oracle's traces count as clean-side material (`ORACLE.md` Q1). This is a
   clean-room policy question for the operator.
7. Whether 1.7.104's behavior data differs from 1.6.1170's, and what the Creation Club and
   `_ResourcePack.bsa` behaviors add (not downloaded).

## Recommended next three steps

1. **Build the oracle's first slice on Windows** (`ORACLE.md`; ~3 weeks estimated). It needs a
   Windows machine with the game. Start with variable and event tracing for player locomotion and
   one melee attack, with scripted input. It answers unknowns 1–5 by measuring.
2. **Write the clean-side spec for the 9 classes that cover 90% of nodes**, from the DIRTY-SIDE
   notes plus traces. Then implement a graph stepper against `model/` that runs a humanoid
   locomotion graph with stubbed physics and IK. That's the first runnable piece.
3. **Write a spline-compression decoder from a spec**: days of work, and on the critical path for
   seeing anything move. The open decoders are GPL-3.0, so it can't be borrowed.

## Not done / blockers

- steamcmd is broken on this Mac (above); worked around with DepotDownloader. The operator had to
  log in by hand once, by design.
- The brief expected 1.6.x; Steam's current build is 1.7.104. No 1.6 depot was fetched.
- No DLC BSAs exist in SE (DLC content is merged in), so "Dawnguard.bsa" etc. were not extracted.
- Nothing ran on Windows; no timing or runtime behaviour was observed. The oracle is design only.
- The fleet's doctor reported `net5` (aubron-roam unreachable on the tailnet) during the run. That
  is unrelated to this zone and was not investigated.
