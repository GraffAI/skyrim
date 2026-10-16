#!/usr/bin/env python3
"""Census of Skyrim SE Havok behavior data (hkpackfile XML, hk_2010.2.0-r1).

Reads hkxc XML output (tools/hkx/bulk_convert.sh) and the raw animationdata .txt files,
writes aggregate statistics only: class counts, per-graph shape, and the identifier
strings (class / variable / event / annotation names) that form the engine<->graph contract.

  python3 -I census.py [--xml DIR] [--anim-xml DIR] [--anim-sample-xml DIR] [--raw DIR] [--out DIR]

--anim-xml is every animations/*.hkx (bulk_convert.sh anim-all); when it is absent the
census falls back to the sample (bulk_convert.sh anim 200) for the full-set keys too.

Stdlib only. Run with -I (inputs are untrusted extracted data).
"""
import argparse
import collections
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

REF = re.compile(r"#\d+")
HOME = os.path.expanduser("~")


# ---------------------------------------------------------------- packfile model

class Obj:
    __slots__ = ("name", "cls", "el")

    def __init__(self, name, cls, el):
        self.name, self.cls, self.el = name, cls, el

    def param(self, pname):
        for p in self.el:
            if p.tag == "hkparam" and p.get("name") == pname:
                return p
        return None

    def text(self, pname):
        p = self.param(pname)
        return None if p is None else (p.text or "").strip()

    def strings(self, pname):
        p = self.param(pname)
        if p is None:
            return []
        return [(c.text or "") for c in p if c.tag == "hkcstring"]

    def structs(self, pname):
        p = self.param(pname)
        return [] if p is None else [c for c in p if c.tag == "hkobject"]

    def refs(self):
        """Every #NNNN reference anywhere in this object's params (incl. nested structs)."""
        out = []
        for e in self.el.iter():
            if e is self.el:
                continue
            if e.text and "#" in e.text:
                out.extend(REF.findall(e.text))
        return out


def struct_text(st, pname):
    for p in st:
        if p.tag == "hkparam" and p.get("name") == pname:
            return (p.text or "").strip()
    return None


def load(path):
    root = ET.parse(path).getroot()
    objs = {}
    for sec in root.iter("hksection"):
        for o in sec:
            if o.tag == "hkobject" and o.get("class"):
                objs[o.get("name")] = Obj(o.get("name"), o.get("class"), o)
    return root.get("toplevelobject"), objs


# ---------------------------------------------------------------- class roles

def role(cls):
    """What we count as a behavior-graph node. Generators, modifiers and state infos are
    nodes; transition effects, child wrappers, conditions, arrays and graph data are not."""
    if cls == "hkbStateMachineStateInfo":
        return "state"
    if cls == "hkbBehaviorGraph":
        return "graph"
    if cls.endswith("TransitionEffect"):
        return "transition"
    if cls.endswith("Generator") or cls == "hkbStateMachine":
        return "generator"
    if cls.endswith("Modifier") or cls == "hkbModifierList":
        return "modifier"
    return "data"


NODE_ROLES = ("generator", "modifier", "state")


# ---------------------------------------------------------------- path helpers

def group_of(rel):
    parts = rel.split("/")
    if len(parts) >= 3 and parts[0] == "meshes" and parts[1] == "actors":
        if parts[2] in ("ambient", "dlc01", "dlc02") and len(parts) >= 5:
            return "actors/" + parts[2] + "/" + parts[3]
        return "actors/" + parts[2]
    return "other:" + "/".join(parts[:3 if len(parts) > 3 else 2])


def category(roots, objs):
    if "hkbBehaviorGraph" in roots:
        return "behavior"
    if "hkbCharacterData" in roots:
        return "character"
    if "hkbProjectData" in roots:
        return "project"
    classes = {o.cls for o in objs.values()}
    if "hkaSkeleton" in classes:
        return "skeleton"
    if any(c.startswith("hka") and c.endswith("Animation") for c in classes):
        return "animation"
    return "other"


# ---------------------------------------------------------------- behavior graph analysis

