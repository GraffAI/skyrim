> DIRTY-SIDE: the names and their graph roles are read from the data files (clean); the engine-input / engine-sent classification applies semantics/contract.md (DIRTY-SIDE). Evidence for 006 M44. Names and counts only (I152). The scripts are tools/slice/.

# Slice 1 names: player locomotion + one-handed right light attack (measurement, 2026-10-19)

Names and counts only (I152). Source: the stock graphs converted to XML at
`aubron-mini:~/skyrim-data-extracted/xml/meshes/actors/character/` (this Mac has no
`~/skyrim-data-extracted`: `ls ~/skyrim-data-extracted` printed nothing). Every list below comes from
stdlib Python scripts run over that XML with `python3 -I`, piped over ssh. The scripts are in
`tools/slice/` (`lib.py`, `slice.py`, `comps.py`, `summ.py`, `sm.py`, `tree2.py`, `path.py`,
`findvar.py`, `ad.py`, `final.py`; its README). The invocation pattern is:

    S=<this scratchpad>; cd $S
    (cat lib.py; echo "sys.argv=['x','<file>.xml','<args>']"; cat <script>.py) | ssh mini python3 -I -
    (cat lib.py; echo "SPEC=[]"; cat slice.py comps.py) | ssh mini python3 -I - | tail -1 > comps.json
    python3 -I final.py     # the unions, the counts and the classification columns below

**Clean or dirty.** The names, the files they sit in and the graph roles (which node reads or writes
a variable, which transition listens for an event, which clip raises it) are read straight from
the data and are **clean**. The **class** column (engine-input, engine-sent and so on) applies
`semantics/contract.md` §1/§2 pooled rules (`graph_contract.json` `V[n].wg/rg`, `ev_sets.json`
L/G/T on mini). It is **DIRTY-SIDE**: the rules depend on a hand-picked list of output members.
"Read or write" also uses that member list (contract.md §0, "Rules used").

## 1. The player's third-person graph set

Command: `grep -o 'behaviorFilename">[^<]*' characters/defaultmale.xml "characters female/defaultfemale.xml"`
and `grep -A3 characterFilenames defaultmale.xml`. Project `meshes/actors/character/defaultmale.hkx`
→ character `characters/defaultmale.hkx` (female: `characters female/defaultfemale.hkx`) → root
`behaviors/0_master.hkx`. The project holds 18 behaviour files (`disc.py`). Together they declare
**301 variables and 1,985 events** (union, `final.py` preamble).

Node counts come from `jq '.graphs["meshes/actors/character/behaviors/<f>.hkx"].nodes' census/census.json`.

| file (under `meshes/actors/character/`) | nodes | vars decl. | events decl. | role in slice |
|---|---|---|---|---|
| `behaviors/0_master.hkx` | 1,123 | 230 | 1,217 | root; `RootModifierList` holds `BSSpeedSamplerModifier`; jump states |
| `behaviors/mt_behavior.hkx` | 2,711 | 67 | 931 | unarmed locomotion (`MT_Default_Behavior`) |
| `behaviors/sprintbehavior.hkx` | 70 | 14 | 26 | sprint (referenced from mt, 1hm_locomotion) |
| `behaviors/1hm_behavior.hkx` | 2,608 | 101 | 461 | weapon readied; `AttackState` |
| `behaviors/1hm_locomotion.hkx` | 293 | 17 | 16 | weapon-drawn movement |
| `behaviors/idlebehavior.hkx` | 866 | 7 | 44 | **excluded** (standing idles, `IdleBFR`) |

How the files nest (from `path.py`, a BFS from each graph root):
- `0_Master`: `Master_Behavior › Root › RootModifierGenerator › … › RootBehaviorGraph › Default_State › Default_Behavior`
  - `› MT_Behavior_State › MT_LeftHandOverride › MT_H2H_State` → `MT_Behavior.hkx`
  - `› Weap_Readied_State` → `1HM_Behavior.hkx`
- `MT_Behavior`: `… › MT_BehaviorGraph › MT_Default_State › MT_Default_Behavior`, whose states are
  - `MT_Standing_State` (turn in place; `IdleBFR`)
  - `MT_LocomotionType_State › MT_Locomotion_Behavior { Default_Locomotion_State, Sprint_State → SprintBehavior.hkx }`
