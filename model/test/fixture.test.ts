// Always runs: the hand-made fixture under test/fixtures/tiny (not game data).
import { test } from "node:test";
import assert from "node:assert/strict";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { Loader, is, stateMachineTree, formatTree, variables, events, graphClosure, graphNodes, references, tokenize, parsePackfile, normalizeRef } from "../src/index.ts";

const root = join(dirname(fileURLToPath(import.meta.url)), "fixtures", "tiny");

test("tokenizer: entities, comments, processing instructions, self-closing tags", () => {
  const toks = [...tokenize(`<?xml version="1.0"?><!-- c --><a x="1&amp;2"><b/>t&lt;&#65;&#x42;</a>`)];
  assert.deepEqual(toks, [
    { t: "open", name: "a", attrs: { x: "1&2" }, selfClosing: false },
    { t: "open", name: "b", attrs: {}, selfClosing: true },
    { t: "text", text: "t<AB" },
    { t: "close", name: "a" },
  ]);
});

test("packfile reader: rejects non-packfiles and unbalanced input", () => {
  assert.throws(() => parsePackfile("<root/>"), /unexpected element/);
  assert.throws(() => parsePackfile(`<hkpackfile toplevelobject="#1"><hksection>`), /unterminated/);
});

test("normalizeRef: Windows paths against the project directory", () => {
  assert.equal(normalizeRef("meshes/actors/x", "Behaviors\\Main.HKX"), "meshes/actors/x/behaviors/main.xml");
  assert.equal(normalizeRef("a/b", "..\\c\\D.hkx"), "a/c/d.xml");
  assert.equal(normalizeRef("", "Characters\\C.hkx"), "characters/c.xml");
});

test("loader: project -> character -> behavior -> referenced behavior (with a cycle)", () => {
  const loader = new Loader(root);
  const project = loader.project("tinyproject.xml");
  assert.ok(project);
  assert.equal(project.characters.length, 1);
  const ch = project.characters[0];
  assert.ok(ch);
  assert.equal(ch.path, "characters/tinychar.xml");
  assert.equal(ch.strings.name, "TinyChar");
  assert.equal(ch.strings.ragdollName, null, "the ␀ marker decodes to null");
  assert.equal(ch.rigPath, "character assets/tinyrig.xml");
  assert.deepEqual(ch.data.modelUpMS, [0, 0, 1, 0]);
  assert.equal(ch.data.scale, 1.5);
  const main = ch.behavior;
  assert.ok(main);
  assert.equal(main.path, "behaviors/main.xml");
  assert.equal(main.references.length, 1);
  const sub = main.references[0]?.target;
  assert.ok(sub);
  assert.equal(sub.path, "behaviors/sub.xml");
  assert.equal(sub.references[0]?.target, main, "Sub -> Main resolves to the same cached object");
  assert.equal(graphClosure(main).length, 2);
  assert.equal(loader.missing.size, 0);
  assert.equal(loader.failures.size, 0);
  assert.deepEqual(loader.diagnostics(), []);
});

test("typed objects: refs resolve to objects, enums/flags/strings decode", () => {
  const loader = new Loader(root);
  const main = loader.behavior("behaviors/main.xml");
  assert.ok(main);
  const sm = main.graph.rootGenerator;
  assert.ok(sm && is(sm, "hkbStateMachine"));
  assert.equal(sm.name, "TinyRoot");
  assert.equal(sm.$id, "#0010");
  assert.equal(sm.startStateMode, "START_STATE_MODE_DEFAULT");
  assert.equal(sm.variableBindingSet, null);
  const [s1, s2] = sm.states;
  assert.ok(s1 && s2);
  const clip = s1.generator;
  assert.ok(is(clip, "hkbClipGenerator"));
  assert.equal(clip.name, "Wave & Smile");
  assert.equal(clip.mode, "MODE_LOOPING");
  assert.ok(is(s2.generator, "hkbBehaviorReferenceGenerator"));
  const t = sm.wildcardTransitions?.transitions[0];
  assert.ok(t);
  assert.deepEqual(t.flags, ["FLAG_IS_LOCAL_WILDCARD", "FLAG_DISABLE_CONDITION"]);
  assert.equal(t.triggerInterval.enterEventId, -1);
  assert.equal(t.condition, null);
  assert.deepEqual(references(sm).map((o) => o.$id), ["#0011", "#0013", "#0020"]);
  assert.equal(graphNodes(main).length, 5, "SM + 2 states + clip + reference generator");
});

test("query: variables, events, state-machine tree", () => {
  const loader = new Loader(root);
  const main = loader.behavior("behaviors/main.xml");
  assert.ok(main);
  const vars = variables(main);
  assert.deepEqual(vars.map((v) => [v.name, v.type]), [["fSpeed", "VARIABLE_TYPE_REAL"], [" leadingSpace", "VARIABLE_TYPE_VECTOR4"]]);
  assert.equal(vars[0]?.initial, 1065353216);
  assert.deepEqual(vars[1]?.initial, [1, 2, 3, 4], "a VECTOR4's word value indexes the quad array");
  assert.deepEqual(events(main).map((e) => [e.name, e.flags]), [["Wave", []], ["GoElsewhere", ["FLAG_SYNC_POINT"]]]);
  const tree = stateMachineTree(main);
  assert.equal(tree.length, 1);
  assert.deepEqual(tree[0]?.states.map((s) => [s.stateId, s.name, s.behaviorRefs[0]?.target?.path]), [[1, "Waving", undefined], [2, "Elsewhere", "behaviors/sub.xml"]]);
  assert.equal(formatTree(tree), ["SM TinyRoot (2 states, start 1)", "  [1] Waving", "  [2] Elsewhere -> behaviors/sub.xml"].join("\n"));
});

test("missing files are reported, not thrown", () => {
  const loader = new Loader(root);
  assert.equal(loader.behavior("behaviors/nope.xml"), undefined);
  assert.equal(loader.missing.get("behaviors/nope.xml"), "(caller)");
});
