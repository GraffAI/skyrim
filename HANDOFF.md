> DIRTY-SIDE: the state of the oracle plugin's work (006 M44), which builds on CommonLibSSE-NG, a reverse-engineered description of the game binary. Not for the clean implementation.

# Handoff — `projects/skyrim`: 006 M44 done (2026-11-01); the oracle host (006 M38, Spot); what is next

Read first: the M44 record `docs/design/006-m44-oracle-first-slice.md` (**§8 as built, §8.1 the
corrections**, §4.1 Part 1.5, then §3–§7), `ORACLE.md` (the plugin design, DIRTY-SIDE; §3 the trace
format, §5.1 the input script, §8 the rows after this slice), the M38 record
`infra/aws/docs/design/006-m38-aws-oracle-host.md` (§8, §10.1), `devx/oracle/AGENTS.md`, then
`AGENTS.md`. This file is the runbook and what is open. No tailnet address or `*.ts.net` name
belongs here (this zone is mirrored).

## What exists now (all measured 2026-11-01, M44 §8)

- **One command runs the slice with no human:** `devx oracle run
  projects/skyrim/oracle/scenarios/loco-1hm-scripted --out <dir> --timeout 10` → the host loads the
  operator's save, injects 380 scripted inputs (stick, mouse-look, buttons) at the engine's input
  poll, records every graph event in and out and every variable change by diff, quits by itself,
  `done`=0 in ~2 min; the trace passes `tools/trace/check`; two runs' attack sequences are EQUAL.
  Coverage of the slice's names: variables 17/53, events 36/88 — the rest never change or fire in
  this scenario (the dialogue, sneak, dodge, shout, left-hand and power-attack families).