- `1HM_Behavior`: `1HM_Behavior { 1HM_Ready_State, AttackState, … }`
  - `1HM_Ready_State › 1HM_Readied_BehaviorGraph › 1HM_1HM_Readied › 1HM_Standing_Locomotion_Behavior { 1HM_Standing_State, 1HM_Locomotion_State → 1HM_Locomotion.hkx }`
  - `AttackState › 1HM_AttackState_Generator › 1HM_AttackBehavior { AttackRight_State (start state 0), … }`
  - `AttackRight_State › AttackRightMSG › AttackRight_WeapTypeSelection { AttackRight_1HMSword … } › AttackRight_1HM_iStateGen › AttackRight_1HM_Behavior › 1HM_AttackRight_DefaultState › 1HM_AttackRight_Behavior`

**How the slice was cut** (`comps.py`). Each component is the downward reference closure of the
named node, stopped at the listed nodes. `ctx` adds the binding sets and enter/exit notify arrays
of the node's ancestors, plus the modifiers of ancestor `hkbModifierGenerator`s (tag `mg`). For
the named ancestor state machines it also adds their transitions *into* (`in`) and *out of*
(`out`) the path.

| component | root | stops |
|---|---|---|
| speed sampler | `0_master` `RootModifierList`, then only `BSSpeedSamplerModifier`'s 4 bindings kept | — |
| mt_default | `mt_behavior` `MT_Default_Behavior` | `IdleBFR`, `SprintBFR`, `SneakIdleTurnState`, `MT_Sneak_Locomotion_State` |
| sprint | `sprintbehavior`, whole file | — |
| 1hm_standing | `1hm_behavior` `1HM_Standing_Locomotion_Behavior` | `Weapon_Locomotion_BFR` |
| 1hm_locomotion | `1hm_locomotion`, whole file | `sprintBFR` |
| attack_right | `1hm_behavior` `AttackRight_State`; ctx SMs `1HM_AttackBehavior`, `1HM_Behavior` | `AttackRight_H2H`, `_2HM_Sword`, `_2HW`, `1HM_AttackRightRoot_Player_OLD`, `1HM_AttackRight_SneakState`, `AttackRight_StaffLeftBlend` |
| 1hm_ready_mods | `1hm_behavior` `1HM_Ready_State_MG` | `1HM_Readied_BehaviorGraph` |
| jump (optional) | `0_master` six `Jump*` states; ctx SM `RootBehaviorGraph` | — |

## 2. Locomotion variables (42; command: `python3 -I final.py`, section LOCO)

**Direction and speed inputs (blend-space parameters), exact names:**
- **`Speed`** (REAL) is read in `0_master` by `BSSpeedSamplerModifier.goalSpeed`, which sits in
  `RootModifierList` and is therefore always active. Its other inputs are `Direction` and `iState`
  (INT32). It writes **`SpeedSampled`** (REAL, `speedOut`).
  - `mt_behavior` and `1hm_locomotion` never bind `Speed`. They read `SpeedSampled` as
    `hkbBlenderGenerator.blendParameter`.
- **`Direction`** (REAL) drives `BSCyclicBlendTransitionGenerator.fBlendParameter` in
  `mt_behavior`, `1hm_locomotion` and the attack.
- **`TurnDelta`** (REAL) is read in three places in `mt_behavior`: `hkbBlenderGenerator.blendParameter`,
  `hkbEventsFromRangeModifier.inputValue` and `hkbRotateCharacterModifier.degreesPerSecond`.
  - The `hkbEventsFromRangeModifier` read is what raises `turnLeft/RightFast/Slow`.
  - In `1hm_behavior`, `TurnDelta` goes through `hkbDampingModifier.rawValue` to `TurnDeltaDamped`,
    which feeds a blend parameter.
- **Not found:** `walkBackRate` is declared in `0_master` but bound by no node.
  `speedForward/Back/Left/Right`, `TargetSpeed` and `MovementDirection` are in no player file.
- Command: `python3 -I -c "…"` over `whole.json` (per-file read/write sites, printed in the session).

Classes are DIRTY-SIDE, pooled over 428 graphs. "player-W" means some node in the 18 player files
writes the variable (`whole.json`).

