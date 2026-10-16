# SCOPE — how big is a behavior-graph interpreter for vanilla Skyrim SE?

006 M35. Every number here is from `census/CENSUS.md` or a `semantics/*.md` note, measured on
build 1.7.104's own files. Estimates are judgment and are marked as such.

## Verdict

**The interpreter is a months project. Making it behave like Skyrim is a years project.**

The node vocabulary is small and regular. What makes it big is everything around the graph that
the data doesn't specify. We could write an interpreter that loads and steps all 428 graphs in
roughly **3–5 engineer-months** (estimate). Vanilla behavior also needs the actor controller that
feeds it, the action/idle system that drives it, the ragdoll and foot IK after it, and an engine
that reacts to its ~740 notification events. That is **roughly 1.5–3 engineer-years** to vanilla
parity (estimate), and most of it is engine-contract work, not graph work. An oracle (`ORACLE.md`)
is what turns that contract work from guessing into measuring, and it is the biggest lever on
the estimate.

## Why the graph itself is tractable (measured)

- **Small vocabulary.** 428 behavior graphs, 33,630 node instances, **47 node classes**. 9 classes
  cover 90% of instances and 25 cover 99% (`CENSUS.md` §5). Behavior files use 66 classes in all.
- **Regular data.** Every one of 9,783 transitions is event-driven. `startStateChooser` is never
  used. `syncVariableIndex` is set if and only if the mode is SYNC. There are no
  `hkbGeneratorTransitionEffect`s and no additive blending in `hkbBlenderGenerator`
  (`graph-core.md`, `generators.md`, re-measured on vanilla).
- **Shallow, mostly.** Median graph is 11 nodes, and 294 of 428 have state-machine depth ≤ 1.
  The humanoid graphs carry the weight: `actors/character` has 47% of all nodes, with nesting
  depth 14 in one file and 21 across behavior references.
- **The toolchain exists and is native.** BSA extraction, HKX→XML (byte-exact round trip for all
  7,699 files) and a typed loader (all 428 graphs in ~0.65 s) work tonight on Apple Silicon.
- **Most modifiers are pure graph logic.** 2,406 of 2,974 modifier instances need only variables,
  events and `dt` (`modifiers.md`).

## Where the work actually is

