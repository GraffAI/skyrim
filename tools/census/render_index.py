#!/usr/bin/env python3
"""Render projects/skyrim/semantics/INDEX.md: one row per class in census.json.

Numeric columns (instances, files, per category) come from census/census.json. The
covering note and its confidence are found by scanning semantics/*.md for a heading that
names the class and taking the first "Confidence:" phrase in that section. Physics/engine
coupling is the hand-kept table COUPLING below, filled from the notes' own text.

  python3 -I projects/skyrim/tools/census/render_index.py
"""
import json
import os
import re

ZONE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEM = os.path.join(ZONE, "semantics")
# order = tie-break when two notes have an entry headed by the class
NOTES = ["generators.md", "modifiers.md", "graph-core.md"]
SKEL = "skeleton-physics.md"
CAT_ORDER = ["behavior", "character", "project", "skeleton", "animation", "other"]

# yes = needs something outside the graph interpreter (physics world, raycasts, ragdoll,
# engine-supplied targets or actor pairing, NIF controllers, world transform). The reason
# is shown in the table. Classes absent here are "no".
COUPLING = {
    "hkbPoweredRagdollControlsModifier": "physics: ragdoll motors",
    "hkbRigidBodyRagdollControlsModifier": "physics: rigid-body ragdoll",
    "hkbKeyframeBonesModifier": "physics: keyframed ragdoll bones",
    "hkbGetUpModifier": "physics: reads ragdoll pose",
    "BSRagdollContactListenerModifier": "physics: contact callbacks",
    "hkbFootIkControlsModifier": "physics: foot-IK raycasts",
    "hkbFootIkModifier": "physics: raycasts",
    "BSLimbIKModifier": "physics: raycasts (per note)",
    "hkbFootIkDriverInfo": "physics: foot-IK driver setup",
    "BSLookAtModifier": "engine: target/camera inputs",
    "BSDirectAtModifier": "engine: aim target/camera inputs",
    "BSSpeedSamplerModifier": "engine: clip speed data",
    "BSTweenerModifier": "engine: world transform tween",
    "BSPassByTargetTriggerModifier": "engine: target interface",
    "hkbRotateCharacterModifier": "engine: character world transform",
    "BSSynchronizedClipGenerator": "engine: pairs two actors",
    "BGSGamebryoSequenceGenerator": "engine: NIF controller sequence",
    "hkbCharacterData": "engine: character controller and property data",
    "hkaRagdollInstance": "physics: ragdoll skeleton and bodies",
    "hkaSkeletonMapper": "physics: maps animation skeleton to ragdoll",
}


def sections(text):
    """[(heading, body)] for every markdown heading."""
    out, cur, buf = [], None, []
    for line in text.split("\n"):
        if line.startswith("#"):
            if cur is not None:
                out.append((cur, "\n".join(buf)))
            cur, buf = line, []
        else:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf)))
    return out


CONF = re.compile(r"Confidence:\s*(.*?)(?:\.\s|\.$|\s\[|$)")


def conf_of(body):
    m = CONF.search(re.sub(r"\s+", " ", body))
    if not m:
        return "not stated"
    c = m.group(1).replace("**", "").strip()
    return c if len(c) <= 120 else c[:117].rstrip() + "..."


def name_re(cls):
    return r"(?<![A-Za-z0-9_])" + re.escape(cls) + r"(?![A-Za-z0-9_])"


def cover(cls, notes):
    """(primary note, confidence, [other notes]). Primary = an entry whose heading starts
    with the class; else any heading naming it."""
    first, other = [], []
    for fn, secs in notes.items():
        for h, body in secs:
            if re.match(r"#+\s*" + name_re(cls), h):
                first.append((fn, body))
            elif re.search(name_re(cls), h):
                other.append((fn, body))
    hits = first + other
    if not hits:
        return None, None, []
    fn, body = hits[0]
    rest = sorted({f for f, _ in hits if f != fn})
    return fn, conf_of(body), rest


