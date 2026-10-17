# Handoff — `projects/skyrim`, the oracle host (006 M38) and the tailnet policy (006 M39), state as of 2026-10-17 ~00:00Z

Read first: `ORACLE.md` (the plugin design, DIRTY-SIDE), `ORACLE-HOST.md` (why a cloud host), the
M38 record `infra/aws/docs/design/006-m38-aws-oracle-host.md` (§8 "As built" is the day's log), the
M39 record `infra/machines/docs/design/006-m39-tailnet-policy.md`, then `AGENTS.md`. This file is the
runbook and what is open. No tailnet address or `*.ts.net` name belongs here (this zone is mirrored).

## Where things are

- **The host:** `oracle-host`, EC2 `i-0a4bcd59bd286950d`, g6.xlarge **on-demand** (the Spot quota
  L-3819A6DF was still 0 when the operator launched; request filed), us-west-2a, 128 GiB gp3. Windows
  Server 2022, NVIDIA gaming driver 616.92 (`Licensed`), a virtual display, Autologon as `runner`,
  Sunshine (web UI with the tailnet origins allowed), Steam **logged in by the operator**, Skyrim SE
  installed: 15.0 GB, `SkyrimSE.exe` **1.7.104.0**. Scheduled tasks `OracleRun` and `OracleIdleStop`.
  Whether Steam's "only update this game when I launch it" was set is **not verified** (the operator
  was asked to).
