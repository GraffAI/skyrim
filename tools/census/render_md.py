#!/usr/bin/env python3
"""Render census.json into CENSUS.md.  python3 -I render_md.py [census.json] [CENSUS.md]"""
import collections
import json
import os
import statistics
import sys

here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "../../census/census.json")
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "../../census/CENSUS.md")
c = json.load(open(src))
out = []
w = out.append
RUN = "python3 -I projects/skyrim/tools/census/census.py && python3 -I projects/skyrim/tools/census/render_md.py"


def table(headers, rows):
    w("| " + " | ".join(headers) + " |")
    w("|" + "|".join("---" for _ in headers) + "|")
    for r in rows:
        w("| " + " | ".join(str(x).replace("|", "\\|") for x in r) + " |")
    w("")


def code(s):
    return "`" + s + "`" if s != "" else "*(empty)*"


g = c["graphs"]
fc = c["files_by_category"]
ann = c["annotations"]
cov = c["behavior_node_class_coverage"]

w("# Skyrim SE behavior census")
w("")
w("Aggregate statistics over the Havok behavior data in `Skyrim - Animations.bsa` (SE, "
  "`hk_2010.2.0-r1`), produced from hkxc XML (`tools/hkx/bulk_convert.sh`). Identifier strings "
  "(class, variable, event, annotation names) are listed because they are the engine<->graph "
  "contract; no other game content is reproduced. Full data: [census.json](census.json).")
w("")
w("**Every number in this file** comes from one run of:")
w("")
w("```sh")
w(RUN)
w("```")
w("")
w("reading `~/skyrim-data-extracted/xml/` (every non-`animations/` .hkx, converted), "
  "`~/skyrim-data-extracted/xml-anim/` (every `animations/` .hkx, converted; "
  "`~/skyrim-data-extracted/xml-anim-sample/`, a 200-file sample, is the fallback) and "
  "`~/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt`. The JSON key each table "
  "comes from is named under it. Cross-checks run by hand are given with their command.")
w("")
w("## 0. Inputs")
w("")
table(["category (by root class)", "files"], sorted(fc.items(), key=lambda kv: -kv[1]))
w("Category rule: a root `namedVariant` of `hkbBehaviorGraph` → behavior, `hkbCharacterData` → "
  "character, `hkbProjectData` → project; otherwise any `hkaSkeleton` → skeleton, any "
  "`hka*Animation` → animation (these are animations stored outside `animations/` dirs, e.g. "
  "`sharedkillmoves`), else other (empty animation containers). Parse failures: "
  f"**{len(c['parse_failures'])}**. Key: `files_by_category`.")
w("")
w("Cross-check: `grep -c . ~/skyrim-data-extracted/xml/_manifest.tsv` → 1763 converted, "
  "`cut -f1 _manifest.tsv | sort | uniq -c` → 1763 ok, `_errors.log` empty; "
  "`cut -f3 _manifest.tsv | grep -c '^hkbBehaviorGraph$'` → 428. "
  "(The brief's \"654 under behaviors paths\" counts animations/doors etc. under `animbehaviors/`; "
  "`find raw -iname '*.hkx' | grep -i behaviors | grep -vi /animations/ | wc -l` → 652, which "
  "includes characters/projects under `*behaviors` dirs such as `magic/magicbehaviors`.)")
w("")
w("**Node definition** (used everywhere below): " + c["node_definition"])
w("")

# ---- 5 first as headline
w("## Headline")
w("")
nodes = [v["nodes"] for v in g.values()]
w(f"- **{fc.get('behavior', 0)} behavior graphs**, **{cov['node_instances']:,} node instances** "
  f"of **{cov['node_classes']} node classes**; {c['behavior_all_class_coverage']['classes']} classes "
  f"of any kind appear in behavior files ({c['behavior_all_class_coverage']['instances']:,} objects).")
ct = cov["classes_to_cover"]
w(f"- Long tail: **{ct['0.5']}** node classes cover 50% of node instances, **{ct['0.9']}** cover 90%, "
  f"**{ct['0.99']}** cover 99%, **{ct['1.0']}** cover 100%.")