| class | names |
|---|---|
| engine-input (read, never graph-written) | `Direction`, `TurnDelta`, `bSprintOK`, `iSyncIdleLocomotion`, `iSyncIdleState`, `iSyncSprintState`, `i1stPerson`, `IsFirstPerson`, `IsNPC`, `IsPlayer`, `iRightHandType`, `iLeftHandType`, `iRightHandEquipped`, `iLeftHandEquipped`, `iWantBlock`, `bWantCastVoice`, `iDrunkVariable`, `weapAdj`; constants `blendDefault`, `blendMove1stP`, `blendMoveStart`, `blendMoveStop` (22) |
| pooled "written+read" but **no writer in the player files** (so the engine writes them for the player) | `Speed`, `iState`, `iSyncTurnState` (3) |
| graph→engine flags (never read in any graph) | `IsSprinting` (sprint SM `isActive`), `bInMoveState` (1hm_locomotion SM `isActive`), `IsSneaking`, `bMotionDrivenDialogue`, `i1HMState` (`1HM_Behavior.currentStateId`) (5) |
| graph-internal / both | `SpeedSampled`, `TurnDeltaDamped`, `bAllowRotation`, `IsAttackReady`, `bHeadTrackSpine`, `bVoiceReady`, `bodyMorphWeight`, `bodyMorphMuscular`, `iIsInSneak`, `IsCastingLeft`, `bBlendOutSlow`, `bForceIdleStop` (12) |

`iSyncSprintState` is also `hkbStateMachine.syncVariableIndex` in `mt_behavior` and sprint.
`iSyncIdleLocomotion` and `iIsPlayer` select start states through `startStateId` bindings.

## 3. Locomotion events (49; `final.py`, LOCO)

The engine-sent and graph-raised classification is DIRTY-SIDE. The listening sites are clean.

- **Start/stop moving:** `moveStart`, `moveStop`. They are listened by transitions in `mt_behavior`
  and `1hm_behavior`. Pooled class "both" (contract.md §2 names them as data that cannot separate
  engine from annotation). No player-slice node raises them.
- **Sprint:**
  - `SprintStart` is engine-sent, listened in `mt_behavior` and `1hm_locomotion`.
  - `SprintStop` is listened there too, and is also raised by a clip trigger in `sprintbehavior`.
  - `sprintbehavior` raises `FootSprintLeft`, `FootSprintRight` and `tailSprint`, and on state
    notify `attackStop`, `StartAnimatedCameraDelta`, `EndAnimatedCamera` and `EndAnimatedCameraDelta`.
- **Turn:**
  - Listened: `turnLeft`, `turnRight`, `turnStop`.
  - `turnLeftFast`, `turnLeftSlow`, `turnRightFast` and `turnRightSlow` are both raised by the
    graph's own `hkbEventsFromRangeModifier` (on `TurnDelta`) and listened.
- **Blend control:** `CyclicCrossBlend`, `CyclicFreeze` (engine-sent; `BSCyclicBlendTransitionGenerator`).
- **Footsteps** (clip triggers; the same names are in `animationdatasinglefile.txt`): `FootLeft`,
  `FootRight`. `MotionDrivenIdle` is raised by 32 `mt_default` clip blocks (`ad.py`).
- **State notifies** (graph-raised): `tailMTIdle`, `tailMTLocomotion`, `tailCombatIdle`,
  `tailCombatLocomotion`, `tailCombatState`, `tailSneakIdle`, `tailSneakLocomotion`, `IdleStop`,
  `IdleOffsetStop`, `OffsetStop`, `HeadTrackingOn`, `StartAnimatedCameraDelta`, `EndAnimatedCamera`,
  `PickNewIdle`, `IdleDefaultStart` (expression), `BeginCastVoice` (modifier).
- **Inside the closure but not locomotion proper (candidates to drop):**
  - dialogue: `IdleDialogueStart/AngryStart/ExpressiveStart/HappyStart`, `LooseDialogueResponsePositive/Negative`;
  - sneak and dodge: `SneakStart`, `SneakStop`, `SneakSprintStartRoll`, `DodgeBack/Left/Right`.
  - Without these 12, locomotion has **37** events.
- **Jump** (optional; +4 vars, +11 events beyond the union; `final.py`, JUMP):
  - entry, engine-sent: `JumpStandingStart`, `JumpDirectionalStart`;
  - clip-raised and listened: `JumpFall`, `JumpFallDirectional`, `JumpLand`, `JumpLandDirectional`, `JumpLandEnd`;
  - notify: `JumpUp`, `JumpDown`, `InterruptCast`; also `StaggerPlayer`;
  - variables: `bInJumpState` (graph→engine), `BlendJump`, `bHumanoidFootIKDisable`, `blendFast`.

