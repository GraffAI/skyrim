// Runs on the real converted corpus when ~/skyrim-data-extracted/xml exists; skips otherwise.
// Cross-checks the loader against census/census.json (aggregate counts committed in the zone).
import { test } from "node:test";
import assert from "node:assert/strict";
import { existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath } from "node:url";
import { Loader, graphClosure, graphNodes, variables, events, stateMachineTree, objectsOf, SCHEMA } from "../src/index.ts";

const root = join(homedir(), "skyrim-data-extracted", "xml");
const skip = existsSync(join(root, "_manifest.tsv")) ? false : `no corpus at ${root}`;
const censusPath = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "census", "census.json");

interface CensusGraph {
  nodes: number;
  state_machines: number;
  clip_generators: number;
  variables: number;
  events: number;
  behavior_references: unknown[];
}

test("0_master project closure loads with every reference resolved", { skip }, () => {
  const loader = new Loader(root);
  const project = loader.project("meshes/actors/character/defaultmale.xml");
  assert.ok(project);
  const master = project.characters[0]?.behavior;
  assert.ok(master);
  assert.equal(master.path, "meshes/actors/character/behaviors/0_master.xml");
  const closure = graphClosure(master);
  assert.ok(closure.length >= 10, `closure has ${closure.length} graphs`);
  for (const b of closure) for (const r of b.references) assert.ok(r.target, `${b.path}: ${r.node.behaviorName} unresolved`);
  assert.ok(variables(master).length > 100);
  assert.ok(events(master).length > 1000);
  assert.equal(stateMachineTree(master)[0]?.name, "Master_Behavior");
  assert.deepEqual(loader.diagnostics(), []);
});

test("every behavior graph matches the census counts", { skip }, () => {
  const census = JSON.parse(readFileSync(censusPath, "utf8")) as { graphs: Record<string, CensusGraph> };
  const loader = new Loader(root);
  let n = 0;
  for (const [hkx, g] of Object.entries(census.graphs)) {
    const path = hkx.replace(/\.hkx$/, ".xml");
    const b = loader.behavior(path);
    assert.ok(b, path);
    const pf = b.packfile;
    assert.equal(graphNodes(b).length, g.nodes, `${path} nodes`);
    assert.equal(objectsOf(pf, "hkbStateMachine").length, g.state_machines, `${path} state machines`);
    assert.equal(objectsOf(pf, "hkbClipGenerator").length, g.clip_generators, `${path} clips`);
    assert.equal(variables(b).length, g.variables, `${path} variables`);
    assert.equal(events(b).length, g.events, `${path} events`);
    assert.equal(new Set(b.references.map((r) => r.path)).size, g.behavior_references.length, `${path} distinct references`);
    n++;
  }
  assert.equal(n, 428);
  assert.deepEqual(loader.diagnostics(), [], "every class and field is in the generated schema");
});

test("generated schema covers the corpus it was generated from", { skip }, () => {
  assert.equal(SCHEMA.corpus.files, 1238);
  assert.ok(Object.keys(SCHEMA.classes).length >= 70);
});
