// A dependency-free reader for Havok packfile XML (the serde-hkx 2.0.0 / hkxcmd dialect).
// Clean side: written from the XML's own structure, no third-party source consulted.
//
// Two layers:
//   tokenize(): a small XML tokenizer (tags, text, comments/PI/doctype skipped, entities decoded).
//   parsePackfile(): builds raw objects: <hkobject name class signature> with <hkparam> children,
//   where a param holds either text, <hkcstring> children, or nested anonymous <hkobject> structs.

export type Token =
  | { readonly t: "open"; readonly name: string; readonly attrs: Record<string, string>; readonly selfClosing: boolean }
  | { readonly t: "close"; readonly name: string }
  | { readonly t: "text"; readonly text: string };

const NAMED_ENTITIES: Record<string, string> = { lt: "<", gt: ">", amp: "&", quot: '"', apos: "'" };

export function decodeEntities(s: string): string {
  if (s.indexOf("&") < 0) return s;
  return s.replace(/&(#x[0-9a-fA-F]+|#[0-9]+|[a-zA-Z]+);/g, (m, body: string) => {
    if (body.charCodeAt(0) === 35 /* # */) {
      const code = body[1] === "x" ? parseInt(body.slice(2), 16) : parseInt(body.slice(1), 10);
      return Number.isFinite(code) ? String.fromCodePoint(code) : m;
    }
    return NAMED_ENTITIES[body] ?? m;
  });
}

export class XmlError extends Error {
  readonly offset: number;
  constructor(message: string, offset: number) {
    super(`${message} at offset ${offset}`);
    this.offset = offset;
  }
}

const ATTR_RE = /([A-Za-z_:][-A-Za-z0-9_:.]*)\s*=\s*("([^"]*)"|'([^']*)')/g;

function parseAttrs(src: string): Record<string, string> {
  const attrs: Record<string, string> = {};
  if (src.length === 0) return attrs;
  ATTR_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = ATTR_RE.exec(src)) !== null) {
    const key = m[1];
    if (key !== undefined) attrs[key] = decodeEntities(m[3] ?? m[4] ?? "");
  }
  return attrs;
}

/** Tokenize an XML document. Whitespace-only text between tags is emitted too; callers ignore it. */
export function* tokenize(src: string): Generator<Token> {
  let i = 0;
  const n = src.length;
  while (i < n) {
    const lt = src.indexOf("<", i);
    if (lt < 0) {
      yield { t: "text", text: decodeEntities(src.slice(i)) };
      return;
    }
    if (lt > i) yield { t: "text", text: decodeEntities(src.slice(i, lt)) };
    const c = src.charCodeAt(lt + 1);
    if (c === 33 /* ! */) {
      if (src.startsWith("<!--", lt)) {
        const end = src.indexOf("-->", lt + 4);
        if (end < 0) throw new XmlError("unterminated comment", lt);
        i = end + 3;
      } else if (src.startsWith("<![CDATA[", lt)) {
        const end = src.indexOf("]]>", lt + 9);
        if (end < 0) throw new XmlError("unterminated CDATA", lt);
        yield { t: "text", text: src.slice(lt + 9, end) };
        i = end + 3;
      } else {
        const end = src.indexOf(">", lt);
        if (end < 0) throw new XmlError("unterminated declaration", lt);
        i = end + 1;
      }
      continue;
    }
    if (c === 63 /* ? */) {
      const end = src.indexOf("?>", lt + 2);
      if (end < 0) throw new XmlError("unterminated processing instruction", lt);
      i = end + 2;
      continue;
    }
    const gt = src.indexOf(">", lt);
    if (gt < 0) throw new XmlError("unterminated tag", lt);
    if (c === 47 /* / */) {
      yield { t: "close", name: src.slice(lt + 2, gt).trim() };
      i = gt + 1;
      continue;
    }
    let inner = src.slice(lt + 1, gt);
    const selfClosing = inner.endsWith("/");
    if (selfClosing) inner = inner.slice(0, -1);
    let sp = 0;
    while (sp < inner.length && !isSpace(inner.charCodeAt(sp))) sp++;
    const name = inner.slice(0, sp);
    if (name.length === 0) throw new XmlError("empty tag name", lt);
    yield { t: "open", name, attrs: parseAttrs(inner.slice(sp)), selfClosing };
    i = gt + 1;
  }
}

function isSpace(c: number): boolean {
  return c === 32 || c === 9 || c === 10 || c === 13;
}

// ---------------------------------------------------------------------------------------------
// Raw packfile structure

/** One <hkparam>. Exactly one of text / strings / objects carries the value. */
export interface RawParam {
  readonly name: string;
  /** The numelements attribute when present (it marks an array). */
  readonly numelements: number | undefined;
  /** Concatenated, entity-decoded text content (untrimmed). */
  readonly text: string;
  /** <hkcstring> children; null for the "␀" (U+2400) null-string marker. */
  readonly strings: (string | null)[] | undefined;
  /** Anonymous nested <hkobject> children (structs). */
  readonly objects: RawStruct[] | undefined;
}

export interface RawStruct {
  readonly params: RawParam[];
}

