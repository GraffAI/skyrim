"""Unit tests against a hand-made packfile (no game data). python3 -I test_census.py"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import census  # noqa: E402

SAMPLE = """<?xml version="1.0" encoding="ascii"?>
<hkpackfile classversion="8" contentsversion="hk_2010.2.0-r1" toplevelobject="#0001">
<hksection name="__data__">
 <hkobject name="#0010" class="hkbClipGenerator" signature="0x1">
  <hkparam name="animationName">Animations\\a.hkx</hkparam><hkparam name="triggers">null</hkparam>
 </hkobject>
 <hkobject name="#0011" class="hkbBehaviorReferenceGenerator" signature="0x1">
  <hkparam name="behaviorName">Behaviors\\Other.hkx</hkparam>
 </hkobject>
 <hkobject name="#0009" class="hkbStateMachineStateInfo" signature="0x1">
  <hkparam name="generator">#0010</hkparam>
 </hkobject>
 <hkobject name="#0008" class="hkbStateMachine" signature="0x1">
  <hkparam name="states" numelements="1">#0009</hkparam>
 </hkobject>
 <hkobject name="#0007" class="hkbStateMachineStateInfo" signature="0x1">
  <hkparam name="generator">#0008</hkparam>
 </hkobject>
 <hkobject name="#0012" class="hkbStateMachineStateInfo" signature="0x1">
  <hkparam name="generator">#0011</hkparam>
 </hkobject>
 <hkobject name="#0013" class="hkbBlendingTransitionEffect" signature="0x1"></hkobject>
 <hkobject name="#0006" class="hkbStateMachine" signature="0x1">
  <hkparam name="states" numelements="2">#0007 #0012</hkparam>
  <hkparam name="wildcardTransitions">null</hkparam>
 </hkobject>
 <hkobject name="#0005" class="hkbBehaviorGraphStringData" signature="0x1">
  <hkparam name="eventNames" numelements="2"><hkcstring>Go</hkcstring><hkcstring>Stop</hkcstring></hkparam>
  <hkparam name="attributeNames" numelements="0"></hkparam>
  <hkparam name="variableNames" numelements="1"><hkcstring>Speed</hkcstring></hkparam>
  <hkparam name="characterPropertyNames" numelements="0"></hkparam>
 </hkobject>
 <hkobject name="#0004" class="hkbBehaviorGraphData" signature="0x1">
  <hkparam name="variableInfos" numelements="1"><hkobject>
   <hkparam name="role"><hkobject><hkparam name="role">ROLE_DEFAULT</hkparam></hkobject></hkparam>
   <hkparam name="type">VARIABLE_TYPE_REAL</hkparam></hkobject></hkparam>
  <hkparam name="eventInfos" numelements="2"><hkobject><hkparam name="flags">0</hkparam></hkobject>
   <hkobject><hkparam name="flags">FLAG_SYNC_POINT</hkparam></hkobject></hkparam>
  <hkparam name="stringData">#0005</hkparam>
 </hkobject>
 <hkobject name="#0002" class="hkbBehaviorGraph" signature="0x1">
  <hkparam name="name">T.hkb</hkparam><hkparam name="rootGenerator">#0006</hkparam>
  <hkparam name="data">#0004</hkparam>
 </hkobject>
 <hkobject name="#0001" class="hkRootLevelContainer" signature="0x1">
  <hkparam name="namedVariants" numelements="1"><hkobject>
   <hkparam name="name">hkbBehaviorGraph</hkparam><hkparam name="className">hkbBehaviorGraph</hkparam>
   <hkparam name="variant">#0002</hkparam></hkobject></hkparam>
 </hkobject>
</hksection></hkpackfile>
"""

ANIM = """<?xml version="1.0" encoding="ascii"?>
<hkpackfile classversion="8" contentsversion="hk_2010.2.0-r1" toplevelobject="#0001">
<hksection name="__data__">
 <hkobject name="#0004" class="hkaAnimationBinding" signature="0x1">
  <hkparam name="originalSkeletonName">Root</hkparam><hkparam name="animation">#0003</hkparam>
  <hkparam name="transformTrackToBoneIndices" numelements="0"></hkparam>
  <hkparam name="blendHint">ADDITIVE</hkparam>
 </hkobject>
 <hkobject name="#0003" class="hkaSplineCompressedAnimation" signature="0x1">
  <hkparam name="type">HK_SPLINE_COMPRESSED_ANIMATION</hkparam>
  <hkparam name="duration">0.333333</hkparam>
  <hkparam name="numberOfTransformTracks">1</hkparam>
  <hkparam name="numberOfFloatTracks">2</hkparam>
  <hkparam name="extractedMotion">null</hkparam>
  <hkparam name="annotationTracks" numelements="1"><hkobject>
   <hkparam name="trackName">root</hkparam>
   <hkparam name="annotations" numelements="2">
    <hkobject><hkparam name="time">0.1</hkparam><hkparam name="text">SoundPlay.Foo</hkparam></hkobject>
    <hkobject><hkparam name="time">0.2</hkparam><hkparam name="text">FootLeft</hkparam></hkobject>
   </hkparam></hkobject></hkparam>
  <hkparam name="numFrames">11</hkparam><hkparam name="numBlocks">1</hkparam>
  <hkparam name="frameDuration">0.033333</hkparam>
 </hkobject>
