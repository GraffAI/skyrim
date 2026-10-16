# Skyrim SE behavior census

Aggregate statistics over the Havok behavior data in `Skyrim - Animations.bsa` (SE, `hk_2010.2.0-r1`), produced from hkxc XML (`tools/hkx/bulk_convert.sh`). Identifier strings (class, variable, event, annotation names) are listed because they are the engine<->graph contract; no other game content is reproduced. Full data: [census.json](census.json).

**Every number in this file** comes from one run of:

```sh
python3 -I projects/skyrim/tools/census/census.py && python3 -I projects/skyrim/tools/census/render_md.py
```

reading `~/skyrim-data-extracted/xml/` (every non-`animations/` .hkx, converted), `~/skyrim-data-extracted/xml-anim/` (every `animations/` .hkx, converted; `~/skyrim-data-extracted/xml-anim-sample/`, a 200-file sample, is the fallback) and `~/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt`. The JSON key each table comes from is named under it. Cross-checks run by hand are given with their command.

## 0. Inputs

| category (by root class) | files |
|---|---|
| project | 457 |
| behavior | 428 |
| character | 353 |
| skeleton | 328 |
| animation | 191 |
| other | 6 |

Category rule: a root `namedVariant` of `hkbBehaviorGraph` → behavior, `hkbCharacterData` → character, `hkbProjectData` → project; otherwise any `hkaSkeleton` → skeleton, any `hka*Animation` → animation (these are animations stored outside `animations/` dirs, e.g. `sharedkillmoves`), else other (empty animation containers). Parse failures: **0**. Key: `files_by_category`.

