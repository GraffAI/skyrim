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

## 4.1 Addendum (2026-11-01) — Part 1.5, input and control: D388–D396, I204–I206

*The operator pulled injection forward from slice 2 on 2026-11-01 ("as autonomous as possible"),
after making the `loco-1hm` save by hand (§8). D357's "the operator at Moonlight" stands for Part 1
as run; from here the scenario is scripted. The research is
[evidence/006-m44-input-control.md](evidence/006-m44-input-control.md) (DIRTY-SIDE; every claim
with its file:line or URL; the Address Library IDs it names were looked up in the 1.7.104 table:
all present but 21890). ORACLE.md §5.1's script format is kept, with the clarifications below.*

- **D388 — Input enters through `BSInputEventQueue`, filled from a context hook at the entry of
  `BSInputDeviceManager::PollInputDevices` (`RELOCATION_ID(67315, 68617)`), installed only if the
  first 10 bytes equal the known prologue; otherwise the plugin logs `input hook refused` and the
  run ends `done`=3, never a guess.** Reason: the one hook point with a live 1.7.104 user
  (devbench, NG #347); events added before the poll reach every sink and the real handlers; no
  handler vtable is hooked, so PR #298's slot shift stays the engine's. Flips if the prologue
  differs on our exe (then the `+0x7B` call site with an `E8` check) or injected events are lost
  (then a splice of `PlayerControls`' handler list). Rejected: SKSE's `TaskInterface` (devbench:
  its tasks run after dispatch and lose events); OS-level input (Sunshine, ViGEmBus, `SendInput`):
  no frame alignment, a foreground dependency, ViGEmBus archived and "Windows Server not
  supported" — the fallback if D388's check fails, not the design.
- **D389 — Movement is a left-thumbstick event every frame while the script's `stick move` is
  non-zero, `device=kGamepad`; one zero on release.** Reason: analog `Speed` (walk and run
  plateaus), one event per frame removes any dependence on persistence. Flips if the probe (§7
  step 0) shows the engine drops gamepad events with no pad connected: then digital `Forward`/
  `Back`/`Strafe *`/`Run` buttons, and analog speed waits for a measured `moveInputVec` write.
- **D390 — Buttons are user-event names (`UserEvents`: `Right Attack/Block`, `Sprint`,
  `Ready Weapon`, …) resolved to codes with `ControlMap::GetMappedKey`, both in the event; a hold is
  down, then a held event with real `heldDownSecs` every frame, then up — never down and held in
  one frame.** Reason: evidence §2.3 and devbench's held-key rules. There is no `Sheathe` event:
  `Ready Weapon` toggles. Flips if a handler ignores a named event with a keyboard code.
- **D391 — `look` is absolute: the player's heading and pitch are written in the hook, third
  person, free rotation off.** Reason: ORACLE.md §5.1; no sensitivity. Flips if the written
  heading yields no `TurnDelta` or snaps the graph (then a right-thumbstick event sized from the
  remaining angle, recorded as such).
- **D392 — The plugin records what it injected and what the engine made of it**: an `in.input`
  line per injected event and the frame's `PlayerControlsData` (`moveInputVec`, `lookInputVec`,
  `running`) read after the original `ProcessEvent`. These are engine-structure fields: they go to
  `oracle.log` or a side file, **not** the clean trace (I187), unless the operator rules otherwise.
- **D393 — Frames are input polls.** Script frame 0 is the first poll after `kPostLoadGame` with
  the loading and fader menus closed and the player's 3D loaded, plus `settle` polls (default 60);
  the engine's frame counter is logged beside it. Reason: the hook runs once per poll; it is the
  only clock the injector owns.
- **D394 — Setup `console` lines run through `Script::CompileAndRun` (the `AE_CHECK` ID 441582,
  present in the 1.7.104 table; 21890 is not) on the main thread from the poll hook, before frame
  0; `save` and `load` are refused in scripts.** Reason: evidence §4; devbench's console-save
  deadlock.
- **D395 — `end` flushes and closes the trace, then issues `qqq`; `run.ps1` waits 30 s for the
  process to exit, then kills it. `done`: 0 exited by itself, 124 killed after a closed trace
  (D357's fallback), 3 input hook refused.** Flips if `qqq` hangs on 1.7.104 (then
  `Main::quitGame`, then the kill alone). The save load itself is Part 2's
  (`BGSSaveLoadManager::Load`).
- **D396 — `run.ps1` sets `bAlwaysActive=1` in the game's INI before launch.** Reason: an
  unattended run must not depend on window focus. Flips if the host measures no pause on focus
  loss.
- **I204 — No handler or camera vtable is written by the injector**; D388's is the input path's
  only hook, and `oracle.log` lists every installed hook at load (`grep -c 'hook installed'` equals
  the documented count).
- **I205 — Injection never exceeds the queue's per-frame capacity silently** (10 button, 2
  thumbstick, 1 mouse): an event that does not fit is logged with its frame; `grep 'input
  dropped'` is empty for the exit's scenario.
- **I206 — Input runs only inside the judged window or setup**: nothing is injected while the
  main menu, a loading menu or the console is open, or before D393's frame 0, except D394's setup.