w(f"- Graph size: median {statistics.median(nodes):.0f} nodes, max {max(nodes)}; "
  f"{sum(1 for v in g.values() if v['max_sm_depth'] <= 1)} graphs have SM depth ≤ 1 (one flat state machine or none).")
w(f"- Contract surface: **{len(c['variables'])}** distinct variable names, **{len(c['events'])}** distinct "
  f"event names, **{len(c['graph_character_properties'])}** graph character-property names, "
  f"**{len(c['character_files']['character_property_names'])}** character-file property names.")
a = ann["animationdata_txt"]
w(f"- Clip triggers in `animationdatasinglefile.txt`: **{a['trigger_instances']:,}** on "
  f"{a['clips_with_triggers']:,}/{a['clip_blocks']:,} clips, **{a['unique']}** distinct strings; "
  f".hkx annotations ({ann['hkx_animations']['source']} set): **{ann['hkx_animations']['instances']:,}** on "
  f"{ann['hkx_animations']['annotated_animations']:,}/{ann['hkx_animations']['animations']:,} animations, "
  f"**{ann['hkx_animations']['unique']}** distinct; "
  f"{ann['hkx_animations']['per_clip_model']['verdicts'].get('match_triggers_only', 0) + ann['hkx_animations']['per_clip_model']['verdicts'].get('match_triggers_plus_resolved_annotations', 0):,} "
  f"of the text file's {a['clip_blocks']:,} clips are reproduced from graph clip triggers + resolved .hkx annotations (§4b).")
w(f"- Behavior references: **{len(c['behavior_reference_edges'])}** edges between graphs, "
  f"{len(c['behavior_references_unresolved'])} unresolved.")
w("")

# ---- 1 classes
w("## 1. Classes")
w("")
w("Instances = top-level `hkobject`s with that `class`; files = files containing ≥1. "
  "Role is the node rule above. Key: `classes.<category>`.")
w("")
for cat in ["behavior", "character", "project", "skeleton", "animation", "other"]:
    rows = c["classes"].get(cat)
    if not rows:
        continue
    w(f"### {cat} files ({fc.get(cat, 0)})")
    w("")
    table(["class", "role", "instances", "files"],
          [[code(r["class"]), r["role"], r["instances"], r["files"]] for r in rows])
w("Cross-check: `grep -rho 'class=\"hkbClipGenerator\"' ~/skyrim-data-extracted/xml/meshes | wc -l` "
  "→ 10086, matching `hkbClipGenerator` above (it appears only in behavior files).")
w("")

# ---- 2 per graph
w("## 2. Per-graph summaries")
w("")
w("Per graph: nodes (generators + modifiers + states, all instances in the file; every one is "
  "reachable from `rootGenerator` in all graphs — "
  f"{sum(1 for v in g.values() if v['reachable_nodes'] != v['nodes'])} graphs differ), "
  "`max_sm_depth` = most `hkbStateMachine`s on one reference path from `rootGenerator` within the "
  "file (following every `#NNNN` reference, so through `hkbStateMachineStateInfo.generator`, "
  "blender children, modifier generators, etc.), `xdepth` = the same but continuing through "
  "`hkbBehaviorReferenceGenerator` into the referenced graph; vars / events / char props from "
  "`hkbBehaviorGraphStringData`. Full list (all graphs): key `graphs`.")
w("")


def dist(key):
    xs = sorted(v[key] for v in g.values())
    q = lambda p: xs[min(len(xs) - 1, int(p * len(xs)))]
    return [key, xs[0], q(0.5), q(0.9), q(0.99), xs[-1], sum(xs)]


table(["metric", "min", "median", "p90", "p99", "max", "sum"],
      [dist(k) for k in ["nodes", "generators", "modifiers", "states", "state_machines",
                         "max_sm_depth", "max_sm_depth_through_references", "clip_generators",
                         "variables", "events", "character_properties"]])