</hksection></hkpackfile>
"""

CLIPS = """<?xml version="1.0" encoding="ascii"?>
<hkpackfile classversion="8" contentsversion="hk_2010.2.0-r1" toplevelobject="#0001">
<hksection name="__data__">
 <hkobject name="#0021" class="hkbClipTriggerArray" signature="0x1">
  <hkparam name="triggers" numelements="2">
   <hkobject><hkparam name="localTime">0.0</hkparam><hkparam name="event"><hkobject>
    <hkparam name="id">1</hkparam><hkparam name="payload">null</hkparam></hkobject></hkparam></hkobject>
   <hkobject><hkparam name="localTime">0.5</hkparam><hkparam name="event"><hkobject>
    <hkparam name="id">7</hkparam><hkparam name="payload">null</hkparam></hkobject></hkparam></hkobject>
  </hkparam>
 </hkobject>
 <hkobject name="#0020" class="hkbClipGenerator" signature="0x1">
  <hkparam name="name">ClipA</hkparam><hkparam name="animationName">Animations\\a.hkx</hkparam>
  <hkparam name="triggers">#0021</hkparam>
 </hkobject>
 <hkobject name="#0022" class="hkbClipGenerator" signature="0x1">
  <hkparam name="name">ClipB</hkparam><hkparam name="animationName">Animations\\b.hkx</hkparam>
  <hkparam name="triggers">null</hkparam>
 </hkobject>
