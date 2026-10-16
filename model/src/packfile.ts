// Object table and reference resolution: turns a raw packfile into typed objects, decoding each
// hkparam by the kind the generator recorded for it, and replacing `#NNNN` with the target object.

import { parsePackfile, NULL_STRING } from "./xml.ts";
import type { RawParam, RawStruct, RawPackfile } from "./xml.ts";
import { classifyScalar, parseFlags, parseNumber, parseVecGroups, splitWs } from "./values.ts";
import { SCHEMA } from "./generated/schema.ts";
import type { FieldSchema, Schema } from "./types.ts";
import type { HkObject, HkClassMap, HkClassName, hkRootLevelContainer } from "./generated/classes.ts";

/** A problem found while decoding; the loader never throws on these, it reports them. */
export interface Diagnostic {
  readonly file: string;
  readonly object: string;
  readonly message: string;
}

export interface Packfile {
  /** Path relative to the loader root (lower-case, `/`), or whatever the caller passed. */
  readonly path: string;
  readonly contentsversion: string;
  /** The toplevelobject (always an hkRootLevelContainer in the vanilla corpus). */
  readonly root: hkRootLevelContainer;
  /** The object table, by packfile name (`#0042`), in file order. */
  readonly objects: ReadonlyMap<string, HkObject>;
  readonly diagnostics: readonly Diagnostic[];
}

type Mutable = Record<string, unknown>;

interface FieldIndex {
  readonly byName: ReadonlyMap<string, FieldSchema>;
}

const classIndex = new Map<string, FieldIndex>();
const structIndex = new Map<string, FieldIndex>();

function indexOf(cache: Map<string, FieldIndex>, table: Schema["classes"] | Schema["structs"], name: string): FieldIndex | undefined {
  let ix = cache.get(name);
  if (ix === undefined) {
    const s = table[name];
    if (s === undefined) return undefined;
    ix = { byName: new Map(s.fields.map((f) => [f.name, f])) };
    cache.set(name, ix);
  }
  return ix;
}

export function isKnownClass(name: string): name is HkClassName {
  return Object.hasOwn(SCHEMA.classes, name);
}

class Decoder {
  readonly diagnostics: Diagnostic[] = [];
  readonly table = new Map<string, Mutable>();
  private current = "";
  private readonly file: string;

  constructor(file: string) {
    this.file = file;
  }

  diag(message: string): void {
    this.diagnostics.push({ file: this.file, object: this.current, message });
  }

  resolve(id: string): unknown {
    const t = this.table.get(id);
    if (t === undefined) {
      this.diag(`dangling reference ${id}`);
      return null;
    }
    return t;
  }

  fill(target: Mutable, raw: RawStruct, ix: FieldIndex | undefined, owner: string, id?: string): void {
    if (id !== undefined) this.current = id;
    if (ix === undefined) this.diag(`unknown ${id !== undefined ? "class" : "struct"} ${owner}; decoded heuristically`);
    for (const p of raw.params) {
      const fs = ix?.byName.get(p.name);
      if (ix !== undefined && fs === undefined) this.diag(`unknown field ${owner}.${p.name}; decoded heuristically`);
      target[p.name] = fs === undefined ? this.guess(p, owner) : this.value(fs.kind, p, owner);
    }
  }

  value(kind: string, p: RawParam, owner: string): unknown {
    if (kind.startsWith("[]")) {
      const el = kind.slice(2);
      if (p.objects !== undefined) return p.objects.map((o) => this.struct(el, o, `${owner}__${p.name}`));
      if (p.strings !== undefined) return p.strings.slice();
      if (p.numelements === 0) return [];
      return this.textArray(el, p.text);
    }
    if (kind.startsWith("struct:")) {
      const o = p.objects?.[0];
      if (o === undefined) {
        this.diag(`expected struct in ${owner}.${p.name}`);
        return null;
      }
      return this.struct(kind, o, `${owner}__${p.name}`);
    }
    return this.scalar(kind, p.text);
  }

  struct(kind: string, raw: RawStruct, fallbackName: string): Mutable {
    const name = kind.startsWith("struct:") ? kind.slice(7) : fallbackName;
    const out: Mutable = {};
    this.fill(out, raw, indexOf(structIndex, SCHEMA.structs, name), name);
    return out;
  }

