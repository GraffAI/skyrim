// Generator: scans the converted packfile XML corpus (behavior, character and project files,
// classified by root class via _manifest.tsv) and emits
//   src/generated/classes.ts  one interface per class / anonymous struct seen, with inferred TS types
//   src/generated/schema.ts   the runtime schema the decoder reads values by
// Output is derived structure only (class/field identifiers, observed enum tokens, counts).
//
// usage: node gen/generate.ts [--root DIR] [--check]
//   --check  regenerate in memory and exit 1 if the committed files differ.

import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { homedir } from "node:os";
import { parsePackfile, NULL_STRING } from "../src/xml.ts";
import type { RawParam, RawStruct } from "../src/xml.ts";
import { classifyScalar, splitWs } from "../src/values.ts";
import type { FieldSchema } from "../src/types.ts";

const ROOT_CLASSES = new Set(["hkbBehaviorGraph", "hkbCharacterData", "hkbProjectData"]);

interface Acc {
  num: boolean;
  zeroOnly: boolean; // every number seen was 0
  bool: boolean;
  str: boolean;
  cstr: boolean;
  enumVals: Set<string>;
  multiToken: boolean;
  ref: boolean;
  targets: Set<string>;
  vecShapes: Set<string>;
  struct: StructStats | undefined;
}

interface FieldStats {
  name: string;
  present: number;
  array: boolean;
  nullSeen: boolean;
  emptySeen: boolean;
  acc: Acc;
}

interface StructStats {
  name: string;
  instances: number;
  fields: Map<string, FieldStats>;
}

interface ClassStats extends StructStats {
  files: Set<string>;
  signatures: Set<string>;
}

function newAcc(): Acc {
  return {
    num: false, zeroOnly: true, bool: false, str: false, cstr: false, enumVals: new Set(), multiToken: false,
    ref: false, targets: new Set(), vecShapes: new Set(), struct: undefined,
  };
}

const structs = new Map<string, StructStats>();
const classes = new Map<string, ClassStats>();

function structStats(name: string): StructStats {
  let s = structs.get(name);
  if (s === undefined) structs.set(name, (s = { name, instances: 0, fields: new Map() }));
  return s;
}

function accumulateStruct(s: StructStats, raw: RawStruct, idClass: Map<string, string>): void {
  s.instances++;
  for (const p of raw.params) {
    let f = s.fields.get(p.name);
    if (f === undefined) {
      f = { name: p.name, present: 0, array: false, nullSeen: false, emptySeen: false, acc: newAcc() };
      s.fields.set(p.name, f);
    }
    f.present++;
    accumulateParam(s.name, f, p, idClass);
  }
}

function accumulateScalar(f: FieldStats, a: Acc, text: string, idClass: Map<string, string>): void {
  if (text === NULL_STRING) {
    f.nullSeen = true;
    a.str = true;
    return;
  }
  const c = classifyScalar(text);
  switch (c.k) {
    case "null":
      f.nullSeen = true;
      return;
    case "empty":
      f.emptySeen = true;
      return;
    case "ref": {
      a.ref = true;
      const cls = idClass.get(c.id);
      if (cls !== undefined) a.targets.add(cls);
      return;
    }
    case "bool":
      a.bool = true;
      return;
    case "num":
      a.num = true;
      if (c.v !== 0) a.zeroOnly = false;
      return;
    case "enum":
      a.enumVals.add(text.trim());
      if (c.tokens.length > 1) a.multiToken = true;
      return;
    case "vec":
      a.vecShapes.add(c.shape);
      return;
    case "str":
      a.str = true;
      return;
  }
}

function accumulateParam(owner: string, f: FieldStats, p: RawParam, idClass: Map<string, string>): void {
  const a = f.acc;
  if (p.numelements !== undefined) f.array = true;
  if (p.objects !== undefined) {
    a.struct ??= structStats(`${owner}__${p.name}`);
    for (const o of p.objects) accumulateStruct(a.struct, o, idClass);
    return;
  }
  if (p.strings !== undefined) {
    a.cstr = true;
    for (const s of p.strings) if (s === null) f.nullSeen = true;
    return;
  }
  if (p.numelements !== undefined) {
    if (p.numelements === 0) {
      f.emptySeen = true;
      return;
    }
    const t = p.text.trim();
    const elems = t.startsWith("(") ? t.split(/\)\s+\(/).map((e, i, all) => (i > 0 ? "(" : "") + e + (i < all.length - 1 ? ")" : "")) : splitWs(t);
    for (const e of elems) accumulateScalar(f, a, e, idClass);
    return;
  }
  accumulateScalar(f, a, p.text, idClass);
}

// ---------------------------------------------------------------------------------------------
// kind resolution and emission

const FLAGISH = /^FLAG_|^F_/;