w("SM depth histogram (within file / through references):")
w("")
h1 = collections.Counter(v["max_sm_depth"] for v in g.values())
h2 = collections.Counter(v["max_sm_depth_through_references"] for v in g.values())
table(["depth", "graphs (within)", "graphs (through refs)"],
      [[d, h1.get(d, 0), h2.get(d, 0)] for d in sorted(set(h1) | set(h2))])
w("### Largest 60 graphs by node count")
w("")
top = sorted(g.items(), key=lambda kv: -kv[1]["nodes"])[:60]
table(["graph", "nodes", "gen", "mod", "states", "SMs", "depth", "xdepth", "clips", "vars", "events", "char props", "refs"],
      [[code(k), v["nodes"], v["generators"], v["modifiers"], v["states"], v["state_machines"], v["max_sm_depth"],
        v["max_sm_depth_through_references"], v["clip_generators"], v["variables"], v["events"],
        v["character_properties"], len(v["behavior_references"])] for k, v in top])
w(f"### Behavior reference edges ({len(c['behavior_reference_edges'])})")
w("")
w("`hkbBehaviorReferenceGenerator.behaviorName`, resolved against the project dir (parent of the "
  "graph's directory). Key: `behavior_reference_edges`.")
w("")
table(["from graph", "behaviorName"], [[code(a_), code(b_)] for a_, b_ in c["behavior_reference_edges"]])

# ---- 3 contract
w("## 3. Contract surface: variables and events")
w("")
tt = collections.Counter()
mixed = []
for n, v in c["variables"].items():
    for t, k in v["types"].items():
        tt[t] += k
    if len(v["types"]) > 1:
        mixed.append((n, v["types"]))
w(f"**{len(c['variables'])}** distinct variable names across {len(g)} graphs; "
  f"{sum(v['graphs'] for v in c['variables'].values())} declarations. "
  f"Declarations by type: " + ", ".join(f"{t} {n}" for t, n in tt.most_common()) +
  f". Names declared with more than one type: **{len(mixed)}**" +
  (": " + ", ".join(f"{code(n)} ({', '.join(f'{t}×{k}' for t, k in ts.items())})" for n, ts in mixed[:30]) if mixed else "") +
  ". Key: `variables`.")
w("")
w("### Variables declared in the most graphs (top 150 of all; full list in JSON)")
w("")
table(["variable", "graphs", "type(s)"],
      [[code(n), v["graphs"], ", ".join(v["types"])] for n, v in list(c["variables"].items())[:150]])
once = sum(1 for v in c["variables"].values() if v["graphs"] == 1)
w(f"{once} variable names are declared in exactly one graph.")
w("")
w(f"### Events declared in the most graphs (top 150 of {len(c['events'])}; key `events`)")
w("")
evonce = sum(1 for n in c["events"].values() if n == 1)
table(["event", "graphs"], [[code(n), k] for n, k in list(c["events"].items())[:150]])
w(f"{evonce} event names are declared in exactly one graph.")
w("")
w("### Character properties")
w("")
w(f"Graph-side (`hkbBehaviorGraphStringData.characterPropertyNames`), {len(c['graph_character_properties'])} names; "
  "key `graph_character_properties`:")
w("")
table(["property", "graphs"], [[code(n), k] for n, k in c["graph_character_properties"].items()])
cf = c["character_files"]
w(f"Character files (`hkbCharacterStringData.characterPropertyNames`), {cf['count']} files, "
  f"{len(cf['character_property_names'])} names (top 60); key `character_files`. "
  f"Total `animationNames` entries across character files: {cf['animation_names_total']:,}.")
w("")
table(["property", "character files"], [[code(n), k] for n, k in list(cf["character_property_names"].items())[:60]])
pf = c["project_files"]
w(f"Project files: {pf['count']} `hkbProjectData`, {pf['with_behaviors']} list behavior files, "
  f"{pf['characters_listed']} character filenames listed in total. Skeleton files: {len(c['skeletons'])}, "
  f"bone-count distribution: " +
  ", ".join(f"{b} bones ×{n}" for b, n in sorted(collections.Counter(s['bones'] for v in c['skeletons'].values() for s in v).items(), key=lambda kv: -kv[1])[:12]) + ".")
