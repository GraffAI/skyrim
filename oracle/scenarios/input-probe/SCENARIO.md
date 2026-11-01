# input-probe — does scripted input reach the player? (006 M44 Part 1.5, §7 step 0)

Run with no human: `devx oracle run projects/skyrim/oracle/scenarios/input-probe --out
~/skyrim-data-extracted/traces/<date>-input-probe --timeout 10`. The oracle plugin loads the
operator's `loco1hm` save, forces the third-person camera, waits until the load has finished plus
60 input polls (frame 0, D393), plays `input.jsonl`, closes its trace at `end` (frame 800) and quits the game
(D395). `run.cmd` sets `bAlwaysActive=1` first (D396). Nothing is saved; the save's sha256 is taken
before and after.

The script (written by `../make-input.py`; frames are input polls, about 60 a second):

| frames | input | question it answers |
|---|---|---|
| 0–59 | nothing | the standing baseline |
| 60–119 | left stick (0, 0.5) every frame, a zero at 120 | are gamepad stick events used with no gamepad connected? at half deflection, does the player walk? |
| 180–239 | left stick (0, 1.0), a zero at 240 | full deflection: a second, faster plateau? |
| 300–359 | the keyboard's `Forward` held (a down, held events, an up at 360) | the digital fallback D389 names |
| 420–479 | the heading written each frame, 0 → π/2, standing | does a written heading turn the player, and does the graph see a turn? |
| 480–539 | the same, π/2 → π, with the stick at (0, 0.5) | and while walking |
| 620–679 | the right stick (0.5, 0) every frame, standing | what real look input does, to compare with the written heading |
| 700–759 | the same, with the left stick at (0, 0.5) | and while walking |
| 800 | `end` | |

What to read in `--out`: `oracle.log` (`input hook installed (prologue ok)`, the poll's first ten
bytes, `clock: frame 0 …`, `input dropped` should not appear), `oracle.input.jsonl` (one `in.input`
line per injected event and a `ctl` line per frame: the player's movement and look vectors as the
controls saw them, position, heading, and three graph variables read as a cross-check), the trace
`oracle.jsonl` (events in and out of the behaviour graph), `oracle.status`, `game-exit.txt`, and
`done`. The side file holds engine-structure fields; it is not the trace and does not leave the
traces directory.

## Measured (2026-11-01, three runs; the plugin repository's NOTES §17 has the log lines)

1. **Stick events with no gamepad connected are used**: the controls' movement vector equals what
   was sent from the first frame; the player walked 100.5 units in 60 frames at (0, 0.5) and
   ~265 at (0, 1.0). The keyboard's `Forward` works too.
2. **The queue's stick, button and mouse layouts hold on 1.7.104**: no crash, values arrive.
3. **A written heading turns the player but the graph sees no turn** (`TurnDelta` 0, no turn
   event); real look input while walking gives `TurnDelta` and the engine's own `TurnRight` /
   `turnRightSlow`. So the scripted scenario turns by look input (D391's flip). The right stick
   turns only ~2.7°/s with no gamepad, so it uses mouse-move input.
4. Both ways of quitting end the game with exit code 0 within 1.6 s; `qqq` is kept.