def analyse_behavior(top, objs):
    rootc = objs.get(top)
    graph = None
    for o in objs.values():
        if o.cls == "hkbBehaviorGraph":
            graph = o
            break
    g = {"graph_name": graph.text("name") if graph else None}
    data = objs.get(graph.text("data")) if graph else None
    sdata = objs.get(data.text("stringData")) if data else None

    var_names = sdata.strings("variableNames") if sdata else []
    var_types = [struct_text(s, "type") for s in data.structs("variableInfos")] if data else []
    ev_names = sdata.strings("eventNames") if sdata else []
    ev_flags = [struct_text(s, "flags") for s in data.structs("eventInfos")] if data else []
    cp_names = sdata.strings("characterPropertyNames") if sdata else []
    cp_types = [struct_text(s, "type") for s in data.structs("characterPropertyInfos")] if data else []
    attr_names = sdata.strings("attributeNames") if sdata else []
    g["variables"] = [[n, var_types[i] if i < len(var_types) else None] for i, n in enumerate(var_names)]
    g["events"] = [[n, ev_flags[i] if i < len(ev_flags) else None] for i, n in enumerate(ev_names)]
    g["character_properties"] = [[n, cp_types[i] if i < len(cp_types) else None] for i, n in enumerate(cp_names)]
    g["attributes"] = attr_names

    # node counts (all instances in file)
    rc = collections.Counter(role(o.cls) for o in objs.values())
    g["generators"], g["modifiers"], g["states"] = rc["generator"], rc["modifier"], rc["state"]
    g["nodes"] = sum(rc[r] for r in NODE_ROLES)
    g["transition_effects"] = rc["transition"]
    g["objects"] = len(objs)
    g["clip_generators"] = sum(1 for o in objs.values() if o.cls == "hkbClipGenerator")
    anims = {o.text("animationName") for o in objs.values() if o.cls == "hkbClipGenerator"}
    g["unique_clip_animations"] = len(anims)
    g["state_machines"] = sum(1 for o in objs.values() if o.cls == "hkbStateMachine")
    g["behavior_references"] = sorted({(o.text("behaviorName") or "").replace("\\", "/")
                                       for o in objs.values() if o.cls == "hkbBehaviorReferenceGenerator"})

    # reachability + SM nesting depth from the root generator
    start = graph.text("rootGenerator") if graph else None
    reach = set()
    stack = [start] if start in objs else []
    while stack:
        n = stack.pop()
        if n in reach:
            continue
        reach.add(n)
        for r in objs[n].refs():
            if r in objs and r not in reach:
                stack.append(r)
    g["reachable_nodes"] = sum(1 for n in reach if role(objs[n].cls) in NODE_ROLES)

    memo, onpath = {}, set()
    cycles = [0]
    sys.setrecursionlimit(100000)

    def depth(n):
        if n in memo:
            return memo[n]
        if n in onpath:
            cycles[0] += 1
            return 0
        onpath.add(n)
        o = objs[n]
        best = 0
        for r in set(o.refs()):
            if r in objs:
                best = max(best, depth(r))
        onpath.discard(n)
        memo[n] = best + (1 if o.cls == "hkbStateMachine" else 0)
        return memo[n]

    g["max_sm_depth"] = depth(start) if start in objs else 0
    g["ref_cycles_seen"] = cycles[0]
    # compact adjacency for the cross-graph pass: name -> (is SM, refs, behaviorName or None)
    g["_adj"] = {n: (o.cls == "hkbStateMachine", sorted(set(r for r in o.refs() if r in objs)),
                     (o.text("behaviorName") or "").replace("\\", "/") if o.cls == "hkbBehaviorReferenceGenerator" else None)
                 for n, o in objs.items()}
    g["_root"] = start
    g["_clips"] = clip_triggers(objs, ev_names)
    g["_event_set"] = set(ev_names)
    return g


def clip_triggers(objs, ev_names):
    """[(clip name, animationName with '/' separators, [trigger event names])] for every
    hkbClipGenerator; a trigger's event id indexes the graph's eventNames."""
    out = []
    for n in sorted(objs):
        o = objs[n]
        if o.cls != "hkbClipGenerator":
            continue
        tr = objs.get(o.text("triggers"))
        names = []
        if tr is not None:
            for t in tr.structs("triggers"):
                ev = next((p for p in t if p.tag == "hkparam" and p.get("name") == "event"), None)
                st = next((c for c in ev if c.tag == "hkobject"), None) if ev is not None else None
                i = _num(struct_text(st, "id"), int) if st is not None else None
                names.append(ev_names[i] if i is not None and 0 <= i < len(ev_names) else f"#{i}")
        out.append((o.text("name") or "", (o.text("animationName") or "").replace("\\", "/"), names))
    return out


def resolve_annotation(text, events):
    """The event an annotation raises in a graph declaring `events`, under the model this
    census tests: the whole text if it is a declared event, else the text before the first
    '.' if that is declared (SoundPlay.X -> SoundPlay), else nothing."""
    if text in events:
        return text
    head = text.split(".", 1)[0]
    return head if head in events else None


