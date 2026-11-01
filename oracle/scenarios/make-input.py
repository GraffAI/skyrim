#!/usr/bin/env python3
"""Writes the input scripts of the oracle's scripted scenarios (006 M44 Part 1.5).

    python3 -I oracle/scenarios/make-input.py           # rewrite <scenario>/input.jsonl for each
    python3 -I oracle/scenarios/make-input.py --check   # exit 1 if a file differs from what it would write

The format is ORACLE.md 5.1 with record 006 M44 section 4.1's clarifications: one JSON object per
line, keyed by frame `f` (input polls counted from frame 0, which is `settle` polls after the
load has finished), `k` one of setup, stick, look, button, console, end. `button` ids are the
game's control-map names; `hold` is the number of frames the button stays pressed (a down, then
held frames, then the release `hold` frames after the down). `look` is the player's absolute
heading (`yaw`) and pitch, in radians, written once per line: a turn is a line per frame. A
`stick` stays at its value until the next `stick` line. Lines are written sorted by frame.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TAU = 2 * math.pi


def line(f, k, **kw):
    return {"f": f, "k": k, **kw}


def turn(f0, frames, yaw0, yaw1):
    """A look line per frame from yaw0 to yaw1 (radians, end inclusive), wrapped to [0, 2*pi)."""
    out = []
    for i in range(1, frames + 1):
        y = yaw0 + (yaw1 - yaw0) * i / frames
        out.append(line(f0 + i - 1, "look", yaw=round(y % TAU, 6), pitch=0.0))
    return out


def stick(f, x, y):
    """The left stick ("move"); a "look" stick line is the right stick."""
    return line(f, "stick", id="move", x=x, y=y)


def input_probe():
    """Section 7 step 0: answers three questions with 60 frames each, standing in between."""
    s = [line(0, "setup", settle=60)]
    s += [stick(60, 0.0, 0.5), stick(120, 0.0, 0.0)]  # left stick half forward
    s += [stick(180, 0.0, 1.0), stick(240, 0.0, 0.0)]  # left stick full forward
    s += [line(300, "button", id="Forward", v=1.0), line(360, "button", id="Forward", v=0.0)]  # the keyboard's Forward
    s += turn(420, 60, 0.0, math.pi / 2)  # a written heading, standing: a quarter turn in 1 s
    s += [stick(480, 0.0, 0.5)] + turn(480, 60, math.pi / 2, math.pi) + [stick(540, 0.0, 0.0)]  # and walking
    # the alternative D391 names: the right stick (real look input), standing, then walking
    s += [line(620, "stick", id="look", x=0.5, y=0.0), line(680, "stick", id="look", x=0.0, y=0.0)]
    s += [stick(700, 0.0, 0.5), line(700, "stick", id="look", x=0.5, y=0.0), line(760, "stick", id="look", x=0.0, y=0.0), stick(760, 0.0, 0.0)]
    s += [line(800, "end")]
    return s


def loco_1hm_scripted():
    """Record 006 M44 section 3's human script, as input (frames at about 60 per second)."""
    s = [line(0, "setup", settle=60), line(0, "look", yaw=0.0, pitch=0.0)]
    # stand 3 s (0-179); walk forward, back, left, right at half stick, 2 s each with 1 s standing after
    for i, (x, y) in enumerate([(0.0, 0.5), (0.0, -0.5), (-0.5, 0.0), (0.5, 0.0)]):
        f = 180 + i * 180
        s += [stick(f, x, y), stick(f + 120, 0.0, 0.0)]
    # run (900) north, the room's long open way, 2 s; then turn 360 degrees one way in 2 s and 360 back
    # in 2 s while running (3 degrees a frame: circles about 220 units across, clear of the pool and
    # the walls the first try found, NOTES/SCENARIO)
    s += [stick(900, 0.0, 1.0)]
    s += turn(1020, 120, 0.0, TAU)
    s += turn(1140, 120, TAU, 0.0)
    # stop (1260); look round 180 degrees standing (the camera turns, the player does not); run back
    # south 100 frames (the player turns to the camera as it starts); stop (1420); look round again
    s += [stick(1260, 0.0, 0.0)] + turn(1260, 60, 0.0, math.pi)
    s += [stick(1320, 0.0, 1.0), stick(1420, 0.0, 0.0)] + turn(1420, 60, math.pi, TAU)
    # sprint 3 s north: run (1500), Sprint held 1530-1709, stop (1740)
    s += [stick(1500, 0.0, 1.0), line(1530, "button", id="Sprint", v=1.0), line(1710, "button", id="Sprint", v=0.0), stick(1740, 0.0, 0.0)]
    # draw the sword, one right light attack from standing (pressed 6 frames), sheathe; stand 3 s; end
    s += [line(1800, "button", id="Ready Weapon", v=1.0, hold=6)]
    s += [line(1920, "button", id="Right Attack/Block", v=1.0, hold=6)]
    s += [line(2100, "button", id="Ready Weapon", v=1.0, hold=6)]
    s += [line(2400, "end")]
    return s


SCRIPTS = {"input-probe": input_probe, "loco-1hm-scripted": loco_1hm_scripted}


def render(lines):
    lines = sorted(lines, key=lambda r: r["f"])  # stable: same-frame lines keep their order
    return "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in lines)


def main(argv):
    check = argv == ["--check"]
    if argv not in ([], ["--check"]):
        print(__doc__, file=sys.stderr)
        return 2
    bad = 0
    for name, fn in SCRIPTS.items():
        path = os.path.join(HERE, name, "input.jsonl")
        text = render(fn())
        if check:
            try:
                with open(path, encoding="utf-8") as f:
                    same = f.read() == text
            except FileNotFoundError:
                same = False
            if not same:
                print(f"{path}: differs from make-input.py's output")
                bad += 1
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"{path}: {text.count(chr(10))} lines")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