function kindOf(f: FieldStats): string {
  const a = f.acc;
  let k: string;
  if (a.struct !== undefined) k = `struct:${a.struct.name}`;
  else if (a.cstr || a.str) k = "str";
  else if (a.ref) k = "ref";
  else if (a.enumVals.size > 0) {
    const allFlagish = [...a.enumVals].every((v) => v.split("|").every((t) => FLAGISH.test(t) || /^\d+$/.test(t)));
    k = a.multiToken || (a.num && a.zeroOnly) || allFlagish ? "flags" : a.num ? "str" : "enum";
  } else if (a.vecShapes.size > 0) k = a.vecShapes.size === 1 ? `vec:${[...a.vecShapes][0] ?? ""}` : "vec:*";
  else if (a.bool && !a.num) k = "bool";
  else if (a.num) k = "num";
  else if (f.array) k = "unknown";
  else if (f.nullSeen) k = "ref";
  else k = "str";
  return f.array ? `[]${k}` : k;
}

function tsIdent(name: string): string {
  return /^[A-Za-z_$][\w$]*$/.test(name) ? name : JSON.stringify(name);
}

function vecType(shape: string): string {
  if (shape === "*") return "number[][]";
  const groups = shape.split(",").map((n) => `[${Array.from({ length: Number(n) }, () => "number").join(", ")}]`);
  if (groups.length === 1) {
    if (shape === "3") return "Vec3";
    if (shape === "4") return "Vec4";
    return groups[0] ?? "number[]";
  }
  return `[${groups.map((g) => (g === "[number, number, number]" ? "Vec3" : g === "[number, number, number, number]" ? "Vec4" : g)).join(", ")}]`;
}

function tsType(f: FieldStats, kind: string): string {
  const a = f.acc;
  const base = kind.startsWith("[]") ? kind.slice(2) : kind;
  let t: string;
  if (base.startsWith("struct:")) t = base.slice(7);
  else if (base.startsWith("vec:")) t = vecType(base.slice(4));
  else {
    switch (base) {
      case "num": t = "number"; break;
      case "bool": t = "boolean"; break;
      case "str": t = "string"; break;
      case "unknown": t = "unknown"; break;
      case "enum": t = [...a.enumVals].sort().map((v) => JSON.stringify(v)).join(" | "); break;
      case "flags": {
        const toks = new Set<string>();
        let numeric = false;
        for (const v of a.enumVals) for (const tok of v.split("|")) if (/^\d+$/.test(tok)) numeric = true; else toks.add(tok);
        const u = [...toks].sort().map((v) => JSON.stringify(v));
        if (numeric || u.length === 0) u.push("`${number}`");
        t = `(${u.join(" | ")})[]`;
        break;
      }
      case "ref": {
        const targets = [...a.targets].sort();
        t = `Ref<${targets.length === 0 ? "HkObject" : targets.join(" | ")}>`;
        break;
      }
      default: t = "unknown";
    }
  }
  const nullable = f.nullSeen && (base === "ref" || base === "str");
  if (kind.startsWith("[]")) {
    const el = nullable ? `(${t} | null)` : t.includes(" | ") && !t.startsWith("(") ? `(${t})` : t;
    return `${el}[]`;
  }
  return nullable ? `${t} | null` : t;
}

function fieldSchema(f: FieldStats, instances: number): FieldSchema {
  const kind = kindOf(f);
  const base: FieldSchema = { name: f.name, kind, null: f.nullSeen, empty: f.emptySeen, optional: f.present < instances };
  return kind.endsWith("ref") ? { ...base, targets: [...f.acc.targets].sort() } : base;
}

function fieldDoc(fs: FieldSchema): string {
  const notes: string[] = [`kind ${fs.kind}`];
  if (fs.null) notes.push("observed null");
  if (fs.empty) notes.push("observed empty");
  if (fs.optional) notes.push("absent in some instances");
  return notes.join("; ");
}

function emitInterface(lines: string[], name: string, s: StructStats, extendsClause: string, doc: string): void {
  lines.push(`/** ${doc} */`);
  lines.push(`export interface ${name}${extendsClause} {`);
  for (const f of s.fields.values()) {
    const fs = fieldSchema(f, s.instances);
    lines.push(`  /** ${fieldDoc(fs)} */`);
    lines.push(`  ${tsIdent(f.name)}${fs.optional ? "?" : ""}: ${tsType(f, fs.kind)};`);
  }
  lines.push("}", "");
}