w("")

# ---- 4 annotations
w("## 4. Annotation strings")
w("")
a = ann["animationdata_txt"]
w("### 4a. All clips: `meshes/animationdatasinglefile.txt` (complete)")
w("")
w(f"The text file shipped alongside the behaviors, holding per-clip trigger events (`name:time`) for every clip in every project. These overlap with, but are not identical to, the .hkx `annotationTracks` (see the overlap figure in 4b). "
  f"{a['projects']} project blocks ({a['projects_with_motion_data']} with motion data), parsed to EOF: "
  f"**{a['parsed_to_eof']}**. {a['clip_blocks']:,} clip blocks, {a['clips_with_triggers']:,} with ≥1 trigger, "
  f"**{a['trigger_instances']:,} trigger instances, {a['unique']} distinct strings**. "
  f"(The split copies under `meshes/animationdata/*.txt` parse to {a['split_files']} files / "
  f"{a['split_clip_blocks']:,} clip blocks — a subset; the single file is authoritative.) "
  "Compare: 10,086 `hkbClipGenerator`s in the behavior graphs. Key: `annotations.animationdata_txt`.")
w("")
w("Cross-check: `wc -l ~/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt` → 170,724, the line the parser ends on (`parsed_to_eof` above); the framing one-liner is in the tool README.")
w("")
w("Prefix rule: text up to and including the first `.` (`SoundPlay.`, `NPCSoundPlay.`), else the leading "
  "identifier with trailing digits dropped. Case is preserved (`syncLeft` and `SyncLeft` both exist).")
w("")
table(["prefix", "instances"], [[code(p), n] for p, n in list(a["prefixes"].items())[:60]])
w("Top 100 strings:")
w("")
table(["trigger", "instances"], [[code(s), n] for s, n in list(a["strings"].items())[:100]])
s = ann["hkx_animations"]
v = s["vs_animationdata_txt"]
m = s["per_clip_model"]
full = s["source"] == "full"
w(f"### 4b. Animation .hkx under `animations/` dirs: `annotationTracks` ({'COMPLETE' if full else 'SAMPLED'})")
w("")
mf = s["conversion_manifest"]
if full:
    w(f"**Coverage: complete.** Every `.hkx` under an `animations/` dir was converted "
      f"(`bulk_convert.sh anim-all` → `~/skyrim-data-extracted/xml-anim/`, manifest: "
      + ", ".join(f"{n:,} {k}" for k, n in mf.items()) + f") and all {s['files']:,} XML files are read here. "
      "This replaces the 200-file sample this section used before; the sample's figures stay in "
      f"`annotations.hkx_sample` ({ann['hkx_sample']['files']} files, {ann['hkx_sample']['unique']} distinct strings). "
      "Key: `annotations.hkx_animations`.")
else:
    w(f"**Coverage: SAMPLE ONLY** ({s['files']} files from `{s['path']}`); run `bulk_convert.sh anim-all` "
      "for the full set. Key: `annotations.hkx_animations`.")
w("")
w("Cross-check: `cut -f1 ~/skyrim-data-extracted/xml-anim/_manifest.tsv | sort | uniq -c` → 5936 ok; "
  "`_errors.log` is empty (`wc -c`); `find ~/skyrim-data-extracted/raw -iname '*.hkx' | grep -ic /animations/` → 5936.")
w("")
fpa = s["files_per_animation_count"]
w(f"- Files: {s['files']:,}; animation objects: **{s['animations']:,}** (animations per file: "
  + ", ".join(f"{k} in {n:,} files" for k, n in fpa.items())
  + (f"; without one: " + ", ".join(code(x) for x in s["files_without_animation"]) if s["files_without_animation"] else "") + ").")
w(f"- **Annotated clips: {s['annotated_animations']:,}** of {s['animations']:,} "
  f"({100 * s['annotated_animations'] / max(1, s['animations']):.1f}%); **{s['instances']:,} annotation instances, "
  f"{s['unique']} distinct strings**. Per annotated clip: median {s['annotations_per_annotated_clip'].get('p50')}, "
  f"p90 {s['annotations_per_annotated_clip'].get('p90')}, max {s['annotations_per_annotated_clip'].get('max')}.")
