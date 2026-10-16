// CLI: load a project closure (or the whole corpus) and print counts.
//
//   node src/cli.ts [--root DIR] [--tree DEPTH] [PATH]   default PATH meshes/actors/character/behaviors/0_master.xml
//   node src/cli.ts [--root DIR] --all                    every project, character and behavior graph in _manifest.tsv
//
// For a behavior PATH, the projects in its project directory whose characters use it are loaded
// (so 0_master.xml loads defaultmale + defaultfemale and everything they reach).

import { readdirSync, readFileSync, existsSync } from "node:fs";
import { join, posix } from "node:path";
import { homedir } from "node:os";
import { Loader } from "./loader.ts";
import type { BehaviorFile } from "./loader.ts";
import { graphClosure, graphNodes, stateMachineTree, formatTree, variables, events, classCounts } from "./query.ts";
import type { HkObject } from "./generated/classes.ts";

function arg(name: string): string | undefined {
  const i = process.argv.indexOf(name);
  return i >= 0 ? process.argv[i + 1] : undefined;
}

const root = arg("--root") ?? join(homedir(), "skyrim-data-extracted", "xml");
const all = process.argv.includes("--all");
const treeDepth = arg("--tree");
const positional = process.argv.slice(2).filter((a, i, xs) => !a.startsWith("--") && !(xs[i - 1] === "--root" || xs[i - 1] === "--tree"));
const target = positional[0] ?? "meshes/actors/character/behaviors/0_master.xml";

if (!existsSync(root)) {
  console.error(`no corpus at ${root}`);
  process.exit(2);
}

const mb = (n: number): string => `${(n / 1048576).toFixed(0)} MB`;
const gcFn = (globalThis as { gc?: () => void }).gc;
const t0 = performance.now();
const loader = new Loader(root);

const rootClass = (path: string): string | undefined => {
  try {
    const pf = loader.packfile(path);
    const v = pf.root.namedVariants[0]?.variant as HkObject | null | undefined;
    return v?.$class;
  } catch {
    return undefined;
  }
};

const starts: BehaviorFile[] = [];
if (all) {
  const rows = readFileSync(join(root, "_manifest.tsv"), "latin1").split("\n").map((l) => l.split("\t"));
  const rel = (r: string[]): string => (r[5] ?? "").replace(/\.hkx$/i, ".xml");
  for (const r of rows) if (r[0] === "ok" && r[2] === "hkbProjectData") loader.project(rel(r));
  for (const r of rows) {
    if (r[0] !== "ok") continue;
    const p = rel(r);
    if (r[2] === "hkbCharacterData") loader.character(p, posix.dirname(posix.dirname(p)));
    if (r[2] === "hkbBehaviorGraph") {
      const b = loader.behavior(p);
      if (b !== undefined) starts.push(b);
    }
  }
} else {
  const cls = rootClass(target);
  if (cls === "hkbProjectData") loader.project(target);
  else if (cls === "hkbCharacterData") loader.character(target, posix.dirname(posix.dirname(target)));
  else if (cls === "hkbBehaviorGraph") {
    const projectDir = posix.dirname(posix.dirname(target));
    for (const f of readdirSync(join(root, projectDir))) {
      if (!f.endsWith(".xml")) continue;
      const p = projectDir === "." ? f : `${projectDir}/${f}`;
      if (rootClass(p) !== "hkbProjectData") continue;
      const pr = loader.project(p);
      if (pr?.characters.some((c) => c.behaviorPath === target)) console.log(`project ${p}: uses ${target}`);
    }
    const b = loader.behavior(target);
    if (b !== undefined) starts.push(b);
  } else {
    console.error(`${target}: not a project, character or behavior packfile (root ${cls ?? "unreadable"})`);
    process.exit(2);
  }
}
const loadMs = performance.now() - t0;
gcFn?.();
const mem = process.memoryUsage();

const behaviors = [...loader.loadedBehaviors()];
let objects = 0;
const allObjects: HkObject[] = [];
for (const pf of loader.loadedPackfiles()) {
  objects += pf.objects.size;
  for (const o of pf.objects.values()) allObjects.push(o);
}
const counts = classCounts(allObjects);
let nodes = 0;
for (const b of behaviors) nodes += graphNodes(b).length;
let refs = 0;
let resolved = 0;
for (const b of behaviors) for (const r of b.references) { refs++; if (r.target !== undefined) resolved++; }
const diags = loader.diagnostics();

console.log(`root            ${root}`);
console.log(`target          ${all ? "--all (manifest)" : target}`);
console.log(`projects        ${[...loader.loadedProjects()].length}`);
console.log(`characters      ${[...loader.loadedCharacters()].length}`);
console.log(`behavior graphs ${behaviors.length}`);
console.log(`packfiles       ${[...loader.loadedPackfiles()].length}`);
console.log(`objects         ${objects} (${counts.size} classes)`);
console.log(`graph nodes     ${nodes} (reachable from root generators; generators+modifiers+states)`);
console.log(`state machines  ${counts.get("hkbStateMachine") ?? 0}, states ${counts.get("hkbStateMachineStateInfo") ?? 0}, clips ${counts.get("hkbClipGenerator") ?? 0}`);
console.log(`behavior refs   ${refs} (${resolved} resolved, ${refs - resolved} unresolved)`);
console.log(`missing files   ${loader.missing.size}${[...loader.missing].slice(0, 5).map(([p, by]) => `\n  ${p} (from ${by})`).join("")}`);
console.log(`load failures   ${loader.failures.size}${[...loader.failures].slice(0, 5).map(([p, e]) => `\n  ${p}: ${e}`).join("")}`);
console.log(`diagnostics     ${diags.length}${diags.slice(0, 5).map((d) => `\n  ${d.file} ${d.object}: ${d.message}`).join("")}`);
const first = starts[0];
if (!all && first !== undefined) {
  console.log(`closure of ${first.path}: ${graphClosure(first).length} graph files`);
  console.log(`  variables ${variables(first).length}, events ${events(first).length}`);
  if (treeDepth !== undefined) console.log(formatTree(stateMachineTree(first), Number(treeDepth)));
}
console.log(`load time       ${(loadMs / 1000).toFixed(2)} s`);
console.log(`memory          rss ${mb(mem.rss)}, heap used ${mb(mem.heapUsed)}${gcFn === undefined ? " (no --expose-gc: heap includes garbage)" : " (after gc)"}`);
