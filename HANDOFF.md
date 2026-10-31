> DIRTY-SIDE: the state of the oracle plugin's work (006 M44), which builds on CommonLibSSE-NG, a reverse-engineered description of the game binary. Not for the clean implementation.

# Handoff — `projects/skyrim`: 006 M44 Part 1 done (2026-10-31); Parts 2–5 next; the oracle host (006 M38, Spot)

Read first: the M44 record `docs/design/006-m44-oracle-first-slice.md` (**§8 as built, §8.1 the
corrections**, then §3–§7), `ORACLE.md` (the plugin design, DIRTY-SIDE), the M38 record
`infra/aws/docs/design/006-m38-aws-oracle-host.md` (§8, §10, **§10.1** the host's log),
`devx/oracle/AGENTS.md`, then `AGENTS.md`. This file is the runbook and what is open. No tailnet
address or `*.ts.net` name belongs here (this zone is mirrored).

## Where things are

- **The host:** `oracle-host`, EC2 `i-0599cd67fc597899a`, g6.xlarge Spot (persistent request,
  stop on interruption), us-west-2c, 128 GiB gp3. On its disk now, all measured 2026-10-31 (M44
  §8): Windows Server 2022, Steam logged in by its token (expiry May 2027), `SkyrimSE.exe`
  **1.7.104.0**, **VS 2026 Build Tools 18.11.0** at `C:\BuildTools` (`cl` 19.51.36260, cmake
  4.3.1, ninja), MinGit at `C:\oracle\tools\git`, vcpkg at `C:\vcpkg` (NG's baseline), **SKSE
  2.3.1 built from `v2.3.1`** and installed in the game dir with the **Address Library 1.7.104
  `.bin`**, and the plugin source at `C:\oracle\src\skyrim-oracle` (commit `e0591bf`, its build
  dir warm: a plugin rebuild is ~19 s, a CommonLib rebuild ~750 s). `oracle.dll` (pinned
  1.7.104.0) is installed in `Data\SKSE\Plugins` and loads: `oracle.log` says `runtime 1.7.104.0
  ok`. **State at handoff: `stopped`** (`devx oracle down` 23:45Z → `stopped` 23:52Z). The retired on-demand host
  is gone (terminated by the operator 2026-10-31); the image `ami-0d9ad24c824907565` (≈
  $2.59/month) is kept until re-imaged (M38 §10.1).
- **The plugin repository:** `GraffAI/skyrim-oracle` (private, GPL-3.0, DIRTY-SIDE; D355),
  `dev cd skyrim-oracle` materialises it (manifest row shipped, PR #283). `main` = `e0591bf`: the
  hello plugin (`src/main.cpp`, I186), `CMakeLists.txt` + `CMakePresets.json` (`release-msvc-ae`),
  `vcpkg.json` + NG's `vcpkg-configuration.json`, `build.ps1` (`-Install`, `-PinnedRuntime`),
  `NOTES.md` (what was verified, where). The NG submodule is pinned at `adebc31d` (v15.4.0). The
  host has no GitHub credential: the tree reached it as a tarball over scp (`C:\oracle\in\`), so
  **after a push, re-copy** (a `git bundle` or a fresh tarball) rather than `git pull` on the host.
- **The Address Library** (D354): `~/skyrim-data-extracted/nexus/address-library-32444/` on both
  Macs, with `SHA256SUMS`; fetched through the Nexus API with the fleet secret `nexus-api-key`
  (the operator's Premium key; `secret get nexus-api-key`, header `apikey`, never argv). M44 §8
  has the hashes and the four-call method.
- **The tool:** `devx oracle up|down|status|ssh|setup|run|check` on both Macs. `setup` now has the
  `toolchain` and `skse` steps (markers `C:\oracle\state\toolchain.done`, `skse.done`; PR #284,
  #286). `run` of a `run.cmd` scenario is proven; `run.ps1`'s SKSE branch is still a **stub**
  (Part 4). Scenarios: `game-launch` (the game starts) and `skse-load` (the game starts through
  the SKSE loader, 90 s, copies `SKSE\skse64.log`/`oracle.log` into `--out`; exit 0 = alive and
  `oracle.log` present).
- **The wall** (I188): `tools/wall/check` is a gate (`clean=73 dirty=18 files=91` on 2026-10-31).
  Clean files may not name the plugin, its repository or CommonLib; mark a file `DIRTY-SIDE` in
  its first three lines or keep the names out.
- **Secrets** (fleet; `infra/machines/bin/secret ls`): `aws-oracle-key-id`/`-secret-key`,
  `tailscale-oracle-authkey`, `tailscale-policy-oauth-id`/`-secret`, **`nexus-api-key`**.
- **Unmerged at handoff:** this file and M44 §8/§8.1 on branch `claude/kickoff-part-1`; the
  `skse-load` scenario on `claude/skse-load-scenario` — both shipping as this is written.

## The runbook

```sh
devx oracle status                       # state, uptime, tailnet, hold or idle stop, this boot's cost
devx oracle up                           # Spot: capacity can refuse (exit 3) — try again later
devx oracle setup                        # every step idempotent; prints already done: <step>
devx oracle ssh -- 'powershell -NoProfile -ExecutionPolicy Bypass -File C:\oracle\src\skyrim-oracle\build.ps1 -Install'
devx oracle run devx/oracle/scenarios/skse-load --out /tmp/sl   # does SKSE load oracle.dll? read oracle.log in --out
devx oracle down                         # always, when a session ends (I165); a Spot stop takes ~7 min
```
Human look: Moonlight (in `/Applications/Nix Apps`) → `oracle-host`. Never RDP (ORACLE-HOST.md §2).

## Open, in order

1. **M44 Part 2** — events both ways and the frame (`run`, `graph`, `frame`, `dt`, `in.evt`,
   `out.evt`, the canonical writer). Needs the operator's save for `loco-1hm` (a flat empty
   interior, one-handed sword, sheathed; §3) — **not yet made**; its existence on the host is
   **not verified**. `tools/slice/names.json` (the 53 variables and 88 events the exit checks)
   is not written yet; its README says so. Part 2 or Part 5 writes it from the evidence.
2. **Parts 3–5** as the record says; Part 4 writes `run.ps1`'s SKSE branch (Steam wait, the
   version check I186, the launch, the end of the run per D357 — `skse-load/run.cmd` is the
   working draft) and `tools/trace/check`; Part 5 the exit and §8's hours and dollars.
3. **The operator's open decisions:** (a) the public mirror of this zone carries DIRTY-SIDE
   files (the M44 record and its evidence, this file, `ORACLE-HOST.md`, `tools/wall/check`,
   `tools/census/render_index.py`); the exclude list holds only `ORACLE.md`, `semantics`,
   `tools/contract`. The operator's lean (2026-10-31): keep both sides in this zone, reading
   disallowed by convention; the exclude list unchanged for now. (b) ORACLE.md Q1 (is a trace
   clean?) before any trace crosses (D358). (c) Re-image the Spot host now that the toolchain is
   on its disk, then drop `ami-0d9ad24c824907565` (M38 §10.1; needs the admin key or the console).
4. **`home-executor`** (D316) and the **policy follow-ups** (M39 §9): not started.

## Traps (each measured; the records have the details)

- **`cmake --build` returns -1 on a failed build**, and a batch file's `if errorlevel 1` means
  `>= 1`: the skse step installed and marked done over a failed target on 2026-10-31. Use
  `if %errorlevel% neq 0` (PR #286). SKSE's `skse64_msstore_loader` does not link with this
  toolchain (LNK1327, a manifest `level` mismatch) and is not built.
- **NG's headers rely on its precompiled header**: include `SKSE/SKSE.h` before any `REL/` or
  `RE/` header in a plugin source, or every `std::` name is missing (`C2039`). And
  `SKSE_SUPPORT_PATCH_SAFETY=OFF` breaks NG's own `Trampoline.cpp` under `/W4 /WX`; keep NG's
  default and pin minhook (hde64) yourself.
- **SKSE 2.3.1 ignores `compatibleVersions` once the Address Library flag is set**: a plugin
  pinned to 1.7.99.0 still reached `loading plugin`; only `SKSEPlugin_Load`'s own check refused it
  (`reported as incompatible during load 0`). I186 lives in `Load`, not in the version data.
- **The DLL's hash changes on every build** (timestamps are embedded): record the hash from the
  `-Install` run, not from an earlier build.
- **A plain `scp` to the host fails** without the tool's options: use `-o UserKnownHostsFile=
  ~/.local/state/devx-oracle/known_hosts -o HostKeyAlias=oracle-host -o IdentitiesOnly=no -i
  ~/.ssh/unattended_ed25519`, destination `runner@<host>:/C:/oracle/in/<file>`.
- **Build Tools install is fast here** (2 min 41 s for 18.11.0), the SKSE build 40 s, the first
  CommonLib build 750 s; an `up … down` session for a plugin iteration is ~10 min of host time.
- **A game launched within ~3 min of boot exits silently**: wait for Steam's logon (the
  scenarios do, up to 180 s). **After `down`, the Spot request reads `marked-for-stop` ~25 s.**
  **Spot capacity for g6.xlarge comes and goes by zone.** `tailscale status` over SSH as `runner`
  is refused. `SkyrimSE.exe` without `SteamAppId` exits 53. `aws-bootstrap` needs an admin key
  only for IAM, images, launches and quota requests. (All from M38 §8 and §10.1.)