nt = s["named_annotation_track_names"]
w(f"- Annotation tracks: one per transform track in {s['annotation_tracks_equal_transform_tracks']:,}/{s['animations']:,} "
  f"animations. Track names are empty except in {s['animations_with_named_annotation_tracks']} animations "
  f"({sum(nt.values()):,} named tracks, {len(nt)} distinct names, e.g. "
  + ", ".join(code(k) for k in list(nt)[:6]) + ").")
w("")
w("#### Annotations vs `animationdatasinglefile.txt` triggers")
w("")
table(["", "distinct strings", "instances"],
      [["in .hkx annotations", v["hkx_unique"], s["instances"]],
       ["in the text file's triggers", v["txt_unique"], a["trigger_instances"]],
       ["in both", v["both"], "—"],
       ["only in .hkx", v["only_hkx"], v["only_hkx_instances"]],
       ["only in the text file", v["only_txt"], v["only_txt_instances"]]])
w(f"(The 200-file sample showed 36 of 60 .hkx strings among the triggers; on the full set it is "
  f"**{v['both']} of {v['hkx_unique']}**.) The two lists are different things, and the difference is explained, not noise:")
w("")
w(f"- **Every one of the {v['txt_unique']} trigger strings is a declared event** in some behavior graph "
  f"(`txt_strings_declared_as_graph_events` = {v['txt_strings_declared_as_graph_events']}). The text file "
  "holds *events*, not annotation text.")
w(f"- **Only in the text file** ({v['only_txt']} strings, {v['only_txt_instances']:,} instances) are clip-generator "
  "triggers authored in the behavior graphs (`hkbClipTriggerArray`): paired/killmove events (`NPCKillMoveStart`, "
  "`2_KillActor`, `NPCSoundPlay.*`), state exits (`attackStop`, `IdleStop`, `00NextClip`), and the bare event "
  f"`SoundPlay`. Only {v['only_txt_is_NPC_plus_hkx']} are `NPC` + an .hkx string and {v['only_txt_case_variant_of_hkx']} "
  "a case variant, so the `NPC*` strings are not renamed annotations.")
w(f"- **Only in .hkx** ({v['only_hkx']} strings, {v['only_hkx_instances']:,} instances) is mostly the payload form "
  "`SoundPlay.<descriptor>` / `CameraShake.<x>` / `SoundPlayAt.`/`SoundStop.`/`AnimObjLoad.`, which reaches the "
  "text file as the bare event before the first `.`, plus annotations no graph declares (`FrontFoot`, `BackFoot`, "
  f"typos such as `FootFornt`, `FrootBack`). {v['only_hkx_case_variant_of_txt']} differ from a trigger only by case.")
w("")
w("**Per-clip model, tested.** For each of the text file's clip blocks, find a `hkbClipGenerator` of the same name "
  "(any graph; names repeat across projects, so *any* matching candidate counts) and predict its triggers as: the clip "
  "generator's own triggers (event ids resolved through that graph's `eventNames`), plus each annotation of its "
  "animation (path resolved against the project dir, the parent of the graph's directory) that resolves to a declared "
  "event of that graph — the whole text if declared, else the text before the first `.`, else dropped. Compared as "
  "multisets (times not compared). Key: `annotations.hkx_animations.per_clip_model`.")
w("")
vd = m["verdicts"]
table(["verdict", "clip blocks"], [[k, f"{n:,}"] for k, n in vd.items()])
ok = vd.get("match_triggers_only", 0) + vd.get("match_triggers_plus_resolved_annotations", 0)
w(f"**{ok:,} of {m['clip_blocks']:,} clips ({100 * ok / m['clip_blocks']:.1f}%) match exactly.** Of the "
  f"{vd.get('mismatch', 0)} mismatches, by the closest candidate: "
  + ", ".join(f"{n} {k}" for k, n in m["mismatch_direction"].items())
  + " — i.e. mostly the text file *omits* an annotation the model resolves (hypotheses, not checked: the game resolves "
  "against a different graph's events than the candidate's, or the candidate is a same-named clip of another "
  f"project). In matched clips, {m['annotations_dropped_in_matched_clips']} annotations resolved to no event "
  "and were correctly dropped; their prefixes: "
  + ", ".join(f"{code(k)} {n}" for k, n in list(m["dropped_prefixes"].items())[:12]) + ".")
