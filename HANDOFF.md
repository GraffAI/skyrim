> DIRTY-SIDE: the state of the oracle plugin's work (006 M44), which builds on CommonLibSSE-NG, a reverse-engineered description of the game binary. Not for the clean implementation.

# Handoff — `projects/skyrim`, the oracle host (006 M38, Spot since 2026-10-19) and the plugin's first slice (006 M44), state as of 2026-10-19 22:00Z

Read first: `ORACLE.md` (the plugin design, DIRTY-SIDE), `ORACLE-HOST.md` (why a cloud host), the
M38 record `infra/aws/docs/design/006-m38-aws-oracle-host.md` (§8 the build day, **§10 the move to
Spot, D352, with its log §10.1**), the M44 record `docs/design/006-m44-oracle-first-slice.md`
(the first slice: D353–D358, I186–I188, its two evidence files), `devx/oracle/AGENTS.md`, then
`AGENTS.md`. This file is the runbook and what is open. No tailnet address or `*.ts.net` name
belongs here (this zone is mirrored).

## Where things are

- **The host:** `oracle-host`, EC2 **`i-0599cd67fc597899a`, g6.xlarge Spot** (persistent request
  `sir-rfqqq74g`, stop on interruption), **us-west-2c**, 128 GiB gp3, launched 2026-10-19 21:44Z
  from an image of the on-demand host's disk (`ami-0d9ad24c824907565`, D352). Everything the old
  host had is on it, measured: Windows Server 2022, the same hostname, NVIDIA gaming driver 616.92
  `Licensed`, the virtual display, Autologon as `runner` at the console, Sunshine, **Steam logged in
  by its token** (the JWT from the operator's 2026-10-16 login, expiry May 2027; D311's question
  is closed), Skyrim SE `SkyrimSE.exe` **1.7.104.0**, the DirectX June 2010 redist, tasks
  `OracleRun` and `OracleIdleStop`, no hold file. **State at handoff: `stopped`** (`devx oracle
  status` 21:58Z → `stopped (Spot, g6.xlarge, us-west-2c)`).
- **Kept, not deleted, the operator's call:** the retired on-demand host `i-0a4bcd59bd286950d`
  (`Name=oracle-host-ondemand`, stopped, 128 GiB root ≈ $10.24/month) and the image
  `ami-0d9ad24c824907565` / `snap-0027fd21ab6b97be1` (51.9 GB used ≈ $2.59/month). `devx oracle
  check` prints the retired one as a `note` line until it is gone. **Never start both** (one
  Tailscale node key, one Steam login). Terminating and deregistering need the admin key or the
  console (I168): M38 §10.1 has the commands and the recommendation.
- **The game launches** from a task with `SteamAppId`/`SteamGameId=489830` in the environment:
  `devx oracle run devx/oracle/scenarios/game-launch --out <dir>` → rc 0, `game.txt` shows
  `SkyrimSE.exe` in the console session (2026-10-19 21:50Z, 877 MB). The scenario waits for
  Steam's logon first (see traps).
- **The tool:** `devx oracle up|down|status|ssh|setup|run|seed|check` on both Macs
  (`AWS_PROFILE=oracle`). `up` clears a stale hold and says so; `down` clears the hold before
  stopping; `status` prints `hold: … is set` or `idle stop: live`; `check` prints the retired
  instance. `run` of a `run.cmd` scenario is proven; `run.ps1`'s SKSE branch is still a **stub**
  (M44 Part 4 writes it).