- **Demo session 2026-10-17 01:59–02:15Z (measured over `devx oracle ssh` / `run`):** the host had
  stopped (exit 4's `down` completed). `up` hit `InsufficientInstanceCapacity` for g6.xlarge in
  us-west-2a once; the retry 45 s later started it (ssh ok after 1 min). The game then **would not
  start**: `SkyrimSE.exe` died in 2 s on `d3dx9_42.dll was not found` — Steam's first-launch install
  script (DirectX June 2010 + the `Installed Path` registry key) needs elevation, and the UAC prompt
  on the console times out after ~2 min (`installscript_log.txt`: `GLE 1223`), so it never ran.
  Fixed by hand: `Steamworks Shared\_CommonRedist\DirectX\Jun2010\DXSETUP.exe /silent` from the
  elevated SSH session (sha256 `8F47D712…1414E40D`, exit 0; `d3dx9_42.dll` in System32 and
  SysWOW64). Launched via a `run.cmd` scenario with `SteamAppId=489830`/`SteamGameId=489830` in the
  environment (without them the Steam stub re-launches through Steam and exits 53): pid alive,
  1.5 GB working set, Responding. `C:\oracle\hold` was left in place for the demo — **remove it
  or `devx oracle down`** afterwards, or the idle stop never fires. Not done: the launcher's PLAY
  and the UAC prompt (the agent's input-injection and UAC changes were refused by the auto-mode
  classifier); Steam will still prompt for elevation on every launch until its install script
  runs once with the operator present, or `ConsentPromptBehaviorAdmin` is changed (the operator's call).
- **State at handoff:** a `devx oracle down → up → down` cycle (the record's exit 4) was started at
  ~23:57Z; `status` read `stopping` at the first step. If the cycle was cut short, the host may be
  **running**: the first thing the next session does is `devx oracle status`, and `devx oracle down`
  if it is not `stopped`. The idle task stops it after 120 min without a run regardless.
- **The tool:** `devx oracle up|down|status|ssh|setup|run|seed|check` on both Macs (`AWS_PROFILE=oracle`).
  `run` of a `run.cmd` scenario is **proven** (2026-10-16 23:49Z: rc 0, five files back, 1 min).
  `setup` is idempotent (3 passes, 7 min on first use). `check` shows the instance, both quotas and
  the day's Spot price.
- **Secrets** (fleet, D234 rev 2; `infra/machines/bin/secret ls`): `aws-oracle-key-id`,
  `aws-oracle-secret-key` (IAM user `oracle-runner`: describe/start/stop/console-read of the tagged
  instance, quotas), `tailscale-oracle-authkey` (consumed at first boot; the SSM parameter deleted),
  `tailscale-policy-oauth-id`/`-secret` (M39's sync). The temporary AWS admin user is **deleted**.
- **The tailnet policy** is `infra/machines/manifests/tailnet-policy.hujson`, applied by the anchor's
  converge every 180 s tick (`tailnet-sync`; doctor `net10`); `tag:oracle` is live. Edit it in a PR:
  `tailnet-sync --validate` first, `--pull` after if the server reformats.
- **Unmerged at handoff:** nothing in `devx/oracle` or `infra/aws`. The branch `claude/m38-handoff`
  (this file + the record's §8 addendum) needs `infra/machines/bin/ship` from its worktree
  (`dev cd //projects/skyrim@m38-handoff`).

## The runbook

```sh
devx oracle status                      # state, uptime, tailnet reachability, this boot's cost
devx oracle up && devx oracle ssh -- 'nvsmi -q | findstr /i licens'
devx oracle run <dir> --out <out>       # <dir> holds run.cmd (today), or a plugin scenario (later)
devx oracle down                        # always, when a session ends (I165)
devx oracle check                       # the credential, the instance, the quotas, the Spot price
```
Human look: Moonlight (in `/Applications/Nix Apps`) → `oracle-host`; Sunshine's UI at port 47990.
Never RDP (ORACLE-HOST.md §2). A Session Manager shell from the EC2 console works too (the role has it).

## Open, in order

1. **Ship `claude/m38-handoff`** and remove its worktree.
2. **Confirm the host is stopped** (`devx oracle status`); finish exit 4 if the cycle was cut:
   `up`, `ssh -- 'query user'` (runner at console), `down`, `status` → `stopped`; put the timings in
   the record's §8.
3. **Spot:** when `devx oracle check` shows L-3819A6DF at 4, decide whether to move to a Spot host
   (a new instance; D311: snapshot the disk or redo `setup` + the Steam login). On-demand is
   ~$0.99/h running, Spot ~$0.29/h; the stopped cost is the same.
4. **The plugin, Part 1 of ORACLE.md §8:** the toolchain on the host (MSVC 2022 Build Tools, vcpkg,
   CommonLibSSE-NG) over `devx oracle ssh`, or the cross-compile from a Mac (ORACLE-HOST.md §3,
   clang-cl + xwin, build CommonLib from source). SKSE 2.3.1 is the build for 1.7.104.
5. **`run.ps1`'s SKSE path** is a marked stub: launching `skse64_loader.exe` with the scenario, waiting
   for the game, collecting `*.jsonl`. Write it with the first plugin build.
6. **`home-executor`** (the operator's Windows desktop, offline): `devx oracle --host home-executor
   setup` is the portable half (D316) — once it is on and has the first-boot steps by hand.
7. **Policy follow-ups (M39 §9):** replace the policy's literal mini addresses with `hosts` names;
   the drift drill (edit a comment in the console; watch `net10` go red then green within ~3 min).

## Traps (each measured on 2026-10-16; the record's §8 has the details)

- EC2 user data must START with `<powershell>` — a tag inside a comment does not count (#225).
- `Add-WindowsCapability` (DISM) is **denied** from Session Manager and SSH sessions; OpenSSH comes
  from the pinned Win32-OpenSSH zip (#228).
- `query.exe user runner` exits 1 even when the runner is logged on; read its output (#237).
- The tool's ssh is nixpkgs' OpenSSH: the fleet ssh config needs `IgnoreUnknown UseKeychain` (#226),
  and the control socket lives under `/tmp`, not `$TMPDIR` (#227).
- Sunshine blocks non-localhost origins unless listed in `csrf_allowed_origins` (#236).
- `reg.exe add` with a quoted value from PowerShell is "Invalid syntax"; use `Set-ItemProperty` (#233).
- Steam's first-launch install script needs elevation; the UAC prompt on the console cannot be answered
  from SSH and times out (~2 min, `GLE 1223`), leaving `d3dx9_42.dll` uninstalled and the game dead in
  2 s. Install `Steamworks Shared\_CommonRedist\DirectX\Jun2010\DXSETUP.exe /silent` over SSH (2026-10-17).
- `SkyrimSE.exe` run directly (no `SteamAppId` in the environment) hands off to Steam and exits 53;
  set `SteamAppId`/`SteamGameId=489830`, as the SKSE loader does, to run it from a task.
- A stopped on-demand g6.xlarge can fail to start on `InsufficientInstanceCapacity`; `up` once more
  after ~45 s worked (2026-10-17 01:59Z).
- Capacity is per availability zone; the bootstrap walks the default VPC's zones (#218). The account
  had no default VPC in us-west-2 (#216).
- `aws-bootstrap` needs an admin key only to make the IAM user, the instance and the quota requests;
  make a temporary admin user, run, delete it. `oracle-runner` can now read the console log.