## 4. One-handed right light attack (`1hm_behavior.hkx`; 23 vars, 44 events; `final.py`, ATTACK)

**Path for a sword** (`sm.py` on `1HM_Behavior,1HM_AttackBehavior,AttackRight_WeapTypeSelection,1HM_AttackRight_Behavior`):
- `1HM_Ready_State` → `AttackState` (stateId 10) on **`attackStart`**. The transition's
  `hkbExpressionCondition` reads `bWantCastLeft`. `streamingQuery_attackStart` also enters.
- `1HM_AttackBehavior` starts in `AttackRight_State` (startStateId 0).
- `AttackRightMSG.selectedGeneratorIndex` is bound to `iLeftHandType`.
- `AttackRight_WeapTypeSelection.startStateId` is bound to `iRightHandType`. 1 selects `AttackRight_1HMSword`.
- `1HM_AttackRight_Behavior.startStateId` is bound to `iIsPlayer`. 1 selects `1HM_AttackRightRoot_Player_TEST`.
- `1HM_AttackRightPerspectiveMSG_TEST.selectedGeneratorIndex` is bound to `i1stPerson`.
- That reaches `1HM_AttackRight_BSCyclicBlendTransitionGenerator` (`fBlendParameter` = `Direction`).
- Below it are four directional blends (`blendParameter` = `SpeedDamped`). The speed-0 child of
  each is clip **`1HM_AttackRight`** (`Animations\1HM_AttackRight.hkx`). Its `playbackSpeed` is
  bound to `weaponSpeedMult` and its `startTime` to `attackIntroLength`.
- The other eight clips are the walk/run attack variants. The 1st-person clip is `1HM_1stPAttackRight`.

**Attack-state variables:**
- **`IsAttacking`** (BOOL) is written by `1HM_AttackBehavior.isActive`.
- **`IsAttackReady`** is written by `BSIsActiveModifier.bIsActive0` in `1HM_Ready_State_MG`.
- `i1HMState` is written by `1HM_Behavior.currentStateId`.
- Inside `AttackRight_State`:
  - `iRegularAttack` and `bLeftHandAttack` are written by `hkbEvaluateExpressionModifier`
    (`EvaluateiRegularAttackTrue`, `EvaluateLeftHandAttackFalse`).
  - `SpeedDamped` comes from `BSInterpValueModifier` (`target` = `Speed`).
- Inputs (engine-input class, DIRTY-SIDE): `attackIntroLength`, `weaponSpeedMult`,
  `iRightHandType`, `iLeftHandType`, `iIsPlayer`, `i1stPerson`, `iWantBlock`, `bWantCastLeft`,
  `bWantCastVoice`, `IsNPC`, `Direction`, plus the constants `blendAttackCombo` and `blendAttackPowerFast`.
- Remaining: `Speed`, `bVoiceReady`, `iBlockState`, `iIsInSneak`.
- No `bAllowRotation` writer on this path. Its 1hm writers are in Bash and in the staff/left-hand
  branch (`findvar.py`).

**Events, by role:**
- **Start**, engine-sent: `attackStart`. Combos chain on the same name: in `AttackRight_State`'s
  transitions, `attackStart` goes to `AttackLeft_State` with trigger interval
  `weaponSwing`→`AttackWinEnd` and initiate interval `AttackWinStart`→`AttackWinEnd` (`iv.py`).
- **Clip annotations on `1HM_AttackRight`:** `preHitFrame`, `weaponSwing`, `HitFrame`, `CastOKStart`,
  `AttackWinStart`, `AttackWinEnd`, `attackStop`.
  - The graph-side `hkbClipTriggerArray` (`sm.py`) and the DefaultMale block in
    `animationdatasinglefile.txt` (`ad.py`) list the same 7 names.
  - The `.hkx` has 99 annotation tracks, all empty (`grep -c 'annotations" numelements="0"'` = 99).
- **End**, `attackStop`, listened by `AttackState`'s transitions:
  - to `1HM_Ready_State` (condition `iWantBlock`, `i1stPerson`);
  - to `BlockState` (condition `iWantBlock`, `iLeftHandType`).
  - `attackStop` is also raised by `BSEventOnDeactivateModifier` and on `1HM_Ready_State` enter.