- **The plugin:** `GraffAI/skyrim-oracle` (private, GPL-3.0, DIRTY-SIDE; `dev cd skyrim-oracle`),
  `main` = `ef7acf9`: `src/main.cpp` (I186), `src/oracle.cpp` (six hooks, all vtable-slot writes
  plus one prologue-checked context hook at `PollInputDevices`; the writer; the injector; the
  snapshots), `src/skse.h` (include order), `build.ps1` (`-Install`, `-PinnedRuntime`),
  `tools/{trace-stats,trace-coverage,input-stats,addrlib-check}.py`, `NOTES.md` §1–26 (every
  verified fact, URL and layout), `README.md` (the `oracle.toml` keys, the outputs). NG pinned at
  `adebc31d` (v15.4.0). The host has no GitHub credential: changes reach it as a `git bundle` or
  tarball over scp to `C:\oracle\in\` (NOTES §13/§18); never `git pull` there.
- **The host** (`oracle-host`, g6.xlarge Spot, us-west-2c): Windows Server 2022, Steam logged in
  (token to May 2027), `SkyrimSE.exe` 1.7.104.0, VS 2026 Build Tools 18.11.0 (`cl` 19.51), MinGit,
  vcpkg, SKSE 2.3.1 from source, the Address Library 1.7.104 `.bin`, `oracle.dll` installed, the
  source at `C:\oracle\src\skyrim-oracle` with a warm build dir (plugin rebuild ~20 s, CommonLib
  ~12 min), the save `Saves\loco1hm.ess` (sha256 `6426ca27…4445`, first person, a room with a pool
  and walls), `Skyrim.ini` `bAlwaysActive=1` (backup in `C:\oracle\in\ini-backup\`). **State at
  handoff: `stopped`.** Three sessions for M44: ≈ 60 + 13 + 125 min ≈ $0.95. The image
  `ami-0d9ad24c824907565` (≈ $2.59/month) is still kept.
- **The tool:** `devx oracle up|down|status|ssh|setup|run|check`. `setup`'s steps incl. `toolchain`
  and `skse` are idempotent by marker. `run <dir>` takes a `run.cmd` scenario, or (no `run.cmd`) the
  SKSE path: I186's version refusal before launch, the Steam wait, the launch, `oracle.status`
  `closed`, the exit; `done` codes in `run.ps1`'s header (0, 1, 2, 3, 5, 7, 86, 87, 88, 124, 127).
  Scenarios: `projects/skyrim/oracle/scenarios/{input-probe,loco-1hm-scripted}` (`oracle.toml`,
  `input.jsonl`, `SCENARIO.md`; `make-input.py` writes a script), `devx/oracle/scenarios/
  {game-launch,skse-load,game-hold}` (`run.cmd` ones; `game-hold` for a human session).
- **Clean-side tools:** `tools/wall/check` (I188, a gate), `tools/trace/check` (I187, a gate on
  fixtures), `tools/slice/names.json` (53 + 88). **Missing**: a clean `tools/trace/coverage` (§7
  step 5 names it; the exit used the plugin repo's `trace-coverage.py`).
- **Traces** (D358, never in git): `~/skyrim-data-extracted/traces/2026-11-01-m44-{part2,part15,
  part3,part4,exit}/` on `aubron-roam`. The operator has not answered ORACLE.md Q1 (is a trace
  clean?): nothing has crossed to the clean side.
- **Secrets** (fleet): `aws-oracle-key-id`/`-secret-key`, `tailscale-oracle-authkey`,
  `tailscale-policy-oauth-id`/`-secret`, `nexus-api-key` (the operator's Nexus Premium key).

## The runbook

```sh
devx oracle status                       # state, uptime, tailnet, hold or idle stop, this boot's cost
devx oracle up                           # Spot: capacity can refuse (exit 3) — try again later
devx oracle setup                        # every step idempotent; prints already done: <step>
devx oracle ssh -- 'powershell -NoProfile -ExecutionPolicy Bypass -File C:\oracle\src\skyrim-oracle\build.ps1 -Install'
devx oracle run projects/skyrim/oracle/scenarios/loco-1hm-scripted --out ~/skyrim-data-extracted/traces/<date>-loco --timeout 10
python3 -I tools/trace/check ~/skyrim-data-extracted/traces/<date>-loco/oracle.jsonl
devx oracle down                         # always, when a session ends (I165); a Spot stop takes ~7 min
```
Human look: Moonlight (in `/Applications/Nix Apps`) → `oracle-host`; `devx oracle run
devx/oracle/scenarios/game-hold --out /tmp/gh --timeout 65` keeps the game up for you. Never RDP.

## Open, in order

1. **The operator's decisions.** (a) **ORACLE.md Q1**: is a trace (names from data files + values)
   clean enough to cross to the clean side (D358)? Nothing crosses until answered. (b) **The
   public mirror** carries DIRTY-SIDE files (the M44 record and evidence, this file,
   `ORACLE-HOST.md`, `tools/wall/check`, `tools/census/render_index.py`); the exclude list holds
   `ORACLE.md`, `semantics`, `tools/contract`. The lean (2026-10-31): both sides stay here, reading
   disallowed by convention. (c) **Re-image the Spot host** now that the toolchain is on its disk,
   then drop `ami-0d9ad24c824907565` (M38 §10.1; needs the admin key or the console).
2. **The next slice** (ORACLE.md §8 rows 4+ and §4.4): attribution (`via: api|chan` — who wrote an
   `in.var`: the engine or the graph inside notify; M44 §8.1), `state`/`nodes`/`clip`/`motion`/
   `snap`, the first-person graph, NPCs, jump, `action` records (the actor-mediator path needs an
   offset hunt), `UpdateAnimationGraphManager` (non-virtual). A record before code (`dev record
   claim`); the M44 record's §8.1 is its reading list.
3. **Small clean work**: `tools/trace/coverage` in world (port the plugin's, trace + `names.json`
   only); the clean trace-format spec lifted from ORACLE.md §3 (D355) with `graph.evts`, `run`'s
   keys, `via: init|diff`, and the `sm`/`node` dictionary question; a third-person save (the
   scenario forces the camera today).
4. **`home-executor`** (D316) and the **policy follow-ups** (M39 §9): not started.

## Traps (each measured; the records have the details)

- **Hooks**: NG's headers rely on its precompiled header — include `SKSE/SKSE.h` first; the input
  context hook needs `SKSE_SUPPORT_XBYAK` (a CommonLib rebuild) and `windows.h`'s macros then break
  NG's headers (`src/skse.h`); `SKSE_SUPPORT_PATCH_SAFETY=OFF` breaks NG under `/W4 /WX`.
- **Input**: gamepad thumbstick events are used with **no pad connected**; a written heading
  turns the player with no `TurnDelta` and no turn events — use mouse-move input sized from the
  **camera** yaw (`look_via = "mouse"`); the right stick turns 2.7°/s with no pad. There is no
  `Sheathe` user event: `Ready Weapon` toggles. Frames are input polls; frame 0 is ~144 polls after
  `kPostLoadGame` plus 60 settle polls.
- **Variables**: `IsSprinting`/`IsAttacking` turn on inside `NotifyAnimationGraph` (an `in.var`),
  off inside the update (an `out.var`); `Speed` is a step with a ~5-frame ramp, not a per-frame
  stream; `TimeDelta` changes every frame. The dictionary spells `turnRight`, the engine sends
  `TurnRight`.
- **SKSE 2.3.1 ignores `compatibleVersions`** once the Address Library flag is set; I186 is the
  check in `Load`. **The DLL's hash changes per build** (timestamps). **`cmake --build` returns
  -1** on failure: batch `if errorlevel 1` misses it; use `if %errorlevel% neq 0`.
- **The host**: `C:\oracle\next` always exists (busy = a `SkyrimSE` process or `OracleRun`
  `Running`); the game launched within ~3 min of boot races Steam's logon (the run path waits);
  a plain `scp` needs the tool's options (`UserKnownHostsFile`, `HostKeyAlias=oracle-host`,
  `IdentitiesOnly=no`, the unattended key); the save loads in **first person**; the room is not
  empty (pool west, walls east and north). After `down`, the Spot request reads `marked-for-stop`
  ~25 s. Spot capacity comes and goes by zone.
- **Costs**: Build Tools 2 min 41 s, SKSE 40 s, CommonLib 750 s, a plugin rebuild 19 s, a scripted
  run 2 min; a session of edit-build-run is ~10 min of host time (≈ $0.05).