def explain_txt_triggers(blocks, graphs, ann_by_path):
    """For each animationdatasinglefile clip block (name, triggers), look for a clip generator
    of the same name (any graph; names are not unique) whose triggers, plus its animation's
    annotations resolved against that graph's events, equal the block's triggers as a multiset."""
    by_name = collections.defaultdict(list)
    for key in sorted(graphs):
        g = graphs[key]
        proj = os.path.dirname(os.path.dirname(key))
        for name, anim, trig in g["_clips"]:
            path = os.path.normpath(proj + "/" + anim).lower() if anim else ""
            by_name[name].append((path, trig, g["_event_set"]))
    res = collections.Counter()
    dropped = collections.Counter()
    mism = collections.Counter()
    for name, trig in blocks:
        cands = by_name.get(name)
        if not cands:
            res["no_clip_generator_named"] += 1
            continue
        want = collections.Counter(trig)
        verdict = None
        best = None   # smallest multiset difference among candidates: (size, direction)
        for path, ct, evs in cands:
            anns = ann_by_path.get(path)
            if anns is None:
                verdict = verdict or "animation_not_found"
                continue
            got = collections.Counter(ct)
            got.update(r for r in (resolve_annotation(t, evs) for t in anns) if r)
            if want == got:
                verdict = "match_triggers_plus_resolved_annotations" if anns and got != collections.Counter(ct) else "match_triggers_only"
                dropped.update(t for t in anns if resolve_annotation(t, evs) is None)
                break
            verdict = "mismatch" if verdict in (None, "animation_not_found") else verdict
            extra, short = want - got, got - want
            d = (sum(extra.values()) + sum(short.values()),
                 "txt_lacks_some_predicted" if not extra else "txt_has_unpredicted" if not short else "both_ways")
            best = d if best is None or d < best else best
        res[verdict] += 1
        if verdict == "mismatch":
            mism[best[1]] += 1
    return {"clip_blocks": len(blocks), "verdicts": ranked(res), "mismatch_direction": ranked(mism),
            "annotations_dropped_in_matched_clips": sum(dropped.values()),
            "dropped_prefixes": dict(list(ranked(prefix_counter(dropped)).items())[:30])}


def cross_graph_depth(graphs):
    """Max SM nesting depth following hkbBehaviorReferenceGenerator into the referenced graph
    (resolved relative to the project dir: the parent of the graph's own directory)."""
    lower = {k.lower(): k for k in graphs}
    total, onstack, unresolved = {}, set(), set()

    def resolve(key, ref):
        base = os.path.dirname(os.path.dirname(key))
        return lower.get((base + "/" + ref).lower())

    def gdepth(key):
        if key in total:
            return total[key]
        if key in onstack:
            return 0
        onstack.add(key)
        g = graphs[key]
        adj, memo, path = g["_adj"], {}, set()

        def d(n):
            if n in memo:
                return memo[n]
            if n in path:
                return 0
            path.add(n)
            sm, refs, bref = adj[n]
            best = max((d(r) for r in refs), default=0)
            if bref:
                t = resolve(key, bref)
                if t:
                    best = max(best, gdepth(t))
                else:
                    unresolved.add((key, bref))
            path.discard(n)
            memo[n] = best + (1 if sm else 0)
            return memo[n]

        total[key] = d(g["_root"]) if g["_root"] in adj else 0
        onstack.discard(key)
        return total[key]

    for k in graphs:
        gdepth(k)
    return total, sorted(unresolved)


# ---------------------------------------------------------------- annotations

def annotations_in(objs):
    out = []
    for o in objs.values():
        if o.cls.startswith("hka") and o.cls.endswith("Animation"):
            for tr in o.structs("annotationTracks"):
                for p in tr:
                    if p.tag == "hkparam" and p.get("name") == "annotations":
                        for a in p:
                            if a.tag == "hkobject":
                                t = struct_text(a, "text")
                                if t:
                                    out.append(t)
    return out


def _num(v, conv=float):
    try:
        return conv(v)
    except (TypeError, ValueError):
        return None


def _numelements(o, pname):
    p = o.param(pname)
    return None if p is None else int(p.get("numelements") or 0)