  textArray(el: string, text: string): unknown[] {
    if (el.startsWith("vec:")) {
      const groups = parseVecGroups(text);
      const per = el === "vec:*" ? 1 : el.slice(4).split(",").length;
      if (per === 1) return groups;
      const out: number[][][] = [];
      for (let i = 0; i < groups.length; i += per) out.push(groups.slice(i, i + per));
      return out;
    }
    return splitWs(text).map((t) => this.scalar(el, t));
  }

  scalar(kind: string, text: string): unknown {
    switch (kind) {
      case "num":
        return parseNumber(text.trim());
      case "bool":
        return text.trim() === "true";
      case "str":
        return text === NULL_STRING ? null : text.includes("\n") ? text.trim() : text;
      case "enum":
        return text.trim();
      case "flags":
        return parseFlags(text);
      case "ref": {
        const t = text.trim();
        return t === "null" || t === "" ? null : this.resolve(t);
      }
      case "unknown":
        return this.guessScalar(text);
      default:
        if (kind.startsWith("vec:")) {
          const g = parseVecGroups(text);
          return g.length === 1 ? g[0] : g;
        }
        this.diag(`unhandled kind ${kind}`);
        return text;
    }
  }

  guess(p: RawParam, owner: string): unknown {
    if (p.objects !== undefined) {
      const structs = p.objects.map((o) => this.struct("", o, `${owner}__${p.name}`));
      return p.numelements === undefined ? structs[0] : structs;
    }
    if (p.strings !== undefined) return p.strings.slice();
    if (p.numelements !== undefined) {
      const t = p.text.trim();
      return t.startsWith("(") ? parseVecGroups(t) : splitWs(t).map((x) => this.guessScalar(x));
    }
    return this.guessScalar(p.text);
  }

  guessScalar(text: string): unknown {
    if (text === NULL_STRING) return null;
    const c = classifyScalar(text);
    switch (c.k) {
      case "null":
        return null;
      case "empty":
        return "";
      case "ref":
        return this.resolve(c.id);
      case "bool":
      case "num":
        return c.v;
      case "vec": {
        const g = parseVecGroups(text);
        return g.length === 1 ? g[0] : g;
      }
      default:
        return text;
    }
  }
}

/** Decode a raw packfile into typed objects with resolved references. */
export function buildPackfile(raw: RawPackfile, path: string): Packfile {
  const d = new Decoder(path);
  // Pass 1: object shells, so references (forward or cyclic) resolve to the final objects.
  for (const o of raw.objects) {
    const shell: Mutable = {};
    Object.defineProperty(shell, "$class", { value: o.class, enumerable: true });
    Object.defineProperty(shell, "$id", { value: o.id, enumerable: true });
    Object.defineProperty(shell, "$file", { value: path, enumerable: false });
    if (d.table.has(o.id)) d.diag(`duplicate object name ${o.id}`);
    d.table.set(o.id, shell);
  }
  // Pass 2: fields.
  for (const o of raw.objects) {
    const shell = d.table.get(o.id);
    if (shell !== undefined) d.fill(shell, o, indexOf(classIndex, SCHEMA.classes, o.class), o.class, o.id);
  }
  const root = d.table.get(raw.toplevelobject);
  if (root === undefined || root["$class"] !== "hkRootLevelContainer") {
    throw new Error(`${path}: toplevelobject ${raw.toplevelobject} is not an hkRootLevelContainer`);
  }
  return {
    path,
    contentsversion: raw.contentsversion,
    root: root as unknown as hkRootLevelContainer,
    objects: d.table as unknown as ReadonlyMap<string, HkObject>,
    diagnostics: d.diagnostics,
  };
}

export function readPackfile(xml: string, path: string): Packfile {
  return buildPackfile(parsePackfile(xml), path);
}

/** The named variants of the root container, e.g. `hkbBehaviorGraph` -> the graph object. */
export function rootVariant<C extends HkClassName>(pf: Packfile, cls: C): HkClassMap[C] | undefined {
  for (const v of pf.root.namedVariants) {
    const o = v.variant as HkObject | null;
    if (o !== null && o.$class === cls) return o as HkClassMap[C];
  }
  return undefined;
}

/** Narrowing helper: `is(o, "hkbStateMachine")`. */
export function is<C extends HkClassName>(o: unknown, cls: C): o is HkClassMap[C] {
  return typeof o === "object" && o !== null && (o as { $class?: unknown }).$class === cls;
}

/** All objects of one class in a packfile. */
export function objectsOf<C extends HkClassName>(pf: Packfile, cls: C): HkClassMap[C][] {
  const out: HkClassMap[C][] = [];
  for (const o of pf.objects.values()) if (is(o, cls)) out.push(o);
  return out;
}
