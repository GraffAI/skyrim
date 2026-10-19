> DIRTY-SIDE: this record plans a plugin built on CommonLibSSE-NG (a reverse-engineered description of the game binary) and cites its headers and SKSE's loader. Not for the clean implementation (D289). The variable and event *names* in §3 come from the game's own data files and are clean; the format they will be traced in is ORACLE.md §3, the one section meant to cross the wall.

# 006 M44 — The oracle's first slice: events and variables for locomotion and one melee attack

*Design record, written 2026-10-19 on `aubron-roam`, before any plugin code exists. It is the
record REPORT.md's "next step 1" and ORACLE.md §8 row 1 ask for, and HANDOFF.md's open items 4
and 5. Decisions **D353–D358** and invariants **I186–I188** are claimed in `docs/NUMBERS.md` after
PR #245 and #246 (`dev record next` → `M44 D353 I186`). Two research passes feed it, both run on
2026-10-19 and kept as evidence: [evidence/006-m44-toolchain.md](evidence/006-m44-toolchain.md)
(SKSE, the Address Library, CommonLib and the two build hosts; every claim has its URL or
command) and [evidence/006-m44-slice-names.md](evidence/006-m44-slice-names.md) (the names,
measured on the stock graphs' XML on `aubron-mini` with the scripts in
[tools/slice](../../tools/slice)). Nothing was built, downloaded onto the host, or run against
the game for this record. No credential was used; none is asked for (I166; the Steam and Nexus
logins are the operator's).*

## 1. The ask

ORACLE.md designs a plugin that records what Skyrim SE's behaviour graphs are given and what they
produce. Its §8 estimates ~3 weeks for a "useful first slice: C1–C5, events + variables + states,
no fixed timestep". The brief of 2026-10-19 narrows the first slice further, to what REPORT.md's
step 1 names: **variable and event tracing for player locomotion and one melee attack**. That is
ORACLE.md §2 items 1–4 (variables in both directions, events in both directions) for the
third-person player, on the scenarios C2, C3 and the one-hand light attack of C5, without C1's
RNG pin, without item 5 (`state`, `nodes`, `clip`), without root motion, and without a fixed
timestep.

The slice answers REPORT.md's open questions 1 and 2 by measurement (the units and smoothing of
the locomotion inputs; what the action system sends when a graph refuses an event) and gives the
clean side its first `drive.jsonl` / `expect.jsonl` pair, once Q1 is settled (§7).

The host is M38's `oracle-host` (Spot after M38 §10 D352): Windows Server 2022, g6.xlarge,
Skyrim SE **1.7.104.0** installed by Steam, launched today by `devx oracle run` of a `run.cmd`
(the SKSE path of `run.ps1` is a stub, HANDOFF.md open item 5).

## 2. What the design rests on

Each fact is measured (its command), documented (its URL) or **not verified**. The two evidence
files hold the details.

**The runtime and its loader** (evidence/006-m44-toolchain.md §1–§2):

- `SkyrimSE.exe` on the host is **1.7.104.0** (M38 §8, measured 2026-10-16). The Steam news post
  is "Update 1.7.99 (Updated Aug 27)" with an August 27 hotfix; the post never prints 1.7.104.
  The link from that hotfix to exe 1.7.104 is SKSE's 1.7.104 commits dated 2026-08-27 plus the
  measured exe. A SteamDB build id is **not verified**.
- **SKSE 2.3.1 targets 1.7.104**: skse.silverlock.org, "Current Anniversary Edition build 2.3.1
  (game version 1.7.104)"; `ianpatt/skse64` tag `v2.3.1` = `7ff865f4a2` (2026-08-27),
  `skse_version.h` `CURRENT_RELEASE_RUNTIME RUNTIME_VERSION_1_7_104`. HANDOFF.md's claim holds.