def animation_info(objs):
    """Per hka*Animation object in a packfile: the class and its `type` enum, duration (s),
    numFrames (spline-compressed only; others: None), transform/float track counts, the number
    of annotation tracks and their (time, text) annotations, plus the binding that points at
    it (blendHint, transformTrackToBoneIndices length, originalSkeletonName)."""
    bind = {}
    for o in objs.values():
        if o.cls == "hkaAnimationBinding":
            bind[o.text("animation")] = o
    out = []
    for n in sorted(objs):
        o = objs[n]
        if not (o.cls.startswith("hka") and o.cls.endswith("Animation")):
            continue
        anns = []
        named = []
        for tr in o.structs("annotationTracks"):
            if struct_text(tr, "trackName"):
                named.append(struct_text(tr, "trackName"))
            for p in tr:
                if p.tag == "hkparam" and p.get("name") == "annotations":
                    for a in p:
                        if a.tag == "hkobject":
                            t = struct_text(a, "text")
                            if t:
                                anns.append((_num(struct_text(a, "time")), t))
        b = bind.get(n)
        out.append({
            "class": o.cls, "type": o.text("type"),
            "duration": _num(o.text("duration")),
            "num_frames": _num(o.text("numFrames"), int),
            "frame_duration": _num(o.text("frameDuration")),
            "num_blocks": _num(o.text("numBlocks"), int),
            "transform_tracks": _num(o.text("numberOfTransformTracks"), int),
            "float_tracks": _num(o.text("numberOfFloatTracks"), int),
            "annotation_tracks": _numelements(o, "annotationTracks") or 0,
            "named_annotation_tracks": named,   # the non-empty trackNames
            "annotations": anns,
            "extracted_motion": (o.text("extractedMotion") or "null") != "null",
            "blend_hint": b.text("blendHint") if b is not None else None,
            "track_to_bone_indices": _numelements(b, "transformTrackToBoneIndices") if b is not None else None,
            "skeleton": b.text("originalSkeletonName") if b is not None else None,
        })
    return out


def dist_stats(vals, nd=6):
    """min / p10 / p50 / p90 / p99 / max / mean / total over non-None values (nearest rank)."""
    v = sorted(x for x in vals if x is not None)
    if not v:
        return {"n": 0}
    def q(f):
        return v[min(len(v) - 1, max(0, int(round(f * len(v) + 0.5)) - 1))]
    r = lambda x: round(x, nd) if isinstance(x, float) else x
    return {"n": len(v), "min": r(v[0]), "p10": r(q(0.10)), "p50": r(q(0.50)), "p90": r(q(0.90)),
            "p99": r(q(0.99)), "max": r(v[-1]), "mean": round(sum(v) / len(v), nd), "total": r(sum(v))}


def prefix_of(s):
    """Annotation prefix: up to and incl. the first '.', else the leading identifier."""
    s = s.strip()
    if "." in s:
        return s.split(".", 1)[0] + "."
    m = re.match(r"[A-Za-z0-9_]*?[A-Za-z_]+", s)  # leading identifier, trailing digits dropped
    return m.group(0) if m else s


def clip_blocks(lines):
    """One project's animationdata block: '1', N, N project-relative paths, a has-motion-data
    flag, then blank-separated blocks. A clip block is name, clip id, playback speed,
    cropStart, cropEnd, nTriggers, then nTriggers 'eventName:time' lines.
    Yields (clip name, [trigger names])."""
    n = int(lines[1])
    blocks, cur = [], []
    for l in lines[2 + n + 1:]:
        if l.strip() == "":
            if cur:
                blocks.append(cur)
            cur = []
        else:
            cur.append(l)
    if cur:
        blocks.append(cur)
    for b in blocks:
        if len(b) < 6 or re.fullmatch(r"-?\d+", b[0].strip()):
            continue
        try:
            nt = int(b[5])
        except ValueError:
            continue
        yield b[0], [t.rsplit(":", 1)[0] for t in b[6:6 + nt]]