Script clarifications (ORACLE.md §5.1 unchanged): `f` counts D393's polls; `button` ids are
`UserEvents` names; `hold` frames are re-emitted held events; `stick` ids are `move` and, if D391
flips, `look`; `setup` gains an optional `settle`; `console` lines with `save`/`load` are rejected.
Rejected: an event-keyed wait — frame keys stay the only clock, so a script is the same input on
every run. Risks, in the evidence's order: gamepad events with no gamepad; `AddThumbstickEvent`/
`AddMouseMoveEvent` validated on 1.7.104 only against disassembly (a wrong offset is a crash on
the first event); heading writes bypassing the turn path; a `qqq` teardown hang (flush first);
focus on a console session with no Moonlight client; two hooks on one poll if Parts 1.5 and 2 do
not share D393's hook and Part 2's load. Estimate: 3–5 engineer-days, 4–8 host sessions of
10–15 min; **not verified** against anyone's velocity.

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
1.5. **Part 1.5 — input and control (D388–D396, I204–I206; added 2026-11-01).** The poll hook,
   the queue writer and held-state machine, the script loader with D393's clock, `console` setup
   and the `qqq` end, `bAlwaysActive`; the probe `input-probe` (§7 step 0) and its three answers
   (gamepad events without a pad; thumbstick offsets live; heading vs `TurnDelta`); then
   `projects/skyrim/oracle/scenarios/loco-1hm-scripted/` (the §3 script as `input.jsonl`). Shares
   Part 2's load and frame hook. Part 2's "a capture of `loco-1hm`" and Parts 4–5's exits then run
   with no human.
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

0. **Input (Part 1.5, added 2026-11-01)**: `devx oracle run …/input-probe` → `oracle.log` has
   `input hook installed (prologue ok)`, and for 60 frames each of a left stick `(0, 0.5)`, `(0, 1)`
   and a keyboard `Forward`, the logged `moveInputVec` is non-zero and the player's position
   changed; `done`=0. Then `devx oracle run projects/skyrim/oracle/scenarios/loco-1hm-scripted`
   with no Moonlight session → the trace shows `Speed` at two distinct non-zero plateaus, the
   side file shows every scripted event injected and `input dropped` absent, and steps 4–6 below
   hold with `done`=0 within `duration_s` + 30 s (or 124 per D395, said so in §8).
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

The host's hours and dollars go here as Part 1 runs, as M38 §8 does.

- **2026-10-31, the Address Library (D354), on `aubron-roam`, no host session.** The operator
  minted a personal Nexus API key (lifetime Premium) and left it in a home-directory file; the
  orchestrator stored it as the fleet secret `nexus-api-key` (`secret set`, stdin) and shredded
  the file (`rm -P`). With Premium, `GET /v1/games/skyrimspecialedition/mods/32444/files/795954/download_link.json`
  returns direct URLs (seven CDN mirrors), so the download is a script with the key in an
  `apikey` header read from a 0600 file, never argv: `users/validate.json` → `is_premium: true`;
  `files.json` lists the `MAIN` file **795954, "Address Library All in One (1.7.104.0) v13"**,
  uploaded 2026-08-27T15:29:54Z, 6,640,552 bytes (Nexus's `size_in_bytes`; the download's
  `ls -l` agrees). Four API calls of the 2,500 a day. The evidence file's "v13" label and the
  file name, **not verified** there, are verified here.
  - `shasum -a 256` of the archive: `be0c7c07fb63fd1c1403690d4797c7a8fdf8799118acceb605f285d7b0ee055f`
  - `shasum -a 256` of `SKSE/Plugins/versionlib-1-7-104-0.bin` from it (2,263,132 bytes; first
    four bytes `05 00 00 00`, format 5 as the evidence predicted): `8aab3dd251d135b849bd983f86a4a205c920fa3e81f8e30c0e63ccfef9423842`
  - The archive carries 26 files: `versionlib-1-7-99-0.bin`, every 1.6.x and 1.5.x table too.
    Only the 1.7.104 `.bin` goes onto the host.
  - Kept, with a `SHA256SUMS`, under `~/skyrim-data-extracted/nexus/address-library-32444/` on
    both Macs (`shasum -c` on `aubron-mini` → `OK` twice), the I152 directory; not the host yet
    (exit 2 installs it). Nexus's own Premium download is the operator's one download (D354).