- **The 2.3.x archive is Nexus-only** (a login; direct silverlock paths 404; no GitHub release
  for the tag). Its name and sha256 are **not verified**. The source at the tag builds with the
  repo's `CMakeLists.txt`/`skse64.sln` (**not verified** on this host).
- **SKSE rejects old plugins**: since commit `71f41da518` (2026-08-24) a plugin claiming
  `kVersionIndependent_AddressLibraryPostAE` must also set
  `kVersionIndependentEx_AddressLibraryV5`, else SKSE reads the DLL's PE timestamp and rejects
  anything built before 2026-08-21 with "must be recompiled for new address library". A build
  under Nix's `SOURCE_DATE_EPOCH` (1980) would trip the fallback if the flag were cleared.
- **The Address Library for 1.7.104 exists**: "All in one", version 1.7.104, uploaded
  2026-08-27 (the mod.pub mirror and a user guide; Nexus itself answered 403, so the file name
  and the "v13" label are **not verified** there). The file SKSE looks for is
  `Data\SKSE\Plugins\versionlib-1-7-104-0.bin`. The **format is 5** (a dense offset array;
  CommonLibSSE-NG PR #299) and the **IDs did not reset**: NG PR #401 found all 913 bindings
  with a 1.7.104 match resolving through their 1.6 AE IDs, three functions moved to new IDs
  around 523k.

**CommonLib** (evidence §3):

- `alandtse/CommonLibSSE-NG`, branch `ng` (GPL-3.0; ORACLE.md S1): `RUNTIME_SSE_1_7_104`,
  the format-5 loader, the 1.7.99 layout changes (PR #298) and the V5 flag by default
  (PR #310). Latest release v13.1.0 (2026-10-19); breaking majors weekly, so a commit is pinned.
  `powerof3/CommonLibSSE` `dev` and `libxse/commonlibsse` also support 1.7.104;
  CharmedBaryon's fork (ORACLE.md S2, MIT) last moved 2024-09 and is dead for 1.7.
- The 1.7.99 layout changes touched PlayerCharacter, SkyrimVM, the **input handlers** and
  `BSInputEventQueue`, menus, RTTI/VTABLE offsets. `hkb*`, `BSAnimationGraphManager` and
  `IAnimationGraphManagerHolder` were **not** in the changed list — NG's model, not a check of
  the binary by us. The input change bears on ORACLE.md §4.6 (injection), which this slice
  defers (D357).
- In the field: OpenAnimationReplacer 3.2.1 (2026-08-31) moved to this NG and gates its
  behaviour-graph hook on `IsAtLeast(RUNTIME_SSE_1_7_99)` (`Hooks.h`, the file ORACLE.md S3
  reads); po3's plugins have 1.7 builds. PayloadInterpreter (S5) and SkyrimIngameEditor (S4)
  have no 1.7 build.
- There is no vcpkg port of NG; it is consumed as a git submodule (its README). No
  `CommonLibSSE-NG-Template` repository exists under either owner; a CMake plugin is its own
  `CMakeLists.txt` plus NG's `add_commonlibsse_plugin`.

**The two build hosts** (evidence §4–§5):

- **On the Windows host, MSVC.** NG's CI builds on `windows-2025-vs2026`, MSVC 14.51, SDK
  10.0.26100; its prebuilt bundle (v13.1.0, toolset 19.51) links only on a major.minor match.
  Two bootstrappers were downloaded and their sha256 measured against the URL's own digest:
  VS 2022 Build Tools 17.14.42 (`68978bb2…4187b`, MSVC 14.44, a source build of CommonLib) and
  **VS 2026 Build Tools 18.11.0** (`89341fb2…db4c71`; whether its cl is 19.51 is **not
  verified**). Unattended install: `--add Microsoft.VisualStudio.Workload.VCTools`,
  `.Component.VC.Tools.x86.x64`, `.Component.Windows11SDK.26100`, `.Component.VC.CMake.Project`
  (the IDs are VS 2022's page; unchanged for 2026 **not verified**). Size ~6–9 GB and a first
  build of ~30–55 min on 4 vCPUs are **estimates** (NG's CI compiles CommonLib in 10 min on a
  4-vCPU runner). Licence: Build Tools need a Visual Studio licence; Community covers an
  individual; the full text was **not read**.
- **From the Mac, clang-cl + xwin.** NG has an official Linux-host path with passing CI, and
  Community Shaders PR #561 built a full DLL on macOS — **both compile DirectXTK's shaders under
  Wine**, which D290 forbids, and NG requires DirectXTK. The no-Wine escapes (DirectXTK's
  prebuilt-shaders option, a stub target, libxse's DirectXTK-free CommonLib) are **not
  verified**. A clang-cl plugin against MSVC-built CommonLib corrupted memory (NG #428: 11 of
  20 loads); CommonLib must be built with the same clang major.minor. nixpkgs on
  aarch64-darwin has xwin 0.9.0 (NG pins 0.10.0; flag parity **not verified**), clang/lld 21.1.8
  and 22.1.8 with `clang-cl` and `lld-link`, cmake, ninja, vcpkg (measured with `nix eval`).
  `xwin splat` requires accepting Microsoft's licence: the operator's call. No cross-compile was
  attempted.

**The slice's names** (evidence/006-m44-slice-names.md; the scripts in `tools/slice`):

- The player's third-person graph set: project `meshes/actors/character/defaultmale.hkx` →
  character `characters/defaultmale.hkx` → root `behaviors/0_master.hkx` (1,123 nodes); the
  slice lives in `mt_behavior` (2,711 nodes), `sprintbehavior` (70), `1hm_behavior` (2,608)
  and `1hm_locomotion` (293). The project's 18 behaviour files declare **301 variables and
  1,985 events** between them.
- **Speed is not the blend input.** `Speed` is read only by an always-on
  `BSSpeedSamplerModifier` in `0_master` (with `Direction` and `iState`), which writes
  `SpeedSampled`; the locomotion blend spaces read `SpeedSampled`. `Direction` drives every
  cyclic blend; `TurnDelta` drives the turn blend, the rotation and the
  `turnLeft/RightFast/Slow` events. ORACLE.md §11's four example names all exist, and
  `weaponSwing` is an event, not a variable.
- **The attack path**: `attackStart` (engine-sent) takes `1HM_Ready_State` to `AttackState`;
  `iRightHandType`, `iIsPlayer` and `i1stPerson` pick the branch; the standing light attack is
  clip `1HM_AttackRight` (`playbackSpeed` ← `weaponSpeedMult`, `startTime` ←
  `attackIntroLength`). Its seven clip events: `preHitFrame`, `weaponSwing`, `HitFrame`,
  `CastOKStart`, `AttackWinStart`, `AttackWinEnd`, `attackStop` (the same seven in the graph's
  trigger array and in `animationdatasinglefile.txt`'s DefaultMale block). `IsAttacking` is
  `1HM_AttackBehavior.isActive`; `IsAttackReady` a modifier in the ready state; `i1HMState`
  `1HM_Behavior.currentStateId`.
- **Counts**: locomotion 42 variables / 49 events (37 without dialogue, sneak and dodge names
  that shared nodes pulled in); the attack 23 / 44 (17 in a hand-picked minimal set); the
  **union 53 variables and 88 events**, 7.6 % of the 696 and 1.8 % of the 4,773 REPORT.md
  counts (17.6 % and 4.4 % of the player's own). With jump: 57 / 99.
- **Not verified** by any run: the branch-selecting values (`iIsPlayer`=1, `i1stPerson`=0,
  `iRightHandType`=1 for a sword); that the engine writes `Speed`, `Direction`, `TurnDelta`,
  `iState`, `iSyncTurnState` (no player-file node writes them; the engine-input class is
  `semantics/contract.md`'s pooled rule, DIRTY-SIDE); whether `moveStart`/`moveStop`/
  `attackStop` come from the engine or from annotations; the first-person graphs (17 files,
  not cut).

**The host and the tool** (M38): `devx oracle run` scps a scenario directory, starts
`OracleRun`, polls `done`, copies the out directory back; `run.ps1`'s no-`run.cmd` branch is the
intended SKSE launch (`skse64_loader.exe` from the game dir, `%ORACLE_SCENARIO%` and
`%ORACLE_OUT%` the handoff) and is a stub; `runner` is an Administrator and the host's disk is
kept (D310), so a toolchain installed once stays. Steam's own Play button raises a UAC prompt
that times out; the exe is launched directly with `SteamAppId`/`SteamGameId=489830` in the
environment, which is what SKSE's loader does too (HANDOFF.md traps).

## 3. The slice, stated

What the first slice captures, per frame, for the third-person player only:

| ORACLE.md §3.2 kind | in the slice | how |
|---|---|---|
| `run`, `graph`, `frame`, `dt` | yes | `run`: runtime version, plugin version, scenario, the ESM/BSA hashes **of the files actually loaded** (R4); `graph`: the project, the root `.hkx`, the full variable dictionary (name → type) and event dictionary of the player's graph; `dt` from `UpdateAnimationGraphManager`'s `BSAnimationUpdateData` |
| `in.evt` | yes | `NotifyAnimationGraph` on the three vtables (§4.2) with the return value; `action` records too, if the actor-mediator hook (S4) resolves on 1.7.104 without a new offset hunt; else deferred and said so |
| `out.evt` | yes | a `BSTEventSink<BSAnimationGraphEvent>` on the player's graph (§4.3 a), re-attached on graph rebuild |
| `in.var` | yes, by diff | the value set snapshotted at the end of each update and at the start of the next; a change between them is an engine write, `via: "diff"`. Set*/channel attribution (§4.4 hooks) is slice 2 |
| `out.var` | yes, by diff | snapshot before and after the update (§4.3) |
| `state`, `nodes`, `clip`, `motion`, `snap` | no | ORACLE.md §8 rows 4 and later |

All **301** declared variables of the player's graph are snapshotted (an array copy per update;
hundreds of words, the estimate ORACLE.md §4.3 makes), not only the 53: the 53 variables and 88
events are what the **exit checks for**, the whole dictionary is what is **recorded**. A trace
that shows a name outside the measured lists is information, not a failure.

The scenario, **`loco-1hm`**: load a save made for it (the operator's, a flat empty interior,
a one-handed sword equipped, weapon sheathed), then for ~90 s: stand 3 s; walk forward, back,
left, right; run forward and turn 360° each way; sprint 3 s and stop; draw the sword; one right
light attack from standing; sheathe; stand 3 s. The plugin captures from `kPostLoadGame` for
`duration_s` (from the scenario's `oracle.toml`, default 120), then closes the trace and ends
the game (§4 D357 says how, and the fallback).

## 4. Decisions

- **D353 — The slice is ORACLE.md §2 items 1–4 for the third-person player on `loco-1hm`, in
  the §3.2 kinds listed above, with variables by snapshot diff and no `state`/`nodes`/`clip`.**
  The measured lists (53 variables, 88 events) are the exit's coverage check; the recorded
  dictionary is the player graph's whole one. Reason: the brief; and the snapshot diff is the
  one path-independent capture (ORACLE.md §4.4), so the slice needs no entry detours on
  non-virtual Set* functions, the part of §4 most exposed to 1.7's relocation changes. Deferred
  to slice 2: Set*/channel attribution (`via`), `action` if its hook needs an offset hunt, the
  first-person graph, NPCs, jump.
- **D354 — The runtime is pinned to 1.7.104.0; SKSE is built from source at tag `v2.3.1`
  (`7ff865f4a2`) on the host; the Address Library 1.7.104 is fetched by the operator from Nexus
  once and hashed; the plugin declares the V5 flag and refuses any other runtime (I186).**
  Building SKSE from the tag removes the Nexus login from the agent's path and pins a commit
  where the archive could pin nothing (its hash is unobtainable without the login); ianpatt's
  archive is built from that same tag, and the operator may download it once to compare hashes
  (recorded in §8 if done). The Address Library has no source form; its `.bin` is the operator's
  one Nexus download, kept on the host's disk (D310) and its sha256 written into §8 and the
  plugin's `run` record. Answers ORACLE.md Q2: the owned copy is AE 1.7.104, so that is the
  runtime; 1.5.97 is not revisited.
- **D355 — CommonLibSSE-NG `ng` at a pinned commit, as a git submodule; therefore the plugin
  is GPL-3.0 and lives in its own repository, `GraffAI/skyrim-oracle`, private, outside
  `world`.** The commit is the newest on `ng` at Part 1's first build (S1's `4ed481641f` of
  2026-10-14 already carries the 1.7 work), written into §8 and never moved without a §8 line.
  The separate repo is ORACLE.md R1 (clean-side agents never see the plugin source; this zone
  is mirrored publicly, I161) and R2 (GPL never enters the engine tree). `world` keeps: this
  record, the scenarios (`projects/skyrim/oracle/scenarios/`), the trace checker and the wall
  gate (`tools/trace`, `tools/wall`), and later the clean trace-format spec lifted from
  ORACLE.md §3. The repo is materialised with `dev cd skyrim-oracle` once its manifest row
  exists (Part 1). Considered: a directory in this zone — rejected by R1; libxse's
  DirectXTK-free CommonLib — it lacks `hkbVariableValueSet.h`, which the snapshot diff needs.
- **D356 — The first slice is built on the host with MSVC: VS 2026 Build Tools 18.11.0, pinned
  by the bootstrapper's sha256, installed unattended as a `toolchain` phase of
  `host-setup.ps1` (D314 b: a marker, idempotent, no reboot), with git and vcpkg at NG's
  `builtin-baseline`; the plugin's `build.ps1` runs over `devx oracle ssh`.** Three facts decide
  it (evidence §6): NG's only Mac path needs Wine (D290); clang-built plugins have a documented
  ABI failure class whose symptom is an in-game crash, and in a first slice every crash must be
  the hooks' fault, not the toolchain's; the host must run the game anyway and a full first
  build costs cents at the Spot rate, with rebuilds in seconds on the kept disk. The toolset
  matches NG's CI (14.51), so NG's prebuilt bundle may serve; if the match fails, CommonLib is
  built from source (~10–16 min, once). **What flips it**, recorded for slice 2 or later: a
  trivial NG plugin built on the Mac under Nix with clang-cl 22.1 + xwin and no Wine (DirectXTK
  by prebuilt shaders or a stub), loading cleanly 20 of 20 times on the host under SKSE 2.3.1.
  The bootstrapper's hash pins the version, not the payload Microsoft serves at install time;
  accepting the Build Tools licence is the operator's (the unattended flags imply it; the
  operator says yes to Part 1 before it runs).
- **D357 — The first slice's input is the operator at Moonlight, not injection.** The scenario
  is a human script (§3), timed loosely; the plugin records whatever happened, which ORACLE.md
  §5.2 already accepts ("the oracle need not replay the game deterministically"). Injection
  (§4.6) is slice 2: 1.7 changed the input classes, and a 90-second human capture costs the
  operator less than the first day of that work. The run ends when the plugin's `duration_s`
  elapses: it flushes and closes the trace, then asks the game to quit (the main-menu quit
  path through SKSE's task interface; **not verified**); if that proves unavailable in Part 4,
  `run.ps1`'s SKSE branch takes `timeout_s` = `duration_s` + 60, kills the game and treats the
  closed trace plus `done`=124 as the slice's success, and says so in §8.
- **D358 — Traces stay off git until the operator answers ORACLE.md Q1.** `devx oracle run
  --out` lands them under `~/skyrim-data-extracted/traces/<date>-<scenario>/` on the Mac that
  ran it (the I152 directory, never the zone); the clean side (`model/`, the clean spec) sees
  nothing from this milestone. §8 records aggregate numbers only (counts, names seen, sizes).
  The decision whether a trace is clean is the operator's and is written down before the first
  `drive.jsonl` crosses (REPORT.md open question 6).

## 5. Invariants

- **I186 — The plugin loads only on 1.7.104.0.** `SKSEPluginVersionData` declares AE +
  AddressLibraryV5 with the one compatible runtime, and `SKSEPlugin_Load` checks
  `REL::Module::get().version()` and refuses otherwise, logging the version seen. `run.ps1`'s
  SKSE branch reads `SkyrimSE.exe`'s file version and refuses a different one **before**
  launching (so a Steam update is caught at the controller, not as a crash). Check:
  `devx oracle ssh -- '(Get-Item "<game>\SkyrimSE.exe").VersionInfo.FileVersion'` →
  `1.7.104.0`, and `oracle.log`'s `runtime 1.7.104.0 ok` line after a run.
- **I187 — A trace holds only §3.2 keys, data-file names and values.** `tools/trace/check
  <trace.jsonl>` fails on any key outside the record's kind, any `n`/`sm`/`node` not in the
  trace's own `graph` dictionary, and any string value that looks like an address or offset
  (`0x[0-9A-Fa-f]{6,}` or an 8+-digit decimal in a name field). It runs on every trace before
  it is kept and is a gate of this zone (on fixtures the gate ships, since traces are off git).
- **I188 — No clean file names the plugin, its repository or CommonLib.** `tools/wall/check`
  fails if any tracked file in this zone whose first three lines lack `DIRTY-SIDE` matches
  `CommonLibSSE|RE::|skyrim-oracle|SKSEPlugin`; it is a gate (`zone.toml`), and the plugin
  repository is a `dep` of no zone.

## 6. Parts

1. **Part 1 — the record, the repository, the toolchain.** This record and its evidence;
   `tools/slice` with a README; `tools/wall/check` and the gate (I188); the manifest row and
   the empty `GraffAI/skyrim-oracle` repo (GPL-3.0, NG submodule pinned, `CMakeLists.txt`,
   `build.ps1`, a hello plugin that logs the runtime and refuses the wrong one, I186);
   `host-setup.ps1`'s `toolchain` phase; SKSE built from `v2.3.1` on the host and installed
   into the game dir; the operator's Address Library download, hashed and installed. Exit 1
   and 2 below.
2. **Part 2 — events both ways and the frame.** `run`, `graph`, `frame`, `dt`, `in.evt`,
   `out.evt`, the canonical writer (fixed key order, `%.9g`, per-frame canonical sort, a writer
   thread), graph-rebuild re-attach. A capture of `loco-1hm` shows `attackStart` in and
   `weaponSwing` out.
3. **Part 3 — variables by diff.** The dictionary in `graph`; the per-update snapshots;
   `in.var` and `out.var` as D353 says; the 53 names checked against a capture.
4. **Part 4 — the run path and the checker.** `run.ps1`'s SKSE branch (version check, the
   launch, `%ORACLE_SCENARIO%`, the end of the run per D357), `projects/skyrim/oracle/
   scenarios/loco-1hm/` (`oracle.toml`, the human script as `SCENARIO.md`), `tools/trace/check`
   with fixtures (I187), `devx oracle run` of the scenario landing a trace under
   `~/skyrim-data-extracted/traces/`.
5. **Part 5 — the exit**, measured and written into §8, with the host hours and dollars (M38
   §8's rule), then HANDOFF.md rewritten.

ORACLE.md §8's estimate for rows 1–3 is 9–13 engineer-days; this slice is those rows minus
attribution plus the run path. Not verified against anyone's velocity.

## 7. Exit

Each step is a command whose output goes into §8.

1. **Toolchain**: `devx oracle setup` prints `toolchain` done once and `already done: toolchain`
   on a second run; `devx oracle ssh -- 'cmd /c "C:\BuildTools\VC\Auxiliary\Build\vcvars64.bat
   >nul && cl 2>&1 | findstr Version"'` → `Microsoft (R) C/C++ Optimizing Compiler Version
   19.5x`.
2. **Build and install**: `devx oracle ssh -- 'C:\oracle\src\skyrim-oracle\build.ps1'` → the
   DLL's path and sha256, NG's pinned commit, SKSE's tag and the loader's sha256, the Address
   Library's sha256; `Get-FileHash` lines for `skse64_loader.exe`, `skse64_1_7_104.dll`,
   `Data\SKSE\Plugins\versionlib-1-7-104-0.bin` and `Data\SKSE\Plugins\oracle.dll` in the game
   dir.
3. **It loads, on this runtime only**: after a run, `SKSE\skse64.log` names `oracle.dll` as
   loaded and `SKSE\oracle.log` has `runtime 1.7.104.0 ok` (I186). The refusal path is shown
   once by building the hello plugin with a wrong pinned version and reading the log line.
4. **A capture**: `devx oracle run projects/skyrim/oracle/scenarios/loco-1hm --out
   ~/skyrim-data-extracted/traces/<date>-loco-1hm` → `loco-1hm.oracle.jsonl` is in `--out`,
   `done` holds the code D357 allows, and `tools/trace/check` on it → `ok`.
5. **Coverage**: `tools/trace/coverage <trace> tools/slice/names.json` prints, for the 53
   variables and 88 events, which were seen as `in.var`/`out.var`/`in.evt`/`out.evt`, and the
   ratio; required: `Speed`, `Direction`, `TurnDelta` seen as `in.var`; `SpeedSampled`,
   `IsSprinting`, `IsAttacking` as `out.var`; `moveStart`, `SprintStart`, `attackStart` as
   `in.evt`; `weaponSwing`, `HitFrame`, `AttackWinStart`, `AttackWinEnd` as `out.evt`, in that
   order within the attack's frames. What was expected and not seen is listed, not hidden.
6. **A weak self-check**: a second capture of `loco-1hm` yields the same `out.evt` name
   sequence for the attack (from `attackStart` to `attackStop`) as the first.
7. **The wall**: `tools/wall/check` → `ok` (I188); `dev check` passes; the trace is under
   `~/skyrim-data-extracted/traces/`, `git status` in the zone shows no `.jsonl`.
8. `devx oracle down` → `stopped` (I165), and the session's hours and dollars in §8.

## 8. As built

(empty until Part 1 runs; the host's hours and dollars go here, as M38 §8 does)

## 9. What this record does not do

- **No code.** Nothing is built until this record is on `main`; the brief said so.
- **Not** `state`, `nodes`, `clip`, `motion` or `snap` records; not a fixed timestep; not RNG
  pins; not input injection; not NPCs, the horse, first person, or any corpus scenario beyond
  `loco-1hm`; not the diff tool (ORACLE.md §6, the clean side's).
- **Not Q1.** Whether a trace is clean is the operator's decision (D358); this record keeps
  every trace off git and out of the clean side's view until then.
- **Not a Mac build.** D356 records the measurement that would flip it and does not run it.
- **Not a change to the game's install** beyond SKSE, the Address Library and the plugin in
  `Data\SKSE\Plugins`; no behaviour patcher, no other mod (R4; the oracle hashes what it loads).
- **Not the SKSE archive's hash**: Nexus-only; D354's source build stands in for it.
