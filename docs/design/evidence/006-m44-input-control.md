> DIRTY-SIDE: reads CommonLibSSE-NG headers, SKSE sources and the source of other SKSE plugins (reverse-engineered descriptions of the game binary). Evidence for 006 M44 (projects/skyrim/docs/design/006-m44-oracle-first-slice.md), input and control pulled forward from D357. Not for the clean implementation (D289).

# Oracle input injection and game control on 1.7.104: what exists, and a proposal

Research only. Read **2026-11-01** (`date -u` → `Sun Nov  1 00:40 UTC 2026`) on `aubron-roam`.
No host access, no `devx oracle` verb, no credential. Nothing downloaded was built or run. "**not
verified**" marks what no primary source or measurement showed. Every NG file:line is at the
plugin's pin, `GraffAI/skyrim-oracle/extern/CommonLibSSE-NG` = `adebc31dcfa6` (v15.4.0,
`git log -1` → 2026-10-31 07:09Z). Other repositories were read through `gh api
repos/<r>/contents/<path>?ref=<sha>` at the commit named beside them.

**One measurement was made**: every Address Library ID cited below was looked up in the 1.7.104
table on this Mac (`~/skyrim-data-extracted/nexus/address-library-32444/versionlib-1-7-104-0.bin`,
sha256 `8aab3dd2…3842`, M44 §8). The script reads the format-5 header (96 bytes: format, version,
name, pointer size, data format, count) and the dense `uint32` offset array after it, the layout
NG's `src/REL/IDDB.cpp:258-303` loads. Header read: `format=5 version=1.7.104.0
name='SkyrimSE.exe' offsetCount=565759`. **A non-zero entry proves the ID has an address in
1.7.104, not that the function there has the same signature or prologue.** The table is §6.

---

## 1. In-engine injection on 1.7.104

### 1.1 `BSInputEventQueue` at the pin: the helpers exist and are 1.7-aware

- `include/RE/B/BSInputEventQueue.h:46-74` — `AddButtonEvent`, `AddCharEvent`, `AddMouseMoveEvent`,
  `AddThumbstickEvent`, `AddConnectEvent`, `AddKinectEvent`, each a variadic template forwarding to
  `AddEvent<T>` (`:300-308`): take the next **pre-built cached event** of that type from the
  queue's own arrays, `Init(...)` it, `PushOntoInputQueue` it, bump the count. `:85-86`
  `PushOntoInputQueue(InputEvent*)` and `ClearInputQueue()` are public.
- Per-frame capacity (`:29-35`): **10 button, 1 mouse-move, 2 thumbstick** events. A frame that
  needs more is dropped at `GetCachedEvent` (`src/RE/B/BSInputEventQueue.cpp:11-49`, returns
  `nullptr` past the max).
- **1.7 layout**: AE 1.7.99 inserted 8 bytes before the arrays and three new event arrays (sixaxis,
  motion gesture, amiibo; `:36-41`, `:172-181`). The accessors switch on
  `REL::Module::IsAtLeast(SKSE::RUNTIME_SSE_1_7_99)`: `GetRuntimeData()` at `0x28` instead of
  `0x20` (`:161-170`); queue head/tail at `0x558/0x560` instead of `0x380/0x388` (`:184-225`);
  per-type cached-array bases `kButtonEventArray{0x20, 0x28, …}` etc. (`:283-288`), stride `0x30`.
- **The singleton**: `RELOCATION_ID(520856, 407374)` (`src/RE/B/BSInputEventQueue.cpp:7`); 407374
  resolves in 1.7.104 (§6).
- **History that matters**: NG PR #298 (merged 2026-08-22, `gh api
  repos/alandtse/CommonLibSSE-NG/pulls/298`) modelled the 1.7.99 layouts and says it cross-checked
  them "against the real 1.6.1170 and 1.7.99 binaries directly in Ghidra". Its queue model was then
  **wrong for button events and was fixed twice**: PR #347 (merged 2026-09-12): "Calling
  `BSInputEventQueue::AddButtonEvent` from a combined SE/AE/VR build can overwrite event fields
  and crash … **DevBench's keyboard `tap` reproduces this on Skyrim AE 1.7.104**", with a table
  read from the engine's enqueue function: Steam AE 1.7.104 `0xCFB340`, first button `0x28`,
  stride `0x30`, head/tail `0x558/0x560`; validated "On Steam AE 1.7.104 / SKSE 2.3.1, the original
  `w` tap no longer crashes". PR #348 (2026-09-12) did the same for char/mouse/thumbstick/connect,
  "read from each runtime's disassembly"; it says other runtimes "have not been tested in a
  running game". Both are in our pin (`git log -- include/RE/B/BSInputEventQueue.h` → `2994ab4f6`
  #347, `0db97a2db` #348). **So `AddButtonEvent` on 1.7.104 has been run in a live game by a third
  party; `AddThumbstickEvent` and `AddMouseMoveEvent` on 1.7.104 have been checked only against
  disassembly (not verified live).**
- **A trap in the API** (devbench `src/KeyboardInput.cpp:52-54`): an `std::int32_t` id binds the
  VR-only `AddButtonEvent` overload (`BSInputEventQueue.h:79-82`, a no-op off VR) when the plugin is
  built with VR enabled. Our plugin is AE-only (M44 §8.1, `release-msvc-ae`), so the overload is not
  compiled in; pass `std::uint32_t` anyway.
- **The events** (all at the pin): `InputEvent` is `{vtable, device@08, eventType@0C, next@10}`,
  `0x18` (`include/RE/I/InputEvent.h:79-83`); `IDEvent` adds `userEvent@18, idCode@20`, `0x28`
  (`include/RE/I/IDEvent.h:23-27`); `ButtonEvent` adds `value, heldDownSecs` at `0x28`, size `0x30`
  on SE/AE (`include/RE/B/ButtonEvent.h:61-72`, `:176`); its `Init(device, id, value, duration,
  userEvent)` (`:145-153`) and a heap `ButtonEvent::Create(device, userEvent, idCode, value, held)`
  (`:35-59`). `IsDown` = value>0 && held==0, `IsHeld` = value>0 && held>0, `IsUp` = value==0 &&
  held>0 (`:27-33`). `ThumbstickEvent` `xValue@28, yValue@2C`, `0x30`, ids `kLeftThumbstick=0x0B`,
  `kRightThumbstick=0x0C`, `Init(id, device, x, y, userEvent)` (`include/RE/T/ThumbstickEvent.h:17-51`).
  `MouseMoveEvent` `mouseInputX/Y` ints, `0x30` (`include/RE/M/MouseMoveEvent.h:15-32`). None of these
  three classes has a 1.7 conditional; PR #298 changed only `InputEvent.h` (new AE event types 6-8,
  `include/RE/I/InputEvent.h:19-24`).

### 1.2 Where in the frame: at `BSInputDeviceManager::PollInputDevices`, not in an SKSE task

- `BSInputDeviceManager` is a `BSTEventSource<InputEvent*>` (`include/RE/B/BSInputDeviceManager.h:25-27`);
  `PollInputDevices(float)` is `RELOCATION_ID(67315, 68617)` (`src/RE/B/BSInputDeviceManager.cpp:153-162`).
  68617 → rva `0xCF95F0` in 1.7.104 (§6), 0x1D50 below PR #347's enqueue function at `0xCFB340`.
  The manager's own `RUNTIME_DATA` has **no** 1.7 conditional (`:71`, `0x80` on SE and AE).
- **SKSE's task queue is the wrong place.** SKSE 2.3.1 runs `TaskInterface` tasks inside
  `BSTaskPool::ProcessTasks`, called from two hooked call sites (`gh api
  repos/ianpatt/skse64/contents/skse64/Hooks_Threads.cpp?ref=v2.3.1`, lines 19-52); where those
  are in the frame relative to input is **not verified**, and devbench's author found the answer the
  hard way: "SKSE tasks can run after input dispatch and lose events at the queue reset"
  (devbench `src/KeyboardInput.cpp:99-100`), and "SKSE tasks can run on worker threads"
  (`src/Tools.cpp:678-679`). Injection must run from a hook of its own on the input pass.
- **Two hook points are proven by prior art**:
  1. **The entry of `PollInputDevices`** (devbench, below): a context hook over its first 10 bytes,
     guarded by a byte compare of the prologue (`48 89 5C 24 10 48 89 74 24 18`, "two five-byte
     register saves on SE, AE and VR"), then `queue->AddButtonEvent(...)`. Events added here are
     in the queue **before** the devices are polled and the list is dispatched, "before control
     mapping and dispatch so every input sink sees the hold" (devbench
     `src/KeyboardInput.cpp:896-917`). NG ships the helper: `SKSE::stl::install_context_hook`
     (`include/SKSE/ContextHook.h:89`).
  2. **The dispatch call inside it, `68617 + 0x7B`**: a 5-byte `E8` call to
     `BSTEventSource<InputEvent*>::SendEvent(InputEvent**)`; the hook prepends events to the list
     the game is about to send (InputBench `source/main.cpp:28-34, 116-142`, with an `E8` pattern
     check before writing). The same site is the standard input hook of menu mods: po3's PhotoMode
     `src/Hooks.cpp:172` `RELOCATION_ID(67315, 68617), 0x7B` (last push 2026-09-11, after 1.7.104),
     and a dozen others (`gh api 'search/code?q=68617+0x7B'`). **Whether `+0x7B` is still that call
     on 1.7.104 is not verified**: Favorite-Wheel's notes (`docs/RUNTIME_COMPATIBILITY.md`, read at
     HEAD) list "输入+0x7B签名 … 实际运行仍需1.7用户测试" (the +0x7B signature on 1.7 still awaits a
     user test), and InputBench was "Built and tested on Skyrim SE 1.5.97" only (README).
- Other points considered: `PlayerControls`' `BSTEventSink<InputEvent*>::ProcessEvent`
  (vtable[0] slot 1; TDM hooks it as `Handle`, `src/Hooks.h:330`) sees the list after the devices but
  only for player controls, not `MenuControls`; a hook on `PlayerControls`' per-frame update is
  not modelled by NG at the pin (no `Update` in `include/RE/P/PlayerControls.h`). Both rejected for
  injection; the first is a good **observation** point (§D-e).

### 1.3 Prior art, read

| project | repo @ commit | what it hooks | 1.7? |
|---|---|---|---|
| **devbench** (alandtse, GPL-3.0, on NG) | https://github.com/alandtse/devbench @ `938c392d5e0f` (pushed 2026-10-25) | context hook at `PollInputDevices` entry (`src/KeyboardInput.cpp:896-917`); per poll it drains its own task list, then re-emits **held** keys as `AddButtonEvent(device, 0, id, 1.0, heldSecs, "")` with `heldSecs` from a game clock, once per held key, and never in the same poll as the down (`:129-173`). Also: console exec via SKSE task + `RE::Console::ExecuteCommand` (`src/Tools.cpp:205-214`); save load via `BGSSaveLoadManager::Load(name, false)` in a task (`:640-677`); console `save`/`load` **rerouted** because a console save "runs the whole save synchronously inside the GFx console drain … can block in SkyrimVM::Freeze" (`:104-110`); engine frame counter `REL::RelocationID(525008, 411489)` (`src/GameState.cpp:13-16`); `bAlwaysActive:General` read/write (`src/BackgroundRun.cpp:7-27`); an opt-in test that `qqq` exits the process with code 0 within 30 s (`tests/http/test_shutdown.py:21-52`) | **yes**: NG PR #347's live validation was devbench on Steam AE 1.7.104 / SKSE 2.3.1. Its replay of a recorded walk is **pose teleports** (`player->SetPosition`, `src/ReplayDriver.cpp:156`), not input — not usable for us |
| **InputBench** (ApocryphaRealm, MIT) | https://github.com/ApocryphaRealm/InputBench @ `a904dd2f0a79` (pushed 2026-10-19) | `write_call<5>` at `68617+0x7B`; splices heap `ButtonEvent::Create(...)` / hand-built `MouseMoveEvent`s at the **head** of the dispatched list, `userEvent` from `ControlMap::GetUserEventName(code, device)`; held = value 1 with growing held secs for N dispatches, then value 0 (`source/main.cpp:46-113`). Comment: `BSInputEventQueue::GetSingleton()` "its SE relocation returned garbage and crashed (2026-08-30)" — before NG #347/#348 | no: "tested on Skyrim SE 1.5.97 … AE builds are expected to work but are not verified" |
| **True Directional Movement** (ersh1, GPL-3.0, on alandtse NG) | https://github.com/ersh1/TrueDirectionalMovement @ `57b913ae17` (v2.3.1, 2026-09-01) | vtable hooks on `MovementHandler` `ProcessThumbstick`/`ProcessButton` at slot `0x2/0x4 + (IsAtLeast(1_7_99) ? 2 : 0)` (`src/Hooks.h:12-15`), likewise `LookHandler`, `TogglePOVHandler`, the camera states' `PlayerInputHandler` sub-vtables (`:47-166`); call sites with `RELOCATION_OFFSET1799(SE, AE, AE1799)` (`src/Hooks.h:333-335`, macro in `src/PCH.h:32`) | **yes** (2.3.0, 2026-08-31, "IsAtLeast(1_7_99)") |
| po3 PhotoMode | https://github.com/powerof3/PhotoMode (HEAD `bf50c35ffb`, 2026-09-11) | `68617+0x7B` thunk call (`src/Hooks.cpp:172-173`) | build after 1.7.104; +0x7B on 1.7 **not verified** |
| ConsoleUtilSSE (VersuchDrei fork, GPL-3.0) | https://github.com/VersuchDrei/ConsoleUtilSSE @ `fd89858660` (2026-08-27) | console commands: `IFormFactory::GetConcreteFormFactoryByType<RE::Script>()->Create()`, `SetCommand`, `CompileAndRun(selectedRef)`, `delete` (`src/Papyrus.h:13-23`) | 1.7 build **not verified** |
| SkyrimPlatform (skymp), SmoothCam | skymp `skyrim-multiplayer/skymp` (pushed 2026-10-30); SmoothCam `mwilsnd/SkyrimSE-SmoothCam` (pushed 2026-10-01) | **not read** (no `BSInputEventQueue` hit in skymp's code search; SmoothCam reads input, does not inject) | not verified |
| OpenAnimationReplacer 3.2.1 | ORACLE.md S3 | its 1.7 change is a behaviour-graph offset (evidence/006-m44-toolchain.md §3), not input | — |

## 2. Movement, buttons and the 1.7 handler change

### 2.1 What PR #298 moved in the input handlers

- **Vtable slots, not fields.** 1.7.99 added two virtuals to `PlayerInputHandler`
  (`ProcessMotionGesture`, `ProcessSixaxis`, slots 2 and 3), so `ProcessThumbstick`/`ProcessMouseMove`/
  `ProcessButton` moved from 2/3/4 to **4/5/6**: `include/RE/P/PlayerInputHandler.h:39-52`
  (`REL::VersionShift(0x02, kAE1799AddedVFuncCount=2, RUNTIME_SSE_1_7_99)`); `HeldStateHandler`'s
  `UpdateHeldStateActive`/`SetHeldStateActive` 5/6 → 7/8 (`include/RE/H/HeldStateHandler.h:21-28`);
  the same for `MenuEventHandler` (`include/RE/M/MenuEventHandler.h:46-58`). PR #444 (merged
  2026-10-24, in our pin as `52d3a8ee8`) found the dispatcher `PlayerControls::DispatchInputEvent`
  at AE 1.7.104 `0x1407b0130` calling slot 2/3 with `&PlayerControls::data`.
- **Fields that moved**: `AttackBlockHandler`'s runtime data (`heldTimeMs`, `controlID`,
  `attackType`, `attackCount`, power-attack delays, `heldLeft/Right`) is at `0x18` before 1.7.99 and
  **`0x58` from 1.7.99** (`include/RE/A/AttackBlockHandler.h:36-55`, size `0xC0`); `LookHandler`
  gained a `0xA8` block at `0x10` (PR #298's patch of `include/RE/L/LookHandler.h`). `HeldStateHandler`
  (`heldStateActive@10, triggerReleaseEvent@11`), `MovementHandler`, `SprintHandler` (`0x18`) and
  `PlayerInputHandler` (`inputEventHandlingEnabled@08`) did not change size on AE.
- **Not 1.7-conditional at the pin**, i.e. NG's model says unchanged: `PlayerControls`
  (`data@024`, handler pointers `@170..1D0`, `blockPlayerInput@1D9`; `include/RE/P/PlayerControls.h:57-96`),
  `PlayerControlsData` (`moveInputVec@00, lookInputVec@08, prevMoveVec@10, autoMove@24, running@25`;
  `include/RE/P/PlayerControlsData.h:11-28`), `UserEvents` (`0x340`, `include/RE/U/UserEvents.h:188`),
  `ControlMap`'s getters. **Not verified** against the binary by us.
- **Consequence for us**: a plugin that **calls** a handler virtual must use NG's wrappers (which
  shift), and one that **hooks** a handler vtable must add 2 on 1.7.99+, as TDM does. A plugin that
  only **adds events to the queue** touches none of this: the engine's own dispatcher calls the
  shifted slots. That is the main argument for queue injection on this runtime.

### 2.2 Movement by `PlayerControlsData` write (TDM's way)

- **Where TDM writes**: inside its `MovementHandler::ProcessThumbstick` / `ProcessButton` hooks it
  saves `moveInputVec`, calls the original (which writes it from the event), restores, applies its
  own logic and writes `moveInputVec` itself, else puts the original's result back
  (`src/Hooks.cpp:126-158, 160-186`). So `moveInputVec` is written **by the handlers, when an event
  arrives**; TDM never writes it outside an event. Its "turn the character" part writes the
  player's heading (`playerCharacter->data.angle.z`, `src/DirectionalMovementHandler.cpp:1004-1014`).
- **Does the game's input pass overwrite a direct write?** Only when a movement event is processed
  (a stick event or a direction key down/up). Between events the vector appears to persist (TDM's
  `prevMoveVec` bookkeeping implies it), **not verified**. Who consumes it each frame: TDM hooks
  `MovementHandlerAgentPlayerControls` (`IMovementHandlerAgent` vtable, slot 2,
  `src/Hooks.h:231-238`) and touches `bDampenPlayerControls` there (`src/Hooks.cpp:1047-1056`), which
  marks that agent as the reader; its signature is `(void*, void*)` in TDM, unmodelled in NG.
- **Is it equivalent to real input?** For `Speed`/`Direction`: the agent reads the same vector
  whichever way it was written, so probably yes, **not verified**. For `IsSprinting` and run/walk:
  **no** — sprint is the `SprintHandler`'s state change (TDM hooks the sprint-state call
  `RELOCATION_ID(41271, 42350)`, `src/Offsets.h:59`), and `running` is toggled by the `Run`/
  `Toggle Always Run` handlers. A direct write is a second, partial model of the handlers; an
  injected event goes through the real ones. **Recommendation: inject events; keep the direct
  write only as a fallback for movement if injected thumbstick events are ignored** (§2.4).

### 2.3 Attacks, sprint, draw: synthesised `ButtonEvent`s, not direct `ProcessButton` calls

- The handlers decide by `userEvent`: their `CanProcess` compares `event->QUserEvent()` with the
  `UserEvents` names (TDM reads `a_event->QUserEvent()` against `UserEvents::GetSingleton()`,
  `src/Hooks.cpp:183-184`). The names at the pin: `"Forward"`, `"Back"`, `"Strafe Left"`,
  `"Strafe Right"`, `"Move"`, `"Look"`, `"Right Attack/Block"`, `"Left Attack/Block"`,
  `"Ready Weapon"`, `"Sprint"`, `"Run"`, `"Toggle Always Run"`, `"Jump"`, `"Console"`
  (`include/RE/U/UserEvents.h:84-116`). **There is no "Sheathe" user event**: `Ready Weapon`
  toggles draw/sheathe.
- **Queue injection reaches them.** devbench injects with an empty user event and a scan code
  and the `w` tap moved the player on 1.7.104 (PR #347's validation; where the engine maps the code
  to `"Forward"` after the poll is **not verified**); InputBench sets `userEvent` from
  `ControlMap::GetUserEventName(code, device)` (`source/main.cpp:48-51`). For a script keyed by
  user-event names (ORACLE.md §5.1), set **both**: the name, and the code from
  `ControlMap::GetMappedKey(name, device)` (`include/RE/C/ControlMap.h:89`), so either lookup works.
- **Holds must be re-emitted every frame.** The handlers are `HeldStateHandler`s; a hold is
  `value=1, held=0` once, then `value=1, held=t` on each later frame, then `value=0, held=t`
  (`ButtonEvent.h:27-33`). devbench re-emits the held event per poll with `t` from a clock, and
  "do[es] not emit a held event in the same poll as the initial down" (`src/KeyboardInput.cpp:149-171`).
  A light attack is a short hold (down + release before `initialPowerAttackDelay`,
  `AttackBlockHandler.h:45`); sprint is held for its duration.
- **Calling `ProcessButton` directly** (through NG's shifting wrapper, `PlayerInputHandler.h:49-52`)
  would also work but skips `PlayerControls`' own gating (`blockPlayerInput`, menu mode, the held-state
  bookkeeping in `heldStateHandlers`, `PlayerControls.h:63, 93`) — a different path from real
  input. Rejected for the oracle.

### 2.4 Thumbstick vs keyboard for movement

- Keyboard gives a digital vector (walk only through `Run`/`Toggle Always Run`). A left-thumbstick
  event `(kLeftThumbstick, x, y)` gives an analog vector; TDM shows `MovementHandler::ProcessThumbstick`
  writes `moveInputVec` from it (`src/Hooks.cpp:126-135`). Analog magnitudes are what make `Speed`
  sweep walk-to-run values, which the oracle wants.
- **Not verified**: whether the engine processes a `kGamepad` thumbstick event when no gamepad is
  connected (`BSInputDeviceManager::IsGamepadConnected`/`IsGamepadEnabled`,
  `BSInputDeviceManager.h:59-60`; `bGamepadEnable`), whether a single event per change suffices or
  one per frame is needed (inject every frame: 2 thumbstick slots per frame, §1.1), and whether a
  gamepad event flips the UI and camera to gamepad mode (TDM checks `IsUsingGamepad`,
  `src/Offsets.h:30-47`). The first host session answers all three (§ Proposal, Part 1.5a).

## 3. OS-level alternatives on the host

- **ViGEmBus** (virtual Xbox 360 pad): `nefarius/ViGEmBus` is **archived** (`archived=true`, last
  push 2023-11-02, latest release `v1.22.0` 2023-11-02, BSD-3-Clause; `gh api repos/nefarius/ViGEmBus`).
  Its README: "THIS PROJECT HAS BEEN RETIRED" and "**Windows Server** might work but is **not
  supported**". A "maintained fork", `NortheBridge/LuminalVGBus` (pushed 2026-08-19, 0 stars), says
  of itself "Status: alpha … not yet signed" and "**Never signed and never loaded**" (README).
  Microsoft: "Windows Server 2016 and greater only loads dashboard signed drivers that successfully
  pass the HLK tests" and "Attestation signing only works on Windows 10 Desktop and later"
  (https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/driver-signing-offerings,
  updated 2026-04-14). Whether ViGEmBus 1.22's `.sys` is HLK- or attestation-signed is **not
  verified**; if attestation, it will not load on our Server 2022 without test signing (a boot-mode
  change on a Spot host: no).
- **HIDMaestro** (`hifihedgehog/HIDMaestro`, pushed 2026-10-27, 129 stars): user-mode (UMDF2) virtual
  controllers "signed with a locally trusted self-signed certificate. No EV certificate, no
  `testsigning`", XInput included, "requires administrator" (README). That a self-signed UMDF2
  driver loads on Server 2022 is **not verified**; licence `NOASSERTION`.
- **Sunshine already does OS-level injection on our host.** The host runs Sunshine
  `v2026.914.233613` (`devx/oracle/host-setup.ps1:84-86`, origin/main). Its Windows input code
  probes ViGEmBus and logs "ViGEmBus is not installed or running" when absent
  (`src/platform/windows/input.cpp:255-260` at that tag); whether the host has ViGEmBus is **not
  verified**. The operator's Moonlight keyboard reached the game in the console session on
  2026-11-01 (the `loco1hm` save was made by typed console commands, M44 §8), so **keyboard
  injection into the runner's console session works there**; by which API Sunshine does it was
  not read.
- **`SendInput`**: needs the game window in the foreground of the interactive session; InputBench's
  README: "`SendInput` from a script — is blocked by the foreground lock the moment the game is not
  the active window". Skyrim reads keyboard/mouse through DirectInput devices
  (`BSWin32KeyboardDevice`/`BSWin32MouseDevice`, `BSInputDeviceManager.h:19-20`); that `SendInput`
  reaches them is what Sunshine's path suggests, **not verified** at source.
- **XInput on Server 2022 with the gaming driver**: **not verified** (no source read; the host's
  NVIDIA gaming driver is a display driver and says nothing about `xinput1_4.dll`).
- **Weighing.** OS-level input is engine-blind and cannot perturb what the plugin measures, but the
  oracle plugin is already inside the engine with graph and event hooks; one more hook at the input
  poll, upstream of everything the oracle observes and touching no graph state, adds little
  perturbation. Against OS-level: no frame alignment (ORACLE.md §5.2 accepts non-determinism, but
  §6.4's self-check and bisecting want repeatable inputs), the focus/foreground dependency, a
  kernel driver of uncertain signing on a Server SKU for analog sticks, and a second process to
  feed it. **In-engine wins**; OS-level is the fallback if the poll hook fails its prologue check.

## 4. Control without input

| need | mechanism at the pin | 1.7 binding (§6) | notes |
|---|---|---|---|
| load a named save from the main menu | `BGSSaveLoadManager::GetSingleton()->Load(name, false)` (`src/RE/B/BGSSaveLoadManager.cpp:35-38` → `Load_Impl`, `:61-65`, `RELOCATION_ID(34819, 35728)`); singleton `(516860, 403340)` | 35728 ✓, 403340 ✓; no 1.7 conditional | devbench calls it from an SKSE task and says "the named path works from the menu", while `LoadMostRecentSaveGame()` "is a silent no-op from the Main Menu (verified live)" (`src/Tools.cpp:635-647`); `checkForMods=false` "skips the mod-mismatch modal" (`:676`). Runtime of that live check **not stated**. **Part 2 owns the auto-load** (another agent, now); this pass only says what it found |
| when to load | `MenuOpenCloseEvent` for `"Main Menu"` (`include/RE/M/MainMenu.h:30`) or `UI::IsMenuOpen` (`src/RE/U/UI.cpp:45`); UI singleton `(514178, 400327)` | 400327 ✓ | |
| console commands (`coc`, `tgm`, `player.additem`, `sgtm`, `tai`) | `Script` from `IFormFactory`, `SetCommand`, `CompileAndRun(ref)` (ConsoleUtilSSE, §1.3; `src/RE/S/Script.cpp:30-62`): `CompileAndRun_Impl` = `RELOCATION_ID(21416, AE_CHECK(RUNTIME_SSE_1_6_1130, 21890, 441582))` | **441582 ✓, 21890 absent** in 1.7.104 — the `AE_CHECK` branch is what makes it resolve | or `Console::ExecuteCommand` (`src/RE/C/Console.cpp:10-22`, `RELOCATION_ID(50157, 51084)`, needs a menu on the stack; devbench uses it); 51084 ✓. **Never `save`/`load` through the console** (devbench's deadlock note, §1.3) |
| pause / slow time | `sgtm <x>` by console; `BSTimer::QGlobalTimeMultiplier()` to read (`include/RE/B/BSTimer.h:14`) | — | `tfc` is the free camera, not a pause |
| end the run | (a) `qqq` by `CompileAndRun`/`ExecuteCommand`: devbench's test expects exit code 0 within 30 s and warns "DLL teardown can hang after the window closes" (`tests/http/test_shutdown.py:43-52`); (b) `Main::GetSingleton()->GetRuntimeData().quitGame = true` (`include/RE/M/Main.h:83-101`, singleton `(516943, 403449)`) | 403449 ✓; `Main`'s data has no 1.7 conditional | that (a) or (b) exits cleanly on 1.7.104 is **not verified**; D357's fallback (kill at `timeout_s`, `done`=124) stays |
| detect state | `kPostLoadGame` (`include/SKSE/Interfaces.h:454`), `"Loading Menu"` closed (`include/RE/L/LoadingMenu.h:21`), `PlayerCharacter::GetSingleton()->Is3DLoaded()`, the engine frame counter `(525008, 411489)` (devbench `src/GameState.cpp:15`) | 411489 ✓ | |
| run in the background | `bAlwaysActive:General` (devbench `src/BackgroundRun.cpp:9`) — the game otherwise stops on focus loss (**not verified** on our host) | — | set it in `SkyrimPrefs.ini`/`Skyrim.ini` by `run.ps1`, not at runtime |

## 5. Camera

- `PlayerCamera::yaw` "target's heading + per-state offset, radians, set by UpdateYaw()"
  (`include/RE/P/PlayerCamera.h:118`); `currentState`, `IsInThirdPerson()`, `ForceThirdPerson()`
  (`:138-164`); singleton `(514642, 400802)`, 400802 ✓. `ThirdPersonState` `targetYaw@7C,
  currentYaw@80, freeRotation@D4, freeRotationEnabled@DC`, `0xE8` (`include/RE/T/ThirdPersonState.h:72-94`).
  **No 1.7 conditional on either**; PR #298 touched only `ThirdPersonState`'s vtable declarations
  (`ProcessButton` slot under `EXCLUSIVE_SKYRIM_VR`). devbench writes these fields live and says its
  yaw sense was "observed on AE 1.7.104" (`src/Tools.cpp:3488-3491`) — for the free camera
  (`FreeCameraState::rotation`); its third-person orbit writes `targetYaw`/`currentYaw`/
  `freeRotation.x` and the player's pitch `pc->data.angle.x` (`src/CameraOrbit.cpp:21-67`).
- **For ORACLE.md §5.1's absolute `look`**: in third person without free rotation the camera
  follows the player's heading, so `look.yaw` is the **player's** heading
  (`data.angle.z`) and `look.pitch` its `data.angle.x`, written from the poll hook. Whether the
  engine then derives `TurnDelta` from a written heading the way it does from look input is **not
  verified** and is exactly what the oracle should record either way; the alternative, injecting a
  `lookInputVec` step toward the target, puts look sensitivity back in the loop. Keep absolute,
  measure (D-d).

## 6. Address Library IDs in the 1.7.104 table (measured)

`python3 -I idcheck.py versionlib-1-7-104-0.bin <label>=<id> …` (a 30-line reader of the format-5
header and offset array, kept in the session scratchpad, not committed), 2026-11-01:

| what (NG file) | AE id | 1.7.104 |
|---|---|---|
| `BSInputEventQueue` singleton | 407374 | rva `0x325A7D8` |
| `BSInputDeviceManager` singleton / `PollInputDevices` / `GetButtonNameFromID` | 402776 / 68617 / 68618 | `0x3204B30` / `0xCF95F0` / `0xCF96C0` |
| `PlayerControls` singleton / ctor / `RegisterHandler` | 400864 / 42336 / 42356 | `0x31A5698` / `0x7AD450` / `0x7AF240` |
| `UserEvents` / `ControlMap` / `MenuControls` / `UI` singletons | 402638 / 400863 / 401263 / 400327 | all present |
| `Console::ExecuteCommand` delegate / selected ref (1.6.1130+) | 51084 / 504099 | present |
| `Script::CompileAndRun_Impl` 1.6.1130+ / pre-1130 | 441582 / 21890 | `0x343D00` / **0 (absent)** |
| `BGSSaveLoadManager` singleton / `Load_Impl` / `Save_Impl` / `LoadMostRecentSaveGame` | 403340 / 35728 / 35727 / 35766 | all present |
| `Main` singleton; devbench's frame counter; `PlayerCamera` singleton | 403449; 411489; 400802 | present |
| vtables: `PlayerInputHandler`, `ThirdPersonState`[0..1], `PlayerControls`[0], `LookHandler`, `MovementHandler`, `SprintHandler`, `AttackBlockHandler`, `MenuControls`[0] | 205234, 205236/205238, 208694, 208710, 208715, 208717, 208719, 215773 | all present |

Consistency, not proof: `PollInputDevices` (`0xCF95F0`) sits just below the enqueue function
PR #347 measured (`0xCFB340`), and `RegisterHandler` (`0x7AF240`) just below the dispatcher PR #444
measured (`0x7B0130`).

---

## § Proposal — "Part 1.5: input and control"

**Summary.** Inject scripted input **in the engine, at the entry of
`BSInputDeviceManager::PollInputDevices`** (a prologue-checked context hook, devbench's 1.7.104-proven
point), by filling NG's `BSInputEventQueue` with `AddThumbstickEvent` (movement, analog, every
frame while non-zero) and `AddButtonEvent` (user events: `Right Attack/Block`, `Sprint`,
`Ready Weapon`, …, down / per-frame held / up), so the engine's own dispatcher and handlers — whose
1.7.99 vtable shift we then never touch — turn it into `PlayerControlsData`, actions and graph
events exactly as they do real input. `look` stays absolute and writes the player's heading and
pitch from the same hook. **Control** (load, setup commands, quit) is in-engine too: the save load
is Part 2's `BGSSaveLoadManager::Load(name, false)`; setup `console` lines run through
`Script::CompileAndRun` (whose 1.7 ID is the `AE_CHECK` branch we measured present); the end is
flush, then `qqq`, with `run.ps1`'s kill as the backstop. OS-level input (Sunshine's path,
ViGEmBus, `SendInput`) is rejected as primary: no frame alignment, a foreground dependency, and a
gamepad driver of doubtful signing on Server 2022; it is the fallback if the hook's check fails.

### Decision candidates

- **D-a — Input enters through `BSInputEventQueue`, filled from a context hook at
  `PollInputDevices`' entry (`RELOCATION_ID(67315, 68617)`), installed only if the first 10 bytes
  equal the known prologue; otherwise the plugin logs `input hook refused` and the run is
  `done`=3 (no input), never a guess.** Reason: the one hook point with a live 1.7.104 user
  (devbench, NG #347); events added before the poll reach every sink and the real handlers; no
  handler vtable is hooked, so PR #298's slot shift is the engine's concern. Flips if: the prologue
  differs on our exe (then `68617+0x7B` with an `E8` check, InputBench/PhotoMode's site), or
  injected events are lost (then `PlayerControls`' `ProcessEvent` list splice).
- **D-b — Movement is a left-thumbstick event every frame while the script's `stick move` is
  non-zero, `device=kGamepad`; a zero is sent once on release.** Reason: analog `Speed`, one event
  per frame removes any dependence on persistence. Flips if Part 1.5a shows the engine ignores
  gamepad events with no pad connected: then digital keys (`Forward`/`Back`/`Strafe *` as buttons)
  plus `Run`, and analog speed is out of scope until a direct `moveInputVec` write is justified by a
  measured equivalence (§2.2).
- **D-c — Buttons are user-event names resolved to codes with `ControlMap::GetMappedKey`; both name
  and code go into the event; a hold is down, then held with real elapsed `heldDownSecs` every
  frame, then up, never down and held in the same frame.** Reason: §2.3; devbench's held-key rules.
  Flips if a handler is shown to ignore a named event with a keyboard code (then device-native
  codes only).
- **D-d — `look` is absolute: the player's heading (`data.angle.z`) and pitch (`data.angle.x`)
  are written in the hook, in third person with free rotation off.** Reason: ORACLE.md §5.1,
  removing sensitivity; the oracle records whatever `TurnDelta` the engine derives. Flips if the
  written heading yields no `TurnDelta` change or snaps the graph (then a right-thumbstick event
  sized from the remaining angle, recorded as such).
- **D-e — The plugin records what it injected and what the engine made of it**: a `in.input` line
  per injected event (name, value, held) and the frame's `PlayerControlsData`
  (`moveInputVec`, `lookInputVec`, `running`) read in `PlayerControls`' `ProcessEvent` after the
  original. Reason: ORACLE.md §4.6's cross-check; a scenario whose input was dropped is visible in
  the trace. These are engine-structure fields: they go to `oracle.log`/a side file, **not** the
  clean trace (I187), unless the operator rules otherwise.
- **D-f — Frames are input polls.** Script frame 0 is the first poll after `kPostLoadGame` with
  `Loading Menu` and `Fader Menu` closed and the player's 3D loaded, plus `settle` polls (default
  60); the engine frame counter (`411489`) is logged beside it. Reason: the hook runs once per poll;
  this is the only clock the injector owns.
- **D-g — Setup `console` lines run through `Script::CompileAndRun` on the main thread, from the
  poll hook, before frame 0; `save`/`load` are refused in scripts.** Reason: §4; devbench's
  console-save deadlock. Flips: none foreseen.
- **D-h — `end` flushes and closes the trace, then issues `qqq`; `run.ps1` waits 30 s for the
  process to exit, then kills it.** `done`: 0 exited by itself, 124 killed after a closed trace
  (D357), 3 input hook refused. Reason: D357 asked for this path; devbench's test is the prior art.
  Flips if `qqq` hangs on 1.7.104 (then `Main::quitGame`, then the kill alone).
- **D-i — `run.ps1` sets `bAlwaysActive=1` in the INI before launch.** Reason: an unattended run
  must not depend on window focus. Flips if the host measures no pause on focus loss.

### Invariant candidates

- **I-a — No handler or camera vtable is written by the injector.** The input path's only hook is
  D-a's; `oracle.log` lists every installed hook at load. Check: `grep -c 'hook installed'
  oracle.log` equals the documented count.
- **I-b — Injection never exceeds the queue's per-frame capacity silently**: an event that does not
  fit (10 button, 2 thumbstick, 1 mouse) is logged with its frame. Check: `grep 'input dropped'`
  is empty for the exit's scenario.
- **I-c — Input runs only inside the judged window or setup**: nothing is injected while
  `Main Menu`, `Loading Menu` or `Console` is open, or before D-f's frame 0, except D-g's setup.

### Script format

ORACLE.md §5.1 is kept. Clarifications, not changes: `f` counts D-f's polls; `button` ids must be
`UserEvents` names (`"Ready Weapon"` draws and sheathes; there is no `"Sheathe"`); `hold` frames are
re-emitted held events (D-c); `stick` ids are `move` (left) and, if D-d flips, `look` (right); the
`setup` line gains an optional `settle` (default 60) and its `dt` is ignored until a fixed timestep
exists; `console` lines with `save`/`load` are rejected by the loader. Considered and rejected: an
event-keyed wait (`{"k":"wait","until":"attackStop"}`); frame keys stay the only clock, so a script
is the same input on every run.

### Exit (what `devx oracle run projects/skyrim/oracle/scenarios/loco-1hm-scripted` must show, no human)

1. Part 1.5a probe (a `run.cmd`-free scenario `input-probe`, ~3 min of game): `oracle.log` →
   `input hook installed (prologue ok)`; for 60 frames each, a left stick `(0, 0.5)` then `(0, 1)`
   and a keyboard `Forward`: the logged `moveInputVec` non-zero and the player's position changed
   (`player x,y` before/after in `oracle.log`); `done`=0. This answers §2.4's three unknowns.
2. The scripted capture: `loco1hm` loaded with no Moonlight session (Part 2's load), the script's
   ~90 s (stand, walk 4 ways at stick 0.5, run at 1.0, turn 360° each way by `look`, sprint 3 s,
   `Ready Weapon`, one `Right Attack/Block` hold 6 frames, `Ready Weapon`, stand), `end`.
3. In `--out`: the trace passes `tools/trace/check` → `ok`; `tools/trace/coverage` shows
   `moveStart`, `SprintStart`, `attackStart` as `in.evt`, `weaponSwing`, `HitFrame` as `out.evt`,
   `Speed` taking at least two distinct non-zero plateaus (walk, run) as `in.var`; the side file
   shows every scripted event injected, `input dropped` absent.
4. The game quit by itself: `done`=0 within `duration_s` + 30 s (or 124 per D-h, said so in §8).
5. Run twice: the `out.evt` name sequence from `attackStart` to `attackStop` equal (M44 exit 6,
   now without a human).
6. `tools/wall/check` → `ok`; `devx oracle down` → `stopped`; hours and dollars in §8.

### Estimate

3–5 engineer-days: the hook, queue writer and held-state machine ~1 d (devbench is a worked
example, GPL-3.0 like our plugin, so its approach can be followed directly); the script loader and
D-f clock ~0.5 d; console/quit ~0.5 d; the probe and its answers 1 d; the scripted scenario and
exit 1–2 d. Host: 4–8 sessions of ~10–15 min (≈ $0.05–0.07 each at the Spot rate in M44 §8).
**Not verified** against anyone's velocity. It depends on Part 2's load and Part 2's frame hook
(share one poll hook rather than two).

### Risks

1. **Gamepad events with no gamepad** (§2.4): if the engine drops them, analog movement needs a
   direct `moveInputVec` write, a second model of the handler with unmeasured fidelity; walk/run
   then come from `Run` only.
2. **Untested queue paths on 1.7.104**: `AddButtonEvent` was validated live there (NG #347);
   `AddThumbstickEvent`/`AddMouseMoveEvent` only against disassembly (#348). A wrong offset is a
   crash in `BSStringPool` on the first event — loud, but a lost session.
3. **Heading writes vs `TurnDelta`** (D-d): writing the heading may bypass the turn path the
   graph's turn blend and `turnLeft/Right*` events depend on; the scenario's 360° turns could show
   no turn events. The fallback (right stick) reintroduces sensitivity.
4. **`qqq` teardown hang** (devbench's own warning): the kill fallback keeps the run bounded; a
   hung exit must not lose the trace (flush before quit, D-h).
5. **Focus and the console session**: with no Moonlight client, the game window's focus and
   `bAlwaysActive`'s effect are not measured on our host; a paused game would look like a dropped
   script.
6. **Coupling with Part 2** (another agent now): two hooks on the same poll, or a load path chosen
   twice; the plan above takes Part 2's load and frame hook as given.
7. **Wall** (I187/I188): D-e's `PlayerControlsData` echo is an engine structure; it must stay out of
   the trace and out of clean files.

### What this pass did not do

- Read SkyrimPlatform's or SmoothCam's source; read OAR's input handling (it has none relevant).
- Check any address against the 1.7.104 exe (only the Address Library table); check the
  `PollInputDevices` prologue or `+0x7B` on our exe.
- Verify ViGEmBus 1.22's signing type, ViGEmBus's presence on the host, XInput on Server 2022, or
  how Sunshine injects keyboard input.
- Verify on which runtime devbench's "named load works from the menu" and `qqq` test were run.
- Write plugin code, touch the host, or use any credential.