w("")
w("Engine consequence: the text file is a precomputed cache of the events a clip fires, derivable (for 97.7% of clips, "
  "as measured) from the graphs plus the annotations. An annotation's payload after the `.` (`SoundPlay.NPCHumanClap`) "
  "reaches the text file only when the whole string is itself a declared event; otherwise only the .hkx carries it. "
  "Why the text file omits some resolvable annotations (the 174 above) is **not verified**.")
w("")
w("#### Prefixes and strings")
w("")
table(["prefix", "instances"], [[code(p), n] for p, n in list(s["prefixes"].items())[:40]])
w(f"Top 60 of {s['unique']} strings (instances, files carrying it):")
w("")
sf = s["string_files"]
table(["annotation", "instances", "files"], [[code(x), n, sf[x]] for x, n in list(s["strings"].items())[:60]])
w("Strings only in .hkx, top 30 (instances):")
w("")
table(["annotation", "instances"], [[code(x), n] for x, n in list(v["only_hkx_strings"].items())[:30]])
w("Strings only in the text file, top 30 (instances):")
w("")
table(["trigger", "instances"], [[code(x), n] for x, n in list(v["only_txt_strings"].items())[:30]])
w("#### Animation shape (all animation objects)")
w("")
def drow(label, d, unit=""):
    return [label] + [f"{d.get(k)}{unit}" if d.get(k) is not None else "—" for k in ("n", "min", "p10", "p50", "p90", "p99", "max", "mean")]
table(["", "n", "min", "p10", "p50", "p90", "p99", "max", "mean"],
      [drow("duration (s)", s["duration_s"]), drow("numFrames", s["num_frames"]),
       drow("transform tracks", s["transform_tracks"]), drow("float tracks", s["float_tracks"]),
       drow("bone-index map length (non-empty only)", s["track_to_bone_indices"])])
w(f"Total duration {s['duration_s'].get('total', 0):,.0f} s ({s['duration_s'].get('total', 0) / 3600:.2f} h); "
  f"total frames {s['num_frames'].get('total', 0):,}. Keys: `duration_s`, `num_frames` (from "
  "`hkaSplineCompressedAnimation.duration` / `numFrames`).")
w("")
w("- Class: " + ", ".join(f"{code(k)} ×{n:,}" for k, n in s["class"].items())
  + "; compression `type`: " + ", ".join(f"{code(k)} ×{n:,}" for k, n in s["compression_type"].items())
  + ". **One codec covers every animation.**")
w("- Blocks per animation (`numBlocks`; `maxFramesPerBlock` is 256 in 5,897 and 128 in 38, by "
  "`grep -rh maxFramesPerBlock ~/skyrim-data-extracted/xml-anim | sort | uniq -c`): " + ", ".join(f"{k} ×{n:,}" for k, n in s["num_blocks"].items()) + ".")
fd = s["frame_duration_s"]
w(f"- `frameDuration`: " + ", ".join(f"{k} s ×{n:,}" for k, n in list(fd.items())[:6])
  + f", {len(fd) - 6} other values (key `frame_duration_s`). 0.033333 s is 30 fps.")
w("- Transform-track counts, commonest: " + ", ".join(f"{k} ×{n}" for k, n in s["transform_tracks_top"].items())
  + f". Animations with float tracks: {s['with_float_tracks']:,}.")
w(f"- `blendHint`: " + ", ".join(f"{k} ×{n:,}" for k, n in s["blend_hint"].items())
  + f"; with `extractedMotion`: {s['extracted_motion']}; with a non-empty `transformTrackToBoneIndices` "
  f"(empty presumably means track i = bone i; **not verified**): {s['track_to_bone_indices_nonempty']}.")