export interface RawObject extends RawStruct {
  readonly id: string;
  readonly class: string;
  readonly signature: string;
}

export interface RawPackfile {
  readonly classversion: string;
  readonly contentsversion: string;
  readonly toplevelobject: string;
  readonly objects: RawObject[];
}

/** The null-string marker hkxcmd/serde-hkx write for a null hkStringPtr / hkcstring. */
export const NULL_STRING = "␀";

interface ParamBuilder {
  name: string;
  numelements: number | undefined;
  text: string;
  strings: (string | null)[] | undefined;
  objects: RawStruct[] | undefined;
  inString: string | undefined;
}

export function parsePackfile(src: string): RawPackfile {
  let classversion = "";
  let contentsversion = "";
  let toplevelobject = "";
  const objects: RawObject[] = [];
  // Stack of open structs (top-level object or nested anonymous struct) and params.
  const structStack: { params: RawParam[]; obj: { id: string; class: string; signature: string } | undefined }[] = [];
  const paramStack: ParamBuilder[] = [];
  let sawPackfile = false;
  const open: string[] = [];

  const finishParam = (p: ParamBuilder): RawParam => ({
    name: p.name,
    numelements: p.numelements,
    text: p.text,
    strings: p.strings,
    objects: p.objects,
  });

  for (const tok of tokenize(src)) {
    if (tok.t === "text") {
      const p = paramStack[paramStack.length - 1];
      if (p === undefined) continue;
      if (p.inString !== undefined) p.inString += tok.text;
      else p.text += tok.text;
      continue;
    }
    if (tok.t === "open") {
      if (!tok.selfClosing) open.push(tok.name);
      switch (tok.name) {
        case "hkpackfile":
          sawPackfile = true;
          classversion = tok.attrs["classversion"] ?? "";
          contentsversion = tok.attrs["contentsversion"] ?? "";
          toplevelobject = tok.attrs["toplevelobject"] ?? "";
          break;
        case "hksection":
          break;
        case "hkobject": {
          const name = tok.attrs["name"];
          const cls = tok.attrs["class"];
          const obj =
            name !== undefined && cls !== undefined && paramStack.length === 0
              ? { id: name, class: cls, signature: tok.attrs["signature"] ?? "" }
              : undefined;
          const frame = { params: [] as RawParam[], obj };
          if (tok.selfClosing) closeStruct(frame);
          else structStack.push(frame);
          break;
        }
        case "hkparam": {
          const ne = tok.attrs["numelements"];
          const p: ParamBuilder = {
            name: tok.attrs["name"] ?? "",
            numelements: ne === undefined ? undefined : Number(ne),
            text: "",
            strings: undefined,
            objects: undefined,
            inString: undefined,
          };
          if (tok.selfClosing) structTop().params.push(finishParam(p));
          else paramStack.push(p);
          break;
        }
        case "hkcstring": {
          const p = paramStack[paramStack.length - 1];
          if (p === undefined) throw new Error("<hkcstring> outside <hkparam>");
          p.strings ??= [];
          if (tok.selfClosing) p.strings.push("");
          else p.inString = "";
          break;
        }
        default:
          throw new Error(`unexpected element <${tok.name}>`);
      }
      continue;
    }
    // close
    const expected = open.pop();
    if (expected !== tok.name) throw new Error(`mismatched </${tok.name}> (open: <${expected ?? "none"}>)`);
    switch (tok.name) {
      case "hkpackfile":
      case "hksection":
        break;
      case "hkobject": {
        const frame = structStack.pop();
        if (frame === undefined) throw new Error("unbalanced </hkobject>");
        closeStruct(frame);
        break;
      }
      case "hkparam": {
        const p = paramStack.pop();
        if (p === undefined) throw new Error("unbalanced </hkparam>");
        structTop().params.push(finishParam(p));
        break;
      }
      case "hkcstring": {
        const p = paramStack[paramStack.length - 1];
        if (p?.inString === undefined || p.strings === undefined) throw new Error("unbalanced </hkcstring>");
        p.strings.push(p.inString === NULL_STRING ? null : p.inString);
        p.inString = undefined;
        break;
      }
      default:
        throw new Error(`unexpected </${tok.name}>`);
    }
  }
  if (!sawPackfile) throw new Error("not a Havok packfile (no <hkpackfile>)");
  if (open.length > 0 || structStack.length > 0 || paramStack.length > 0) throw new Error("unterminated packfile");
  return { classversion, contentsversion, toplevelobject, objects };

  function structTop(): { params: RawParam[] } {
    const s = structStack[structStack.length - 1];
    if (s === undefined) throw new Error("<hkparam> outside <hkobject>");
    return s;
  }

  function closeStruct(frame: { params: RawParam[]; obj: { id: string; class: string; signature: string } | undefined }): void {
    if (frame.obj !== undefined) {
      objects.push({ ...frame.obj, params: frame.params });
      return;
    }
    const p = paramStack[paramStack.length - 1];
    if (p === undefined) throw new Error("anonymous <hkobject> outside <hkparam>");
    p.objects ??= [];
    p.objects.push({ params: frame.params });
  }
}