- **The bootstrap** (`infra/aws/bin/aws-bootstrap`, the operator's, a temporary admin key):
  `--spot-from-host` (D352) is done and idempotent (it would now report the Spot host and
  nothing to do); `--wait-capacity <min>` repeats the zone walk every 2 min when every zone
  refuses capacity.
- **Secrets** (fleet, D234 rev 2; `infra/machines/bin/secret ls`): `aws-oracle-key-id`,
  `aws-oracle-secret-key` (IAM user `oracle-runner`), `tailscale-oracle-authkey`,
  `tailscale-policy-oauth-id`/`-secret`. No admin key exists between bootstrap runs.
- **The tailnet policy** is `infra/machines/manifests/tailnet-policy.hujson` (M39), applied by the
  anchor's converge; `tag:oracle` is live; the node `oracle-host` is the same node as before the
  move (the clone carried the node key).
- **Unmerged at handoff:** nothing, once the PR carrying this file (branch `claude/oracle-spot`:
  §10.1, the scenario's Steam wait, `up`'s interruption fix) has shipped.

## The runbook

```sh
devx oracle status                      # state, uptime, tailnet reachability, hold or idle stop, this boot's cost
devx oracle up && devx oracle ssh -- 'nvsmi -q | findstr /i licens'
devx oracle run devx/oracle/scenarios/game-launch --out /tmp/gl   # does the game start? rc 0 = yes
devx oracle run <dir> --out <out>       # <dir> holds run.cmd (today), or a plugin scenario (M44)
devx oracle down                        # always, when a session ends (I165); a Spot stop takes ~7 min
devx oracle check                       # the credential, the instance(s), the quotas, the Spot price
```
Human look: Moonlight (in `/Applications/Nix Apps`) → `oracle-host`; Sunshine's UI at port 47990.
Never RDP (ORACLE-HOST.md §2). Steam's Play button raises a UAC prompt that times out; launch the
exe directly (the scenario does).

## Open, in order

1. **Ship this branch**, then remove its worktree (`dev wt rm oracle-spot` after `dev cd` out).
2. **The operator decides** about `i-0a4bcd59bd286950d` and `ami-0d9ad24c824907565` (above).
3. **M44 Part 1** (the record is on main, PR #248): the repo `GraffAI/skyrim-oracle` (GPL-3.0,
   CommonLibSSE-NG `ng` pinned as a submodule, D355), `host-setup.ps1`'s `toolchain` phase (VS
   2026 Build Tools pinned by sha256, D356), SKSE built from tag `v2.3.1` on the host (D354),
   the hello plugin that refuses any runtime but 1.7.104.0 (I186), `tools/wall/check` (I188).
   **Needs the operator first:** the Address Library 1.7.104 download from Nexus (D354) and a
   yes to the Build Tools licence. Each host session: `up` … `down`, hours into M44 §8.
4. **M44 Parts 2–5** as the record says; Part 4 writes `run.ps1`'s SKSE branch (wait for Steam's
   logon, the version check, the launch, the end of the run per D357).
5. **`home-executor`** (D316) and the **policy follow-ups** (M39 §9): unchanged from the previous
   handoff; not started.

## Traps (each measured; the records have the details)

- **A game launched within ~3 min of boot exits silently**: Steam starts ~2 min after boot and
  logs on ~1 min later (2026-10-19: boot 21:45:22Z, Steam 21:47:26Z, logon 21:48:29Z); a launch
  before the logon dies with no crash event. Wait for
  `HKCU\Software\Valve\Steam\ActiveProcess\ActiveUser` ≠ 0 (the scenario does, up to 180 s).
- **After `down`, the Spot request reads `marked-for-stop` for ~25 s** before
  `instance-stopped-by-user`; the instance's StateReason is `Client.UserInitiatedShutdown`. `up`
  decides an interruption by the StateReason now; a real interruption is `Server.SpotInstanceShutdown`
  or `instance-stopped-no-capacity|by-price`, and only EC2 restarts that (never cancel the request).
- **Spot capacity for g6.xlarge comes and goes by zone**: at 18:30Z all four us-west-2 zones
  refused; at 21:44Z 2c took it. `--wait-capacity` exists for this; a stopped Spot host restarts
  only in its own zone, so `up` can also hit capacity (exit 3; try again later).
- **An image of the disk keeps everything** (D352, measured): Steam's token, the tailnet node
  identity, the SSH host key (`known_hosts` unchanged), the hold file (cleared by `up`), and
  EC2Launch's run-once state (no user data ran again).
- `tailscale status` over SSH as `runner` is refused (tailscaled serves `ssm-user`); read the
  tailnet from `devx oracle status`.
- EC2 user data must START with `<powershell>`; `Add-WindowsCapability` is denied from SSH/SSM
  sessions (OpenSSH comes from the pinned zip); `query.exe user` exits 1 even when the runner is
  logged on; the tool's ssh needs `IgnoreUnknown UseKeychain` and a control socket under `/tmp`;
  Sunshine needs `csrf_allowed_origins`; `reg.exe add` with a quoted value from PowerShell is
  "Invalid syntax" (use `Set-ItemProperty`) — all from 2026-10-16/17, M38 §8.
- `SkyrimSE.exe` without `SteamAppId` in the environment hands off to Steam and exits 53.
- `aws-bootstrap` needs an admin key only for IAM, images, launches and quota requests; make a
  temporary admin user, run, delete it. `oracle-runner` can read the console log and describe
  everything, start/stop only `world=oracle` instances.