- **Notifies:** `PowerAttack_Start_end` and `HeadTrackingOff` on `AttackState` enter;
  `HeadTrackingOn` on exit; `CastOKStop` on `AttackRight_State` exit; `BeginCastVoice`.
- **Other exits from `AttackState`:** `PowerAttackStop`, `BeginCast`, `blockStart`, `shoutStart`,
  `NPCshoutStart`, and `AttackWinStart`/`AttackWinStartLeft` (to block when `IsNPC`).
- **Chains out of `AttackRight_State`:** `attackStartLeftHand`, `AttackStartH2HRight`,
  `AttackStartH2HLeft`, and `attackPowerStart{InPlace,Backward,Left,Right,Forward,ForwardH2HRightHand,H2HCombo}`.
- **Entries to sibling attack states** (in the 44, can be dropped):
  - `attackStartSprint(LeftHand)`, `attackStartDualWield`, `attackPowerStartDualWield`;
  - `attackPowerStart*LeftHand` (6), `attackPowerStartForwardH2HLeftHand`;
  - `streamingQuery_attackStartLeft`, `selfTransEvent`.
- Plus `CyclicCrossBlend` and `CyclicFreeze`.

**Minimal light-attack event set (17):** `attackStart`, `streamingQuery_attackStart`, the 7 clip
annotations, `PowerAttack_Start_end`, `HeadTrackingOff`, `HeadTrackingOn`, `CastOKStop`,
`CyclicCrossBlend`, `CyclicFreeze`, `PowerAttackStop`, `blockStart`. These are hand-picked from the
44 above.

## 5. Size of the slice (`final.py` last line; totals from REPORT.md and contract.md §1/§2)

| set | variables | events |
|---|---|---|
| locomotion (unarmed + weapon-drawn + sprint + speed sampler) | 42 | 49 (37 without dialogue/sneak/dodge) |
| one-handed right light attack (+ ready-state modifiers) | 23 | 44 (17 minimal) |
| **union, locomotion + attack** | **53** (7.6 % of 696; 17.6 % of the player's 301) | **88** (1.8 % of 4,773; 4.4 % of the player's 1,985) |
| union + jump | 57 | 99 |

## 6. ORACLE.md §11 names, checked

| name | status |
|---|---|
| `Speed` | exists, REAL. In the player graph it is read only by `BSSpeedSamplerModifier.goalSpeed` (0_master) and `BSInterpValueModifier.target` plus expressions (1hm). The blend spaces read **`SpeedSampled`** |
| `Direction` | exists, REAL; the `fBlendParameter` of every cyclic blend in the slice |
| `TurnDelta` | exists, REAL; see §2 |
| `weaponSwing` | exists as an **event**: a clip trigger on `1HM_AttackRight`, also the enter event of the combo trigger interval. Papyrus spells it `WeaponSwing` (contract.md §2.1) |

## 7. Not verified

- **Not verified:** the player's runtime values that select the branches: `iIsPlayer`=1 (`Player_TEST`
  rather than `_NPC`; both reach the same 3rd-person generator), `i1stPerson`=0, `iRightHandType`=1
  for a sword, `iLeftHandType`=0. These come from names and indices, not from a run. The oracle's
  `in.var` decides.
- **Not verified:** that the engine writes `Speed`, `iState`, `iSyncTurnState`, `Direction` and `TurnDelta`
  for the player. The only evidence is that no player-file node writes them, plus the DIRTY-SIDE
  pooled class.
- **Not verified:** engine-sent vs annotation-raised for `moveStart`/`moveStop` and `attackStop` (pooled
  "both"). The slice's own nodes never raise `moveStart`/`moveStop`.
- **Not verified:** the direction of the 1st-person graphs (`_1stperson/*`, 17 files). They were not cut.
  The engine probably runs both graphs and syncs them through `iSync*`, but that is not measured.
- Not measured: `RootModifierList`'s other 17 variables (look-at, foot IK, `camerafrom*`,
  `TargetLocation`, `LookAtOutOfRange`). They are always active and may matter to a trace, but
  were left out of the counts.
- Not measured: which side-file trigger rows outside the slice's clip generators the engine uses
  for the player. The 3 `1HM_AttackRight` blocks in `animationdatasinglefile.txt` belong to 3
  projects; only DefaultMale's was read.
- Closure-by-reference over-includes shared nodes. That is how dialogue/sneak/dodge names entered
  locomotion, and why the A1 cut from `AttackRight_1HMSword` (not used) leaked into readied locomotion.
