// Scalar classification and parsing of hkparam text, shared by the generator (to infer kinds)
// and the decoder (to read values by their generated kind).

export type ScalarClass =
  | { readonly k: "null" }
  | { readonly k: "empty" }
  | { readonly k: "ref"; readonly id: string }
  | { readonly k: "bool"; readonly v: boolean }
  | { readonly k: "num"; readonly v: number }
  | { readonly k: "enum"; readonly tokens: readonly string[] }
  | { readonly k: "vec"; readonly shape: string }
  | { readonly k: "str" };

const NUM_RE = /^[-+]?(?:\d+\.?\d*(?:[eE][-+]?\d+)?|\.\d+(?:[eE][-+]?\d+)?|NaN|nan|inf|-?inf|Infinity)$/;
const ENUM_TOKEN_RE = /^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$/;
const REF_RE = /^#\d+$/;
const VEC_RE = /^(?:\(\s*[^()]*\))+$/;

export function parseNumber(t: string): number {
  switch (t) {
    case "NaN":
    case "nan":
      return NaN;
    case "inf":
    case "Infinity":
    case "+inf":
      return Infinity;
    case "-inf":
      return -Infinity;
    default:
      return Number(t);
  }
}

/** Group sizes of a parenthesised vector/matrix, e.g. "(1 2 3)(4 5 6 7)" -> "3,4". */
export function vecShape(t: string): string {
  const sizes: number[] = [];
  for (const g of t.matchAll(/\(([^()]*)\)/g)) sizes.push(splitWs(g[1] ?? "").length);
  return sizes.join(",");
}

export function parseVecGroups(t: string): number[][] {
  const out: number[][] = [];
  for (const g of t.matchAll(/\(([^()]*)\)/g)) out.push(splitWs(g[1] ?? "").map(parseNumber));
  return out;
}

export function splitWs(t: string): string[] {
  const s = t.trim();
  return s.length === 0 ? [] : s.split(/\s+/);
}

export function classifyScalar(raw: string): ScalarClass {
  const t = raw.trim();
  if (t.length === 0) return { k: "empty" };
  if (t === "null") return { k: "null" };
  if (t === "true") return { k: "bool", v: true };
  if (t === "false") return { k: "bool", v: false };
  if (REF_RE.test(t)) return { k: "ref", id: t };
  if (NUM_RE.test(t)) return { k: "num", v: parseNumber(t) };
  if (t.charCodeAt(0) === 40 /* ( */ && VEC_RE.test(t)) return { k: "vec", shape: vecShape(t) };
  const parts = t.split("|");
  if (parts.every((p) => ENUM_TOKEN_RE.test(p) || /^\d+$/.test(p)) && parts.some((p) => ENUM_TOKEN_RE.test(p))) {
    return { k: "enum", tokens: parts };
  }
  return { k: "str" };
}

/** Flag-set text: "A|B" -> ["A","B"]; "0" / "" -> []. */
export function parseFlags(raw: string): string[] {
  const t = raw.trim();
  if (t.length === 0 || t === "0") return [];
  return t.split("|");
}