function generate(root: string): { classesTs: string; schemaTs: string; summary: string } {
  const manifest = readFileSync(join(root, "_manifest.tsv"), "utf8");
  const files: string[] = [];
  for (const line of manifest.split("\n")) {
    const cols = line.split("\t");
    if (cols[0] === "ok" && ROOT_CLASSES.has(cols[2] ?? "") && cols[5] !== undefined) {
      files.push(cols[5].replace(/\.hkx$/i, ".xml"));
    }
  }
  files.sort();
  let objects = 0;
  for (const rel of files) {
    const pf = parsePackfile(readFileSync(join(root, rel), "latin1"));
    const idClass = new Map(pf.objects.map((o) => [o.id, o.class]));
    for (const o of pf.objects) {
      objects++;
      let c = classes.get(o.class);
      if (c === undefined) {
        c = { name: o.class, instances: 0, fields: new Map(), files: new Set(), signatures: new Set() };
        classes.set(o.class, c);
      }
      c.files.add(rel);
      c.signatures.add(o.signature);
      accumulateStruct(c, o, idClass);
    }
  }

  const classNames = [...classes.keys()].sort();
  const structNames = [...structs.keys()].sort();
  const header = [
    "// GENERATED by gen/generate.ts from the converted vanilla packfile XML corpus. Do not edit.",
    `// Corpus: ${files.length} files (root class hkbBehaviorGraph | hkbCharacterData | hkbProjectData), ${objects} objects,`,
    `// ${classNames.length} classes, ${structNames.length} anonymous structs. Derived structure only: identifiers and counts.`,
    "",
  ];
  const lines = [...header, `import type { Ref, HkObjectBase, Vec3, Vec4 } from "../types.ts";`, ""];
  lines.push("// Anonymous structs are named <owner class>__<field>, since the XML does not name them.", "");
  for (const n of structNames) {
    const s = structs.get(n);
    if (s !== undefined) emitInterface(lines, n, s, "", `struct seen ${s.instances} times`);
  }
  for (const n of classNames) {
    const c = classes.get(n);
    if (c !== undefined) {
      emitInterface(lines, n, c, ` extends HkObjectBase<${JSON.stringify(n)}>`, `${c.instances} instances in ${c.files.size} files; signature ${[...c.signatures].join(", ")}`);
    }
  }
  lines.push("/** Every class observed in the corpus. Discriminate on `$class`. */");
  lines.push(`export type HkObject =\n${classNames.map((n) => `  | ${n}`).join("\n")};`, "");
  lines.push("/** Class name -> interface. */");
  lines.push("export interface HkClassMap {");
  for (const n of classNames) lines.push(`  ${n}: ${n};`);
  lines.push("}", "", "export type HkClassName = keyof HkClassMap;", "");
  // Vec3/Vec4 may be unused; reference them so the import is always valid under noUnusedLocals.
  lines.push("export type { Vec3, Vec4 };", "");

  const schema = {
    corpus: { files: files.length, objects },
    classes: Object.fromEntries(
      classNames.map((n) => {
        const c = classes.get(n);
        if (c === undefined) throw new Error(n);
        return [n, { signatures: [...c.signatures], instances: c.instances, files: c.files.size, fields: [...c.fields.values()].map((f) => fieldSchema(f, c.instances)) }];
      }),
    ),
    structs: Object.fromEntries(
      structNames.map((n) => {
        const s = structs.get(n);
        if (s === undefined) throw new Error(n);
        return [n, { fields: [...s.fields.values()].map((f) => fieldSchema(f, s.instances)) }];
      }),
    ),
  };
  const schemaTs = [
    ...header,
    `import type { Schema } from "../types.ts";`,
    "",
    `export const SCHEMA: Schema = ${JSON.stringify(schema, null, 1)};`,
    "",
  ].join("\n");
  const summary = `${files.length} files, ${objects} objects, ${classNames.length} classes, ${structNames.length} structs`;
  return { classesTs: lines.join("\n"), schemaTs, summary };
}

function main(): void {
  const args = process.argv.slice(2);
  let root = join(homedir(), "skyrim-data-extracted", "xml");
  const ri = args.indexOf("--root");
  if (ri >= 0) root = args[ri + 1] ?? root;
  const check = args.includes("--check");
  if (!existsSync(join(root, "_manifest.tsv"))) {
    console.error(`no corpus at ${root} (need _manifest.tsv)`);
    process.exit(check ? 0 : 2);
  }
  const t0 = performance.now();
  const { classesTs, schemaTs, summary } = generate(root);
  const outDir = join(dirname(fileURLToPath(import.meta.url)), "..", "src", "generated");
  const targets: [string, string][] = [[join(outDir, "classes.ts"), classesTs], [join(outDir, "schema.ts"), schemaTs]];
  if (check) {
    const stale = targets.filter(([p, c]) => !existsSync(p) || readFileSync(p, "utf8") !== c).map(([p]) => p);
    if (stale.length > 0) {
      console.error(`stale generated files: ${stale.join(", ")}`);
      process.exit(1);
    }
    console.log(`generated files are up to date (${summary})`);
    return;
  }
  for (const [p, c] of targets) writeFileSync(p, c);
  console.log(`wrote ${targets.map(([p]) => p).join(", ")}: ${summary} in ${((performance.now() - t0) / 1000).toFixed(1)} s`);
}

main();