def animationdata_triggers(raw):
    """Parse meshes/animationdatasinglefile.txt, the file the game reads: N, N project names,
    then per project: L, L lines of the project block, and when the block's flag is 1, M and
    M lines of motion data (skipped). The split files under meshes/animationdata/ are parsed
    too, as a cross-check only."""
    res = {"projects": 0, "projects_with_motion_data": 0, "clip_blocks": 0,
           "clips_with_triggers": 0, "parsed_to_eof": False,
           "triggers": collections.Counter(), "split_files": 0, "split_clip_blocks": 0, "blocks": []}
    sf = os.path.join(raw, "meshes", "animationdatasinglefile.txt")
    if os.path.isfile(sf):
        with open(sf, encoding="latin-1") as f:
            L = f.read().split("\n")
        L = [l.rstrip("\r") for l in L]
        n = int(L[0])
        i = 1 + n
        for _ in range(n):
            c = int(L[i])
            blk = L[i + 1:i + 1 + c]
            i += 1 + c
            k = int(blk[1])
            if blk[2 + k].strip() == "1":
                m = int(L[i])
                i += 1 + m
                res["projects_with_motion_data"] += 1
            res["projects"] += 1
            for name, trig in clip_blocks(blk):
                res["blocks"].append((name, trig))
                res["clip_blocks"] += 1
                if trig:
                    res["clips_with_triggers"] += 1
                res["triggers"].update(trig)
        res["parsed_to_eof"] = all(x == "" for x in L[i:])
    d = os.path.join(raw, "meshes", "animationdata")
    if os.path.isdir(d):
        for fn in sorted(os.listdir(d)):
            p = os.path.join(d, fn)
            if fn.endswith(".txt") and os.path.isfile(p):
                with open(p, encoding="latin-1") as f:
                    lines = [l.rstrip("\r\n") for l in f]
                try:
                    res["split_clip_blocks"] += sum(1 for _ in clip_blocks(lines))
                    res["split_files"] += 1
                except (IndexError, ValueError):
                    pass
    return res


# ---------------------------------------------------------------- animation set

def prefix_counter(counter):
    p = collections.Counter()
    for s, n in counter.items():
        p[prefix_of(s)] += n
    return p


def ranked(counter):
    return dict(sorted(counter.items(), key=lambda kv: (-kv[1], kv[0])))


def animation_set_stats(recs, triggers, source, path, manifest):
    """Aggregate animation_info() records [(relpath, [info...])] and compare the annotation
    strings with the animationdata trigger Counter."""
    anims = [x for _, infos in recs for x in infos]
    ann = collections.Counter(t for x in anims for _, t in x["annotations"])
    ann_files = collections.Counter()   # string -> files carrying it
    for _, infos in recs:
        ann_files.update({t for x in infos for _, t in x["annotations"]})
    hk, tx = set(ann), set(triggers)
    only_h, only_t = hk - tx, tx - hk
    low_t = {t.lower() for t in tx}
    low_h = {h.lower() for h in hk}

    def npc_strip(t):
        return t[3:] if t.startswith("NPC") else None
    only_t_npc = {t for t in only_t if npc_strip(t) in hk}
    only_t_case = {t for t in only_t - only_t_npc if t.lower() in low_h}
    only_h_case = {h for h in only_h if h.lower() in low_t}
    only_h_npc = {h for h in only_h - only_h_case if "NPC" + h in tx}
    per_file_n = [len(infos) for _, infos in recs]
    return {
        "source": source, "path": path,
        "conversion_manifest": dict(sorted(manifest.items())),
        "files": len(recs),
        "animations": len(anims),
        "files_per_animation_count": dict(sorted(collections.Counter(per_file_n).items())),
        "annotated_animations": sum(1 for x in anims if x["annotations"]),
        "files_with_annotations": sum(1 for _, infos in recs if any(x["annotations"] for x in infos)),
        "instances": sum(ann.values()), "unique": len(ann),
        "annotations_per_annotated_clip": dist_stats([len(x["annotations"]) for x in anims if x["annotations"]]),
        "annotation_tracks_equal_transform_tracks": sum(1 for x in anims if x["annotation_tracks"] == x["transform_tracks"]),
        "animations_with_named_annotation_tracks": sum(1 for x in anims if x["named_annotation_tracks"]),
        "named_annotation_track_names": ranked(collections.Counter(t for x in anims for t in x["named_annotation_tracks"])),
        "files_without_animation": [rel for rel, infos in recs if not infos],
        "strings": ranked(ann),
        "string_files": ranked(ann_files),
        "prefixes": ranked(prefix_counter(ann)),
        "vs_animationdata_txt": {
            "hkx_unique": len(hk), "txt_unique": len(tx), "both": len(hk & tx),
            "only_hkx": len(only_h), "only_txt": len(only_t),
            "only_hkx_strings": ranked({h: ann[h] for h in only_h}),
            "only_txt_strings": ranked({t: triggers[t] for t in only_t}),
            "only_hkx_prefixes": ranked(prefix_counter({h: ann[h] for h in only_h})),
            "only_txt_prefixes": ranked(prefix_counter({t: triggers[t] for t in only_t})),
            "only_txt_is_NPC_plus_hkx": len(only_t_npc),
            "only_txt_case_variant_of_hkx": len(only_t_case),
            "only_hkx_case_variant_of_txt": len(only_h_case),
            "only_hkx_with_NPC_form_in_txt": len(only_h_npc),
            "only_txt_instances": sum(triggers[t] for t in only_t),
            "only_hkx_instances": sum(ann[h] for h in only_h),
        },
        "class": ranked(collections.Counter(x["class"] for x in anims)),
        "compression_type": ranked(collections.Counter(x["type"] or "-" for x in anims)),
        "blend_hint": ranked(collections.Counter(x["blend_hint"] or "-" for x in anims)),
        "extracted_motion": sum(1 for x in anims if x["extracted_motion"]),
        "duration_s": dist_stats([x["duration"] for x in anims]),
        "num_frames": dist_stats([x["num_frames"] for x in anims]),
        "frame_duration_s": ranked(collections.Counter(
            "-" if x["frame_duration"] is None else f"{x['frame_duration']:.6f}" for x in anims)),
        "num_blocks": ranked(collections.Counter(str(x["num_blocks"]) for x in anims)),
        "transform_tracks": dist_stats([x["transform_tracks"] for x in anims]),
        "transform_tracks_top": dict(collections.Counter(x["transform_tracks"] for x in anims).most_common(15)),
        "float_tracks": dist_stats([x["float_tracks"] for x in anims]),
        "with_float_tracks": sum(1 for x in anims if x["float_tracks"]),
        "track_to_bone_indices_nonempty": sum(1 for x in anims if x["track_to_bone_indices"]),
        "track_to_bone_indices": dist_stats([x["track_to_bone_indices"] for x in anims if x["track_to_bone_indices"]]),
        "skeletons": ranked(collections.Counter(x["skeleton"] or "-" for x in anims)),
    }