</hksection></hkpackfile>
"""


class T(unittest.TestCase):
    def load(self, text):
        with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as f:
            f.write(text)
        try:
            return census.load(f.name)
        finally:
            os.unlink(f.name)

    def test_behavior(self):
        top, objs = self.load(SAMPLE)
        self.assertEqual(top, "#0001")
        g = census.analyse_behavior(top, objs)
        self.assertEqual(g["states"], 3)
        self.assertEqual(g["generators"], 4)          # 2 SM + clip + behavior reference
        self.assertEqual(g["nodes"], 7)
        self.assertEqual(g["transition_effects"], 1)
        self.assertEqual(g["reachable_nodes"], 7)
        self.assertEqual(g["max_sm_depth"], 2)
        self.assertEqual(g["clip_generators"], 1)
        self.assertEqual(g["behavior_references"], ["Behaviors/Other.hkx"])
        self.assertEqual(g["variables"], [["Speed", "VARIABLE_TYPE_REAL"]])
        self.assertEqual(g["events"], [["Go", "0"], ["Stop", "FLAG_SYNC_POINT"]])

    def test_cross_depth(self):
        top, objs = self.load(SAMPLE)
        a = census.analyse_behavior(top, objs)
        b = census.analyse_behavior(top, objs)
        b["_adj"]["#0011"] = (False, [], None)  # leaf graph: no further reference
        graphs = {"m/x/behaviors/t.hkx": a, "m/x/behaviors/other.hkx": b}
        depth, unresolved = census.cross_graph_depth(graphs)
        self.assertEqual(depth["m/x/behaviors/other.hkx"], 2)
        self.assertEqual(depth["m/x/behaviors/t.hkx"], 3)  # outer SM + other's 2
        self.assertEqual(unresolved, [])

    def test_annotations(self):
        _, objs = self.load(ANIM)
        self.assertEqual(census.annotations_in(objs), ["SoundPlay.Foo", "FootLeft"])
        self.assertEqual(census.prefix_of("SoundPlay.Foo"), "SoundPlay.")
        self.assertEqual(census.prefix_of("NPCPlayAnim01"), "NPCPlayAnim")

    def test_animation_info(self):
        _, objs = self.load(ANIM)
        [x] = census.animation_info(objs)
        self.assertEqual(x["class"], "hkaSplineCompressedAnimation")
        self.assertEqual(x["type"], "HK_SPLINE_COMPRESSED_ANIMATION")
        self.assertAlmostEqual(x["duration"], 0.333333)
        self.assertEqual((x["num_frames"], x["num_blocks"]), (11, 1))
        self.assertEqual((x["transform_tracks"], x["float_tracks"], x["annotation_tracks"]), (1, 2, 1))
        self.assertEqual(x["annotations"], [(0.1, "SoundPlay.Foo"), (0.2, "FootLeft")])
        self.assertEqual((x["blend_hint"], x["track_to_bone_indices"], x["skeleton"]), ("ADDITIVE", 0, "Root"))
        self.assertFalse(x["extracted_motion"])

    def test_dist_stats(self):
        d = census.dist_stats([5, 1, None, 3, 2, 4])
        self.assertEqual((d["n"], d["min"], d["p50"], d["max"], d["total"]), (5, 1, 3, 5, 15))
        self.assertEqual(census.dist_stats([None]), {"n": 0})

    def test_set_stats_overlap(self):
        _, objs = self.load(ANIM)
        trig = census.collections.Counter({"FootLeft": 3, "NPCFootLeft": 1, "attackStop": 2})
        st = census.animation_set_stats([("a.xml", census.animation_info(objs))], trig, "full", "/x", {})
        v = st["vs_animationdata_txt"]
        self.assertEqual((st["files"], st["annotated_animations"], st["instances"], st["unique"]), (1, 1, 2, 2))
        self.assertEqual((v["both"], v["only_hkx"], v["only_txt"]), (1, 1, 2))
        self.assertEqual(v["only_hkx_strings"], {"SoundPlay.Foo": 1})
        self.assertEqual(v["only_txt_is_NPC_plus_hkx"], 1)
        self.assertEqual(st["num_frames"]["max"], 11)

    def test_resolve_annotation(self):
        ev = {"SoundPlay", "FootLeft", "CameraShake.X"}
        self.assertEqual(census.resolve_annotation("FootLeft", ev), "FootLeft")
        self.assertEqual(census.resolve_annotation("SoundPlay.NPCFoo", ev), "SoundPlay")
        self.assertEqual(census.resolve_annotation("CameraShake.X", ev), "CameraShake.X")
        self.assertIsNone(census.resolve_annotation("FrontFoot", ev))

    def test_clip_triggers_and_model(self):
        _, objs = self.load(CLIPS)
        ev = ["A", "Stop", "", "", "", "", "", "SoundPlay"]
        clips = census.clip_triggers(objs, ev)
        self.assertEqual(clips, [("ClipA", "Animations/a.hkx", ["Stop", "SoundPlay"]),
                                 ("ClipB", "Animations/b.hkx", [])])
        graphs = {"m/x/behaviors/g.hkx": {"_clips": clips, "_event_set": set(ev)}}
        ann = {"m/x/animations/a.hkx": ["SoundPlay.Bar", "Junk"], "m/x/animations/b.hkx": []}
        blocks = [("ClipA", ["Stop", "SoundPlay", "SoundPlay"]), ("ClipB", []), ("ClipB", ["Stop"]), ("Nope", [])]
        r = census.explain_txt_triggers(blocks, graphs, ann)
        self.assertEqual(r["verdicts"], {"match_triggers_only": 1, "match_triggers_plus_resolved_annotations": 1,
                                         "mismatch": 1, "no_clip_generator_named": 1})
        self.assertEqual(r["mismatch_direction"], {"txt_has_unpredicted": 1})
        self.assertEqual(r["annotations_dropped_in_matched_clips"], 1)

    def test_roles(self):
        self.assertEqual(census.role("hkbModifierList"), "modifier")
        self.assertEqual(census.role("BSCyclicBlendTransitionGenerator"), "generator")
        self.assertEqual(census.role("hkbBlendingTransitionEffect"), "transition")
        self.assertEqual(census.role("hkbBlenderGeneratorChild"), "data")

    def test_clip_blocks(self):
        lines = ["1", "1", "Behaviors\\X.hkx", "0",
                 "ClipA", "3", "1", "0", "0", "2", "Foo:0.1", "Bar.Baz:1.5", "",
                 "ClipB", "4", "1", "0", "0", "0", "", "0", "1.2", "1", "1.2 0 0 0", ""]
        got = list(census.clip_blocks(lines))
        self.assertEqual(got, [("ClipA", ["Foo", "Bar.Baz"]), ("ClipB", [])])


if __name__ == "__main__":
    unittest.main()