def main():
    census = json.load(open(os.path.join(ZONE, "census", "census.json")))
    notes = {fn: sections(open(os.path.join(SEM, fn)).read()) for fn in NOTES}
    rows = {}
    for cat in CAT_ORDER:
        for c in census["classes"].get(cat, []):
            r = rows.setdefault(c["class"], {"role": c["role"], "per": []})
            r["per"].append((cat, c["instances"], c["files"]))
    out = []
    for cls, r in rows.items():
        cats = [p[0] for p in r["per"]]
        inst = sum(p[1] for p in r["per"])
        files = sum(p[2] for p in r["per"])
        split = "" if len(r["per"]) == 1 else " (" + ", ".join(
            f"{c} {i}/{f}" for c, i, f in r["per"]) + ")"
        fn, conf, also = cover(cls, notes)
        skel = cls.startswith(("hka", "hkp", "hkMemoryResource"))
        if skel:
            fn, conf, also = SKEL, "see that note", []
        if fn is None:
            fn, conf, also = "**none**", "-", []
        coup = COUPLING.get(cls)
        if coup is None and cls.startswith("hkp"):
            coup = "physics: Havok Physics object"
        if also:
            fn = fn + "|" + ",".join(also)
        out.append((cats, -inst, cls, r["role"], inst, files, split, fn, conf,
                    ("yes — " + coup) if coup else "no"))
    out.sort(key=lambda t: (CAT_ORDER.index(t[0][0]), t[1], t[2]))
    lines = [
        "> DIRTY-SIDE: derived from community reverse-engineering (Nemesis, Pandora, HKX2Library, CommonLibSSE). Not for the clean implementation.",
        "",
        "# Semantics index: every class the vanilla census found",
        "",
        "One row per class in `census/census.json` (`classes`, all categories), vanilla Skyrim SE",
        "1.7.104: 428 behavior, 353 character, 457 project, 328 skeleton, 191 sampled animation and",
        "6 other files. **Generated** by `tools/census/render_index.py`; do not edit by hand, rerun it.",
        "",
        "- **instances / files**: summed over the categories the class appears in; the split is",
        "  given as `category instances/files` when there is more than one. A class's `files` is the",
        "  number of files of that category holding at least one instance (census definition).",
        "  The animation category is a 191-file sample, not the whole corpus.",
        "- **role**: the census's `role()` (generator, modifier, state, transition, graph, data).",
        "- **note**: the semantics file whose heading names the class. `hka*`, `hkp*` and",
        "  `hkMemoryResource*` classes are covered by `skeleton-physics.md` (written separately).",
        "- **confidence**: the first `Confidence:` phrase in that entry, verbatim; `not stated` when",
        "  the entry has none. When two notes head an entry with the class, the primary is",
        "  generators, then modifiers, then graph-core; the other is listed as \"also\".",
        "- **coupling**: yes when the class needs something outside a pure graph interpreter",
        "  (physics world, raycasts, ragdoll, engine-supplied targets, actor pairing, NIF controller",
        "  sequences, world transform), per the notes; the reason follows.",
        "",
        "Structs that are not class-bearing objects in the packfile (`hkbStateMachineTransitionInfo`,",
        "`hkbClipTrigger`, `hkbVariableInfo`, `hkbEventInfo`, binding entries, …) are not census",
        "classes and have no row; they are covered inside their owners' entries.",
        "",
        "| class | category | role | instances | files | note | confidence | physics / engine coupling |",
        "|---|---|---|---:|---:|---|---|---|",
    ]
    for cats, _, cls, role, inst, files, split, fn, conf, coup in out:
        if fn.startswith("**"):
            note = fn
        else:
            main_fn, _, also = fn.partition("|")
            note = f"[{main_fn}]({main_fn})" + ("".join(f" (also [{a}]({a}))" for a in also.split(",")) if also else "")
        lines.append(f"| `{cls}` | {', '.join(cats)}{split} | {role} | {inst} | {files} | {note} | {conf} | {coup} |")
    missing = [t[2] for t in out if t[7] == "**none**"]
    lines += ["", f"Rows: {len(out)}. Classes with no covering entry: {len(missing)}"
              + (" (" + ", ".join(f"`{m}`" for m in missing) + ")." if missing else "."), ""]
    open(os.path.join(SEM, "INDEX.md"), "w").write("\n".join(lines))
    print(len(out), "rows;", "missing:", missing)


if __name__ == "__main__":
    main()
