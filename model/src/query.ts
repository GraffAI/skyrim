// A small query API over loaded graphs: references out of an object, reachability walks,
// the state-machine tree, and a graph's variables and events.

import type { HkObject, hkbStateMachine, hkbStateMachineStateInfo, hkbBehaviorReferenceGenerator, hkbBehaviorGraphData__variableInfos } from "./generated/classes.ts";
import type { BehaviorFile } from "./loader.ts";
import { is } from "./packfile.ts";

function isObject(v: unknown): v is HkObject {
  return typeof v === "object" && v !== null && "$class" in v;
}

/** Objects directly referenced by `o` (through fields, arrays and nested structs), in field order. */
export function references(o: HkObject): HkObject[] {
  const out: HkObject[] = [];
  const visit = (v: unknown, top: boolean): void => {
    if (v === null || typeof v !== "object") return;
    if (Array.isArray(v)) {
      for (const x of v) visit(x, false);
      return;
    }
    if (!top && isObject(v)) {
      out.push(v);
      return;
    }
    for (const x of Object.values(v)) visit(x, false);
  };
  visit(o, true);
  return out;
}

/** The census's node definition: generators, modifiers and states. */
export function isNode(o: HkObject): boolean {
  const c = o.$class;
  return c.endsWith("Generator") || c === "hkbStateMachine" || c.endsWith("Modifier") || c === "hkbModifierList" || c === "hkbStateMachineStateInfo";
}

/** Every object reachable from `start`, depth-first pre-order, each once. */
export function reachable(start: HkObject): HkObject[] {
  const seen = new Set<HkObject>();
  const order: HkObject[] = [];
  const stack: HkObject[] = [start];
  while (stack.length > 0) {
    const o = stack.pop();
    if (o === undefined || seen.has(o)) continue;
    seen.add(o);
    order.push(o);
    const refs = references(o);
    for (let i = refs.length - 1; i >= 0; i--) {
      const r = refs[i];
      if (r !== undefined && !seen.has(r)) stack.push(r);
    }
  }
  return order;
}

/** The nodes of one graph file reachable from its root generator. */
export function graphNodes(bf: BehaviorFile): HkObject[] {
  const root = bf.graph.rootGenerator;
  return root === null ? [] : reachable(root).filter(isNode);
}

/** All graph files reachable from `bf` through behavior references (including `bf`). */
export function graphClosure(bf: BehaviorFile): BehaviorFile[] {
  const seen = new Set<BehaviorFile>();
  const stack = [bf];
  while (stack.length > 0) {
    const b = stack.pop();
    if (b === undefined || seen.has(b)) continue;
    seen.add(b);
    for (const r of b.references) if (r.target !== undefined) stack.push(r.target);
  }
  return [...seen];
}

export interface StateNode {
  readonly info: hkbStateMachineStateInfo;
  readonly name: string;
  readonly stateId: number;
  /** State machines nested under this state's generator (before any deeper state machine). */
  readonly machines: MachineNode[];
  /** Behavior references under this state's generator, resolved to their graph file when loaded. */
  readonly behaviorRefs: { readonly node: hkbBehaviorReferenceGenerator; readonly target: BehaviorFile | undefined }[];
}

export interface MachineNode {
  readonly machine: hkbStateMachine;
  readonly name: string;
  readonly startStateId: number;
  readonly states: StateNode[];
}

/**
 * The state-machine tree of a graph: each machine's states, and under each state the machines
 * (and behavior references) its generator subtree contains. Does not descend into other files;
 * follow `behaviorRefs[].target` for that.
 */
export function stateMachineTree(bf: BehaviorFile): MachineNode[] {
  const targets = new Map(bf.references.map((r) => [r.node as HkObject, r.target]));
  const below = (start: HkObject | null): { machines: MachineNode[]; refs: StateNode["behaviorRefs"] } => {
    const machines: MachineNode[] = [];
    const refs: { node: hkbBehaviorReferenceGenerator; target: BehaviorFile | undefined }[] = [];
    if (start === null) return { machines, refs };
    const seen = new Set<HkObject>();
    const stack: HkObject[] = [start];
    while (stack.length > 0) {
      const o = stack.pop();
      if (o === undefined || seen.has(o)) continue;
      seen.add(o);
      if (is(o, "hkbStateMachine")) {
        machines.push(machine(o));
        continue;
      }
      if (is(o, "hkbBehaviorReferenceGenerator")) refs.push({ node: o, target: targets.get(o) });
      const r = references(o);
      for (let i = r.length - 1; i >= 0; i--) {
        const x = r[i];
        if (x !== undefined) stack.push(x);
      }
    }
    return { machines, refs };
  };
  const machine = (sm: hkbStateMachine): MachineNode => ({
    machine: sm,
    name: sm.name,
    startStateId: sm.startStateId,
    states: sm.states.map((info) => {
      const b = below(info.generator);
      return { info, name: info.name, stateId: info.stateId, machines: b.machines, behaviorRefs: b.refs };
    }),
  });
  return below(bf.graph.rootGenerator).machines;
}

/** Render a state-machine tree as indented text. */
export function formatTree(machines: readonly MachineNode[], maxDepth = Infinity, indent = ""): string {
  const lines: string[] = [];
  const rec = (ms: readonly MachineNode[], depth: number, pad: string): void => {
    if (depth > maxDepth) return;
    for (const m of ms) {
      lines.push(`${pad}SM ${m.name} (${m.states.length} states, start ${m.startStateId})`);
      for (const s of m.states) {
        const refs = s.behaviorRefs.map((r) => ` -> ${r.target?.path ?? `${r.node.behaviorName} (unresolved)`}`).join("");
        lines.push(`${pad}  [${s.stateId}] ${s.name}${refs}`);
        rec(s.machines, depth + 1, `${pad}    `);
      }
    }
  };
  rec(machines, 0, indent);
  return lines.join("\n");
}

export interface VariableInfo {
  readonly index: number;
  readonly name: string | null;
  readonly type: hkbBehaviorGraphData__variableInfos["type"];
  readonly role: hkbBehaviorGraphData__variableInfos["role"];
  /** word value for scalar types; the quad for VECTOR4/QUATERNION; the variant object for POINTER. */
  readonly initial: unknown;
}

export function variables(bf: BehaviorFile): VariableInfo[] {
  const d = bf.data;
  if (d === undefined) return [];
  const names = d.stringData.variableNames;
  const init = d.variableInitialValues;
  return d.variableInfos.map((v, index) => {
    const word = init.wordVariableValues[index]?.value;
    let initial: unknown = word;
    if (word !== undefined && (v.type === "VARIABLE_TYPE_VECTOR4" || v.type === "VARIABLE_TYPE_QUATERNION")) initial = init.quadVariableValues[word];
    else if (word !== undefined && (v.type as string) === "VARIABLE_TYPE_POINTER") initial = init.variantVariableValues[word] ?? null;
    return { index, name: names[index] ?? null, type: v.type, role: v.role, initial };
  });
}

export interface EventInfo {
  readonly index: number;
  readonly name: string | null;
  readonly flags: readonly string[];
}

export function events(bf: BehaviorFile): EventInfo[] {
  const d = bf.data;
  if (d === undefined) return [];
  const names = d.stringData.eventNames;
  return d.eventInfos.map((e, index) => ({ index, name: names[index] ?? null, flags: e.flags }));
}

/** Count objects by class across files. */
export function classCounts(objects: Iterable<HkObject>): Map<string, number> {
  const m = new Map<string, number>();
  for (const o of objects) m.set(o.$class, (m.get(o.$class) ?? 0) + 1);
  return m;
}