Cross-check: `grep -c . ~/skyrim-data-extracted/xml/_manifest.tsv` → 1763 converted, `cut -f1 _manifest.tsv | sort | uniq -c` → 1763 ok, `_errors.log` empty; `cut -f3 _manifest.tsv | grep -c '^hkbBehaviorGraph$'` → 428. (The brief's "654 under behaviors paths" counts animations/doors etc. under `animbehaviors/`; `find raw -iname '*.hkx' | grep -i behaviors | grep -vi /animations/ | wc -l` → 652, which includes characters/projects under `*behaviors` dirs such as `magic/magicbehaviors`.)

**Node definition** (used everywhere below): node = object whose class role is generator (class ends in 'Generator', or hkbStateMachine), modifier (ends in 'Modifier', or hkbModifierList), or state (hkbStateMachineStateInfo). hkbBehaviorGraph, transition effects, child wrappers, conditions, arrays and graph data are not nodes.

## Headline

- **428 behavior graphs**, **33,630 node instances** of **47 node classes**; 66 classes of any kind appear in behavior files (68,041 objects).
- Long tail: **2** node classes cover 50% of node instances, **9** cover 90%, **25** cover 99%, **47** cover 100%.
- Graph size: median 11 nodes, max 2711; 294 graphs have SM depth ≤ 1 (one flat state machine or none).
- Contract surface: **696** distinct variable names, **4773** distinct event names, **75** graph character-property names, **99** character-file property names.
- Clip triggers in `animationdatasinglefile.txt`: **36,584** on 9,127/10,597 clips, **721** distinct strings; .hkx annotations (full set): **7,645** on 1,857/5,935 animations, **512** distinct; 10,354 of the text file's 10,597 clips are reproduced from graph clip triggers + resolved .hkx annotations (§4b).
- Behavior references: **95** edges between graphs, 0 unresolved.

## 1. Classes

Instances = top-level `hkobject`s with that `class`; files = files containing ≥1. Role is the node rule above. Key: `classes.<category>`.

### behavior files (428)

| class | role | instances | files |
|---|---|---|---|
| `hkbStateMachineStateInfo` | state | 10619 | 422 |
| `hkbClipGenerator` | generator | 10086 | 300 |
| `hkbBlenderGeneratorChild` | data | 6485 | 157 |
| `hkbVariableBindingSet` | data | 6482 | 142 |
| `hkbClipTriggerArray` | data | 6397 | 283 |
| `hkbStateMachineTransitionInfoArray` | data | 5482 | 397 |
| `hkbStateMachine` | generator | 3643 | 425 |
| `hkbStateMachineEventPropertyArray` | data | 2727 | 196 |
| `hkbBlendingTransitionEffect` | transition | 2031 | 395 |
| `hkbBlenderGenerator` | generator | 2009 | 146 |
| `hkbModifierGenerator` | generator | 1918 | 118 |
| `hkbBoneWeightArray` | data | 1328 | 91 |
| `hkbModifierList` | modifier | 710 | 82 |
| `BSIsActiveModifier` | modifier | 671 | 95 |
| `BGSGamebryoSequenceGenerator` | generator | 603 | 146 |
| `hkbManualSelectorGenerator` | generator | 582 | 78 |
| `BSSynchronizedClipGenerator` | generator | 537 | 30 |
| `hkbEvaluateExpressionModifier` | modifier | 468 | 66 |
| `hkbExpressionDataArray` | data | 468 | 66 |
| `hkRootLevelContainer` | data | 428 | 428 |
| `hkbBehaviorGraph` | graph | 428 | 428 |
| `hkbBehaviorGraphData` | data | 425 | 425 |
| `hkbBehaviorGraphStringData` | data | 425 | 425 |
| `hkbVariableValueSet` | data | 425 | 425 |
| `hkbExpressionCondition` | data | 320 | 63 |
| `hkbBoneIndexArray` | data | 289 | 55 |
| `BSiStateTaggingGenerator` | generator | 170 | 25 |
| `hkbEventDrivenModifier` | modifier | 158 | 67 |
| `BSCyclicBlendTransitionGenerator` | generator | 153 | 45 |
| `BSBoneSwitchGenerator` | generator | 137 | 13 |
| `BSBoneSwitchGeneratorBoneData` | data | 137 | 13 |
| `BSLookAtModifier` | modifier | 128 | 36 |
| `hkbStringEventPayload` | data | 126 | 26 |
| `BSEventOnDeactivateModifier` | modifier | 98 | 19 |
| `hkbBehaviorReferenceGenerator` | generator | 97 | 42 |
| `hkbPoseMatchingGenerator` | generator | 96 | 47 |
| `hkbPoweredRagdollControlsModifier` | modifier | 93 | 47 |
| `hkbKeyframeBonesModifier` | modifier | 91 | 50 |
| `BSEventEveryNEventsModifier` | modifier | 85 | 20 |
| `hkbTimerModifier` | modifier | 59 | 54 |
| `hkbRigidBodyRagdollControlsModifier` | modifier | 55 | 50 |
| `BSRagdollContactListenerModifier` | modifier | 50 | 42 |
| `hkbGetUpModifier` | modifier | 46 | 46 |
| `hkbDampingModifier` | modifier | 43 | 38 |
| `BSSpeedSamplerModifier` | modifier | 42 | 42 |
| `BSInterpValueModifier` | modifier | 36 | 10 |
| `BSModifyOnceModifier` | modifier | 26 | 20 |
| `hkbFootIkControlsModifier` | modifier | 25 | 25 |
| `BSDirectAtModifier` | modifier | 23 | 13 |
| `BSEventOnFalseToTrueModifier` | modifier | 23 | 14 |
| `hkbTwistModifier` | modifier | 19 | 12 |
| `hkbRotateCharacterModifier` | modifier | 6 | 6 |
| `BSTweenerModifier` | modifier | 5 | 1 |
| `hkbStringCondition` | data | 5 | 4 |
| `hkbReferencePoseGenerator` | generator | 4 | 4 |
| `BSIStateManagerModifier` | modifier | 3 | 3 |
| `hkbEventRangeDataArray` | data | 3 | 2 |
| `hkbEventsFromRangeModifier` | modifier | 3 | 2 |
| `BSOffsetAnimationGenerator` | generator | 2 | 2 |
| `hkbFootIkModifier` | modifier | 2 | 1 |
| `BSDecomposeVectorModifier` | modifier | 1 | 1 |
| `BSGetTimeStepModifier` | modifier | 1 | 1 |
| `BSLimbIKModifier` | modifier | 1 | 1 |
| `BSPassByTargetTriggerModifier` | modifier | 1 | 1 |
| `BSTimerModifier` | modifier | 1 | 1 |
| `hkbTransformVectorModifier` | modifier | 1 | 1 |

### character files (353)

| class | role | instances | files |
|---|---|---|---|
| `hkRootLevelContainer` | data | 353 | 353 |
| `hkbCharacterData` | data | 353 | 353 |
| `hkbCharacterStringData` | data | 353 | 353 |
| `hkbMirroredSkeletonInfo` | data | 353 | 353 |
| `hkbVariableValueSet` | data | 353 | 353 |
| `hkbBoneWeightArray` | data | 143 | 23 |
| `hkbFootIkDriverInfo` | data | 16 | 16 |

### project files (457)

| class | role | instances | files |
|---|---|---|---|
| `hkRootLevelContainer` | data | 457 | 457 |
| `hkbProjectData` | data | 457 | 457 |
| `hkbProjectStringData` | data | 457 | 457 |

### skeleton files (328)

| class | role | instances | files |
|---|---|---|---|
| `hkMemoryResourceContainer` | data | 3691 | 327 |
| `hkMemoryResourceHandle` | data | 2016 | 47 |
| `hkpConstraintInstance` | data | 1922 | 48 |
| `hkpRigidBody` | data | 1040 | 48 |
| `hkpRagdollConstraintData` | data | 1024 | 48 |
| `hkpShapeInfo` | data | 1008 | 47 |
| `hkpCapsuleShape` | data | 941 | 47 |
| `hkpLimitedHingeConstraintData` | data | 898 | 42 |
| `hkaSkeleton` | data | 376 | 328 |
| `hkRootLevelContainer` | data | 328 | 328 |
| `hkaAnimationContainer` | data | 328 | 328 |
| `hkpConvexTranslateShape` | data | 108 | 8 |
| `hkpBoxShape` | data | 106 | 6 |
| `hkaSkeletonMapper` | data | 96 | 48 |
| `hkaRagdollInstance` | data | 48 | 48 |
| `hkpPhysicsData` | data | 48 | 48 |
| `hkpPhysicsSystem` | data | 48 | 48 |
| `hkpPositionConstraintMotor` | data | 48 | 48 |
| `hkpConvexTransformShape` | data | 7 | 2 |
| `hkpConvexVerticesConnectivity` | data | 7 | 4 |
| `hkpConvexVerticesShape` | data | 7 | 4 |
| `hkpListShape` | data | 3 | 3 |
| `hkpMoppBvTreeShape` | data | 2 | 2 |
| `hkpMoppCode` | data | 2 | 2 |

### animation files (191)

| class | role | instances | files |
|---|---|---|---|
| `hkMemoryResourceContainer` | data | 191 | 191 |
| `hkRootLevelContainer` | data | 191 | 191 |
| `hkaAnimationBinding` | data | 191 | 191 |
| `hkaAnimationContainer` | data | 191 | 191 |
| `hkaSplineCompressedAnimation` | data | 191 | 191 |

### other files (6)

| class | role | instances | files |
|---|---|---|---|
| `hkMemoryResourceContainer` | data | 6 | 6 |
| `hkRootLevelContainer` | data | 6 | 6 |
| `hkaAnimationContainer` | data | 6 | 6 |

Cross-check: `grep -rho 'class="hkbClipGenerator"' ~/skyrim-data-extracted/xml/meshes | wc -l` → 10086, matching `hkbClipGenerator` above (it appears only in behavior files).

## 2. Per-graph summaries

Per graph: nodes (generators + modifiers + states, all instances in the file; every one is reachable from `rootGenerator` in all graphs — 0 graphs differ), `max_sm_depth` = most `hkbStateMachine`s on one reference path from `rootGenerator` within the file (following every `#NNNN` reference, so through `hkbStateMachineStateInfo.generator`, blender children, modifier generators, etc.), `xdepth` = the same but continuing through `hkbBehaviorReferenceGenerator` into the referenced graph; vars / events / char props from `hkbBehaviorGraphStringData`. Full list (all graphs): key `graphs`.

| metric | min | median | p90 | p99 | max | sum |
|---|---|---|---|---|---|---|
| nodes | 0 | 11 | 220 | 975 | 2711 | 33630 |
| generators | 0 | 6 | 114 | 684 | 1621 | 20037 |
| modifiers | 0 | 0 | 27 | 79 | 181 | 2974 |
| states | 0 | 4 | 58 | 336 | 1198 | 10619 |
| state_machines | 0 | 1 | 21 | 98 | 507 | 3643 |
| max_sm_depth | 0 | 1 | 6 | 10 | 14 | 913 |
| max_sm_depth_through_references | 0 | 1 | 7 | 12 | 21 | 1045 |
| clip_generators | 0 | 4 | 59 | 345 | 934 | 10086 |
| variables | 0 | 0 | 63 | 118 | 230 | 5862 |
| events | 0 | 9 | 120 | 482 | 1217 | 19358 |
| character_properties | 0 | 0 | 0 | 25 | 25 | 419 |

SM depth histogram (within file / through references):

| depth | graphs (within) | graphs (through refs) |
|---|---|---|
| 0 | 3 | 3 |
| 1 | 291 | 278 |
| 2 | 55 | 55 |
| 3 | 11 | 9 |
| 4 | 6 | 6 |
| 5 | 5 | 3 |
| 6 | 18 | 20 |
| 7 | 21 | 21 |
| 8 | 5 | 14 |
| 9 | 8 | 13 |
| 10 | 1 | 1 |
| 12 | 1 | 1 |
| 13 | 1 | 0 |
| 14 | 2 | 0 |
| 16 | 0 | 2 |
| 20 | 0 | 1 |
| 21 | 0 | 1 |

### Largest 60 graphs by node count

| graph | nodes | gen | mod | states | SMs | depth | xdepth | clips | vars | events | char props | refs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `meshes/actors/character/behaviors/mt_behavior.hkx` | 2711 | 1426 | 87 | 1198 | 281 | 10 | 12 | 934 | 67 | 931 | 2 | 3 |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | 2608 | 1621 | 56 | 931 | 507 | 14 | 16 | 525 | 101 | 461 | 9 | 8 |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | 2423 | 1497 | 56 | 870 | 490 | 14 | 16 | 452 | 101 | 461 | 9 | 8 |
| `meshes/actors/character/behaviors/0_master.hkx` | 1123 | 703 | 84 | 336 | 112 | 13 | 21 | 289 | 230 | 1217 | 15 | 12 |
| `meshes/actors/draugr/behaviors/draugrbehavior.hkx` | 975 | 684 | 59 | 232 | 79 | 8 | 8 | 414 | 77 | 277 | 0 | 0 |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | 870 | 553 | 51 | 266 | 98 | 12 | 20 | 223 | 230 | 1217 | 15 | 10 |
| `meshes/actors/character/behaviors/idlebehavior.hkx` | 866 | 407 | 10 | 449 | 37 | 5 | 5 | 345 | 7 | 44 | 0 | 0 |
| `meshes/actors/dragon/behaviors/dragonbehavior.hkx` | 830 | 431 | 181 | 218 | 66 | 9 | 9 | 214 | 153 | 482 | 0 | 0 |
| `meshes/actors/falmer/behaviors/falmerbehavior.hkx` | 616 | 377 | 48 | 191 | 67 | 9 | 9 | 190 | 74 | 155 | 2 | 0 |
| `meshes/actors/character/behaviors/magicbehavior.hkx` | 562 | 406 | 22 | 134 | 48 | 9 | 9 | 213 | 81 | 97 | 7 | 2 |
| `meshes/actors/werewolfbeast/behaviors/werewolfbehavior.hkx` | 548 | 362 | 39 | 147 | 67 | 8 | 8 | 200 | 68 | 241 | 1 | 0 |
| `meshes/actors/vampirelord/behaviors/vampirelord.hkx` | 466 | 283 | 58 | 125 | 44 | 9 | 9 | 116 | 74 | 200 | 3 | 0 |
| `meshes/actors/character/_1stperson/behaviors/magicbehavior.hkx` | 453 | 306 | 22 | 125 | 47 | 9 | 9 | 152 | 81 | 97 | 7 | 2 |
| `meshes/actors/giant/behaviors/giantbehavior.hkx` | 379 | 244 | 37 | 98 | 42 | 9 | 9 | 124 | 61 | 120 | 0 | 0 |
| `meshes/actors/character/_1stperson/behaviors/mt_behavior.hkx` | 378 | 234 | 21 | 123 | 39 | 8 | 10 | 135 | 67 | 931 | 2 | 3 |
| `meshes/actors/character/behaviors/blockbehavior.hkx` | 378 | 297 | 22 | 59 | 26 | 6 | 6 | 187 | 33 | 39 | 3 | 2 |
| `meshes/actors/dragonpriest/behaviors/dragon_priest.hkx` | 377 | 226 | 42 | 109 | 36 | 7 | 7 | 117 | 70 | 107 | 2 | 0 |
| `meshes/actors/dwarvenspherecenturion/behaviors/scbehavior.hkx` | 359 | 237 | 41 | 81 | 36 | 8 | 8 | 132 | 37 | 113 | 0 | 0 |
| `meshes/actors/dlc02/riekling/behaviors/rieklingbehavior.hkx` | 355 | 219 | 46 | 90 | 30 | 7 | 7 | 127 | 60 | 111 | 1 | 0 |
| `meshes/actors/canine/behaviors wolf/quadrupedbehavior.hkx` | 354 | 164 | 79 | 111 | 33 | 7 | 7 | 76 | 89 | 336 | 25 | 2 |
| `meshes/actors/character/behaviors/horsebehavior.hkx` | 346 | 213 | 38 | 95 | 35 | 9 | 9 | 106 | 118 | 212 | 2 | 0 |
| `meshes/actors/character/_1stperson/behaviors/horsebehavior.hkx` | 341 | 210 | 38 | 93 | 34 | 9 | 9 | 105 | 118 | 212 | 2 | 0 |
| `meshes/actors/troll/behaviors/trollbehavior.hkx` | 335 | 204 | 41 | 90 | 24 | 6 | 6 | 116 | 48 | 171 | 2 | 0 |
| `meshes/actors/dlc02/benthiclurker/behaviors/benthiclurkerbehavior.hkx` | 330 | 216 | 36 | 78 | 36 | 7 | 7 | 111 | 63 | 150 | 0 | 0 |
| `meshes/actors/canine/behaviors/quadrupedbehavior.hkx` | 328 | 148 | 76 | 104 | 32 | 7 | 8 | 70 | 89 | 336 | 25 | 2 |
| `meshes/actors/character/_1stperson/behaviors/blockbehavior.hkx` | 324 | 256 | 22 | 46 | 22 | 6 | 6 | 162 | 33 | 39 | 3 | 2 |
| `meshes/actors/dlc02/boarriekling/behaviors/quadrupedbehavior.hkx` | 321 | 141 | 79 | 101 | 33 | 6 | 6 | 66 | 89 | 336 | 25 | 2 |
| `meshes/actors/character/behaviors/1hm_locomotion.hkx` | 293 | 275 | 1 | 17 | 3 | 3 | 4 | 196 | 17 | 16 | 0 | 1 |
| `meshes/actors/sabrecat/behaviors/quadrupedbehavior.hkx` | 284 | 124 | 70 | 90 | 29 | 7 | 7 | 54 | 89 | 309 | 25 | 2 |
| `meshes/auxbones/tail/behaviors/tailbehavior.hkx` | 281 | 191 | 2 | 88 | 7 | 3 | 3 | 154 | 17 | 89 | 0 | 0 |
| `meshes/actors/character/_1stperson/behaviors/magicmountedbehavior.hkx` | 280 | 164 | 17 | 99 | 32 | 6 | 6 | 77 | 79 | 95 | 4 | 1 |
| `meshes/actors/character/behaviors/magicmountedbehavior.hkx` | 280 | 164 | 17 | 99 | 32 | 6 | 6 | 77 | 79 | 95 | 4 | 1 |
| `meshes/actors/dlc02/scrib/behaviors/scribbehavior.hkx` | 266 | 137 | 55 | 74 | 25 | 6 | 6 | 71 | 88 | 146 | 11 | 0 |
| `meshes/actors/spriggan/behaviors/sprigganbehavior.hkx` | 266 | 166 | 35 | 65 | 21 | 6 | 6 | 92 | 44 | 110 | 0 | 0 |
| `meshes/actors/hagraven/behaviors/havgravenbehavior.hkx` | 265 | 166 | 38 | 61 | 21 | 6 | 6 | 96 | 155 | 93 | 1 | 0 |
| `meshes/actors/dwarvensteamcenturion/behaviors/steambehavior.hkx` | 260 | 154 | 38 | 68 | 24 | 6 | 6 | 80 | 41 | 130 | 0 | 0 |
| `meshes/actors/dlc02/boarriekling/behaviors/boarbehavior.hkx` | 255 | 137 | 56 | 62 | 22 | 6 | 6 | 68 | 88 | 137 | 9 | 0 |
| `meshes/actors/character/_1stperson/behaviors/1hm_locomotion.hkx` | 248 | 231 | 1 | 16 | 3 | 3 | 4 | 163 | 17 | 16 | 0 | 1 |
| `meshes/actors/horker/behaviors/quadrupedbehavior.hkx` | 238 | 101 | 63 | 74 | 28 | 7 | 7 | 49 | 89 | 309 | 25 | 2 |
| `meshes/actors/horse/behaviors/horsebehavior.hkx` | 233 | 129 | 38 | 66 | 20 | 8 | 8 | 65 | 76 | 141 | 1 | 0 |
| `meshes/actors/bear/behaviors/quadrupedbehavior.hkx` | 232 | 98 | 67 | 67 | 23 | 7 | 7 | 40 | 89 | 309 | 25 | 2 |
| `meshes/actors/chaurus/behaviors/chaurusbehavior.hkx` | 230 | 128 | 36 | 66 | 18 | 7 | 7 | 66 | 79 | 137 | 0 | 0 |
| `meshes/actors/dlc01/vampirebrute/behaviors/vampirebrutebehavior.hkx` | 220 | 129 | 32 | 59 | 24 | 7 | 7 | 69 | 60 | 120 | 0 | 0 |
| `meshes/actors/dlc02/hmdaedra/behaviors/hmdaedra.hkx` | 212 | 123 | 33 | 56 | 21 | 6 | 6 | 68 | 31 | 149 | 0 | 0 |
| `meshes/actors/mudcrab/behaviors/mudcrabbehavior.hkx` | 206 | 114 | 37 | 55 | 19 | 7 | 7 | 56 | 44 | 134 | 0 | 0 |
| `meshes/actors/skeever/behaviors/quadrupedbehavior.hkx` | 200 | 76 | 66 | 58 | 21 | 7 | 7 | 32 | 89 | 309 | 25 | 2 |
| `meshes/actors/cow/behaviors/quadrupedbehavior.hkx` | 194 | 75 | 61 | 58 | 21 | 7 | 8 | 30 | 89 | 309 | 25 | 2 |
| `meshes/actors/dlc02/dwarvenballistacenturion/behaviors/bcbehavior.hkx` | 190 | 108 | 36 | 46 | 19 | 6 | 6 | 55 | 38 | 158 | 2 | 0 |
| `meshes/actors/goat/behaviors/quadrupedbehavior.hkx` | 188 | 72 | 60 | 56 | 20 | 7 | 8 | 29 | 89 | 309 | 25 | 2 |
| `meshes/actors/atronachflame/behaviors/atronachflamebehavior.hkx` | 186 | 98 | 31 | 57 | 24 | 7 | 7 | 45 | 75 | 74 | 0 | 0 |
| `meshes/actors/deer/behaviors/quadrupedbehavior.hkx` | 186 | 73 | 56 | 57 | 21 | 7 | 7 | 29 | 89 | 309 | 25 | 2 |
| `meshes/actors/atronachfrost/behaviors/atronachfrostbehavior.hkx` | 177 | 107 | 21 | 49 | 18 | 7 | 7 | 59 | 48 | 60 | 0 | 0 |
| `meshes/actors/wisp/behaviors/wispbehavior.hkx` | 172 | 86 | 25 | 61 | 22 | 6 | 6 | 47 | 38 | 69 | 0 | 0 |
| `meshes/actors/frostbitespider/behaviors/frostbitespiderbehavior.hkx` | 171 | 94 | 25 | 52 | 14 | 6 | 6 | 53 | 36 | 141 | 0 | 0 |
| `meshes/actors/mammoth/behaviors/quadrupedbehavior.hkx` | 171 | 64 | 60 | 47 | 18 | 7 | 7 | 25 | 89 | 309 | 25 | 2 |
| `meshes/actors/dlc01/chaurusflyer/behaviors/chaurusflyerbehavior.hkx` | 162 | 87 | 24 | 51 | 13 | 5 | 5 | 51 | 24 | 88 | 0 | 0 |
| `meshes/actors/dwarvenspider/behaviors/dwarvenspiderbehavior.hkx` | 158 | 85 | 27 | 46 | 12 | 7 | 7 | 44 | 72 | 119 | 1 | 0 |
| `meshes/actors/character/_1stperson/behaviors/shout_behavior.hkx` | 148 | 106 | 5 | 37 | 14 | 5 | 6 | 56 | 37 | 41 | 0 | 1 |
| `meshes/actors/character/behaviors/shout_behavior.hkx` | 148 | 106 | 5 | 37 | 14 | 5 | 6 | 56 | 37 | 41 | 0 | 1 |
| `meshes/actors/atronachstorm/behaviors/atronachstormbehavior.hkx` | 142 | 79 | 19 | 44 | 16 | 7 | 7 | 38 | 32 | 59 | 0 | 0 |

### Behavior reference edges (95)

`hkbBehaviorReferenceGenerator.behaviorName`, resolved against the project dir (parent of the graph's directory). Key: `behavior_reference_edges`.

| from graph | behaviorName |
|---|---|
| `meshes/actors/bear/behaviors/bearbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/bear/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/bear/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/canine/behaviors wolf/quadrupedbehavior.hkx` | `Behaviors Wolf/ForwardLocomotion.hkx` |
| `meshes/actors/canine/behaviors wolf/quadrupedbehavior.hkx` | `Behaviors Wolf/NonCombatIdle.hkx` |
| `meshes/actors/canine/behaviors wolf/wolfbehavior.hkx` | `Behaviors Wolf/QuadrupedBehavior.hkx` |
| `meshes/actors/canine/behaviors/dogbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/canine/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/canine/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/canine/behaviors/wolfbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/1HM_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/BashBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/BlockBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/HorseBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/MT_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/MagicBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/StaggerBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/0_master.hkx` | `Behaviors/WeapEquip.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/BashBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/BlockBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/Bow_Direction_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/CrossBow_Direction_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/MagicBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/1hm_locomotion.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/blockbehavior.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/_1stperson/behaviors/blockbehavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/magicbehavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/magicbehavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/magicmountedbehavior.hkx` | `Behaviors/ShoutMounted_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/mt_behavior.hkx` | `Behaviors/IdleBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/mt_behavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/mt_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/shout_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/_1stperson/behaviors/weapequip.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/1HM_Behavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/BashBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/BlockBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/HorseBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/MT_Behavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/MagicBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/MagicMountedBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/ShoutMounted_Behavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/StaggerBehavior.hkx` |
| `meshes/actors/character/behaviors/0_master.hkx` | `Behaviors/WeapEquip.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/BashBehavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/BlockBehavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/Bow_Direction_Behavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/CrossBow_Direction_Behavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/MagicBehavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/behaviors/1hm_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/1hm_locomotion.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/blockbehavior.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/character/behaviors/blockbehavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/magicbehavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/behaviors/magicbehavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/magicmountedbehavior.hkx` | `Behaviors/ShoutMounted_Behavior.hkx` |
| `meshes/actors/character/behaviors/mt_behavior.hkx` | `Behaviors/IdleBehavior.hkx` |
| `meshes/actors/character/behaviors/mt_behavior.hkx` | `Behaviors/Shout_Behavior.hkx` |
| `meshes/actors/character/behaviors/mt_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/shout_behavior.hkx` | `Behaviors/SprintBehavior.hkx` |
| `meshes/actors/character/behaviors/weapequip.hkx` | `Behaviors/1HM_Locomotion.hkx` |
| `meshes/actors/cow/behaviors/h-cowbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/cow/behaviors/h-cowbehavior_lod.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/cow/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/cow/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/deer/behaviors/deerbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/deer/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/deer/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/dlc02/boarriekling/behaviors/bearbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/dlc02/boarriekling/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/dlc02/boarriekling/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/goat/behaviors/goatbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/goat/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/goat/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/horker/behaviors/horkerbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/horker/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/horker/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/mammoth/behaviors/mammothbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/mammoth/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/mammoth/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/sabrecat/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/sabrecat/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/sabrecat/behaviors/sabrecatbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |
| `meshes/actors/skeever/behaviors/quadrupedbehavior.hkx` | `Behaviors/ForwardLocomotion.hkx` |
| `meshes/actors/skeever/behaviors/quadrupedbehavior.hkx` | `Behaviors/NonCombatIdle.hkx` |
| `meshes/actors/skeever/behaviors/skeeverbehavior.hkx` | `Behaviors/QuadrupedBehavior.hkx` |

## 3. Contract surface: variables and events

**696** distinct variable names across 428 graphs; 5862 declarations. Declarations by type: VARIABLE_TYPE_REAL 2598, VARIABLE_TYPE_BOOL 1887, VARIABLE_TYPE_INT32 1281, VARIABLE_TYPE_VECTOR4 72, VARIABLE_TYPE_INT8 16, VARIABLE_TYPE_QUATERNION 8. Names declared with more than one type: **8**: `iGetUpType` (VARIABLE_TYPE_INT32×40, VARIABLE_TYPE_INT8×11), `IsBashing` (VARIABLE_TYPE_BOOL×45, VARIABLE_TYPE_INT32×6), `iRightHandType` (VARIABLE_TYPE_INT32×38, VARIABLE_TYPE_INT8×1), `iIsInSneak` (VARIABLE_TYPE_INT32×31, VARIABLE_TYPE_BOOL×2), `test` (VARIABLE_TYPE_REAL×25, VARIABLE_TYPE_INT32×2), `bAttached` (VARIABLE_TYPE_REAL×3, VARIABLE_TYPE_BOOL×2), `bPerkQuickDraw` (VARIABLE_TYPE_BOOL×4, VARIABLE_TYPE_INT8×1), `IsLoaded` (VARIABLE_TYPE_BOOL×1, VARIABLE_TYPE_INT32×1). Key: `variables`.

### Variables declared in the most graphs (top 150 of all; full list in JSON)

| variable | graphs | type(s) |
|---|---|---|
| `TurnDelta` | 90 | VARIABLE_TYPE_REAL |
| `Direction` | 87 | VARIABLE_TYPE_REAL |
| `blendDefault` | 86 | VARIABLE_TYPE_REAL |
| `bAnimationDriven` | 85 | VARIABLE_TYPE_BOOL |
| `iState` | 83 | VARIABLE_TYPE_INT32 |
| `bAllowRotation` | 79 | VARIABLE_TYPE_BOOL |
| `iSyncIdleLocomotion` | 79 | VARIABLE_TYPE_INT32 |
| `Speed` | 79 | VARIABLE_TYPE_REAL |
| `SpeedSampled` | 76 | VARIABLE_TYPE_REAL |
| `staggerMagnitude` | 76 | VARIABLE_TYPE_REAL |
| `IsAttackReady` | 75 | VARIABLE_TYPE_BOOL |
| `bEquipOK` | 73 | VARIABLE_TYPE_BOOL |
| `IsStaggering` | 73 | VARIABLE_TYPE_BOOL |
| `iSyncTurnState` | 70 | VARIABLE_TYPE_INT32 |
| `IsRecoiling` | 64 | VARIABLE_TYPE_BOOL |
| `TurnDeltaDamped` | 63 | VARIABLE_TYPE_REAL |
| `IsAttacking` | 61 | VARIABLE_TYPE_BOOL |
| `blendFast` | 60 | VARIABLE_TYPE_REAL |
| `TargetLocation` | 53 | VARIABLE_TYPE_VECTOR4 |
| `bIsSynced` | 52 | VARIABLE_TYPE_BOOL |
| `iGetUpType` | 51 | VARIABLE_TYPE_INT32, VARIABLE_TYPE_INT8 |
| `IsBashing` | 51 | VARIABLE_TYPE_BOOL, VARIABLE_TYPE_INT32 |
| `staggerDirection` | 50 | VARIABLE_TYPE_REAL |
| `camerafromx` | 49 | VARIABLE_TYPE_REAL |
| `camerafromy` | 49 | VARIABLE_TYPE_REAL |
| `camerafromz` | 49 | VARIABLE_TYPE_REAL |
| `bHeadTracking` | 48 | VARIABLE_TYPE_BOOL |
| `bCanHeadTrack` | 45 | VARIABLE_TYPE_BOOL |
| `blendSlow` | 45 | VARIABLE_TYPE_REAL |
| `iCombatStance` | 44 | VARIABLE_TYPE_INT32 |
| `FootIKEnable` | 42 | VARIABLE_TYPE_BOOL |
| `bHeadTrackingOn` | 41 | VARIABLE_TYPE_BOOL |
| `fMinSpeed` | 41 | VARIABLE_TYPE_REAL |
| `m_alignWorldFromModelGain` | 40 | VARIABLE_TYPE_REAL |
| `m_worldFromModelFeedbackGain` | 40 | VARIABLE_TYPE_REAL |
| `bDisableHeadTrack` | 39 | VARIABLE_TYPE_BOOL |
| `iRightHandType` | 39 | VARIABLE_TYPE_INT32, VARIABLE_TYPE_INT8 |
| `bNoHeadTrack` | 38 | VARIABLE_TYPE_BOOL |
| `iLeftHandType` | 38 | VARIABLE_TYPE_INT32 |
| `iSyncSprintState` | 38 | VARIABLE_TYPE_INT32 |
| `m_errorUpDownBias` | 38 | VARIABLE_TYPE_REAL |
| `m_footPlantedGain` | 38 | VARIABLE_TYPE_REAL |
| `m_footRaisedGain` | 38 | VARIABLE_TYPE_REAL |
| `m_footUnlockGain` | 38 | VARIABLE_TYPE_REAL |
| `m_groundAscendingGain` | 38 | VARIABLE_TYPE_REAL |
| `m_groundDescendingGain` | 38 | VARIABLE_TYPE_REAL |
| `m_hipOrientationGain` | 38 | VARIABLE_TYPE_REAL |
| `m_onOffGain` | 38 | VARIABLE_TYPE_REAL |
| `turnSpeedMult` | 38 | VARIABLE_TYPE_REAL |
| `fMinTurnDelta` | 37 | VARIABLE_TYPE_REAL |
| `IsBleedingOut` | 37 | VARIABLE_TYPE_BOOL |
| `m_footPlantedAnkleHeightMS` | 37 | VARIABLE_TYPE_REAL |
| `m_footRaisedAnkleHeightMS` | 37 | VARIABLE_TYPE_REAL |
| `m_maxAnkleHeightMS` | 37 | VARIABLE_TYPE_REAL |
| `m_minAnkleHeightMS` | 37 | VARIABLE_TYPE_REAL |
| `bForceIdleStop` | 36 | VARIABLE_TYPE_BOOL |
| `iCharacterSelector` | 35 | VARIABLE_TYPE_INT32 |
| `isIdleSitting` | 35 | VARIABLE_TYPE_BOOL |
| `iIsInSneak` | 33 | VARIABLE_TYPE_INT32, VARIABLE_TYPE_BOOL |
| `walkBackRate` | 31 | VARIABLE_TYPE_REAL |
| `bMirroredAttack` | 29 | VARIABLE_TYPE_BOOL |
| `IsSneaking` | 27 | VARIABLE_TYPE_BOOL |
| `iSyncForwardState` | 27 | VARIABLE_TYPE_INT32 |
| `iTurnMirrored` | 27 | VARIABLE_TYPE_INT32 |
| `test` | 27 | VARIABLE_TYPE_REAL, VARIABLE_TYPE_INT32 |
| `bIsWolf` | 26 | VARIABLE_TYPE_BOOL |
| `bMLh_Ready` | 26 | VARIABLE_TYPE_BOOL |
| `bSkeeverLunge` | 26 | VARIABLE_TYPE_BOOL |
| `bWantCastLeft` | 26 | VARIABLE_TYPE_BOOL |
| `iIsCanine` | 26 | VARIABLE_TYPE_INT32 |
| `iMovementSpeed` | 25 | VARIABLE_TYPE_INT32 |
| `i1stPerson` | 24 | VARIABLE_TYPE_INT32 |
| `isIdleLay` | 23 | VARIABLE_TYPE_BOOL |
| `SpeedDamped` | 23 | VARIABLE_TYPE_REAL |
| `IsPlayer` | 21 | VARIABLE_TYPE_BOOL |
| `TurnMin` | 21 | VARIABLE_TYPE_REAL |
| `IsFirstPerson` | 20 | VARIABLE_TYPE_BOOL |
| `IsNPC` | 20 | VARIABLE_TYPE_BOOL |
| `TimeDelta` | 20 | VARIABLE_TYPE_REAL |
| `blendMoveStop` | 19 | VARIABLE_TYPE_REAL |
| `IsBlocking` | 19 | VARIABLE_TYPE_BOOL |
| `IsSprinting` | 19 | VARIABLE_TYPE_BOOL |
| `fMinMoveSpeed` | 18 | VARIABLE_TYPE_REAL |
| `IntDirection` | 18 | VARIABLE_TYPE_INT32 |
| `IsSideAttacking` | 18 | VARIABLE_TYPE_BOOL |
| `bFootIKEnable` | 17 | VARIABLE_TYPE_BOOL |
| `bMotionDriven` | 17 | VARIABLE_TYPE_BOOL |
| `weaponSpeedMult` | 17 | VARIABLE_TYPE_REAL |
| `bWantCastVoice` | 16 | VARIABLE_TYPE_BOOL |
| `currentDefaultState` | 16 | VARIABLE_TYPE_INT32 |
| `fTwistDirection` | 16 | VARIABLE_TYPE_REAL |
| `iState_HorseSprint` | 16 | VARIABLE_TYPE_INT32 |
| `walkBackSpeedMult` | 16 | VARIABLE_TYPE_REAL |
| `blendMove1stP` | 15 | VARIABLE_TYPE_REAL |
| `blendMoveStart` | 15 | VARIABLE_TYPE_REAL |
| `isMoving` | 15 | VARIABLE_TYPE_BOOL |
| `IsShouting` | 15 | VARIABLE_TYPE_BOOL |
| `Pitch` | 15 | VARIABLE_TYPE_REAL |
| `bMRh_Ready` | 14 | VARIABLE_TYPE_BOOL |
| `bVoiceReady` | 14 | VARIABLE_TYPE_BOOL |
| `bWantCastRight` | 14 | VARIABLE_TYPE_BOOL |
| `iState_HorseDefault` | 14 | VARIABLE_TYPE_INT32 |
| `iState_NPCSneaking` | 14 | VARIABLE_TYPE_INT32 |
| `iSyncDefaultState` | 14 | VARIABLE_TYPE_INT32 |
| `DirectionDamped` | 13 | VARIABLE_TYPE_REAL |
| `iState_BearDefault` | 13 | VARIABLE_TYPE_INT32 |
| `iState_BearSwimDefault` | 13 | VARIABLE_TYPE_INT32 |
| `iState_CowDefault` | 13 | VARIABLE_TYPE_INT32 |
| `iState_DeerDefault` | 13 | VARIABLE_TYPE_INT32 |
| `iState_DeerDefaultRun` | 13 | VARIABLE_TYPE_INT32 |
| `iState_WolfDefault` | 13 | VARIABLE_TYPE_INT32 |
| `AimHeadingCurrent` | 12 | VARIABLE_TYPE_REAL |
| `AimPitchCurrent` | 12 | VARIABLE_TYPE_REAL |
| `bAimActive` | 12 | VARIABLE_TYPE_BOOL |
| `bHeadTrackSpine` | 12 | VARIABLE_TYPE_BOOL |
| `iRightHandEquipped` | 12 | VARIABLE_TYPE_INT32 |
| `iState_DogDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_GoatDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_HorkerDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_HorkerSwimDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_MammothDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_NPCDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_SabreCatDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_SkeeverDefault` | 12 | VARIABLE_TYPE_INT32 |
| `iState_SkeeverLunge` | 12 | VARIABLE_TYPE_INT32 |
| `AimGainOff` | 11 | VARIABLE_TYPE_REAL |
| `bowZoom` | 11 | VARIABLE_TYPE_REAL |
| `iLeftHandEquipped` | 11 | VARIABLE_TYPE_INT32 |
| `IsCastingLeft` | 11 | VARIABLE_TYPE_BOOL |
| `isSwimming` | 11 | VARIABLE_TYPE_BOOL |
| `iState_CowSwimDefault` | 11 | VARIABLE_TYPE_INT32 |
| `iWantBlock` | 11 | VARIABLE_TYPE_INT32 |
| `OldDirection` | 11 | VARIABLE_TYPE_REAL |
| `SlowBlend` | 11 | VARIABLE_TYPE_REAL |
| `AimHeadingMax` | 10 | VARIABLE_TYPE_REAL |
| `AimPitchMax` | 10 | VARIABLE_TYPE_REAL |
| `bLeftHand` | 10 | VARIABLE_TYPE_BOOL |
| `bowZoomAmt` | 10 | VARIABLE_TYPE_REAL |
| `bPerkQuickShot` | 10 | VARIABLE_TYPE_INT32 |
| `bRightHand` | 10 | VARIABLE_TYPE_BOOL |
| `bSprintOK` | 10 | VARIABLE_TYPE_BOOL |
| `RotMax` | 10 | VARIABLE_TYPE_REAL |
| `AimGainOn` | 9 | VARIABLE_TYPE_REAL |
| `bDisableInterp` | 9 | VARIABLE_TYPE_BOOL |
| `BowAimOffsetHeading` | 9 | VARIABLE_TYPE_REAL |
| `BowAimOffsetPitch` | 9 | VARIABLE_TYPE_REAL |
| `CastBlend` | 9 | VARIABLE_TYPE_REAL |
| `CastBlendDamped` | 9 | VARIABLE_TYPE_REAL |
| `InDualMagicState` | 9 | VARIABLE_TYPE_REAL |
| `IsCasting` | 9 | VARIABLE_TYPE_BOOL |

153 variable names are declared in exactly one graph.

### Events declared in the most graphs (top 150 of 4773; key `events`)

| event | graphs |
|---|---|
| `SoundPlay` | 122 |
| `Done` | 88 |
| `End` | 83 |
| `moveStart` | 79 |
| `moveStop` | 79 |
| `preHitFrame` | 77 |
| `staggerStop` | 77 |
| `attackStop` | 75 |
| `staggerStart` | 75 |
| `turnStop` | 75 |
| `Reset` | 74 |
| `turnLeft` | 74 |
| `turnRight` | 74 |
| `HitFrame` | 73 |
| `PickNewIdle` | 73 |
| `weaponSwing` | 70 |
| `weaponDraw` | 69 |
| `Ragdoll` | 65 |
| `recoilStart` | 65 |
| `weaponSheathe` | 64 |
| `IdleStop` | 63 |
| `recoilStop` | 63 |
| `AddCharacterControllerToWorld` | 62 |
| `GetUpBegin` | 61 |
| `GetUpEnd` | 61 |
| `GetUpStart` | 61 |
| `Reanimated` | 61 |
| `RemoveCharacterControllerFromWorld` | 61 |
| `Trans01` | 61 |
| `AddRagdollToWorld` | 59 |
| `Open` | 59 |
| `Getup` | 58 |
| `SyncLeft` | 58 |
| `SyncRight` | 58 |
| `DeathAnimation` | 55 |
| `FootLeft` | 54 |
| `PairEnd` | 54 |
| `FootFront` | 52 |
| `FootBack` | 51 |
| `FootRight` | 51 |
| `recoilLargeStart` | 48 |
| `returnToDefault` | 48 |
| `2_KillActor` | 47 |
| `CyclicCrossBlend` | 47 |
| `CyclicFreeze` | 47 |
| `Trans02` | 47 |
| `bleedOutStop` | 46 |
| `Close` | 46 |
| `bleedOutStart` | 45 |
| `HeadTrackingOff` | 45 |
| `SprintStop` | 45 |
| `deathStart` | 44 |
| `HeadTrackingOn` | 43 |
| `SprintStart` | 43 |
| `KillActor` | 42 |
| `2_KillMoveEnd` | 41 |
| `2_KillMoveStart` | 41 |
| `moveForward` | 41 |
| `combatStanceStart` | 40 |
| `KillMoveStart` | 40 |
| `KillMoveEnd` | 39 |
| `moveBackward` | 39 |
| `pairedStop` | 39 |
| `RagdollInstant` | 39 |
| `Trigger01` | 38 |
| `cannedTurnStop` | 36 |
| `combatStanceStop` | 35 |
| `deathStop` | 35 |
| `NPCpairedStop` | 35 |
| `2_PairEnd` | 34 |
| `cannedTurnLeft180` | 34 |
| `cannedTurnLeft90` | 34 |
| `cannedTurnRight180` | 34 |
| `cannedTurnRight90` | 34 |
| `end` | 34 |
| `IdleCount` | 34 |
| `swimStart` | 34 |
| `swimStop` | 34 |
| `2_DeathEmote` | 33 |
| `aggroWarningStart` | 33 |
| `idleExit` | 33 |
| `runStart` | 33 |
| `walkStart` | 33 |
| `2_pairedStop` | 32 |
| `Trigger02` | 32 |
| `Event00` | 31 |
| `SneakStart` | 31 |
| `SneakStop` | 31 |
| `attackStart_Attack1` | 30 |
| `FootScuffLeft` | 30 |
| `FootScuffRight` | 30 |
| `attackStart_Attack2` | 29 |
| `bleedOutEnterOut` | 29 |
| `DeathEmote` | 29 |
| `Intialize` | 29 |
| `StartAnimationDriven` | 29 |
| `aggroWarningStop` | 27 |
| `BeginCastLeft` | 25 |
| `cannedTurnLeft180Flee` | 25 |
| `cannedTurnLeft90Flee` | 25 |
| `cannedTurnRight180Flee` | 25 |
| `cannedTurnRight90Flee` | 25 |
| `attackStart_ForwardPower` | 24 |
| `clipEnd` | 24 |
| `MLh_SpellFire_Event` | 24 |
| `StartOpen` | 24 |
| `idleChairGetUp` | 23 |
| `SoundRelease` | 23 |
| `weapEquip` | 23 |
| `attackStart_StandingPower` | 22 |
| `bashStop` | 22 |
| `cannedTurnMove` | 21 |
| `Down` | 21 |
| `InitiateEnd` | 21 |
| `staggerForwardStart` | 21 |
| `StartAllowRotation` | 21 |
| `SyncPoint` | 21 |
| `TransDown` | 21 |
| `weapUnequip` | 21 |
| `2_HitFrame` | 20 |
| `bashStart` | 20 |
| `blockStop` | 20 |
| `Idle_In` | 20 |
| `Idle_Out` | 20 |
| `idleLayStart` | 20 |
| `InitiateStart` | 20 |
| `NPCKillMoveEnd` | 20 |
| `NPCKillMoveStart` | 20 |
| `Start` | 20 |
| `Voice_SpellFire_Event` | 20 |
| `attackStart_AttackLeft1` | 19 |
| `attackStart_AttackRight1` | 19 |
| `DisableBumper` | 19 |
| `EnableBumper` | 19 |
| `HeadStart` | 19 |
| `LieDownEnter` | 19 |
| `LieDownExit` | 19 |
| `PickNewHead` | 19 |
| `PickNewTail` | 19 |
| `StopEffect` | 19 |
| `StrafeReturn` | 19 |
| `tailSneakIdle` | 19 |
| `TrapExitEnd` | 19 |
| `attackStart_ForwardPowerShort` | 18 |
| `AttackWinEnd` | 18 |
| `CameraShake` | 18 |
| `cannedTurnStrafeLeft90` | 18 |
| `cannedTurnStrafeRight90` | 18 |
| `idleStop` | 18 |
| `InterruptCast` | 18 |

1869 event names are declared in exactly one graph.

### Character properties

Graph-side (`hkbBehaviorGraphStringData.characterPropertyNames`), 75 names; key `graph_character_properties`:

| property | graphs |
|---|---|
| `UpperBody` | 14 |
| `FootIKDisable_AttackPowerForwardShort` | 13 |
| `FootIKDisable_AttackPowerStanding` | 13 |
| `FootIKDisable_AttackStandard` | 13 |
| `FootIKDisable_Recoil` | 13 |
| `FootIKDisable_RecoilLarge` | 13 |
| `m_alignWorldFromModelGain` | 13 |
| `m_ankleOrientationGain` | 13 |
| `m_errorUpDownBias` | 13 |
| `m_worldFromModelFeedbackGain` | 13 |
| `FootIKDisable_AttackPowerForward` | 12 |
| `FootIKDisable_IdleCombat` | 12 |
| `IsCanine` | 12 |
| `IsCow` | 12 |
| `IsSabreCat` | 12 |
| `IsSkeever` | 12 |
| `Body` | 11 |
| `FootIKDisable_AttackSpecial` | 11 |
| `Head` | 11 |
| `IsBear` | 11 |
| `IsDeer` | 11 |
| `IsGoat` | 11 |
| `IsHorker` | 11 |
| `IsMammoth` | 11 |
| `Tail` | 11 |
| `bAnimationDrivenAttacks` | 11 |
| `LeftArm` | 10 |
| `RightArm` | 10 |
| `Arms` | 6 |
| `ExcludeRoot+Cam+CamCtrl+Look` | 6 |
| `MLhFavorBoneSwitch` | 5 |
| `MRhFavorBoneSwitch` | 5 |
| `LeftForearm` | 4 |
| `SaddleOffsetBoneWeights` | 3 |
| `ArmsAndHead` | 2 |
| `ExcludeRoot` | 2 |
| `ExcludeRootAndCamera` | 2 |
| `Hands` | 2 |
| `IsMale` | 2 |
| `IsThirdPerson` | 2 |
| `LHStaffOnly` | 2 |
| `LeftHand` | 2 |
| `MountedCombatBowBlend` | 2 |
| `Quiver` | 2 |
| `RHStaffOnly` | 2 |
| `RightHandAndQuiver` | 2 |
| `ShieldAndLeftFingers` | 2 |
| `ShieldOnly` | 2 |
| `Spine2Descendents` | 2 |
| `UpperBodyNoRightArm` | 2 |
| `AnimObjectA_and_Camera` | 1 |
| `H2HTurnWeights_Arm` | 1 |
| `H2HTurnWeights_Body` | 1 |
| `HeadPartsBlend` | 1 |
| `IsWolf` | 1 |
| `JawBone` | 1 |
| `LArm_Forearm` | 1 |
| `LArm_Hand` | 1 |
| `LArm_UpperArm` | 1 |
| `LH_WardBoneWeights` | 1 |
| `LLeg_Calf` | 1 |
| `LLeg_Foot` | 1 |
| `LLeg_Thigh` | 1 |
| `LowerBody` | 1 |
| `RArm_Forearm` | 1 |
| `RArm_Hand` | 1 |
| `RArm_UpperArm` | 1 |
| `RH_WardBoneWeights` | 1 |
| `RLeg_Calf` | 1 |
| `RLeg_Foot` | 1 |
| `RLeg_Thigh` | 1 |
| `StaffMagicNode` | 1 |
| `cameraOut` | 1 |
| `jaw` | 1 |
| `wolfFaceOffsetWeightArray` | 1 |

Character files (`hkbCharacterStringData.characterPropertyNames`), 353 files, 99 names (top 60); key `character_files`. Total `animationNames` entries across character files: 7,736.

| property | character files |
|---|---|
| `FootIKDisable_AttackPowerForward` | 12 |
| `FootIKDisable_AttackPowerForwardShort` | 12 |
| `FootIKDisable_AttackPowerStanding` | 12 |
| `FootIKDisable_AttackStandard` | 12 |
| `FootIKDisable_IdleCombat` | 12 |
| `FootIKDisable_Recoil` | 12 |
| `FootIKDisable_RecoilLarge` | 12 |
| `IsBear` | 12 |
| `IsCanine` | 12 |
| `IsCow` | 12 |
| `IsDeer` | 12 |
| `IsGoat` | 12 |
| `IsHorker` | 12 |
| `IsHorse` | 12 |
| `IsMammoth` | 12 |
| `IsSabreCat` | 12 |
| `IsSkeever` | 12 |
| `bAnimationDrivenAttacks` | 12 |
| `m_alignWorldFromModelGain` | 12 |
| `m_ankleOrientationGain` | 12 |
| `m_errorUpDownBias` | 12 |
| `m_worldFromModelFeedbackGain` | 12 |
| `Body` | 10 |
| `FootIKDisable_AttackSpecial` | 10 |
| `Head` | 10 |
| `Tail` | 10 |
| `UpperBody` | 6 |
| `MLhFavorBoneSwitch` | 4 |
| `MRhFavorBoneSwitch` | 4 |
| `SaddleOffsetBoneWeights` | 4 |
| `cCharacterSelector` | 4 |
| `Arms` | 3 |
| `ArmsAndHead` | 3 |
| `Blend_AttackToBlock` | 3 |
| `ExcludeRoot` | 3 |
| `ExcludeRoot+Cam+CamCtrl+Look` | 3 |
| `ExcludeRoot+CamAndCamCtrlAndLook` | 3 |
| `ExcludeRootAndCamAndCamCtrlAndLook` | 3 |
| `ExcludeRootAndCamera` | 3 |
| `H2HTurnWeights_Arm` | 3 |
| `H2HTurnWeights_Body` | 3 |
| `Hands` | 3 |
| `IsFemale` | 3 |
| `IsMale` | 3 |
| `IsMale00` | 3 |
| `IsMale01` | 3 |
| `IsThirdPerson` | 3 |
| `LHStaffOnly` | 3 |
| `LeftArm` | 3 |
| `LeftForearm` | 3 |
| `LeftHand` | 3 |
| `MountedCombatBowBlend` | 3 |
| `Quiver` | 3 |
| `RHStaffOnly` | 3 |
| `RightArm` | 3 |
| `RightHand` | 3 |
| `RightHandAndQuiver` | 3 |
| `ShieldAndLeftFingers` | 3 |
| `ShieldOnly` | 3 |
| `SneakMagicLowerBody` | 3 |

Project files: 457 `hkbProjectData`, 3 list behavior files, 456 character filenames listed in total. Skeleton files: 328, bone-count distribution: 1 bones ×114, 2 bones ×45, 3 bones ×27, 7 bones ×12, 4 bones ×12, 12 bones ×8, 19 bones ×7, 18 bones ×7, 6 bones ×7, 24 bones ×6, 10 bones ×6, 5 bones ×6.

## 4. Annotation strings

### 4a. All clips: `meshes/animationdatasinglefile.txt` (complete)

The text file shipped alongside the behaviors, holding per-clip trigger events (`name:time`) for every clip in every project. These overlap with, but are not identical to, the .hkx `annotationTracks` (see the overlap figure in 4b). 429 project blocks (49 with motion data), parsed to EOF: **True**. 10,597 clip blocks, 9,127 with ≥1 trigger, **36,584 trigger instances, 721 distinct strings**. (The split copies under `meshes/animationdata/*.txt` parse to 323 files / 8,827 clip blocks — a subset; the single file is authoritative.) Compare: 10,086 `hkbClipGenerator`s in the behavior graphs. Key: `annotations.animationdata_txt`.

Cross-check: `wc -l ~/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt` → 170,724, the line the parser ends on (`parsed_to_eof` above); the framing one-liner is in the tool README.

Prefix rule: text up to and including the first `.` (`SoundPlay.`, `NPCSoundPlay.`), else the leading identifier with trailing digits dropped. Case is preserved (`syncLeft` and `SyncLeft` both exist).

| prefix | instances |
|---|---|
| `FootRight` | 3128 |
| `FootLeft` | 3096 |
| `NPCSoundPlay.` | 2610 |
| `FootBack` | 1462 |
| `FootFront` | 1265 |
| `SoundPlay.` | 1072 |
| `HitFrame` | 928 |
| `preHitFrame` | 905 |
| `SoundPlay` | 861 |
| `NPCFootScuffLeft` | 841 |
| `weaponSwing` | 816 |
| `NPCFootScuffRight` | 789 |
| `SyncLeft` | 751 |
| `SyncRight` | 744 |
| `00NextClip` | 636 |
| `syncRight` | 625 |
| `syncLeft` | 624 |
| `NPCHitFrame` | 599 |
| `attackStop` | 541 |
| `NPCweaponSwing` | 533 |
| `NPCpairedStop` | 453 |
| `NPCKillMoveEnd` | 442 |
| `NPCKillMoveStart` | 427 |
| `IdleStop` | 413 |
| `InitiateWinBegin` | 304 |
| `00PreviousClip` | 300 |
| `AttackWinEnd` | 284 |
| `AttackWinStart` | 284 |
| `FootScuffLeft` | 282 |
| `NPCPairEnd` | 277 |
| `2_KillMoveEnd` | 275 |
| `2_KillMoveStart` | 269 |
| `2_KillActor` | 267 |
| `returnToDefault` | 260 |
| `IdleFurnitureExit` | 253 |
| `FootScuffRight` | 241 |
| `staggerStop` | 239 |
| `InitiateWinEnd` | 238 |
| `CastOKStart` | 221 |
| `CountDownTick` | 218 |
| `PairEnd` | 217 |
| `2_PairEnd` | 202 |
| `AddCharacterControllerToWorld` | 187 |
| `GetUpEnd` | 186 |
| `FootSprintLeft` | 176 |
| `FootSprintRight` | 160 |
| `weaponDraw` | 149 |
| `2_DeathEmote` | 145 |
| `2_SoundPlay.` | 140 |
| `AttackWinEndLeft` | 136 |
| `AttackWinStartLeft` | 136 |
| `CameraShake` | 133 |
| `MotionDrivenIdle` | 132 |
| `weaponSheathe` | 123 |
| `attackRelease` | 120 |
| `BeginWeaponDraw` | 112 |
| `BeginWeaponSheathe` | 107 |
| `recoilStop` | 104 |
| `2_FootScuffLeft` | 102 |
| `Getup` | 99 |

Top 100 strings:

| trigger | instances |
|---|---|
| `FootRight` | 3038 |
| `FootLeft` | 3006 |
| `FootBack` | 1462 |
| `FootFront` | 1265 |
| `HitFrame` | 928 |
| `NPCSoundPlay.NPCKillStruggle` | 920 |
| `preHitFrame` | 905 |
| `SoundPlay` | 861 |
| `NPCFootScuffLeft` | 841 |
| `weaponSwing` | 816 |
| `NPCFootScuffRight` | 789 |
| `SyncLeft` | 751 |
| `SyncRight` | 744 |
| `00NextClip` | 636 |
| `syncRight` | 625 |
| `syncLeft` | 624 |
| `NPCHitFrame` | 599 |
| `attackStop` | 541 |
| `NPCweaponSwing` | 533 |
| `NPCpairedStop` | 453 |
| `NPCKillMoveEnd` | 442 |
| `NPCKillMoveStart` | 427 |
| `IdleStop` | 413 |
| `NPCSoundPlay.NPCKillShove` | 327 |
| `InitiateWinBegin` | 304 |
| `00PreviousClip` | 300 |
| `AttackWinEnd` | 284 |
| `AttackWinStart` | 284 |
| `FootScuffLeft` | 282 |
| `NPCPairEnd` | 277 |
| `2_KillMoveEnd` | 275 |
| `2_KillMoveStart` | 269 |
| `2_KillActor` | 267 |
| `NPCSoundPlay.NPCKillChop` | 267 |
| `returnToDefault` | 260 |
| `IdleFurnitureExit` | 253 |
| `NPCSoundPlay.NPCKillSlash` | 249 |
| `FootScuffRight` | 241 |
| `staggerStop` | 239 |
| `InitiateWinEnd` | 238 |
| `CastOKStart` | 221 |
| `CountDownTick` | 218 |
| `PairEnd` | 217 |
| `2_PairEnd` | 202 |
| `AddCharacterControllerToWorld` | 187 |
| `GetUpEnd` | 186 |
| `FootSprintLeft` | 176 |
| `NPCSoundPlay.NPCKillStabOut` | 176 |
| `NPCSoundPlay.NPCKillBodyfall` | 161 |
| `FootSprintRight` | 160 |
| `NPCSoundPlay.NPCKillStabIn` | 155 |
| `weaponDraw` | 149 |
| `2_DeathEmote` | 145 |
| `AttackWinEndLeft` | 136 |
| `AttackWinStartLeft` | 136 |
| `CameraShake` | 133 |
| `MotionDrivenIdle` | 132 |
| `weaponSheathe` | 123 |
| `attackRelease` | 120 |
| `BeginWeaponDraw` | 112 |
| `BeginWeaponSheathe` | 107 |
| `NPCSoundPlay.NPCKillGore` | 105 |
| `recoilStop` | 104 |
| `2_FootScuffLeft` | 102 |
| `Getup` | 99 |
| `NPCSoundPlay.NPCKillSmash` | 99 |
| `2_FootScuffRight` | 92 |
| `InitiateStart` | 92 |
| `InitiateEnd` | 91 |
| `FootLeft2` | 90 |
| `FootRight2` | 90 |
| `ReturnToDefault` | 90 |
| `CameraShake.0.2` | 87 |
| `Reanimated` | 84 |
| `cannedTurnStop` | 84 |
| `WeapEquip_Out` | 81 |
| `PowerAttackStop` | 77 |
| `arrowAttach` | 76 |
| `weaponLeftSwing` | 70 |
| `SoundPlay.NPCDragonWingFlapTakeoff` | 68 |
| `Unequip_Out` | 66 |
| `initWinBegin` | 66 |
| `shoutStop` | 66 |
| `SoundPlay.NPCWerewolfAttackB` | 64 |
| `AnimObjDraw` | 63 |
| `AttackStop` | 63 |
| `SoundPlay.NPCGoatFootBell` | 62 |
| `SoundPlay.NPCDragonWingFlap` | 60 |
| `RF_Talk_Out` | 58 |
| `NPCSoundPlay.NPCKillMelee` | 57 |
| `WeapEquip_OutMoving` | 57 |
| `InitiateStartLeft` | 56 |
| `InitiateStartRight` | 55 |
| `StartAnimationDriven` | 55 |
| `Voice_SpellFire_Event` | 54 |
| `arrowRelease` | 54 |
| `idleStop` | 54 |
| `Ragdoll` | 52 |
| `blockHitStop` | 52 |
| `MLh_SpellFire_Event` | 51 |

### 4b. Animation .hkx under `animations/` dirs: `annotationTracks` (COMPLETE)

**Coverage: complete.** Every `.hkx` under an `animations/` dir was converted (`bulk_convert.sh anim-all` → `~/skyrim-data-extracted/xml-anim/`, manifest: 5,936 ok) and all 5,936 XML files are read here. This replaces the 200-file sample this section used before; the sample's figures stay in `annotations.hkx_sample` (200 files, 60 distinct strings). Key: `annotations.hkx_animations`.

Cross-check: `cut -f1 ~/skyrim-data-extracted/xml-anim/_manifest.tsv | sort | uniq -c` → 5936 ok; `_errors.log` is empty (`wc -c`); `find ~/skyrim-data-extracted/raw -iname '*.hkx' | grep -ic /animations/` → 5936.

- Files: 5,936; animation objects: **5,935** (animations per file: 0 in 1 files, 1 in 5,935 files; without one: `meshes/actors/character/animations/byoh/special_childdollplay2.xml`).
- **Annotated clips: 1,857** of 5,935 (31.3%); **7,645 annotation instances, 512 distinct strings**. Per annotated clip: median 4, p90 7, max 29.
- Annotation tracks: one per transform track in 5,935/5,935 animations. Track names are empty except in 120 animations (22,834 named tracks, 275 distinct names, e.g. `Camera Control`, `MagicEffectsNode`, `NPC COM [COM ]`, `NPC Head MagicNode [Hmag]`, `NPC Head [Head]`, `NPC L Calf [LClf]`).

#### Annotations vs `animationdatasinglefile.txt` triggers

|  | distinct strings | instances |
|---|---|---|
| in .hkx annotations | 512 | 7645 |
| in the text file's triggers | 721 | 36584 |
| in both | 205 | — |
| only in .hkx | 307 | 692 |
| only in the text file | 516 | 18347 |

(The 200-file sample showed 36 of 60 .hkx strings among the triggers; on the full set it is **205 of 512**.) The two lists are different things, and the difference is explained, not noise:

- **Every one of the 721 trigger strings is a declared event** in some behavior graph (`txt_strings_declared_as_graph_events` = 721). The text file holds *events*, not annotation text.
- **Only in the text file** (516 strings, 18,347 instances) are clip-generator triggers authored in the behavior graphs (`hkbClipTriggerArray`): paired/killmove events (`NPCKillMoveStart`, `2_KillActor`, `NPCSoundPlay.*`), state exits (`attackStop`, `IdleStop`, `00NextClip`), and the bare event `SoundPlay`. Only 4 are `NPC` + an .hkx string and 1 a case variant, so the `NPC*` strings are not renamed annotations.
- **Only in .hkx** (307 strings, 692 instances) is mostly the payload form `SoundPlay.<descriptor>` / `CameraShake.<x>` / `SoundPlayAt.`/`SoundStop.`/`AnimObjLoad.`, which reaches the text file as the bare event before the first `.`, plus annotations no graph declares (`FrontFoot`, `BackFoot`, typos such as `FootFornt`, `FrootBack`). 3 differ from a trigger only by case.

**Per-clip model, tested.** For each of the text file's clip blocks, find a `hkbClipGenerator` of the same name (any graph; names repeat across projects, so *any* matching candidate counts) and predict its triggers as: the clip generator's own triggers (event ids resolved through that graph's `eventNames`), plus each annotation of its animation (path resolved against the project dir, the parent of the graph's directory) that resolves to a declared event of that graph — the whole text if declared, else the text before the first `.`, else dropped. Compared as multisets (times not compared). Key: `annotations.hkx_animations.per_clip_model`.

| verdict | clip blocks |
|---|---|
| match_triggers_only | 6,796 |
| match_triggers_plus_resolved_annotations | 3,558 |
| mismatch | 216 |
| animation_not_found | 24 |
| no_clip_generator_named | 3 |

**10,354 of 10,597 clips (97.7%) match exactly.** Of the 216 mismatches, by the closest candidate: 174 txt_lacks_some_predicted, 36 txt_has_unpredicted, 6 both_ways — i.e. mostly the text file *omits* an annotation the model resolves (hypotheses, not checked: the game resolves against a different graph's events than the candidate's, or the candidate is a same-named clip of another project). In matched clips, 130 annotations resolved to no event and were correctly dropped; their prefixes: `FrontFoot` 36, `BackFoot` 33, `NPCPlayAnim` 10, `PlayAnim` 10, `FootFornt` 6, `SoundPlay.` 6, `2_SoundPlay.` 5, `CameraShake.` 5, `FrootBack` 4, `FoorRight` 2, `FootBack` 2, `FootRight` 2.

Engine consequence: the text file is a precomputed cache of the events a clip fires, derivable (for 97.7% of clips, as measured) from the graphs plus the annotations. An annotation's payload after the `.` (`SoundPlay.NPCHumanClap`) reaches the text file only when the whole string is itself a declared event; otherwise only the .hkx carries it. Why the text file omits some resolvable annotations (the 174 above) is **not verified**.

#### Prefixes and strings

| prefix | instances |
|---|---|
| `FootLeft` | 1053 |
| `FootRight` | 1043 |
| `SoundPlay.` | 986 |
| `FootBack` | 768 |
| `FootFront` | 683 |
| `SyncLeft` | 387 |
| `SyncRight` | 382 |
| `preHitFrame` | 262 |
| `weaponSwing` | 255 |
| `HitFrame` | 244 |
| `syncLeft` | 178 |
| `syncRight` | 178 |
| `FootScuffLeft` | 120 |
| `CameraShake.` | 118 |
| `FootScuffRight` | 111 |
| `FootSprintLeft` | 98 |
| `FootSprintRight` | 97 |
| `weaponDraw` | 48 |
| `weaponSheathe` | 33 |
| `arrowAttach` | 31 |
| `StartAnimationDriven` | 28 |
| `FrontFoot` | 26 |
| `BackFoot` | 25 |
| `FlightLandingEffect` | 25 |
| `arrowRelease` | 24 |
| `BeginWeaponDraw` | 22 |
| `MLh_SpellFire_Event` | 22 |
| `SoundPlayAt.` | 20 |
| `DragonTakeoffEffect` | 19 |
| `SoundStop.` | 17 |
| `hitFrame` | 17 |
| `BeginWeaponSheathe` | 14 |
| `Voice_SpellFire_Event` | 14 |
| `FlightCrashLandLoadEffect` | 11 |
| `NPCDogHuskyIdleWhine` | 11 |
| `NPCDogIdleWhine` | 11 |
| `FlapThrustBegin` | 9 |
| `FlapThrustEnd` | 9 |
| `SyncB_Right` | 9 |
| `SyncF_Left` | 9 |

Top 60 of 512 strings (instances, files carrying it):

| annotation | instances | files |
|---|---|---|
| `FootLeft` | 1004 | 789 |
| `FootRight` | 994 | 771 |
| `FootBack` | 768 | 340 |
| `FootFront` | 683 | 319 |
| `SyncLeft` | 387 | 387 |
| `SyncRight` | 382 | 381 |
| `preHitFrame` | 262 | 240 |
| `weaponSwing` | 255 | 234 |
| `HitFrame` | 244 | 222 |
| `syncLeft` | 178 | 172 |
| `syncRight` | 178 | 172 |
| `FootScuffLeft` | 120 | 61 |
| `FootScuffRight` | 111 | 64 |
| `FootSprintLeft` | 98 | 22 |
| `FootSprintRight` | 97 | 21 |
| `SoundPlay.NPCDragonWingFlapTakeoff` | 62 | 16 |
| `SoundPlay.NPCDragonWingFlap` | 60 | 34 |
| `SoundPlay.NPCHumanClap` | 54 | 5 |
| `CameraShake.0.3` | 52 | 28 |
| `FootLeft2` | 49 | 49 |
| `FootRight2` | 49 | 49 |
| `weaponDraw` | 48 | 48 |
| `CameraShake.0.2` | 47 | 16 |
| `SoundPlay.NPCGoatFootBell` | 37 | 22 |
| `weaponSheathe` | 33 | 33 |
| `arrowAttach` | 31 | 31 |
| `StartAnimationDriven` | 28 | 28 |
| `FrontFoot` | 26 | 11 |
| `BackFoot` | 25 | 11 |
| `FlightLandingEffect` | 25 | 10 |
| `arrowRelease` | 24 | 24 |
| `BeginWeaponDraw` | 22 | 22 |
| `MLh_SpellFire_Event` | 22 | 22 |
| `SoundPlay.NPCGoatChew` | 21 | 5 |
| `SoundPlay.NPCTrollAttackB` | 21 | 17 |
| `DragonTakeoffEffect` | 19 | 7 |
| `SoundPlay.WPNCrossbowReload` | 19 | 19 |
| `SoundPlay.NPCTrollAttackA` | 17 | 17 |
| `hitFrame` | 17 | 17 |
| `SoundPlay.WPNCrossbowReloadQuickShotPerk` | 16 | 16 |
| `BeginWeaponSheathe` | 14 | 14 |
| `SoundPlay.NPCCowChewCud` | 14 | 6 |
| `SoundPlay.OBJSawMillSawMoveDown` | 14 | 1 |
| `Voice_SpellFire_Event` | 14 | 14 |
| `SoundPlay.NPCSpiderFrostbiteAttackA` | 13 | 13 |
| `SoundPlay.NPCChickenPeck` | 12 | 2 |
| `SoundPlay.NPCHumanEat` | 12 | 9 |
| `FlightCrashLandLoadEffect` | 11 | 11 |
| `NPCDogHuskyIdleWhine` | 11 | 7 |
| `NPCDogIdleWhine` | 11 | 7 |
| `CameraShake.0.1` | 10 | 5 |
| `SoundPlay.NPCHumanBookPageTurn` | 10 | 4 |
| `SoundPlay.OBJSawMillSawMoveUp` | 10 | 1 |
| `FlapThrustBegin` | 9 | 9 |
| `FlapThrustEnd` | 9 | 9 |
| `SoundPlay.NPCHumanBartenderWipe` | 9 | 1 |
| `SoundPlay.NPCHumanSweepB` | 9 | 1 |
| `SoundPlay.NPCSlaughterfishLocomotion` | 9 | 9 |
| `SyncB_Right` | 9 | 9 |
| `SyncF_Left` | 9 | 9 |

Strings only in .hkx, top 30 (instances):

| annotation | instances |
|---|---|
| `SoundPlay.NPCHumanClap` | 54 |
| `FrontFoot` | 26 |
| `BackFoot` | 25 |
| `SoundPlay.WPNCrossbowReload` | 19 |
| `SoundPlay.WPNCrossbowReloadQuickShotPerk` | 16 |
| `SoundPlay.OBJSawMillSawMoveDown` | 14 |
| `SoundPlay.NPCHumanEat` | 12 |
| `CameraShake.0.1` | 10 |
| `SoundPlay.NPCHumanBookPageTurn` | 10 |
| `SoundPlay.OBJSawMillSawMoveUp` | 10 |
| `SoundPlay.NPCHumanBartenderWipe` | 9 |
| `SoundPlay.NPCHumanSweepB` | 9 |
| `CameraShake.0.5` | 8 |
| `SoundPlayAt.OBJSawMillSawMoveDown.SoundNode01` | 8 |
| `SoundPlay.FSTSwimTread` | 7 |
| `SoundPlay.NPCChaurusAttack` | 7 |
| `SoundPlay.NPCHumanSweepA` | 7 |
| `SoundPlayAt.OBJSawMillSawMoveUp.SoundNode01` | 7 |
| `SoundPlay.NPCHumanDrink` | 6 |
| `SoundPlay.NPCSkeeverAttack` | 6 |
| `SoundPlay.NPCSabreCatAttack` | 5 |
| `SoundPlay.NPCVampireLordAttackLeft` | 5 |
| `SoundPlay.NPCVampireLordAttackRight` | 5 |
| `FrootBack` | 4 |
| `NPCFoxBreathe` | 4 |
| `SoundPlay.NPCAtronachStormAttackA` | 4 |
| `SoundPlay.NPCAtronachStormAttackB` | 4 |
| `SoundPlay.NPCGiantAttackClub02` | 4 |
| `SoundPlay.NPCHumanSitChairDownLR` | 4 |
| `SoundPlay.NPCHumanSitChairUpLR` | 4 |

Strings only in the text file, top 30 (instances):

| trigger | instances |
|---|---|
| `NPCSoundPlay.NPCKillStruggle` | 920 |
| `SoundPlay` | 861 |
| `NPCFootScuffLeft` | 841 |
| `NPCFootScuffRight` | 789 |
| `00NextClip` | 636 |
| `NPCHitFrame` | 599 |
| `attackStop` | 541 |
| `NPCweaponSwing` | 533 |
| `NPCpairedStop` | 453 |
| `NPCKillMoveEnd` | 442 |
| `NPCKillMoveStart` | 427 |
| `IdleStop` | 413 |
| `NPCSoundPlay.NPCKillShove` | 327 |
| `InitiateWinBegin` | 304 |
| `00PreviousClip` | 300 |
| `NPCPairEnd` | 277 |
| `2_KillMoveEnd` | 275 |
| `2_KillMoveStart` | 269 |
| `2_KillActor` | 267 |
| `NPCSoundPlay.NPCKillChop` | 267 |
| `returnToDefault` | 260 |
| `IdleFurnitureExit` | 253 |
| `NPCSoundPlay.NPCKillSlash` | 249 |
| `staggerStop` | 239 |
| `InitiateWinEnd` | 238 |
| `CastOKStart` | 221 |
| `CountDownTick` | 218 |
| `PairEnd` | 217 |
| `2_PairEnd` | 202 |
| `AddCharacterControllerToWorld` | 187 |

#### Animation shape (all animation objects)

|  | n | min | p10 | p50 | p90 | p99 | max | mean |
|---|---|---|---|---|---|---|---|---|
| duration (s) | 5935 | 0.033333 | 0.633333 | 1.566667 | 5.833333 | 12.2 | 49.0 | 2.517074 |
| numFrames | 5935 | 2 | 19 | 47 | 176 | 361 | 1471 | 75.657119 |
| transform tracks | 5935 | 1 | 5 | 84 | 99 | 201 | 210 | 73.225442 |
| float tracks | 5935 | 0 | 0 | 0 | 4 | 4 | 11 | 1.599158 |
| bone-index map length (non-empty only) | 205 | 1 | 2 | 23 | 98 | 98 | 98 | 47.980488 |

Total duration 14,939 s (4.15 h); total frames 449,025. Keys: `duration_s`, `num_frames` (from `hkaSplineCompressedAnimation.duration` / `numFrames`).

- Class: `hkaSplineCompressedAnimation` ×5,935; compression `type`: `HK_SPLINE_COMPRESSED_ANIMATION` ×5,935. **One codec covers every animation.**
- Blocks per animation (`numBlocks`; `maxFramesPerBlock` is 256 in 5,897 and 128 in 38, by `grep -rh maxFramesPerBlock ~/skyrim-data-extracted/xml-anim | sort | uniq -c`): 1 ×5,666, 2 ×235, 3 ×22, 4 ×8, 5 ×3, 6 ×1.
- `frameDuration`: 0.033333 s ×5,873, 0.333333 s ×10, 0.166667 s ×8, 6.666667 s ×7, 1.000000 s ×4, 1.466667 s ×3, 19 other values (key `frame_duration_s`). 0.033333 s is 30 fps.
- Transform-track counts, commonest: 99 ×2332, 5 ×338, 84 ×247, 83 ×220, 80 ×155, 2 ×130, 82 ×126, 85 ×118, 88 ×117, 44 ×106, 93 ×102, 50 ×101, 1 ×85, 201 ×84, 98 ×82. Animations with float tracks: 2,497.
- `blendHint`: NORMAL ×5,914, ADDITIVE ×21; with `extractedMotion`: 13; with a non-empty `transformTrackToBoneIndices` (empty presumably means track i = bone i; **not verified**): 205.
- `originalSkeletonName`, top 10: `NPC Root [Root]` ×4,916, `TailExport01` ×322, `Base01` ×267, `PairedRoot` ×114, `NPC Root [Root] Male` ×85, `DomeBase01` ×27, `Base` ×17, `SkyHavenBloodRing01Anim` ×16, `ArmillaryBase01` ×15, `DownRoot` ×13; 52 distinct.

### 4c. Animations stored outside `animations/` dirs (complete for those 191 files)

37 annotation instances, 11 distinct. Key: `annotations.hkx_outside_animations_dirs`.

| annotation | instances |
|---|---|
| `SoundPlay.NPCWolfAggroWarning` | 7 |
| `2_SoundPlay.NPCKill1HMD` | 5 |
| `NPCPlayAnim01` | 5 |
| `PlayAnim01` | 5 |
| `SoundPlay.NPCKill1HMD` | 5 |
| `HitFrame` | 2 |
| `NPCSoundPlay.NPCVampireLordFeed` | 2 |
| `preHitFrame` | 2 |
| `weaponSwing` | 2 |
| `SoundPlay.NPCHorseDismount` | 1 |
| `SoundPlay.NPCHorseMount` | 1 |

## 5. Long tail

Node classes only (47 classes, 33,630 instances over behavior graphs). Key: `behavior_node_class_coverage`.

| coverage of node instances | classes needed |
|---|---|
| 50% | 2 |
| 90% | 9 |
| 99% | 25 |
| 100% | 47 |

All classes in behavior files (66 classes, 68,041 objects, incl. data/arrays/transition effects):

| coverage of all objects | classes needed |
|---|---|
| 50% | 5 |
| 90% | 16 |
| 99% | 37 |
| 100% | 66 |

Node classes by instance count, cumulative:

| # | class | role | instances | graphs | cumulative |
|---|---|---|---|---|---|
| 1 | `hkbStateMachineStateInfo` | state | 10619 | 422 | 31.58% |
| 2 | `hkbClipGenerator` | generator | 10086 | 300 | 61.57% |
| 3 | `hkbStateMachine` | generator | 3643 | 425 | 72.40% |
| 4 | `hkbBlenderGenerator` | generator | 2009 | 146 | 78.37% |
| 5 | `hkbModifierGenerator` | generator | 1918 | 118 | 84.08% |
| 6 | `hkbModifierList` | modifier | 710 | 82 | 86.19% |
| 7 | `BSIsActiveModifier` | modifier | 671 | 95 | 88.18% |
| 8 | `BGSGamebryoSequenceGenerator` | generator | 603 | 146 | 89.98% |
| 9 | `hkbManualSelectorGenerator` | generator | 582 | 78 | 91.71% |
| 10 | `BSSynchronizedClipGenerator` | generator | 537 | 30 | 93.30% |
| 11 | `hkbEvaluateExpressionModifier` | modifier | 468 | 66 | 94.70% |
| 12 | `BSiStateTaggingGenerator` | generator | 170 | 25 | 95.20% |
| 13 | `hkbEventDrivenModifier` | modifier | 158 | 67 | 95.67% |
| 14 | `BSCyclicBlendTransitionGenerator` | generator | 153 | 45 | 96.13% |
| 15 | `BSBoneSwitchGenerator` | generator | 137 | 13 | 96.53% |
| 16 | `BSLookAtModifier` | modifier | 128 | 36 | 96.91% |
| 17 | `BSEventOnDeactivateModifier` | modifier | 98 | 19 | 97.20% |
| 18 | `hkbBehaviorReferenceGenerator` | generator | 97 | 42 | 97.49% |
| 19 | `hkbPoseMatchingGenerator` | generator | 96 | 47 | 97.78% |
| 20 | `hkbPoweredRagdollControlsModifier` | modifier | 93 | 47 | 98.06% |
| 21 | `hkbKeyframeBonesModifier` | modifier | 91 | 50 | 98.33% |
| 22 | `BSEventEveryNEventsModifier` | modifier | 85 | 20 | 98.58% |
| 23 | `hkbTimerModifier` | modifier | 59 | 54 | 98.75% |
| 24 | `hkbRigidBodyRagdollControlsModifier` | modifier | 55 | 50 | 98.92% |
| 25 | `BSRagdollContactListenerModifier` | modifier | 50 | 42 | 99.07% |
| 26 | `hkbGetUpModifier` | modifier | 46 | 46 | 99.20% |
| 27 | `hkbDampingModifier` | modifier | 43 | 38 | 99.33% |
| 28 | `BSSpeedSamplerModifier` | modifier | 42 | 42 | 99.46% |
| 29 | `BSInterpValueModifier` | modifier | 36 | 10 | 99.56% |
| 30 | `BSModifyOnceModifier` | modifier | 26 | 20 | 99.64% |
| 31 | `hkbFootIkControlsModifier` | modifier | 25 | 25 | 99.71% |
| 32 | `BSDirectAtModifier` | modifier | 23 | 13 | 99.78% |
| 33 | `BSEventOnFalseToTrueModifier` | modifier | 23 | 14 | 99.85% |
| 34 | `hkbTwistModifier` | modifier | 19 | 12 | 99.91% |
| 35 | `hkbRotateCharacterModifier` | modifier | 6 | 6 | 99.93% |
| 36 | `BSTweenerModifier` | modifier | 5 | 1 | 99.94% |
| 37 | `hkbReferencePoseGenerator` | generator | 4 | 4 | 99.95% |
| 38 | `BSIStateManagerModifier` | modifier | 3 | 3 | 99.96% |
| 39 | `hkbEventsFromRangeModifier` | modifier | 3 | 2 | 99.97% |
| 40 | `BSOffsetAnimationGenerator` | generator | 2 | 2 | 99.98% |
| 41 | `hkbFootIkModifier` | modifier | 2 | 1 | 99.98% |
| 42 | `BSDecomposeVectorModifier` | modifier | 1 | 1 | 99.99% |
| 43 | `BSGetTimeStepModifier` | modifier | 1 | 1 | 99.99% |
| 44 | `BSLimbIKModifier` | modifier | 1 | 1 | 99.99% |
| 45 | `BSPassByTargetTriggerModifier` | modifier | 1 | 1 | 99.99% |
| 46 | `BSTimerModifier` | modifier | 1 | 1 | 100.00% |
| 47 | `hkbTransformVectorModifier` | modifier | 1 | 1 | 100.00% |

## 6. Per actor / directory

Group = `actors/<dir>` (`actors/ambient/*`, `actors/dlc01/*`, `actors/dlc02/*` one level deeper); non-actor paths are `other:meshes/<dir>`. Key: `per_group`.

| group | graphs | nodes | SMs | clips | max depth | max xdepth | characters | projects |
|---|---|---|---|---|---|---|---|---|
| `actors/character` | 35 | 15924 | 1963 | 4975 | 14 | 21 | 3 | 3 |
| `actors/draugr` | 1 | 975 | 79 | 414 | 8 | 8 | 3 | 2 |
| `actors/canine` | 9 | 898 | 81 | 222 | 7 | 9 | 2 | 2 |
| `actors/dragon` | 1 | 830 | 66 | 214 | 9 | 9 | 1 | 1 |
| `actors/dlc02/boarriekling` | 6 | 662 | 60 | 166 | 6 | 7 | 1 | 1 |
| `actors/falmer` | 1 | 616 | 67 | 190 | 9 | 9 | 1 | 1 |
| `other:meshes/dungeons/dwemer` | 23 | 605 | 47 | 212 | 3 | 3 | 23 | 25 |
| `actors/werewolfbeast` | 1 | 548 | 67 | 200 | 8 | 8 | 1 | 1 |
| `actors/vampirelord` | 1 | 466 | 44 | 116 | 9 | 9 | 1 | 1 |
| `actors/sabrecat` | 4 | 396 | 36 | 91 | 7 | 8 | 1 | 1 |
| `actors/giant` | 1 | 379 | 42 | 124 | 9 | 9 | 1 | 1 |
| `actors/dragonpriest` | 1 | 377 | 36 | 117 | 7 | 7 | 1 | 1 |
| `actors/cow` | 6 | 361 | 29 | 80 | 7 | 9 | 1 | 1 |
| `actors/dwarvenspherecenturion` | 1 | 359 | 36 | 132 | 8 | 8 | 1 | 1 |
| `actors/dlc02/riekling` | 1 | 355 | 30 | 127 | 7 | 7 | 1 | 1 |
| `other:meshes/dlc02/dungeons` | 27 | 349 | 41 | 83 | 2 | 2 | 27 | 27 |
| `actors/troll` | 1 | 335 | 24 | 116 | 6 | 6 | 1 | 1 |
| `actors/dlc02/benthiclurker` | 1 | 330 | 36 | 111 | 7 | 7 | 1 | 1 |
| `actors/bear` | 4 | 319 | 27 | 74 | 7 | 8 | 1 | 1 |
| `actors/horker` | 4 | 317 | 32 | 75 | 7 | 8 | 1 | 1 |
| `actors/goat` | 6 | 292 | 27 | 62 | 7 | 9 | 1 | 1 |
| `other:meshes/auxbones/tail` | 1 | 281 | 7 | 154 | 3 | 3 | 1 | 1 |
| `actors/deer` | 4 | 275 | 25 | 59 | 7 | 8 | 1 | 1 |
| `actors/mammoth` | 4 | 268 | 26 | 59 | 7 | 8 | 1 | 1 |
| `actors/dlc02/scrib` | 1 | 266 | 25 | 71 | 6 | 6 | 1 | 1 |
| `actors/spriggan` | 1 | 266 | 21 | 92 | 6 | 6 | 1 | 1 |
| `actors/hagraven` | 1 | 265 | 21 | 96 | 6 | 6 | 1 | 1 |
| `other:meshes/dungeons/nordic` | 20 | 262 | 24 | 97 | 2 | 2 | 20 | 45 |
| `actors/dwarvensteamcenturion` | 1 | 260 | 24 | 80 | 6 | 6 | 1 | 1 |
| `actors/skeever` | 4 | 254 | 24 | 50 | 7 | 8 | 1 | 1 |
| `other:meshes/dlc01/dungeons` | 16 | 246 | 22 | 86 | 2 | 2 | 16 | 16 |
| `actors/horse` | 1 | 233 | 20 | 65 | 8 | 8 | 1 | 1 |
| `actors/chaurus` | 1 | 230 | 18 | 66 | 7 | 7 | 1 | 1 |
| `actors/dlc01/vampirebrute` | 1 | 220 | 24 | 69 | 7 | 7 | 1 | 1 |
| `actors/dlc02/hmdaedra` | 1 | 212 | 21 | 68 | 6 | 6 | 1 | 1 |
| `actors/mudcrab` | 1 | 206 | 19 | 56 | 7 | 7 | 1 | 1 |
| `actors/dlc02/dwarvenballistacenturion` | 1 | 190 | 19 | 55 | 6 | 6 | 1 | 1 |
| `actors/atronachflame` | 1 | 186 | 24 | 45 | 7 | 7 | 1 | 1 |
| `actors/atronachfrost` | 1 | 177 | 18 | 59 | 7 | 7 | 1 | 1 |
| `actors/wisp` | 1 | 172 | 22 | 47 | 6 | 6 | 1 | 1 |
| `actors/frostbitespider` | 2 | 171 | 14 | 53 | 6 | 6 | 1 | 1 |
| `actors/dlc01/chaurusflyer` | 1 | 162 | 13 | 51 | 5 | 5 | 1 | 1 |
| `other:meshes/magic/magicbehaviors` | 17 | 159 | 19 | 0 | 2 | 2 | 15 | 0 |
| `actors/dwarvenspider` | 1 | 158 | 12 | 44 | 7 | 7 | 1 | 1 |
| `actors/atronachstorm` | 1 | 142 | 16 | 38 | 7 | 7 | 1 | 1 |
| `actors/ambient/chicken` | 1 | 127 | 11 | 36 | 6 | 6 | 1 | 1 |
| `actors/ambient/hare` | 1 | 116 | 11 | 29 | 6 | 6 | 1 | 1 |
| `actors/slaughterfish` | 1 | 102 | 13 | 27 | 7 | 7 | 1 | 1 |
| `other:meshes/dlc02/sharedbehaviors` | 12 | 102 | 12 | 0 | 1 | 1 | 12 | 12 |
| `actors/dlc02/netch` | 1 | 100 | 12 | 19 | 6 | 6 | 1 | 1 |
| `actors/icewraith` | 1 | 95 | 11 | 24 | 5 | 5 | 1 | 1 |
| `other:meshes/architecture/skyhaventemple` | 6 | 90 | 6 | 42 | 1 | 1 | 6 | 6 |
| `other:meshes/dlc01/clutter` | 7 | 81 | 7 | 37 | 1 | 1 | 7 | 7 |
| `other:meshes/traps/norplatformtrap` | 1 | 79 | 1 | 13 | 1 | 1 | 1 | 2 |
| `other:meshes/dlc01/sharedbehaviors` | 6 | 62 | 7 | 0 | 2 | 2 | 6 | 6 |
| `other:meshes/genericbehaviors/behaviors` | 7 | 51 | 8 | 0 | 2 | 2 | 0 | 0 |
| `other:meshes/furniture/clutter` | 5 | 48 | 5 | 15 | 1 | 1 | 5 | 5 |
| `other:meshes/dlc01/traps` | 4 | 46 | 4 | 12 | 1 | 1 | 4 | 4 |
| `actors/witchlight` | 1 | 45 | 6 | 11 | 4 | 4 | 1 | 1 |
| `other:meshes/dlc01/architecture` | 4 | 36 | 4 | 12 | 1 | 1 | 4 | 4 |
| `other:meshes/dungeons/imperial` | 4 | 36 | 4 | 16 | 1 | 1 | 4 | 18 |
| `other:meshes/clutter/ruins` | 4 | 34 | 4 | 11 | 1 | 1 | 4 | 4 |
| `other:meshes/clutter/sarcophagusboltlock` | 2 | 34 | 2 | 16 | 1 | 1 | 2 | 2 |
| `other:meshes/interface/interfacebehaviors` | 2 | 32 | 2 | 0 | 1 | 1 | 2 | 0 |
| `other:meshes/traps/bowtrap` | 1 | 31 | 1 | 15 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/walltrap` | 1 | 31 | 1 | 15 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/books` | 2 | 30 | 2 | 12 | 1 | 1 | 2 | 4 |
| `other:meshes/dlc01/magic` | 2 | 28 | 3 | 0 | 2 | 2 | 2 | 2 |
| `other:meshes/dlc01/plants` | 3 | 27 | 3 | 12 | 1 | 1 | 3 | 3 |
| `other:meshes/uniquebehaviors/sprigganfx` | 1 | 27 | 3 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/weapons/boundweapons` | 1 | 25 | 4 | 7 | 3 | 3 | 1 | 1 |
| `other:meshes/clutter/eyeofmagnus` | 1 | 23 | 3 | 4 | 2 | 2 | 1 | 1 |
| `other:meshes/clutter/blackpool` | 2 | 22 | 4 | 5 | 2 | 2 | 2 | 2 |
| `other:meshes/clutter/lumbermill` | 3 | 21 | 3 | 0 | 1 | 1 | 3 | 3 |
| `other:meshes/clutter/mehrunesdagonaltar` | 1 | 21 | 3 | 4 | 2 | 2 | 1 | 1 |
| `other:meshes/genericbehaviors/idleplayidle3` | 1 | 21 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/effects/effectsbehaviors` | 3 | 19 | 3 | 0 | 1 | 1 | 3 | 0 |
| `other:meshes/uniquebehaviors/dragonbloodhead` | 1 | 19 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonbloodtail` | 1 | 19 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonbloodwingl` | 1 | 19 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonbloodwingr` | 1 | 19 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/dragonpriestmaskaltar` | 2 | 18 | 2 | 8 | 1 | 1 | 2 | 2 |
| `other:meshes/dlc01/furniture` | 3 | 17 | 3 | 3 | 1 | 1 | 3 | 3 |
| `other:meshes/traps/spinningrailblade` | 1 | 17 | 1 | 8 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/swingingblade` | 1 | 17 | 3 | 3 | 2 | 2 | 1 | 1 |
| `other:meshes/traps/whiterundragontrap` | 1 | 17 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonfly` | 1 | 17 | 3 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/weapons/bow` | 1 | 17 | 2 | 7 | 2 | 2 | 1 | 1 |
| `other:meshes/clutter/statues` | 2 | 16 | 2 | 7 | 1 | 1 | 2 | 2 |
| `other:meshes/traps/dwefirepillar` | 1 | 16 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/furniture/dragonfurniture` | 1 | 15 | 3 | 3 | 2 | 2 | 1 | 1 |
| `other:meshes/furniture/furniturebehaviors` | 1 | 15 | 1 | 0 | 1 | 1 | 1 | 0 |
| `other:meshes/architecture/riften` | 2 | 14 | 2 | 6 | 1 | 1 | 2 | 2 |
| `other:meshes/critters/birds` | 2 | 14 | 2 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/critters/crittersbehaviors` | 2 | 14 | 2 | 0 | 1 | 1 | 1 | 0 |
| `other:meshes/dlc01/weapons` | 1 | 13 | 1 | 5 | 1 | 1 | 2 | 2 |
| `other:meshes/genericbehaviors/autoplayragdoll` | 1 | 13 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonskin` | 1 | 13 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/sfarmhousemill` | 1 | 11 | 2 | 2 | 2 | 2 | 1 | 1 |
| `other:meshes/dlc01/effects` | 1 | 11 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/idleplayidlereset` | 1 | 11 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/firefly` | 1 | 11 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/uniquebehaviors/forge` | 1 | 11 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/ms06potemaeffects` | 1 | 11 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonmound` | 2 | 10 | 2 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/animbehaviors/doors` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/civilwar` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/common` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/daedric` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/nightingale` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/smelter` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/dlc02/attachobjects` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/dlc02/furniture` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/effects/sovngardeportalseal` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/choosefrom3` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/chooserandomanim3` | 1 | 9 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/genericbehaviors/waitplayidleaway` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/markers/commenttrigger` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/markers/commenttrigger02` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/beartrap` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/doordeadbolt` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/doordeadboltdbl` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/falmerclaw180` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/falmerclaw270` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/falmerclaw90` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/largetrap` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/largetrap02` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/largetrap02180` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/largetrap0290` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/largetrap180` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/largetrap90` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/leantotrap` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/magiccaster` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/magiccaster02` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/oillamptrap02` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/pedestaltrap` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/pistontrap` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/pressureplate` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 2 |
| `other:meshes/traps/pressureplatedwe` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/pressureplatefire` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/pressureplatemetal` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/skypressureplate01` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/skypressureplate02` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/skypressureplate03` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/skypressureplate04` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/skypressureplate05` | 1 | 9 | 1 | 4 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/dragonunderskin` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/icewraithfx` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/moth` | 1 | 9 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/mothblended` | 1 | 9 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/architecture/farmhouse` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/architecture/solitude` | 1 | 7 | 1 | 3 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/beehive` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/powershrines` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/critters/fish` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/furniture/shackle` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/blendbetweenstatesvariable` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/idlerandomized` | 1 | 7 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/genericbehaviors/stagesnoloops` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/landscape/trees` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/batteringram` | 1 | 7 | 1 | 3 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/dwecollapsingbalcony` | 1 | 7 | 1 | 3 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/gargoyleheadtrap01` | 1 | 7 | 1 | 3 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/hingetrap` | 1 | 7 | 1 | 3 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/fxnocturnalbird` | 1 | 7 | 2 | 0 | 2 | 2 | 1 | 1 |
| `other:meshes/uniquebehaviors/mgfmagicfirepillarfx` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/sarcophagustopopen` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxmanfootsteps` | 1 | 7 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/blacksmith` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/dlc02/clutter` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 1 |
| `other:meshes/dlc02/effects` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/dlc02/traps` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/bonealarm01` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/bonealarm02` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/riggedrockfall` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 1 |
| `other:meshes/traps/spiketrap` | 1 | 5 | 1 | 2 | 1 | 1 | 1 | 3 |
| `other:meshes/uniquebehaviors/creaturecasting` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxdragonbreath` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxdragonlanding` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxdragontakeoff` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxmanbreath` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/tfxswordblood` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/trailerfx` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/trailerfx02` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/uniquebehaviors/trailerfx03` | 1 | 5 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/clutter/stockade` | 1 | 3 | 1 | 0 | 1 | 1 | 1 | 1 |
| `other:meshes/genericbehaviors/characters` | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| `other:meshes/critters` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/effects` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| `other:meshes/furniture` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/genericbehaviors` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 |
| `other:meshes/interface` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 |
| `other:meshes/magic` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 52 |
| `other:meshes/weapons/draugr` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/ebony` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/falmer` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/glass` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/iron` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/nightingale` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/orcish` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/steel` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |
| `other:meshes/weapons/wooden` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

Actor groups: 45, holding 121 graphs and 29,637 nodes; non-actor groups: 157, 307 graphs, 3,993 nodes.

## Not done / caveats

- §4b covers every animation; its per-clip model joins clips by name across all graphs, so a match may be with a same-named clip of another project. Trigger times are not compared.
- Node counts are per file: a graph referenced by several others is counted once, in its own file.
- `max_sm_depth` follows every reference, including from modifiers and transition data; it is a path maximum, not a runtime-reachable maximum.
- Variable types come from `hkbBehaviorGraphData.variableInfos[i].type`, aligned by index with `variableNames`; event flags (`eventInfos`) are read but not reported.