| area | why it is big | est. share |
|---|---|---|
| **Engine contract: inputs** | ~107 engine-written variables (locomotion 28, weapons/combat 26, …). Nothing in the data gives `Speed`/`Direction`/`TurnDelta` units, smoothing or encoding (`contract.md` §5 #1) | high |
| **Action and idle system** | 4,370 IDLE records, 1,273 distinct behavior events, 4,354 conditions over **111 condition functions**, 71 actions. Walk order and fallbacks are not in the data (#2). It needs a large slice of the game's condition system, which is a whole subsystem of its own | high |
| **Engine reactions to graph events** | 742 graph-only notification events, plus 61 graph-written flags the engine polls (`bEquipOK`, `IsAttackReady`, `bAllowRotation`…); getting them wrong soft-locks combat and equip (#3, #4) | high |
| **Physics coupling** | Ragdoll modifiers sit in the root list of 37 of 57 top-level actor graphs. Ragdolls are trees of 3–48 capsule/box bodies with only two constraint types (ragdoll cone 53%, limited hinge 47%). Jolt covers it, except that Havok's asymmetric cone-plus-planes swing limit has to be approximated (`skeleton-physics.md`). There's also a post-graph stage, ragdoll driver → foot IK, in an order that is not verified | medium-high |
| **Animation decoding** | All 6,126 clips are `hkaSplineCompressedAnimation`. The decoder looks like days, not weeks, but the only open decoders are GPL-3.0, so ours must be written from a spec | low-medium |
| **Root motion** | Lives in `animationdatasinglefile.txt` (6,725 clips with motion, 2,614 translating), not in the `.hkx`, apart from 13 dragon flight clips. When it overrides the controller is unknown (#5) | medium |
| **Paired animations / killmoves** | 537 `BSSynchronizedClipGenerator`; partner alignment, `2_` annotation routing, `pa_` event pairing is a hypothesis (#6) | medium (deferrable) |
| **Non-actor graphs** | 603 `BGSGamebryoSequenceGenerator` drive NIF controller sequences (doors, traps, dwemer machines), so a NIF animation system is required; their events are mostly sent by Papyrus | medium |

## The hardest classes

1. **`hkbStateMachine` + `hkbStateMachineStateInfo` + transitions** (3,643 + 10,619 + 9,783):
   nested machines, global and local wildcards, transition intervals, blending transition effects
   and enter/exit notify events. Event propagation order and wildcard resolution are inferred, not
   known (`graph-core.md` open questions). The behaviour is simple to state and subtle to match.
2. **`hkbClipGenerator`** (10,086): modes, negative playback speed (80 clips), crop/enforced
   duration, triggers vs annotations, annotation-to-event splitting, sync.
3. **`hkbBlenderGenerator`** (2,009): 1,493 are parametric and 1,358 sync cycles. The exact blend
   and sync maths is medium-low confidence.
4. **`BSSynchronizedClipGenerator`** (537): couples two actors' graphs.
5. **Ragdoll modifiers**: `hkbPoweredRagdollControlsModifier` (93),
   `hkbRigidBodyRagdollControlsModifier` (55), `hkbKeyframeBonesModifier` (91), `hkbGetUpModifier`
   (46) and `BSRagdollContactListenerModifier` (50). They only write control data; the physics
   happens after the graph.
6. **`hkbFootIkControlsModifier`** (25, through the foot-IK driver): raycasts against level collision.
7. **`BGSGamebryoSequenceGenerator`** (603): it bridges into Gamebryo/NIF animation.
8. **`BSCyclicBlendTransitionGenerator`, `BSiStateTaggingGenerator`, `BSOffsetAnimationGenerator`**:
   Bethesda's own classes, inferred from field names only (low confidence).

## Biggest unknowns in the engine contract (from `contract.md` §5)

1. How the per-frame actor controller computes `Speed`, `Direction`, `TurnDelta`, `Pitch`,
   `TimeDelta` and `iSync*`. Every locomotion blend keys on these. **Very high risk.**
2. The action system: when each of the 71 actions fires, the idle-tree walk, condition evaluation,
   and what happens when a graph refuses an event. **Very high.**
3. What each graph-written flag gates in gameplay. **High.**
4. Side effects of notification events: hit frames, weapon draw, spell fire, sound, camera shake. **High.**
5. When root motion replaces the controller. **High.**
6. The ragdoll and get-up hand-off, and stagger inputs. **High.**
7. What is left hard-coded once ESM records and Papyrus are accounted for: 1,677 of 1,884
   engine-sent events (89%) are named by data (IDLE/RACE records, Papyrus call sites, script
   properties). About 122 actor-graph events, ~98 engine inputs and 38 of the 61 output flags are
   named by nothing and must come from the engine (`contract.md` §3, §5; partly upper bounds).

## What would move this estimate

- **Down:** a working oracle early. Nearly every unknown above is answered by a trace
  (`ORACLE.md`, 7–12 engineer-weeks estimated, ~3 weeks for a first slice), and it needs a Windows
  machine with the game. Also, a first playable target narrower than parity, e.g. humanoid
  locomotion + melee + death, with ragdolls keyframed to the animation pose and foot IK off; both
  stubs are invisible until hits and slopes.
- **Up:** clean-room discipline. Every DIRTY-SIDE fact has to be re-derived into a spec and
  reviewed before clean code uses it, which adds process to every item above. Mods: Nemesis and
  Pandora patch these graphs, and supporting patched graphs widens the input space (out of scope
  for "vanilla").

## Not measured tonight

Creation Club and `_ResourcePack.bsa` behaviors (not downloaded). Behavior differences between
1.6.x and 1.7.104. Whether the post-graph driver order is as inferred. Engine timings of any kind:
nothing ran on Windows.
