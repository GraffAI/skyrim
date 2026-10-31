> DIRTY-SIDE: §3's risks name the plugin's build dependency, CommonLibSSE-NG (reverse-engineered). The rest is host cost and viability.

# ORACLE-HOST — where the oracle runner can live: cost and viability (2026-10-16)

The host chosen from this research is designed in `infra/aws/docs/design/006-m38-aws-oracle-host.md` (006 M38).

Status: research only. Nothing was launched, no cloud account was touched, no credentials used.
Four Opus research passes (cloud VMs, streaming services, headless automation mechanics,
local/Proton/Parallels/CrossOver). Every price was read on 2026-10-16 from the source named;
anything else is marked **not verified**. The plugin itself is `ORACLE.md` (dirty-side); this
file is about its host and is clean.

## 0. Verdict

| Host | Viable? | Cost | Fidelity risk | Setup |
|---|---|---|---|---|
| Consumer game streaming (GeForce NOW, Xbox Cloud, Luna, Boosteroid) | **No.** No file system, no SKSE, no DLLs, no automation | — | — | — |
| Shadow PC | Only Pro tier + "Always On" add-on (price unpublished); no API; idle/disconnect shutdown on every other tier is enforced and bypassing it is a ToS violation | ≥ $45–60/mo, whole months | low | — |
| **Cloud Windows GPU VM, Spot, stopped between runs** | **Yes** | AWS g6.xlarge ≈ $32/mo dev, $13/mo CI; Azure NV6ads_A10_v5 ≈ $20 / $11 | low (native Windows, datacenter driver) | 2–4 days + a quota request |
| GCP (the fleet's existing project) | Possible but worst fit: DirectX on Windows seems to need the vWS licence (not verified), ≈ $52–61/mo dev on Spot, and a persistent Windows disk contradicts I139 "nothing stays running" | ≈ $52–61 / $18–19 | low | new decision needed |
| Local Windows PC on Tailscale | **Yes, best long-term** | ≈ $370–700 once + $2–11/mo power | lowest (the reference environment) | 1–2 days |
| Proton on a Linux GPU VM | Probably; one report of a custom SKSE plugin loading only 1 boot in 3–4 under Wine | ≈ $8–10/mo dev (Linux Spot L4 ≈ $0.10/h) | medium | 3–6 days |
| CrossOver on the Mac mini | Stopgap only: 1.7.104 reported to crash on D3DMetal at the main menu, 1-in-10 on DXMT, needs a patch DLL; Rosetta + Wine + Metal | $74/yr | highest | 1–2 days |
| Parallels / Fusion on the Mac mini | Not recommended: no 1.7.104 report, Prism x64 translation, 8+ GB of the mini's measured 24 GB | $120–320 yr 1 | medium-high | 1–2 days + unknown |

**Recommendation.** Until the Windows machine is available, a Spot Windows GPU VM is a sound
bridge for the plugin's development phase at roughly $30–40/month, and the automation recipe
(§3) is the same one the local box will use, so nothing is thrown away. The long pole is not
money, it is the GPU quota on a fresh cloud account (AWS "Running On-Demand G and VT instances"
defaults to 0; Spot is a separate quota; denials for new accounts are reported). File it on
day 0. Over two to three years the local box wins on cost and fidelity.

## 1. Cost inputs

Usage profiles assumed (mine, not measured): **P1** dev phase 80 h/month for 2–3 months;
**P2** CI phase 10 h/month of 16 scenarios × 3 runs. Stopped cost = a 128 GiB boot disk billed
all month. Egress is megabytes of JSONL: < $0.01/month everywhere.

| Option | GPU | Win on-demand $/h | Win Spot $/h | Disk $/mo | P1 Spot | P2 Spot | Source |
|---|---|---|---|---|---|---|---|
| AWS g6.xlarge (us-east-1) | L4 24 GB | 0.989 | 0.269 | 10.24 | **31.73** | **12.93** | AWS price JSON (published 2026-10-15), spot.js feed |
| AWS g4dn.xlarge | T4 | 0.710 | 0.369 | 10.24 | 39.76 | 13.93 | same |
| AWS g6f.xlarge (1/8 L4, 3 GB) | L4 slice | 0.4215 | none in feed | 10.24 | 43.96 (on-demand) | 14.46 | same |
| Azure NV6ads_A10_v5 (eastus) | 1/6 A10 | 0.730 | 0.1349 | 9.60 | **20.39** | **10.95** | prices.azure.com retail API |
| Azure NV4ads_V710_v5 | 1/6 AMD V710 | 0.517 | 0.0955 | 9.60 | 17.24 | 10.56 | same; AMD driver not checked |
| Azure NG8ads_V620_v1 (eastus2) | 1/4 V620 | 1.003 | 0.1854 | 9.60 | 24.43 | 11.45 | same |
| GCP n1-standard-4 + T4, no vWS | T4 | 0.724 | 0.485 | 12.80 | 51.63 | 17.65 | cloud.google.com spot + disks pricing; Windows licence $0.046/vCPU-h is not discounted on Spot |
| GCP g2-standard-4 | L4 | 0.891 | 0.607 | 12.80 | 61.36 | 18.87 | same |
| Airgpu | T4 / L4 | 0.65 / 0.90 | — | 10.50 | 62.50 / 82.50 | 17–19.50 | airgpu.com; API/idle policy not verified |
| Vagon Planet | T4 | 0.99 | — | 8–20 | ~87–99 | ~18–30 | vagon.io; no API found |
| Shadow PC Neo / Power | — | flat 37.99 / 54.99 | — | incl. | 37.99+ | 37.99+ | shadow.tech/us/shadowpc/offers; Pro 44.99/59.99 + unpublished Always On |

Azure NVv3/NVv4 retired 2026-09-30. Paperspace closed Windows to new users 2024-07-01.

Local hardware (listings read 2026-10-16): refurb Dell OptiPlex 7070 SFF i5-9500 16 GB with
Windows 11 Pro $364–399 (Best Buy, Newegg); MSI RTX 3050 LP 6G $280 new / ~$195 used; GMKtec
K8 Plus (8845HS/780M, 32 GB) $689–920; Beelink SER8 $939–1,099. Avoid 6th/7th-gen OptiPlexes
(below Windows 11's CPU list). Electricity at 15–30 W idle / 100–200 W load, $0.15–0.30/kWh:
$2.70–10.80 per dev month, $1.80–7.20 per CI month; WoL + sleep removes most of it.

Break-even, cloud (AWS Spot) vs local (OptiPlex, iGPU first): cloud ≈ $213 year 1, ≈ $156 each
later year; local ≈ $405–480 year 1, ≈ $22–86 each later year. They cross in year 2–3.

## 2. Viability findings that drive the choice

- **Steam must be running.** SKSE's loader needs the Steam client up or the game launches
  without SKSE (Nexus SKSE64 guide). Offline mode is "designed to be indefinite" (Valve, 2013–16)
  but needs one online login with "remember me" and the token must survive on disk. **So the
  host needs a persistent disk, not a reimaged one**, and the operator logs in once through
  Parsec/Sunshine and approves Steam Guard on the phone. Steam credentials stay the operator's.
- **Never RDP on the run path.** An RDP session sits on the RDP display adapter and
  disconnecting locks the session; `tscon <id> /dest:console` moves it back. Peek with
  Parsec or Sunshine/Moonlight. Cloud VMs also need an always-attached virtual display
  (VirtualDrivers VDD or ParsecVDA-Always-Connected); a local box uses an HDMI dummy plug.
- **Drivers.** AWS ships a free NVIDIA *gaming* driver for G4dn/G5/G6 (WDDM, DirectX, licensed
  under the GRID Cloud EULA) — the clearest story. Azure redistributes a licensed GRID driver
  for NVadsA10_v5 (use vGPU 19/20). GCP's T4 shows up as "Microsoft Remote Display Adapter"
  without the GRID/vWS driver, and vWS is $0.55/h vs $0.35/h; Spot vWS price not verified.
- **Session 0.** Windows OpenSSH's children cannot show a desktop. Tailscale SSH has no Windows
  server, so use Windows OpenSSH over the tailnet IP. Launch via Sysinternals Autologon + a
  scheduled task created with `/it` (run only when the user is logged on), fired with
  `schtasks /run`; that this lands in the console session is standard practice but **not
  verified** by a primary source — test first.
- **Fidelity.** One plugin author (tphilipgh/skyrim-map-texture-ref-fix) reports a game-side
  use-after-free in 1.7.104 that "rarely crashes" on native Windows, crashes ~1 in 10 map opens
  on CrossOver+DXMT, and deterministically at the main menu on D3DMetal; Proton may be affected.
  Single source, **not verified independently**, but it is the reason non-Windows hosts rank
  low. A second report (chasmlol/SkyCraft #43, 2026-10-09, open) has a custom SKSE plugin on
  1.7.104 loading only 1 boot in 3–4 under Proton 9/Experimental (`_Mtx_lock` null in MSVCP140).
- **Legal.** The Steam Subscriber Agreement grants a personal licence, never mentions VMs,
  forbids renting to others; running your own copy on a VM you rent is not prohibited by the
  text. §4.C's bot clause sits under "Online Conduct" and reads as aimed at online play; an
  offline scripted run looks outside its intent (a reading, **not verified**). Steam emulators
  to skip the client would breach §4.B: do not.
- **GCP home field is weaker than it looks.** The builder project's design (M31 D254, I139) is
  one Spot VM per job, deleted, no persistent disk; a standing Windows disk with a Steam login
  on it is a different thing and would be a new decision, plus the vWS question.
- **Streaming services.** GeForce NOW's "mods" for Skyrim SE means Creation Club only; Xbox
  Cloud streams the Game Pass build SKSE does not support; Luna removed third-party stores in
  2026; Boosteroid bans non-Workshop mods. Shadow is a real Windows VM but every tier except
  Pro+Always On shuts down on disconnect, and bypassing that is a listed prohibited activity.

## 3. The recipe (identical for cloud and local; only the display step differs)

1. Persistent machine with a dGPU-class driver: cloud VM on a kept disk (AWS g6.xlarge Windows
   Server 2022 Spot with the AWS gaming driver, or Azure NV6ads_A10_v5), or the local box with
   an HDMI dummy plug.
2. Cloud only: install an always-attached IddCx virtual display and make it primary.
3. Tailscale + Windows OpenSSH Server; reach SSH over the tailnet.
4. Local `runner` user in Administrators (it installs the plugin under Program Files, builds with MSVC, runs setup and kills the game; the SSH key is already the whole trust boundary), Sysinternals Autologon, lock screen / sleep / blanking off.
5. Steam client in startup; operator logs in once via Parsec/Sunshine, "remember me", approves
   Steam Guard; set Skyrim to update only on launch or pin the build. Game files may be seeded
   from the mini's DepotDownloader copy, but Steam still launches it.
6. Scheduled task `SkyrimRun` as `runner` with `/it`, running a wrapper `.ps1`: wait for
   steam.exe, start `skse64_loader.exe`, wait for the JSONL and process exit, kill on timeout.
7. Controller: `ssh box schtasks /run /tn SkyrimRun`; poll a done-marker; `scp` the trace;
   `shutdown /s /t 0`. Wake via the cloud API or Wake-on-LAN.
8. Humans look through Parsec or Sunshine, never RDP; if RDP was used, end with
   `tscon %sessionid% /dest:console`.

Risks ranked by chance of eating a day: Steam prompts (update, re-login, Guard, "offline"
dialog); game not on the real GPU; `schtasks /run` not landing on the console or a UAC
prompt; cloud driver/quota/Spot capacity; AE first-run dialogs (Bethesda.net, Creation Club)
**not verified**; cross-compiled DLL mismatches if the plugin is built on the Mac (clang-cl +
xwin is documented for CommonLibSSE-NG; build CommonLib from source, not the MSVC prebuilt).

## 4. Measured while researching

- `ssh mini 'sysctl -n hw.memsize; sw_vers'` → 25769803776 (24 GB), M4 Pro, macOS 26.5.1.
  roam: M1 Max, 64 GB (`sysctl`, local).
- SKSE 2.3.1 is the build for 1.7.104 (skse.silverlock.org).

## 5. Not verified

Cloud: AWS Spot for g6f; GCP vWS Spot price, vWS quota metric, whether T4/L4 render DirectX on
Windows without vWS; Azure fresh-subscription GPU quota and NV eviction rates; AWS free egress
tier; whether Amazon DCV is free on G instances. Steam: the exact DRM check in SkyrimSE.exe;
whether a copied `config/` + `loginusers.vdf` restores an offline token on a reimaged disk;
the SSA reading above. Windows: `/it` + `schtasks /run` landing on the console. Performance:
Skyrim SE fps on T4, V620, UHD 630 (native) and 780M (calculator estimate only); llvmpipe —
no report found. Hosts: the D3DMetal crash claim; SKSE under Parallels/Prism on 1.7.104;
CrossOver headless on an M4 mini. Shadow: Always On fee, offline grace period, whether
Tailscale/OpenSSH counts as "server hosting". Retail Windows 11 licence prices, dummy plug
price, real wattage. Nothing here was exercised end to end.