# ---------------------------------------------------------------- main

def coverage(counter, fracs=(0.5, 0.9, 0.99, 1.0)):
    tot = sum(counter.values())
    out, acc, k = {}, 0, 0
    items = counter.most_common()
    for f in fracs:
        while k < len(items) and acc < f * tot - 1e-9:
            acc += items[k][1]
            k += 1
        out[str(f)] = k
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xml", default=os.path.join(HOME, "skyrim-data-extracted/xml"))
    ap.add_argument("--anim-xml", default=os.path.join(HOME, "skyrim-data-extracted/xml-anim"))
    ap.add_argument("--anim-sample-xml", default=os.path.join(HOME, "skyrim-data-extracted/xml-anim-sample"))
    ap.add_argument("--raw", default=os.path.join(HOME, "skyrim-data-extracted/raw"))
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../census"))
    a = ap.parse_args()

    files = []
    for dp, _, fns in os.walk(a.xml):
        for fn in fns:
            if fn.endswith(".xml"):
                files.append(os.path.relpath(os.path.join(dp, fn), a.xml))
    files.sort()

    cls_inst = collections.defaultdict(collections.Counter)   # category -> class -> instances
    cls_files = collections.defaultdict(collections.Counter)  # category -> class -> files
    cat_files = collections.Counter()
    graphs = {}
    characters = {}
    projects = {}
    skeletons = {}
    ann_bundled = collections.Counter()
    ann_bundled_clips = 0
    ann_by_path = {}   # lower-case raw .hkx path -> annotation texts (for the per-clip join)
    failures = []

    for rel in files:
        try:
            top, objs = load(os.path.join(a.xml, rel))
        except ET.ParseError as e:
            failures.append([rel, str(e)])
            continue
        rootc = objs.get(top)
        roots = []
        if rootc is not None:
            roots = [struct_text(s, "className") for s in rootc.structs("namedVariants")]
        cat = category(roots, objs)
        cat_files[cat] += 1
        seen = collections.Counter(o.cls for o in objs.values())
        cls_inst[cat].update(seen)
        cls_files[cat].update(seen.keys())
        key = rel[:-4] + ".hkx"
        if cat == "behavior":
            g = analyse_behavior(top, objs)
            g["group"] = group_of(rel)
            graphs[key] = g
        elif cat == "character":
            sd = next((o for o in objs.values() if o.cls == "hkbCharacterStringData"), None)
            if sd:
                characters[key] = {
                    "group": group_of(rel),
                    "character_properties": sd.strings("characterPropertyNames"),
                    "animation_names": len(sd.strings("animationNames")),
                    "behavior_filename": (sd.text("behaviorFilename") or "").replace("\\", "/"),
                    "rig": (sd.text("rigName") or "").replace("\\", "/"),
                    "ragdoll": (sd.text("ragdollName") or "").replace("\\", "/"),
                }
        elif cat == "project":
            sd = next((o for o in objs.values() if o.cls == "hkbProjectStringData"), None)
            if sd:
                projects[key] = {
                    "group": group_of(rel),
                    "characters": len(sd.strings("characterFilenames")),
                    "behaviors": len(sd.strings("behaviorFilenames")),
                    "animations": len(sd.strings("animationFilenames")),
                }
        elif cat == "skeleton":
            sk = [o for o in objs.values() if o.cls == "hkaSkeleton"]
            skeletons[key] = [{"name": s.text("name"),
                               "bones": int((s.param("bones").get("numelements") or 0)) if s.param("bones") is not None else 0}
                              for s in sk]
        if cat == "animation":
            anns = annotations_in(objs)
            ann_bundled.update(anns)
            ann_by_path[key.lower()] = anns
            ann_bundled_clips += 1

    # sampled animations (animations/ dirs)
    ann_sample = collections.Counter()
    sample_files = 0
    sample_with = 0
    if os.path.isdir(a.anim_sample_xml):
        for dp, _, fns in os.walk(a.anim_sample_xml):
            for fn in fns:
                if not fn.endswith(".xml"):
                    continue
                try:
                    _, objs = load(os.path.join(dp, fn))
                except ET.ParseError as e:
                    failures.append([os.path.join(dp, fn), str(e)])
                    continue
                sample_files += 1
                anns = annotations_in(objs)
                if anns:
                    sample_with += 1
                ann_sample.update(anns)

    # every animation under animations/ dirs (falls back to the sample when the full set is absent)
    full_dir = a.anim_xml if os.path.isdir(a.anim_xml) else a.anim_sample_xml
    full_source = "full" if full_dir == a.anim_xml else "sample"
    full_manifest = collections.Counter()
    mf = os.path.join(full_dir, "_manifest.tsv")
    if os.path.isfile(mf):
        with open(mf) as f:
            full_manifest.update(l.split("\t", 1)[0] for l in f if l.strip())
    anim_files = []
    for dp, _, fns in os.walk(full_dir):
        for fn in fns:
            if fn.endswith(".xml"):
                anim_files.append(os.path.relpath(os.path.join(dp, fn), full_dir))
    anim_files.sort()
    anim_recs = []
    for rel in anim_files:
        try:
            _, objs = load(os.path.join(full_dir, rel))
        except ET.ParseError as e:
            failures.append([os.path.join(full_dir, rel), str(e)])
            continue
        infos = animation_info(objs)
        anim_recs.append((rel, infos))
        ann_by_path[(rel[:-4] + ".hkx").lower()] = [t for x in infos for _, t in x["annotations"]]

    adata = animationdata_triggers(a.raw)
    full = animation_set_stats(anim_recs, adata["triggers"], full_source, full_dir, full_manifest)
    full["vs_animationdata_txt"]["txt_strings_declared_as_graph_events"] = sum(
        1 for t in adata["triggers"] if any(t in g["_event_set"] for g in graphs.values()))
    full["per_clip_model"] = explain_txt_triggers(adata["blocks"], graphs, ann_by_path)

    # ---- aggregates
    beh_nodes = collections.Counter({c: n for c, n in cls_inst["behavior"].items() if role(c) in NODE_ROLES})
    var_decl = collections.defaultdict(lambda: {"graphs": 0, "types": collections.Counter()})
    ev_decl = collections.Counter()
    cp_decl = collections.Counter()
    for g in graphs.values():
        for n, t in g["variables"]:
            var_decl[n]["graphs"] += 1
            var_decl[n]["types"][t] += 1
        for n in {e[0] for e in g["events"]}:
            ev_decl[n] += 1
        for n in {c[0] for c in g["character_properties"]}:
            cp_decl[n] += 1
    char_cp = collections.Counter()
    for c in characters.values():
        char_cp.update(set(c["character_properties"]))

    edges = sorted({(k, r) for k, g in graphs.items() for r in g["behavior_references"]})
    xdepth, unresolved = cross_graph_depth(graphs)
    for k, g in graphs.items():
        g["max_sm_depth_through_references"] = xdepth[k]
        del g["_adj"], g["_root"], g["_clips"], g["_event_set"]
    groups = collections.defaultdict(lambda: collections.Counter())
    for g in graphs.values():
        gg = groups[g["group"]]
        gg["graphs"] += 1
        gg["nodes"] += g["nodes"]
        gg["clips"] += g["clip_generators"]
        gg["state_machines"] += g["state_machines"]
        gg["max_sm_depth"] = max(gg["max_sm_depth"], g["max_sm_depth"])
        gg["max_sm_depth_through_references"] = max(gg["max_sm_depth_through_references"], g["max_sm_depth_through_references"])
    for c in characters.values():
        groups[c["group"]]["characters"] += 1
    for p in projects.values():
        groups[p["group"]]["projects"] += 1


    def cls_table(cat):
        return [{"class": c, "role": role(c), "instances": n, "files": cls_files[cat][c]}
                for c, n in sorted(cls_inst[cat].items(), key=lambda kv: (-kv[1], kv[0]))]

    def prefixes(counter):
        p = collections.Counter()
        for s, n in counter.items():
            p[prefix_of(s)] += n
        return p

    census = {
        "inputs": {"xml": a.xml, "anim_xml": a.anim_xml, "anim_sample_xml": a.anim_sample_xml, "raw": a.raw},
        "node_definition": "node = object whose class role is generator (class ends in 'Generator', "
                           "or hkbStateMachine), modifier (ends in 'Modifier', or hkbModifierList), "
                           "or state (hkbStateMachineStateInfo). hkbBehaviorGraph, transition effects, "
                           "child wrappers, conditions, arrays and graph data are not nodes.",
        "files_by_category": dict(cat_files),
        "parse_failures": failures,
        "classes": {cat: cls_table(cat) for cat in sorted(cls_inst)},
        "behavior_node_class_coverage": {"node_instances": sum(beh_nodes.values()),
                                         "node_classes": len(beh_nodes),
                                         "classes_to_cover": coverage(beh_nodes)},
        "behavior_all_class_coverage": {"instances": sum(cls_inst["behavior"].values()),
                                        "classes": len(cls_inst["behavior"]),
                                        "classes_to_cover": coverage(cls_inst["behavior"])},
        "graphs": {k: {kk: vv for kk, vv in g.items() if kk not in ("variables", "events", "character_properties", "attributes")}
                   | {"variables": len(g["variables"]), "events": len(g["events"]),
                      "character_properties": len(g["character_properties"]), "attributes": len(g["attributes"])}
                   for k, g in sorted(graphs.items())},
        "behavior_reference_edges": [list(e) for e in edges],
        "behavior_references_unresolved": [list(e) for e in unresolved],
        "variables": {n: {"graphs": v["graphs"], "types": dict(sorted(v["types"].items(), key=lambda kv: (-kv[1], str(kv[0]))))}
                      for n, v in sorted(var_decl.items(), key=lambda kv: (-kv[1]["graphs"], kv[0].lower(), kv[0]))},
        "events": dict(sorted(ev_decl.items(), key=lambda kv: (-kv[1], kv[0].lower(), kv[0]))),
        "graph_character_properties": ranked(cp_decl),
        "character_files": {"count": len(characters),
                            "character_property_names": ranked(char_cp),
                            "animation_names_total": sum(c["animation_names"] for c in characters.values())},
        "project_files": {"count": len(projects),
                          "with_behaviors": sum(1 for p in projects.values() if p["behaviors"]),
                          "characters_listed": sum(p["characters"] for p in projects.values())},
        "skeletons": skeletons,
        "per_group": {k: dict(v) for k, v in sorted(groups.items(), key=lambda kv: -kv[1]["nodes"])},
        "annotations": {
            "animationdata_txt": {k: v for k, v in adata.items() if k not in ("triggers", "blocks")} | {
                                  "trigger_instances": sum(adata["triggers"].values()),
                                  "unique": len(adata["triggers"]),
                                  "strings": ranked(adata["triggers"]),
                                  "prefixes": ranked(prefixes(adata["triggers"]))},
            "hkx_sample": {"files": sample_files, "files_with_annotations": sample_with,
                           "instances": sum(ann_sample.values()), "unique": len(ann_sample),
                           "strings": ranked(ann_sample),
                           "prefixes": ranked(prefixes(ann_sample))},
            "hkx_animations": full,
            "hkx_outside_animations_dirs": {"files": ann_bundled_clips,
                                            "instances": sum(ann_bundled.values()), "unique": len(ann_bundled),
                                            "strings": ranked(ann_bundled),
                                            "prefixes": ranked(prefixes(ann_bundled))},
        },
    }
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "census.json"), "w") as f:
        json.dump(census, f, indent=1, sort_keys=False)
    print(json.dumps({"files_by_category": dict(cat_files), "graphs": len(graphs),
                      "failures": len(failures), "sample_anims": sample_files,
                      "anims": full["files"], "anim_source": full_source}))


if __name__ == "__main__":
    main()