- **2026-10-31, Part 1 on the host: exits 1, 2 and 3 met.** The operator said yes to the Build
  Tools licence (D356) and terminated the retired on-demand host (M38 §10.1) before the session.
  Three Opus agents built the pieces in parallel worktrees; the orchestrator ran the host. Shipped:
  PR #280 (`nexus-api-key` declared), #283 (the wall gate I188, `clean=73 dirty=18 files=91`, and
  the `skyrim-oracle` manifest row), #284 (`host-setup.ps1`'s `toolchain` and `skse` steps), #286
  (the skse step's exit-code fix, below). The repository `GraffAI/skyrim-oracle` (private,
  GPL-3.0) was created by the operator (`gh repo create`; the orchestrator's call was refused by
  the harness) and holds commits `79ddaa0` (the scaffold) and `e0591bf` (the build fixes).
  - **Host session**: `up` 22:51:47Z → `running`, ssh ok after 1 min (Spot, us-west-2c, no
    capacity refusal); `down` at 23:44Z (the stop's end and the boot's dollars: the line below).
    The Address Library `.bin` was `scp`'d to `C:\oracle\in\` first (hash on the host
    `8aab3dd2…3842`, 2,263,132 bytes).
  - **Exit 1, the toolchain** (`devx oracle setup`, the worktree's `host-setup.ps1`): eight
    `already done:` lines, then `vs_BuildTools.exe exited 0` after **2 min 41 s** (22:53:48Z →
    22:56:29Z; the evidence's 15–25 min estimate was pessimistic), MinGit 2.56.0.4, vcpkg at
    `ee12231b…`; the banner through `vcvars64.bat`: **`cmake version 4.3.1-msvc1`**,
    **`Microsoft (R) C/C++ Optimizing Compiler Version 19.51.36260 for x64`** (MSVC toolset
    directory 14.51.36231). The "cl 19.51 **not verified**" of §2 is closed: it is 19.51.
  - **Exit 2, SKSE** (the `skse` step): `skse64 v2.3.1 = 7ff865f4a27d6dc936ab5fd0533ff2d706c8f857;
    common = 64e233c096735551f6ac9a773726a8a3960e46cd`; common and skse64 configured and built
    with Ninja in **40 s** (22:57:15Z → 22:57:55Z); installed into the game dir:
    `skse64_loader.exe` `8d8885f23f42ad7b6fb01e2e9a43df891892e50c22f56e83f922582bde7dc0c7`,
    `skse64_1_7_104.dll` `2fc575e9adfd8aa0861e976ff79ce5bbf947e447e2aad0ef1465914bdca1547b`
    (FileVersion 0.2.3.1), `skse64_steam_loader.dll`
    `565be3e1eae24e96b8579c422b0bd891b3b5126a9f3f64e0214b3ab4845f7b80`,
    `Data\SKSE\Plugins\versionlib-1-7-104-0.bin` `8aab3dd2…3842`. `Data\Scripts` `.pex` files
    are **not** installed: a source build has only `.psc` sources and the plugin needs none.
    **A bug, found and fixed**: ninja failed on `skse64_msstore_loader.exe` (LNK1327, mt.exe
    "Values of attribute level not equal in different manifest snippets", `require_admin.manifest`)
    and the step went on, installed the three files that had linked, and wrote its marker.
    Measured cause: `cmake --build` returns **-1**, and `if errorlevel 1` means `>= 1`. PR #286
    makes the check `if %errorlevel% neq 0` and builds only the three targets; verified on the
    host: a test `.cmd` with the old check reached its end with exit 0, with the new check it
    stopped with exit 1; the step re-run with its marker removed (23:05:12Z → 23:05:19Z) printed
    `ninja: no work to do.` and the same four hashes.
  - **Exit 2, the plugin** (`build.ps1` over ssh, as `runner`, Windows PowerShell 5.1): the
    first build (22:59Z) failed in `main.cpp` with 100+ `C2039 'string': is not a member of 'std'`
    in `REL/Version.h`, which the agent traced to two causes of its own, not the toolchain: NG's
    headers rely on its precompiled header, so `SKSE/SKSE.h` must be included first; and
    `SKSE_SUPPORT_PATCH_SAFETY=OFF` makes NG's `Trampoline.cpp` fail `/W4 /WX` (NG's CI never
    builds with it off). With both fixed (`e0591bf`): the full CommonLib build **750 s**, 525
    edges, 0 warnings; a plugin-only rebuild **19 s**. `build.ps1 -Install` 23:36:44Z →
    23:36:54Z: `oracle.dll` 550,912 bytes, sha256
    `c4ebee16009361aa6934bf6b21f46a6805a410ad4e4134536829633b9a2866c1` (the hash changes per
    build: timestamps are embedded; the installed DLL at the session's end is
    `6b5b7f979dfcb63aa1d106819ffbdc3a0c6ece8844795f53aeef9cc8edfe4f7c`), NG `adebc31dcfa6…`
    (tag v15.4.0), `SkyrimSE.exe` FileVersion 1.7.104.0, and the four `Get-FileHash` lines.
  - **Exit 3, it loads on this runtime only**: a scenario `skse-load` (`run.cmd`: wait for
    Steam's logon, start `skse64_loader.exe` with `SteamAppId` set, 90 s, copy the logs, kill the
    game) via `devx oracle run`, rc 0 each time, the game alive at 90 s. **The ok path**
    (23:37Z): `SKSE\skse64.log` → `plugin oracle.dll (00000001 oracle 00010000) loaded correctly
    (handle 1)`; `SKSE\oracle.log` → `oracle 0.1.0.0 (GraffAI/skyrim-oracle e0591bfccf1b),
    CommonLibSSE-NG adebc31…`, `pinned runtime 1.7.104.0`, **`runtime 1.7.104.0 ok`** (I186).
    **The refusal path** (`build.ps1 -Install -PinnedRuntime 1.7.99.0`, 23:39Z): `oracle.log` →
    `[E] runtime 1.7.104.0 refused: this plugin is built for 1.7.99.0 only`; `skse64.log` →
    `reported as incompatible during load 0`. Then the 1.7.104.0 build reinstalled and loaded
    again (23:42Z, `runtime 1.7.104.0 ok`). Note what the refusal shows: SKSE 2.3.1 still said
    `loading plugin "oracle"` with a wrong `compatibleVersions` — with the Address Library flag
    set, SKSE never reads that list (§9 below); I186's enforcement is the check in `Load`.
  - **Costs**: the host ran 22:51:51Z → `down` 23:45:28Z → `stopped` 23:52:05Z (the stop 6 min 37 s;
    `status` → `stopped (Spot, g6.xlarge, us-west-2c)`, I165): **60 min ≈ $0.29** at $0.2875/h
    (`status` at 23:43:48Z: `up 52 min`, `~$0.25`). The image `ami-0d9ad24c824907565` (≈ $2.59/month) is still kept: the
    toolchain is now on the Spot host's disk, so M38 §10.1's re-image-and-drop can follow.
  - **The `loco-1hm` save (D357, §3), 2026-11-01, a second session.** `up` 00:06:13Z (ssh ok after
    1 min); the game started through `skse64_loader.exe` by the `game-hold` scenario at 00:07:05Z
    (Steam already logged on: `ActiveUser` ≠ 0 at 00:07:20Z, 1.5 min after boot — faster than the
    2026-10-19 trap says); the operator at Moonlight made the save and quit at 00:10:18Z (the
    hold saw the quit and ended, rc 0, 4 min). On the host, `Documents\My Games\Skyrim Special
    Edition\Saves\loco1hm.ess`, **2,491,946 bytes**, sha256
    `6426ca27c1153e37519fc995bbb0bd489ca8be083674917c63355f359f7c4445`, beside `loco1hm.skse`
    (506 bytes, SKSE's co-save: SKSE and the plugin were loaded when it was written). The steps
    given were `coc qasmoke`, an iron sword (`player.additem 00012EB7 1`) equipped and sheathed,
    `save loco1hm`; the cell and the equipped weapon are the operator's doing, **not verified** by
    a read of the save. The save is the operator's and stays on the host's disk (I152: it is
    Bethesda-format data; nothing of it enters the zone but this line). Six saves from 2020 are
    also in that directory, from Steam's cloud (`steam_autocloud.vdf`): the operator's own.
    Host: `down` 00:12Z → `stopped` 00:19Z; the session 00:06:13Z → 00:19Z ≈ 13 min ≈ **$0.06**.

- **2026-11-01, Part 2 built and measured: events both ways and the frame, unattended.** One Opus
  agent, five runs 00:46Z–01:05Z on the host session that began 00:28Z (the session also served
  the Part 1.5 research; its `down` is recorded with Part 1.5). `GraffAI/skyrim-oracle` `main`
  `e0591bf..aec8402`: `a0175d5` (the writer, the `oracle.toml` reader, file hashes), `9dae62f`
  (hooks, capture, run control), `58715ca` (`tools/trace-stats.py`, `tools/addrlib-check.py`),
  `aded25f`/`aec8402` (NOTES §11–16, README). I186 unchanged: capture starts after `runtime
  1.7.104.0 ok`.
  - **Hooks, all vtable slot writes** (no code patches, no offsets into functions; each slot checked
    to point into `.text` before the write; each ID present in the 1.7.104 table by
    `tools/addrlib-check.py`, with 21890 shown absent as the control; the player's live vptrs
    matched at `kDataLoaded`): `NotifyAnimationGraph` slot 0x01 on `VTABLE_TESObjectREFR[3]`
    (190265), `VTABLE_Character[3]` (207892), `VTABLE_PlayerCharacter[3]` (208046) → `in.evt` with
    the return value as `ok`; `hkbBehaviorGraph::Update` slot 0x05 (220287), filtered to the root
    of the player's graph 0 → the frame boundary and `dt`; `PlayerCharacter[0]` slot 0x79
    (`ModifyAnimationUpdateData`) → the `BSAnimationUpdateData` cross-check, to `oracle.log` only
    (7,191 calls; min/mean/max `deltaTime` 0.016333/0.016720/0.036111 s, equal to the `Update`
    timesteps as totals, **not** compared frame by frame); a `BSAnimationGraphEvent` sink on
    `graphs.front()` → `out.evt`, re-attached by a 250 ms game-thread poll after a rebuild.
    **Not hooked:** `UpdateAnimationGraphManager` (32899) is non-virtual (an entry detour or a
    call-site offset); `action` records skipped for the same reason (§3 allowed it).
  - **Control, measured** (the final run's log): `main menu open; loading 'loco1hm' in 5 s`
    01:03:24Z → `'load loco1hm' issued (console: Script::CompileAndRun)` 01:03:30Z →
    `kPostLoadGame (success true)` ~1.6 s later; after `duration_s`, `oracle.status` beside the
    trace: `closed reason=duration frames=7189`; `quit requested (Main.quitGame = true)`
    01:05:31Z → the process exited 01:05:33Z, **exit code 0**. The fallbacks (`qqq` at 20 s,
    `TerminateProcess` at 40 s) never fired. **D357's quit path is verified**: `Main::quitGame`.
    `loco1hm.ess` has the same sha256 (`6426ca27…4445`) before and after every run (`certutil`).
  - **The capture.** Run 1 (load, 60 s standing): 3,604 frames, **0 `in.evt`, 0 `out.evt`** — the
    save loads in **first person** (`activeGraph 1 (FirstPerson)`), and nothing reaches the
    third-person graph. With `third_person = true` and nothing pressed: the only event is
    `out.evt` `PickNewIdle` every 9–11 s. With the agent's test aids (`steps`: console
    `player.sae attackStart`, and `oracle:draw`/`oracle:sheathe` through `DrawWeaponMagicHands`):
    `in.evt` `IdleForceDefaultState`, `WeapEquip`, `attackStart` ×3, `Unequip`, all `ok:true`;
    an `attackStart` sent while sheathed → `ok:false`; 37 distinct `out.evt` names; each attack's
    sequence identical, including after two graph rebuilds: `PowerAttack_Start_end
    HeadTrackingOff preHitFrame weaponSwing HitFrame CastOKStart AttackWinStart AttackWinEnd
    attackStop …`. The final run at `aec8402`: 7,189 frames, 3 `graph`, 7 `in.evt`, 110
    `out.evt`, `tools/trace-stats.py` → `no problems`.
  - **`graph`**: **301 variables** (as §3 says), 1,217 events, root `Behaviors\0_Master.hkx`,
    written as `evts` (ORACLE.md §3.2's `graph` row lacks the event dictionary §3 asks for).
  - **Frames**: 7,191 in 120.2 s (59.8/s); `dt` min 0.0163333, median 0.0166667, max 0.0361111;
    `dt.n` is always 1 (no main-loop hook). **Cost**: ~14.0 µs of hook time per frame, the writer
    thread not counted; ~0.9 MB of trace per minute.
  - **`run`**: every `Data\*.bsa` listed with size, only `*Animations*` hashed; the ESM/ESP list
    hashed. Hashing all 15.7 GB was skipped (~2 min cold, an estimate). Which BSAs the game opened
    is **not verified**.
  - **Part 2's stated exit** ("a capture of `loco-1hm` shows `attackStart` in and `weaponSwing`
    out") is met with console-provoked events, which the `run` record declares (`steps`); with
    real input it is Part 1.5's step 0. Traces and logs of the five runs: `~/skyrim-data-extracted/
    traces/2026-11-01-m44-part2/` on `aubron-roam` (6.1 MB; D358).
  - **Not verified**: that an `attackStart` from real input arrives through the same
    `NotifyAnimationGraph` slot; `dt` frame by frame; whether events the graph consumes silently
    reach the sink; the `TESObjectREFR`/`Character` hooks on NPCs (0 player calls, as expected).

- **2026-11-01, Part 1.5 built and measured: `loco-1hm` runs with no human.** One Opus agent,
  01:11Z–01:59Z on the host (builds and 8 runs, ≈ 48 min ≈ $0.23), on the session begun 00:28Z.
  `GraffAI/skyrim-oracle` `main` `aec8402..d8e06ca`: `38beb05` (the poll hook, the injector, the
  clock, the side file), `71ef05f` (`tools/input-stats.py`, `tools/trace-coverage.py`, the new IDs
  in `addrlib-check`, all present in the 1.7.104 table), `7bc1d8d`/`d8e06ca` (NOTES §17–21,
  README). `world`: `projects/skyrim/oracle/scenarios/{input-probe,loco-1hm-scripted}/` and
  `make-input.py` (this PR). The wall: `clean=86 dirty=19`, `ok`.
  - **D388, the hook**: `oracle.log` prints `PollInputDevices` (68617)'s first 10 bytes
    `48 89 5C 24 10 48 89 74 24 18`, then `input hook installed (prologue ok)`. `grep -c 'hook
    installed'` → **6** every run (I204): the three `NotifyAnimationGraph` slots,
    `hkbBehaviorGraph.Update`, `ModifyAnimationUpdateData`, the input context hook. D392's reader
    is an event sink on `BSInputDeviceManager` after `PlayerControls` (sink index 5 vs 2), not a
    hook. **Cost not foreseen**: NG's `install_context_hook` needs `SKSE_SUPPORT_XBYAK` (forced
    in CMake; one CommonLib rebuild, ~12 min), and it pulls `windows.h` into `SKSE/SKSE.h`, whose
    macros break NG's headers — `src/skse.h` fixes the include order.
  - **The probe's three answers** (`input-probe`, side file `oracle.input.jsonl`): (1) **gamepad
    events with no pad are used**: `gamepad connected false, enabled false`, yet `moveInputVec` =
    (0, 0.5) from the first injected frame; at (0, 0.5) the player moved 100.5 units in 60 frames
    (side-file `Speed` 116.78), at (0, 1) 262.9 units (343.46); `moveStart`/`moveStop` arrived as
    `in.evt`; the keyboard `Forward` (0x11) works too — **D389 holds**, no digital fallback.
    (2) **The thumbstick, button and mouse-move queue paths are live on 1.7.104**: no crash.
    (3) **A written heading turns the player but gives `TurnDelta` 0 and no turn events**, where
    real look input while walking gives `TurnDelta` −1.35 and engine-sent `TurnRight`/
    `turnRightSlow`: **D391 flips** — and its named fallback, the right stick, turns only 2.7°/s
    with no pad (`lookInputVec` 0.015 at full deflection), so the agent added `look_via = "mouse"`:
    mouse-move events sized from the remaining **camera** yaw (~22 counts per degree), tracking
    within ~6–13°, `TurnDelta` reading ±90/±180. `look_via` is an `oracle.toml` key (`heading`
    default, `stick`, `mouse`); the scripted scenario uses `mouse`.
  - **Quit (D395)**: both paths exit 0 — `qqq` 1.2–1.6 s after `oracle.status` (5 runs),
    `Main.quitGame` 1.6 s (1 run); `qqq` kept. The plugin's own fallbacks (the other path at 15 s,
    `TerminateProcess` at 25 s) and the 30 s kill (124) never fired; the refusal (`done`=3) and 124
    paths are written, **never triggered**.
  - **The scripted runs** (loco3, loco4, at `7bc1d8d`): script f 0–2400 (2,401 polls, ~40 s),
    trace 2,600 / 2,599 frames, `trace-stats` → `no problems`; frame 0 came 144 polls after
    `kPostLoadGame` plus 60 settle polls (engine frame 489 / 494). **380 of 380 scripted lines
    injected at their frame, `input dropped` 0** (I205). `in.evt`, all engine-sent: `moveStart
    moveStop CyclicFreeze CyclicCrossBlend TurnRight turnStop TurnLeft SprintStart SprintStop
    WeapEquip attackStart attackRelease Unequip`. **The attack**: `in.evt attackStart` at f 2123 /
    2122, then `out.evt` `PowerAttack_Start_end HeadTrackingOff preHitFrame weaponSwing HitFrame
    CastOKStart AttackWinStart AttackWinEnd attackStop` — `weaponSwing` → `HitFrame` →
    `AttackWinStart` → `AttackWinEnd` in order (§7 step 5). **Twice-run comparison**
    (`trace-coverage --compare`) → **EQUAL** (§7 step 6, with no human). `moveInputVec` plateaus
    (the side file; `Speed` as `in.var` is Part 3): (0, ±0.5)/(±0.5, 0) ≈ 218 units each with
    side-file `Speed` 116.78; (0, 1) running 343.46; sprinting 500. **`done`=0**, the game's exit
    code 0, 1.3–1.5 s after the trace closed; `run.cmd` 59 s per run. `loco1hm.ess` sha256
    `6426ca27…4445` before and after all 8 runs.
  - **The room**: §3's "flat empty interior" is not: a pool west of the spawn, walls ~250 units
    east and ~1,200–1,300 north (loco1 walked into a wall, loco2 ran into the pool: `SwimStart`,
    no attack); a scratch run mapped the floor, and the committed route keeps the open lane north
    of the spawn (run 2 s, two 360° circles at 3°/frame, a look-round, sprint north; the sprint's
    last ~0.8 s is against the north wall with `Speed` 500 and `IsSprinting` true).
  - **D396**: `bAlwaysActive=1` set in the runner's `Skyrim.ini` by the scenario's interim
    `run.cmd` (the original at `C:\oracle\in\ini-backup\Skyrim.ini`); its effect **not verified**
    (no run without it). The `done` codes come from the scenario's `wait-game.ps1` until Part 4
    moves them into `run.ps1`.
  - **Not verified**: whether the handlers read the user-event name or the code (both set); why
    the right stick is so slow with no pad; that the poll runs on the main thread (its thread id
    differs from the one SKSE's messages ran on); the variable coverage of §7 step 5 (Part 3).
    Traces: `~/skyrim-data-extracted/traces/2026-11-01-m44-part15/` on `aubron-roam` (D358).

- **2026-11-01, Parts 3 and 4 built, in parallel on the same host session (01:59Z–02:28Z).**
  - **Part 3, variables by diff** (`GraffAI/skyrim-oracle` `d8e06ca..ef7acf9`: `50b4363` snapshots,
    `in.var`/`out.var`, `trace-stats.py --plateaus`, `trace-coverage.py --names`; `3b1d633` a
    log-only watch of the value set around `NotifyAnimationGraph`; `e83f136`/`ef7acf9` NOTES
    §22–26; world PR #307: `tools/slice/names.json`, 53 + 88, regenerated on `aubron-mini` from the
    stock graphs with `tools/slice`'s scripts). **The layout read** (NG `adebc31d`):
    `hkbVariableValueSet` = `hkReferencedObject` (0x10), words at 0x10, quads at 0x20, variants at
    0x30, each an `hkArray` of 0x10, total 0x40; the set hangs off `hkbBehaviorGraph` at 0xD8; read
    through a mirror struct with `static_assert`s. **Measured**: 301 words (capacity 301), 4 quads,
    0 variants; types among the 301: bool 107, int8 1, int32 66, real 123, vector4 3, quaternion 1
    (int16, pointer, vector3: 0); the four quad variables (`AdditiveHeadTransl/Scale/Rot`,
    `TargetLocation`) index the quad array. Every run, 297 of 297 word variables equal the engine's
    own `GetGraphVariable*`; the trace's `Speed` equals the side file's accessor at 2,400 of 2,400
    polls. On a graph's first update (start or rebuild) every variable is written once as `in.var`
    `via:"init"` (ORACLE.md §3.2's `init`); diffs are `via:"diff"`; keys are §3.2's exactly (`in.var`
    `n v via`, `out.var` `n v prev`). A rebuild (two `setrace` steps): `graph` at f 0, 607, 1511,
    each with 301 `init` records. **Cost**: 20.93 µs of hook time per frame, 7.15 of it the
    snapshots, diff and records (13.79 without; Part 2 measured 14.0), from timers in one run;
    **1.24 MB of trace per minute** (0.89 without the variable records, +38 %).
  - **Part 4, the run path and the checker** (world PR #306, `29ca85f`, `b4f35ae`): `run.ps1`'s
    SKSE path (a scenario dir with no `run.cmd`): I186's version refusal before launch (`done`=86),
    `bAlwaysActive=1` once with a backup (D396), the Steam wait (87), a running game refused (88),
    the launch with `ORACLE_SCENARIO`/`ORACLE_OUT`/`SteamAppId`, `oracle.status` `closed` then the
    process's own exit (0), the 30 s kill (124), `input hook refused` (3), an exit with no `closed`
    (7), the SKSE logs copied, the scenario's save hashed before and after. The `done` table is
    `run.ps1`'s header. `test/run-contract.sh` runs the SKSE cases under pwsh on the Mac with a fake
    game and test-only env knobs (86, 87, 0, 124, 3, 7, 2, the INI set once). Only `done`=0 has run
    on the host; the other codes ran only under pwsh 7. `tools/trace/check` (clean, I187 as §8.1
    corrects it): §3.2's kinds and keys; names against the trace's own `graph` dictionary
    **case-insensitively** (the engine sends `TurnRight`/`TurnLeft` where the dictionary spells
    `turnRight`/`turnLeft`: counted, listed, not failed); `out.evt` names outside `evts` counted, not
    failed; `graph.evts` a warning; no address-like strings; `run` first; frames monotonic; eight
    synthetic fixtures under `tools/trace/test`, a gate of the zone. Every real trace under
    `~/skyrim-data-extracted/traces` prints `ok`. The two scenarios lost their interim
    `run.cmd`/`wait-game.ps1`/`set-ini.ps1`.
- **2026-11-01, Part 5: the exit (§7), run by the orchestrator through the finished path.**
  - **Step 0** was Part 1.5's probe and scripted runs (above). **Step 1**: `devx oracle setup` →
    ten `already done:` lines incl. `toolchain` and `skse`, `HOST-SETUP DONE` (02:29:07Z); the
    banner → `Microsoft (R) C/C++ Optimizing Compiler Version 19.51.36260 for x64`. **Step 2**:
    `build.ps1 -Install` → `BUILD OK`; `skse64_1_7_104.dll` `2fc575e9…547b`,
    `versionlib-1-7-104-0.bin` `8aab3dd2…3842`, `oracle.dll` (this build)
    `946e56ab2865c6de476c54249301a439958084d88866ddf94d31b29009866714`.
  - **Steps 3, 4, 6**: `devx oracle run projects/skyrim/oracle/scenarios/loco-1hm-scripted --out
    ~/skyrim-data-extracted/traces/2026-11-01-m44-exit/run{1,2} --timeout 10` (02:30:26Z and
    02:31:33Z, 2 min each, 14 files each): **`done`=0** both; `oracle.status` `closed
    reason=script-end frames=2599`, run1 `records=7876 bytes=903148 … in.var=2289 in.evt=38
    out.evt=168 out.var=181 input frames=2401 stick=1180 mouse=379 down=4 held=194 up=4
    dropped=0 hook=installed`, run2 `records=7859 … in.var=2272 … out.var=181 … dropped=0`; six
    `hook installed` lines (I204); `oracle.log` `runtime 1.7.104.0 ok` (I186); `skse64.log`
    `plugin oracle.dll (00000001 oracle 00020000) loaded correctly (handle 1)`; `save-after.txt`
    `6426ca27…4445` both runs. `tools/trace/check` → **`ok`** both (`run=1 graph=1 frame=2599
    dt=2599 in.var=2289/2272 in.evt=38 out.evt=168 out.var=181`; 22/23 `out.evt` records of 6
    names outside `evts`: `EndAnimatedCameraDelta IdleOffsetStop tailMTLocomotion tailSprint
    turnRightFast turnRightSlow`; 5 case-only matches). 2.0 MB per run directory.
  - **Step 5, coverage** (`trace-coverage.py --names tools/slice/names.json`, the plugin's tool; §7
    names a clean world tool `tools/trace/coverage` that does **not** exist yet — the gap, below):
    **variables 17/53 = 32.1 %** (`in.var` 14, `out.var` 8, both 5; the other 36 have an `init`
    value and never change in this scenario), **events 36/88 = 40.9 %** (`in.evt` 8, `out.evt`
    28), both runs identical. **Required: all seen** — `Speed` 147× `in.var` (f 387…), `Direction`
    8×, `TurnDelta` 231×; `SpeedSampled` 148× `out.var`, `IsSprinting` 1× (f 1950), `IsAttacking`
    1× (f 2211); `moveStart` 7× `in.evt`, `SprintStart` 1× (f 1729), `attackStart` 1× (f 2123);
    `weaponSwing`@2142, `HitFrame`@2144, `AttackWinStart`@2174, `AttackWinEnd`@2198 as `out.evt`,
    **in that order**; the attack's 9 `out.evt` to `attackStop`@2199: `PowerAttack_Start_end
    HeadTrackingOff preHitFrame weaponSwing HitFrame CastOKStart AttackWinStart AttackWinEnd
    attackStop`. `Speed` plateaus (≥ 30 frames): **116.775215** (walk), **343.456512** (run),
    **500** (sprint) — three distinct non-zero values. Not seen: 52 events (the dialogue, sneak,
    dodge, shout, left-hand and power-attack families the scenario never exercises) and `turnLeft`/
    `turnRight` in the dictionary's case.
  - **Step 6**: `--compare run2` → **`out.evt` sequences EQUAL**, 1 vs 1 attack. **Step 7**:
    `tools/wall/check` → `ok`; `dev check` → `OK: 0 failed`; `git ls-files` shows ten `.jsonl` in
    the zone, all ours: the two scenarios' `input.jsonl` and eight synthetic fixtures — no trace
    (§7's "no `.jsonl`" meant no trace; amended in §8.1).
  - **Step 8**: `devx oracle down` 02:33:10Z (the host's third session: `up` 00:28:21Z, `status` at
    02:33Z → `up 124 min`, `~$0.59 at $0.2872/h`; `stopped` at 02:40Z, `status` → `stopped (Spot, g6.xlarge, us-west-2c)`, I165; the session 00:28:21Z → 02:40Z ≈ 125 min ≈ $0.60). **M44's whole host
    bill**: Part 1 ≈ $0.29 + the save ≈ $0.06 + this session ≈ $0.60 ≈ **$0.95**, plus the standing
    root volume ($10.24/month) and the kept image ($2.59/month).
  - **The gap left open, named**: `tools/trace/coverage` as a clean world tool (§7 step 5); the
    exit used the plugin repo's `trace-coverage.py` and `trace-stats.py --plateaus`, which read only
    the trace and `names.json`. Porting them is clean work for the next slice.

## 8.1 Corrections from Part 1 (2026-10-31)

Measured or read at the pins by the Part 1 agents; the record above is left as written and
these lines take precedence.

- **§2, the SKSE timestamp fallback**: commit `14db2124fa`, 47 min after `71f41da518` and in
  `v2.3.1`, changed the window to `520128000 <= t < 1748217600` (1986-06-26 to 2025-05-26). A
  Nix `SOURCE_DATE_EPOCH` of 1980 would not be rejected by it.
- **§5 I186 / §2**: with `kVersionIndependent_AddressLibraryPostAE` set, SKSE 2.3.1 never reads
  `compatibleVersions` (shown above: the wrong pin was still "loading"). The declared runtime is a
  statement; the check in `SKSEPlugin_Load` is the enforcement.
- **D354, the SKSE build**: it also needs `ianpatt/common` (no tags; `64e233c0`, 2026-02-19,
  pinned), and the `.sln`/`CMakeLists.txt` line left it out. SKSE's `Data\Scripts` payload has no
  source form a build can produce.
- **D355, NG's version**: S1's `4ed481641f` was v13.x; the pin is v15.4.0 `adebc31d`. The V5
  flag has no option or macro: it is the default of `PluginVersionData::versionIndependenceEx`
  (PR #310; `PluginDeclaration` got it in PR #360). NG's `PluginDeclaration` can declare the
  Address Library or a runtime list, not both, so the plugin uses the raw `PluginVersionData`.
  `hkbVariableValueSet.h` exists at the pin; its value arrays are private (Part 3 reads by layout).
- **D356, the prebuilt bundle**: `Prebuilt.cmake` uses it only when SE, AE and VR are all
  enabled; an AE-only build compiles CommonLib from source, once (750 s here). "May serve" does
  not hold. The VS 2022 component IDs are listed for 18.x on Microsoft's page: closed.
- **D356, vcpkg's baseline**: NG's `builtin-baseline` `ee12231` is the tool checkout; its
  `vcpkg-configuration.json` overrides the port baseline to `00c5775` (2026-08-25), the set NG's
  CI compiles against (spdlog 1.17, fmt 12.2, directxtk 2026-05). The plugin repo copies that file.
- **D354, SKSE's archive**: still **not verified** (the operator did not download it); the
  built loader is the one in the game dir, by hash above.

Corrections from Part 2 (2026-11-01):

- **ORACLE.md §3.2's `graph` row** has no event dictionary; §3 of this record asks for one. The
  plugin writes it as `evts`; Part 4's checker allows that key.
- **I187 as written** ("any `n`/`sm`/`node` not in the trace's own `graph` dictionary" fails)
  would reject a real trace: `out.evt` `IdleOffsetStop` is not among the root graph's 1,217 event
  names (sub-graph or engine-tagged events). The checker needs a rule for `out.evt` names outside
  the root dictionary (allow, and count them) rather than a failure.
- **§3 "load a save, then stand 3 s" assumes third person**; the operator's save loads in first
  person. The scenario sets `third_person = true` (the plugin forces the camera) until a
  third-person save exists.
- **D357's quit path** is no longer **not verified**: `Main::quitGame = true` exits with code 0
  in ~1.5 s on 1.7.104.

Corrections from Part 1.5 (2026-11-01):

- **D391 flipped**, and past its own fallback: the right stick is unusable with no pad; mouse-move
  input sized from the remaining **camera** yaw is what turns the player with `TurnDelta` and turn
  events (standing look input turns only the camera, so the tracked angle must be the camera's).
  `look_via = "mouse"` is the scenario's setting; `look` targets are camera yaws relative to frame 0.
- **§3**: the start is not a flat empty interior (a pool and walls); the scripted run is ~40 s, not
  ~90 s. The variables and events it exercises are the same.
- **D395**: the plugin carries its own fallbacks (the other quit path at 15 s, `TerminateProcess`
  at 25 s); until Part 4, `done` is written by the scenario's `wait-game.ps1`, not `run.ps1`.
- **§7 step 0**: "`Speed` at two plateaus in the trace" cannot be shown before Part 3 (it was
  shown in the side file); the "run.cmd-free" probe needs a `run.cmd` until Part 4.
- **D388's cost**: the context hook needs `SKSE_SUPPORT_XBYAK` (a CommonLib rebuild) and an
  include-order fix for `windows.h`; neither the evidence nor §4.1 said so.

Corrections from Parts 3, 4 and 5 (2026-11-01):

- **§7 step 5's `out.var` expectation holds only on the way down.** `IsSprinting` and
  `IsAttacking` turn **on** inside `NotifyAnimationGraph`, between updates, so that change is an
  `in.var` in the frame of `SprintStart`/`attackStart`; they turn **off** inside an update, an
  `out.var`. Measured by the Part 3 watch: 38 notify calls, 19 changed a variable inside the call
  (`SprintStart` → `IsSprinting iState iSyncSprintState`; `attackStart` → `IsAttacking iState`;
  `WeapEquip`/`Unequip` → the equip flags; `moveStart` → `bHeadTrackSpine`).
- **D353 and §3: "a change between updates is an engine write" is false** as stated. An `in.var`
  diff means "changed between updates"; the graph itself does work there (inside notify), and
  `IsAttackReady`/`TurnDeltaDamped` change outside both the update and the notify (generate or
  sync, not hooked). The real engine streams are `TimeDelta` (1,410 changes), `TurnDelta`,
  `Speed`, `m_worldFromModelFeedbackGain`, `iSync*`. Attribution is slice 2, as D353 says.
- **`Speed`/`Direction` do not change every frame while moving**: `Speed` is a step (146 changes
  in 2,599 frames, a ~5-frame ramp at each start and stop), `Direction` changed 8 times; the
  smoothing is `SpeedSampled`.
- **Letter case**: the dictionary spells `turnLeft`/`turnRight`; the engine sends `TurnLeft`/
  `TurnRight`. The checker matches case-insensitively and reports it; the coverage tool does not
  count a case-only match. `names.json` keeps the dictionary's spelling.
- **I187, as implemented**: two exceptions to "not in the graph's dictionary fails" —
  case-insensitive matching, and `out.evt` names outside `evts` counted, not failed.
- **§8's Part 1.5 lines** that say `done` comes from `wait-game.ps1` "until Part 4" are now
  history: `run.ps1` owns the table; the Steam code is 87 (the interim 8), an exit without `closed`
  is 7, a kill is 124.
- **§7 step 7's "`git status` shows no `.jsonl`"** means no *trace*: the scenarios' `input.jsonl`
  and the checker's synthetic fixtures are tracked on purpose.
- **ORACLE.md §3.2 vs the plugin**: `graph.evts` (not in §3.2); `run` has none of the common
  `f t a g` keys; `in.var` `via` takes `init|diff` (§3.2 lists `api|chan|init`); `sm`/`node` have
  no dictionary to check against (no trace has them yet). The clean trace-format spec lifted from
  ORACLE.md §3 (D355's "later") should say all four.
- **`C:\oracle\next` always exists** (`run.ps1` reads it and never deletes it); "the host is
  busy" is a `SkyrimSE` process, the `OracleRun` task `Running`, or a changed `next` timestamp.

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
