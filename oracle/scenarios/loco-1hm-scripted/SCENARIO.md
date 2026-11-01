# loco-1hm-scripted — record 006 M44 §3's scenario, with no human (Part 1.5)

The `loco-1hm` scenario of the record's §3, played from `input.jsonl` instead of by the operator:
`devx oracle run projects/skyrim/oracle/scenarios/loco-1hm-scripted --out
~/skyrim-data-extracted/traces/<date>-loco-1hm-scripted --timeout 10`. Start state: the operator's
`loco1hm` save (a flat empty interior, a one-handed sword equipped and sheathed; record §8), the
camera forced to third person. `look` targets are camera yaws relative to frame 0, reached by
mouse-move input sized from the remaining angle (`look_via = "mouse"`), not written: the probe showed that a written heading turns
the player without the turn the behaviour graph sees from real look input (D391's flip). The
room (`qasmoke`) has a pool west of the start and walls 1,100–1,200 units north and 250 east;
the route keeps to the measured open floor, and the sprint may end against the north wall. Frame 0 is 60 input polls after the load has finished (D393); a
frame is one input poll, about 1/60 s.

| frames | seconds | what the player does | input |
|---|---|---|---|
| 0–179 | 0–3 | stands; the heading is set to 0 at frame 0 | `look` yaw 0 |
| 180–299, 360–479, 540–659, 720–839 | 2 each | walks forward, back, left, right, standing 1 s after each | left stick at half deflection |
| 900–1019 | 2 | runs north, the room's long open way | left stick full forward |
| 1020–1139, 1140–1259 | 2 + 2 | keeps running, turning 360° one way, then 360° back | a target yaw each frame, 3° a frame (`look`) |
| 1260–1499 | 4 | stops, looks round 180°, runs back south 100 frames, stops, looks round again | `look` while standing turns only the camera; the player turns to it as the run starts |
| 1500–1739 | 4 | runs north; sprints 1530–1709 (3 s); stops at 1740 | stick full forward, `Sprint` held |
| 1800 | | draws the sword | `Ready Weapon`, pressed 6 frames |
| 1920 | | one right light attack from standing | `Right Attack/Block`, pressed 6 frames |
| 2100 | | sheathes | `Ready Weapon` again (it toggles) |
| 2106–2399 | ~5 | stands | nothing |
| 2400 | | the trace closes and the game quits | `end` |

The exit (record §7 step 0): the trace shows `attackStart` going into the graph and `weaponSwing`,
`HitFrame`, `AttackWinStart`, `AttackWinEnd` coming out, in that order; the side file shows every
scripted event injected and no drop; `done` is 0 (or 124, said so); a second run gives the same
out-event sequence from `attackStart` to `attackStop`.

## Measured (2026-11-01, two runs; the plugin repository's NOTES §20)

Both runs: `done` 0, the game's exit code 0 about 1.4 s after the trace closed; every one of the
380 input lines injected at its frame, none dropped; the attack's out-events from `attackStart`
to `attackStop` the same in both: `PowerAttack_Start_end HeadTrackingOff preHitFrame weaponSwing
HitFrame CastOKStart AttackWinStart AttackWinEnd attackStop`. Movement-vector plateaus (0, ±0.5)
and (±0.5, 0) for walking, (0, 1) for running and sprinting; the graph's `Speed`, read in the side
file as a cross-check, 116.78 walking, 343.46 running, 500 sprinting (as an `in.var` it is Part 3).