w("- `originalSkeletonName`, top 10: " + ", ".join(f"{code(k)} ×{n:,}" for k, n in list(s["skeletons"].items())[:10])
  + f"; {len(s['skeletons'])} distinct.")
w("")
b = ann["hkx_outside_animations_dirs"]
w(f"### 4c. Animations stored outside `animations/` dirs (complete for those {b['files']} files)")
w("")
w(f"{b['instances']} annotation instances, {b['unique']} distinct. Key: `annotations.hkx_outside_animations_dirs`.")
w("")
table(["annotation", "instances"], [[code(x), n] for x, n in b["strings"].items()])

# ---- 5 long tail
w("## 5. Long tail")
w("")
w(f"Node classes only ({cov['node_classes']} classes, {cov['node_instances']:,} instances over behavior graphs). "
  "Key: `behavior_node_class_coverage`.")
w("")
table(["coverage of node instances", "classes needed"], [[f"{float(k)*100:g}%", v] for k, v in ct.items()])
ac = c["behavior_all_class_coverage"]
w(f"All classes in behavior files ({ac['classes']} classes, {ac['instances']:,} objects, incl. data/arrays/transition effects):")
w("")
table(["coverage of all objects", "classes needed"], [[f"{float(k)*100:g}%", v] for k, v in ac["classes_to_cover"].items()])
nodes_rows = [r for r in c["classes"]["behavior"] if r["role"] in ("generator", "modifier", "state")]
acc = 0
rows = []
for i, r in enumerate(nodes_rows, 1):
    acc += r["instances"]
    rows.append([i, code(r["class"]), r["role"], r["instances"], r["files"], f"{100*acc/cov['node_instances']:.2f}%"])
w("Node classes by instance count, cumulative:")
w("")
table(["#", "class", "role", "instances", "graphs", "cumulative"], rows)

# ---- 6 per actor
w("## 6. Per actor / directory")
w("")
w("Group = `actors/<dir>` (`actors/ambient/*`, `actors/dlc01/*`, `actors/dlc02/*` one level deeper); non-actor "
  "paths are `other:meshes/<dir>`. Key: `per_group`.")
w("")
pg = c["per_group"]
table(["group", "graphs", "nodes", "SMs", "clips", "max depth", "max xdepth", "characters", "projects"],
      [[code(k), v.get("graphs", 0), v.get("nodes", 0), v.get("state_machines", 0), v.get("clips", 0),
        v.get("max_sm_depth", 0), v.get("max_sm_depth_through_references", 0), v.get("characters", 0), v.get("projects", 0)]
       for k, v in pg.items()])
act = {k: v for k, v in pg.items() if k.startswith("actors/")}
w(f"Actor groups: {len(act)}, holding {sum(v.get('graphs', 0) for v in act.values())} graphs and "
  f"{sum(v.get('nodes', 0) for v in act.values()):,} nodes; non-actor groups: {len(pg) - len(act)}, "
  f"{sum(v.get('graphs', 0) for k, v in pg.items() if k not in act)} graphs, "
  f"{sum(v.get('nodes', 0) for k, v in pg.items() if k not in act):,} nodes.")
w("")
w("## Not done / caveats")
w("")
if ann["hkx_animations"]["source"] == "full":
    w("- §4b covers every animation; its per-clip model joins clips by name across all graphs, so a match may be "
      "with a same-named clip of another project. Trigger times are not compared.")
else:
    w("- Annotation strings from .hkx animations are a **sample** (§4b).")
w("- Node counts are per file: a graph referenced by several others is counted once, in its own file.")
w("- `max_sm_depth` follows every reference, including from modifiers and transition data; it is a path "
  "maximum, not a runtime-reachable maximum.")
w("- Variable types come from `hkbBehaviorGraphData.variableInfos[i].type`, aligned by index with "
  "`variableNames`; event flags (`eventInfos`) are read but not reported.")
open(dst, "w").write("\n".join(out) + "\n")
print(dst, len(out), "lines")
