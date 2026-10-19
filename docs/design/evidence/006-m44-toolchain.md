> DIRTY-SIDE: reads CommonLibSSE-NG and SKSE sources (reverse-engineered descriptions of the game binary). Evidence for 006 M44 (projects/skyrim/docs/design/006-m44-oracle-first-slice.md). Not for the clean implementation.

# Oracle toolchain research: SKSE / Address Library / CommonLib on 1.7.104, and where to build

Research only. Everything below was read on **2026-10-19** (`date -u` → `Mon Oct 19 17:30 UTC 2026`)
from roam unless stated. "**not verified**" marks what I could not confirm from a primary source.
No credential was used or requested. Nothing downloaded was executed.

---

## 1. SKSE for runtime 1.7.104: confirmed

**The premise holds.** The handoff's "SKSE 2.3.1 is the build for 1.7.104" is correct.

- `curl -sSL https://skse.silverlock.org/` (homepage text):
  - "2026-08-14: After two and a half years, Bethesda has announced an incoming update to Skyrim."
  - "**Current Anniversary Edition build 2.3.1 (game version 1.7.104)**: Nexus" (the only link is
    https://www.nexusmods.com/skyrimspecialedition/mods/30379?tab=files; there is no direct `.7z` on silverlock).
  - "Current GOG Anniversary Edition build 2.2.6 (game version 1.6.1179)". "Current Special Edition build 2.0.20 (1.5.97)".
  - The compatibility paragraph still says "currently 1.9.32", which is stale boilerplate from the old LE text.
- GitHub mirror `ianpatt/skse64` (`gh api 'repos/ianpatt/skse64/commits?per_page=25'`; `gh api repos/ianpatt/skse64/tags`):
  - `ebc800022a 2026-08-20 initial 1.7.99 address update` → tag **v2.3.0** (`d8803874aa`, 2026-08-20).
  - `d96a964691 2026-08-27 first pass address update 1.7.104`, `17844c4bf8 version 1.7.104 tick` → tag **v2.3.1** = `7ff865f4a2` (2026-08-27).
  - `skse64_common/skse_version.h` on master: `RUNTIME_VERSION_1_7_104 MAKE_EXE_VERSION(1, 7, 104) // 0x01070680 hotfix`,
    `CURRENT_RELEASE_RUNTIME RUNTIME_VERSION_1_7_104`, `CURRENT_RELEASE_SKSE_STR "2.3.1"`.
  - `skse64_whatsnew.txt` on master: "2.3.1 - fix PlayerCharacter functions - better compatibility reporting for plugins that
    need to be rebuilt due to the address library change - support for 1.7.104"; "2.3.0 - support for 1.7.99".
    Master already has an unreleased **2.3.2** entry (a rare UI::InvokeString bug fix, 2026-09-06).
- **The Steam side.** I used `curl 'https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?appid=489830&count=15&feeds=steam_community_announcements'`.
  The newest patch post is "The Elder Scrolls V: Skyrim Anniversary Edition - Update 1.7.99 (Updated Aug 27)", dated
  2026-08-20, and it has an "Additional Hotfix — August 27" section. The post never prints "1.7.104". The link from
  that hotfix to exe 1.7.104 rests on two things: SKSE's 1.7.104 commits are dated 2026-08-27, and your measured
  `SkyrimSE.exe` is 1.7.104.0. SteamDB build/depot ids were **not checked** (SteamDB blocks scripted fetches; not attempted).
- **Archive and sha256: not obtained.** SKSE 2.3.x is distributed only through Nexus, which needs a login to download.
  - Probes for direct downloads all returned 404: `curl -I https://skse.silverlock.org/{beta,download/archive}/skse64_2_03_0{0,1,2}.7z`.
  - GitHub has no release for the tag: `gh api repos/ianpatt/skse64/releases/tags/v2.3.1` → 404. The newest GitHub release is v2.2.6.
  - Archive name: probably `skse64_2_03_01.7z`, following the naming pattern. **Not verified.**
  - Options: the operator downloads it from Nexus once and we hash that copy, or we build SKSE from source at tag
    `v2.3.1` (`7ff865f4a2`; the repo has `CMakeLists.txt` and `skse64.sln`) on the Windows host.
- **A loader rule that matters to us** (commit `71f41da518`, "logic for plugins declaring new address library compat", 2026-08-24, in `skse64/PluginManager.cpp`):
  - A plugin that claims `kVersionIndependent_AddressLibraryPostAE` must also set the new
    `kVersionIndependentEx_AddressLibraryV5` (`1<<1`) bit in `SKSEPluginVersionData.versionIndependenceEx`.
  - Without that bit, SKSE reads the DLL's PE `TimeDateStamp`. If it is earlier than `1787270400` (2026-08-21 GMT), the plugin
    is rejected with "**must be recompiled for new address library**".
  - CommonLibSSE-NG sets the bit by default (see §3), so a fresh build passes.
  - Cross-compile trap: if a build tool sets `/Brepro` or `SOURCE_DATE_EPOCH` (Nix sets 1980 inside derivations), the
    timestamp fallback would also reject the DLL. Only a plugin that clears the flag would hit this.

## 2. Address Library for 1.7.104: exists, with a new file format but the same ID space

- **It exists.** Nexus mod 32444 itself returned HTTP 403 to WebFetch, so this comes from secondary sources:
  - The mod.pub mirror (https://mod.pub/skyrim-se/212/files): "Address Library - All in one (all game versions)",
    version **1.7.104**, uploaded **27 Aug 2026**, 6.33 MiB.
  - A search snippet of the Nexus files tab, and a user guide (https://rpgmodding.blogspot.com/2026/09/skyrim-171040-skse-231-address-library.html),
    call it "**Address Library All in One (1.7.104.0) v13**"; v12 was the 1.7.99 build.
  - The exact Nexus file names and the "v13" label were **not verified** on Nexus itself.
  - The file SKSE looks for is `Data\SKSE\Plugins\versionlib-1-7-104-0.bin` (`CheckAddressLibrary()` in `ianpatt/skse64` `PluginManager.cpp`).
  - meh321's GitHub (`meh321/AddressLibraryDatabase`, last push 2025-05-28) has nothing for 1.7.
- **The format changed; the ID space did not reset.**
  - The format is now **5**, a dense `uint32` offset array indexed by ID. 1.6.x used the delta-encoded format 2.
    Source: `alandtse/CommonLibSSE-NG` `src/REL/IDDB.cpp` (`load_v5`, `_id2offsetDense[a_id]`), added in PR #299
    "feat(rel): support AE 1.7.99 address library format 5", merged 2026-08-21.
  - IDs carry over from 1.6.x. PR #401 ("fix(AE): add 1.7 ids for two bindings", closed 2026-09-29) reports a sweep:
    "For all 913 bindings that have a 1.7.104 match, the AE id resolves to the same address through the 1.7.104 table as
    the matched function". Only three AE IDs were missing in 1.7; their functions moved to **new IDs in the 52xxxx range**
    (e.g. `TES::GetWaterHeight` 13358 → 523463), selected with `AE_CHECK(SKSE::RUNTIME_SSE_1_7_99, old, new)`.
  - So 1.6 AE IDs are reused, a few functions get new high IDs, and any old CommonLib's parser fails on format 5.
    The guide's crashes at `REL/ID.h(223)` (Community Shaders 1.8.4, Prisma UI, SkyrimNet) are that failure.
- Struct layouts also changed in 1.7.99 (PR #298, merged 2026-08-22):
  - Changed: PlayerCharacter, SkyrimVM, the input handlers (`MenuEventHandler`, `PlayerInputHandler`, `HeldStateHandler`,
    `LookHandler`, …), `BSInputEventQueue`/`InputEvent`, bhkWorld, BGSDefaultObjectManager, several menus, and the
    RTTI/VTABLE offsets.
  - **Not** in the changed-file list: `hkb*`, `BSAnimationGraphManager`, `IAnimationGraphManagerHolder`. That is good for
    ORACLE §4.1–4.5, but it is NG's model, not a binary check by us.
  - The **input** classes changed. That bears on §4.6 input injection.

## 3. CommonLib with 1.7.104 support exists today: alandtse/CommonLibSSE-NG `ng`

| fork | 1.7 status (command) |
|---|---|
| **alandtse/CommonLibSSE-NG** `ng` (GPL-3.0) | **Supports it.** `include/SKSE/Version.h`: `RUNTIME_SSE_1_7_99`, `RUNTIME_SSE_1_7_104`, `RUNTIME_SSE_LATEST_AE = RUNTIME_SSE_1_7_104`. `include/SKSE/Interfaces.h:598` defaults `versionIndependenceEx = kVersionIndependentEx_AddressLibraryV5` (PR #310, 2026-08-24). Format-5 loader in #299; layouts in #298; 1.7 IDs in #401/#403; PlayerCharacter 1.7 fixes #342/#343. Pushed 2026-10-19; latest release **v13.1.0** (2026-10-19). Majors are frequent and breaking (v11 10-04, v12 10-11, v13 10-18), so pin a commit. (`gh api repos/alandtse/CommonLibSSE-NG/commits?sha=ng`, `gh api search/issues?q=repo:alandtse/CommonLibSSE-NG+1.7`) |
| CharmedBaryon/CommonLibSSE-NG (MIT) | **Dead for 1.7.** Last push 2024-09-04 (`gh api repos/CharmedBaryon/CommonLibSSE-NG --jq .pushed_at`). |
| powerof3/CommonLibSSE `dev` (GPL-3.0) | **Supports it.** `RUNTIME_SSE_1_7_104`, `RUNTIME_SSE_LATEST = RUNTIME_SSE_1_7_104`, and the V5 flag default in `Interfaces.h`. AE-only line; NG syncs from it ("chore: sync powerof3/CommonLibSSE dev"). |
| libxse/commonlibsse (GPL-3.0, xmake) | **Supports it.** `RUNTIME_1_7_104`, `RUNTIME_LATEST = RUNTIME_1_7_104`. Its only required dependency is spdlog, via `libxse/commonlib-shared` `xmake.lua`, with **no DirectXTK**. It has `hkbNodeInfo.h`, `hkbBehaviorGraph.h` and `BSAnimationGraphManager.h` but **no `hkbVariableValueSet.h`**. |
| vcpkg port | `commonlibsse-ng` is **not** in microsoft/vcpkg (`gh api repos/microsoft/vcpkg/contents/ports/commonlibsse-ng` → 404). The colorglass registry only carries older releases (NG README). Consume NG as a **git submodule** on `ng`, as the README shows. |

Ecosystem evidence that the 1.7.104 CommonLib really works in the field:
- **OpenAnimationReplacer 3.2.1** (`4d8c0f1b08`, 2026-08-31, after 1.7.104):
  - It switched its submodule from alandtse/CommonLibVR to **alandtse/CommonLibSSE-NG**.
  - It added `REL::Module::IsAtLeast(SKSE::RUNTIME_SSE_1_7_99) ? 0xC38 : 0xC26` in `Hooks.h`, which is the behaviour-graph hook file ORACLE §1 S3 reads.
- **po3**:
  - po3-Tweaks v1.17.0/1.17.1 (2026-08-24/25, "Initial 1.7.99 refactor").
  - PapyrusExtenderSSE v6.5.2 (2026-09-05; the guide says it was "Updated for Skyrim 1.7.104.0").
  - Both are built on powerof3/CommonLibSSE plus commonlib-shared.
- **No 1.7 build found**:
  - PayloadInterpreter: last push 2023-04-18.
  - SkyrimIngameEditor: 2025-05-25.
  - Behavior Data Injector: closed source, **not checked**.
- **Migration for a plugin author** (from the PRs above):
  1. Bump NG to a post-2026-08-24 commit. This gets format-5 loading and the V5 flag by default; rebuilding alone clears
     SKSE's "must be recompiled" error.
  2. Any hard-coded AE ID absent from the 1.7 table needs `AE_CHECK(RUNTIME_SSE_1_7_99, old, new)`.
  3. Any direct member access on the re-laid-out classes must go through NG's version-gated accessors.
  4. Raw offsets copied from 1.6 (like OAR's `0xC26`) must be re-derived.
  - Our plugin is new, so it simply targets NG at a pinned commit, pinned to 1.7.104 only (ORACLE §7 "refuse to load on
    any other version").
  - Note that S1's commit `4ed481641f` (2026-10-14) already includes all of this.

## 4. Building on the Windows host with MSVC

What is needed on Windows Server 2022:

1. **Build Tools**, pinned with hash-checkable fixed-version bootstrappers. The second path segment of each URL is the file's sha256.
   - **VS 2022 17.14.42** (2026-10-13, build 17.14.37806.7), from https://learn.microsoft.com/en-us/visualstudio/releases/2022/release-history:
     `https://download.visualstudio.microsoft.com/download/pr/c95450be-0a45-4779-b142-33f567ccfd6e/68978bb28916156802e60e04c5ee50b94348d802fe151a3ca24433f27984187b/vs_BuildTools.exe`.
     Downloaded to `scratchpad/dl-vsbt/`: 4,474,848 bytes, `shasum -a 256` = `68978bb2…4187b` (matches the URL), PE32. Not run.
   - **VS 2026 18.11.0** (2026-10-13, build 12306.390), from https://learn.microsoft.com/en-us/visualstudio/releases/2026/release-history:
     `https://download.visualstudio.microsoft.com/download/pr/4ee8a2e7-bc71-435a-8180-6703ab4d2017/89341fb2edf12ef29977078fdc72a9e47767ce6895cc297f274bc4a379db4c71/vs_BuildTools.exe`.
     Downloaded to `scratchpad/dl-vsbt2026/`: 5,690,624 bytes, sha256 = `89341fb2…71` (matches). Not run.
   - **Which one.** NG's own CI now runs on image `windows-2025-vs2026` with `VCToolsVersion: 14.51.36231` and
     `WindowsSDKVersion: 10.0.26100.0`. Source: `gh run view 39224141439 -R alandtse/CommonLibSSE-NG --log --job <release,ae,msvc>`.
     - NG's MSVC prebuilt bundle v13.1.0 is stamped `TOOLSET_VERSION.txt` = `19.51.36260.0`.
       `cmake/Prebuilt.cmake` links a bundle only on a **major.minor** toolset match.
     - VS 2022 17.14 ships MSVC 14.44 / cl 19.44 (also what NG's Linux CI pins as `XWIN_CRT_VERSION 14.44.17.14`), so a
       VS 2022 host falls back to a source build of CommonLib.
     - The cl 19.51 claim for VS 2026 18.11 is **not verified**; CI shows 14.51 on the runner image, and I did not map it to an 18.x release.
     - **Recommendation: install VS 2026 Build Tools** so the host matches NG's CI and can use the prebuilt bundle.
       VS 2022 also works, with a source build.
   - Unattended install. Component IDs are from https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools?view=vs-2022;
     I assumed the same IDs apply to VS 2026, **not verified**:
     ```
     vs_BuildTools.exe --quiet --wait --norestart --nocache --installPath C:\BuildTools ^
       --add Microsoft.VisualStudio.Workload.VCTools ^
       --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
       --add Microsoft.VisualStudio.Component.Windows11SDK.26100 ^
       --add Microsoft.VisualStudio.Component.VC.CMake.Project
     ```
     - `VC.CMake.Project` brings CMake and Ninja.
     - Optional: `Microsoft.VisualStudio.ComponentGroup.NativeDesktop.Llvm.Clang` (clang-cl 19.1.5 in VS 2022), only if we
       want the host to build exactly what a Mac clang-cl build would.
     - The bootstrapper downloads its payload from Microsoft at install time. The bootstrapper hash pins the version, not the bytes of the payload.
2. **git**, for submodules and for vcpkg.
3. **vcpkg**: `git clone https://github.com/microsoft/vcpkg` at NG's `builtin-baseline` (`ee12231b20c95013c6638d845d04c91559a1d1ff`, from NG's `vcpkg.json`), then `bootstrap-vcpkg.bat -disableMetrics`. Triplet `x64-windows-static-md`, as in NG's CI log.
4. **Dependencies** (NG `vcpkg.json`): directxmath, directxtk, fmt, nlohmann-json, rapidcsv, simpleini, spdlog, toml11, xbyak, plus catch2 for tests.
5. **Template.** Neither `CharmedBaryon/CommonLibSSE-NG-Template` nor `alandtse/CommonLibSSE-NG-Template` exists (`gh api` → 404). Live templates:
   - `libxse/commonlibsse-ng-template` (xmake; pushed 2026-08-02; its submodule points at `alandtse/CommonLibVR`, so check what it pins).
   - `qudix/commonlibsse-template` (xmake, libxse/commonlibsse, 2026-09-20).
   - `AdoringStan/commonlibsse-ng-template-hello-world-linux` (CMake + NG + xwin, 2026-10-13; the author calls it AI-assembled).
   - For a CMake build, the simplest is our own `CMakeLists.txt` with NG as a submodule and `add_commonlibsse_plugin(...)` (NG README "Simplified Plugin Declaration").

**Size and time** (no measurement on g6.xlarge):
- Install size: estimate **~6–9 GB** for VCTools + MSVC + SDK 26100 + CMake. Not on the components page; **estimate**.
  Add ~1.2 GB for NG's prebuilt bundle, extracted (`PREBUILT.md` in the bundle: "~1.2 GB extracted").
- NG CI on the GitHub `windows-latest` runner, assumed 4 vCPU / 16 GB, the same shape as g6.xlarge; spec **not verified**.
  Job timings for run 39224141439, 2026-10-19:
  - `release, ae, msvc` took 12 m 17 s in total. The CommonLib compile itself, `[1/535]`→`[535/535]` including tests,
    took 10 m 00 s, with vcpkg dependencies **restored from cache** in 1.1 s.
  - `release, all, msvc` took 18 m 48 s.
  - PR #431 says a clang-cl consumer's source build of CommonLib is "about 16 minutes".
- First build on the host, **estimate**: Build Tools install 15–25 min + cold vcpkg dependencies 5–15 min (DirectXTK is
  the largest) + CommonLib 10–16 min (or ~0 with the prebuilt bundle on a matching toolset) + plugin under 1 min.
  That is **~30–55 min, ≈ $0.15–0.27 at $0.29/h**. Later incremental plugin builds take seconds to about a minute.
  The installed tools persist on the kept EBS disk.

**Licence (Build Tools):**
- Microsoft's position (https://learn.microsoft.com/en-us/answers/questions/1683872/ ; devblogs post "Updates to Visual Studio Build Tools
  license for C and C++ Open-Source projects", https://devblogs.microsoft.com/cppblog/?p=30919):
  - Build Tools are licensed as a supplement to a valid Visual Studio licence.
  - A later carve-out lets anyone compile OSI-licensed open-source dependencies without one.
  - Developing your own C++ code needs a VS licence, and VS **Community** qualifies for an individual, including for
    commercial use.
- So an individual operator building a private GPL plugin is covered by the Community terms. I did **not** read the
  full licence text (the licence page rendered no body to WebFetch), so treat this as **not verified** against the text.
- The same Microsoft terms apply to the CRT/SDK that `xwin --accept-license` downloads, so cross-compiling does not avoid them.

## 5. Cross-compiling from macOS: documented for Linux, shown working once on macOS, and it needs Wine

- **The documented path.** NG has an official Linux-host clang-cl + lld-link + xwin path:
  - PR #302 (merged 2026-08-22), `cmake/toolchain-linux-clangcl.cmake`, presets `build-*-linux-clangcl-vcpkg-*`, and
    `examples/linux-cross-compile/README.md`.
  - It has a CI job on `ubuntu-latest`. In run 39224141439 it passed in 12 m 50 s, with Clang 19 from apt.llvm.org and
    xwin 0.10.0 pinned to manifest 17, SDK 10.0.26100, CRT 14.44.17.14.
  - The toolchain file has nothing Linux-specific in it; it uses `find_program` for `clang-cl`, `lld-link`, `llvm-rc`, `llvm-mt`.
- **Wine is required, and that conflicts with D290.**
  - `directxtk` is `find_package(directxtk CONFIG REQUIRED)` in NG's `CMakeLists.txt`.
  - It compiles HLSL with `fxc.exe`, which xwin does not provide. NG's overlay port runs an `fxc2` stand-in **under Wine**,
    built with llvm-mingw.
- **The no-Wine escape is unproven.** DirectXTK's `CMakeLists.txt` has `option(USE_PREBUILT_SHADERS ...)` plus
  `COMPILED_SHADERS`, so the shaders could be compiled once on the Windows host and fed in. Alternatively, a plugin that
  never calls DirectXTK could provide a stub target, or we could use libxse/commonlibsse, which has no DirectXTK at all.
  None of these was tried; all **not verified**.
- **A macOS-host build has worked once.** alandtse/open-shaders PR #561 (merged 2026-08-30), "build: add Linux/macOS-host
  cross-compile support", built a full `CommunityShaders.dll` locally on macOS with clang-cl + xwin + Wine. Gotchas it records:
  - `clang-scan-deps` misparses `/Users/...` paths as `/U` (fix: `CMAKE_CXX_SCAN_FOR_MODULES OFF`).
  - Define `_MSVC_LANG` explicitly so the MSVC STL's C++23 feature gates fire under clang-cl.
  - MSVC-only `__cpuid` forms in stb.
  - Ambiguous brace-init assignments that MSVC accepts and clang rejects.
  - `/bin/sh` brace-expansion of `-DOPT={0,1}` arguments on macOS.
  - Missing `/EHsc` in vcpkg port builds (fixed in NG's toolchain file).
  - Wine's built-in `d3dcompiler_47` producing bogus shader errors.
- **What breaks, in general**:
  - **Mixing compilers corrupts memory.** NG PR #428 (2026-10-10): a clang-cl plugin linked against the MSVC-built prebuilt
    `CommonLibSSE.lib` disagreed on how `std::strong_ordering` is returned. It loaded 11 of 20 times, and 80 of 80 once
    CommonLib was built from source with clang.
    - So a clang-cl plugin must build CommonLib with the **same clang**, or use the clang-cl bundle, which must match
      **clang major.minor**. The v13.1.0 clang bundle is stamped `22.1.3`.
    - nixpkgs has `llvmPackages_22` 22.1.8 (`nix eval --raw nixpkgs#llvmPackages_22.clang-unwrapped.version`), so 22.1 matches.
  - MSVC STL headers need Clang 19+ (NG CI comment).
  - Mixing LLVM versions across clang-cl, lld-link, llvm-rc and llvm-mt "crashes lld" (NG CI comment).
  - NG's README warns: "struct layout or vtable mismatches between clang-cl output and the real MSVC game binary compile
    fine and only surface as an in-game crash."
  - SEH and `__declspec` work in clang-cl.
  - `/EHa` and MSVC-specific intrinsics were **not individually verified**.
- **nixpkgs on aarch64-darwin, measured.** Flake registry `nixpkgs` = nixpkgs-weekly `494ce7fd23ff`. Commands:
  `nix eval --json nixpkgs#<pkg>.meta.platforms` and `nix build --no-link --print-out-paths`.
  - `xwin` **0.9.0**; aarch64-darwin is in its platforms; the binary is present. NG pins **0.10.0**; whether 0.9.0 supports
    the same `--manifest-version`, `--use-winsysroot-style` and `--preserve-ms-arch-notation` flags is **not verified**.
  - `llvmPackages_21` 21.1.8: `clang-cl` and `lld-link` present; `llvm-rc`, `llvm-mt` and `llvm-lib` in `.llvm`.
    `clang-cl --version` prints `Target: arm64-pc-windows-msvc` by default, so `--target=x86_64-pc-windows-msvc` is required
    (the toolchain file sets it).
  - `llvmPackages_22` 22.1.8, `llvmPackages_latest` 23.1.0, `cmake` 4.4.3, `ninja` 1.13.2, `vcpkg` 2026.06.24: all list aarch64-darwin.
  - The world flake's own `nixpkgs` input is `c5c4a43b0e80` (flakehub NixOS 0.2605); the versions there were **not checked**.
- **Not done:** no actual cross-compile was attempted. `xwin splat` requires `--accept-license` for Microsoft's CRT/SDK
  terms, which is the operator's call, not mine.

## 6. Recommendation for the first slice: build on the Windows host with MSVC

Build the first slice **on the g6.xlarge with MSVC** (VS 2026 Build Tools, pinned by hash). Three facts decide it:

1. **NG's only Mac/Linux path needs Wine** (DirectXTK shaders via `fxc2`), which D290 forbids. The no-Wine workarounds
   are unproven.
2. **Clang-built plugins have a documented failure class.** ABI mismatch with MSVC objects corrupted memory (#428), and
   layout mismatches only show up as in-game crashes. In the first slice, every crash has to be attributable to our
   hooks, not the toolchain.
3. **The host is the cheaper loop.** It must run the game and SKSE anyway, a full first build costs about $0.15–0.27
   (estimate), the kept disk makes rebuilds seconds, and the host's MSVC can match NG's CI toolset (14.51) and use the
   prebuilt bundle.

**What would flip it:** one measurement, done on the Mac and under Nix with no Wine. Build a trivial NG plugin (SKSE load
plus one `BSAnimationGraphEvent` sink) with clang-cl 22.1 + xwin against NG built from source, with DirectXTK satisfied
by prebuilt shaders or a stub. Then run that DLL on the host for something like 20 of 20 clean loads into 1.7.104 under
SKSE 2.3.1. If it builds and loads, the Mac becomes the fast edit-compile loop and the host only runs the game.

## Open items / not verified (collected)

- The sha256 of the SKSE 2.3.1 archive and its exact file name, because the download is Nexus-only behind a login.
- The Nexus page for the Address Library: the "v13" label and the file names come from secondary sources.
- A SteamDB build/depot id for the 1.7.104 hotfix.
- Whether VS 2026 18.11's MSVC is 19.51.x, matching the prebuilt bundle; whether the VS 2022 component IDs are unchanged in VS 2026.
- Build Tools install size; any timing measured on g6.xlarge itself.
- The full Build Tools licence text.
- Whether nixpkgs xwin 0.9.0 supports the flags NG's recipe uses with 0.10.0.
- Any actual cross-compile on the Mac; the DirectXTK no-Wine workarounds.
- Whether 1.7 changed any `hkb*` or animation-graph layout. NG did not touch those classes in #298, but neither NG nor
  we have proven they are unchanged.
- Behavior Data Injector's 1.7.104 status.
