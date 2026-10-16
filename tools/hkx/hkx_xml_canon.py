#!/usr/bin/env python3
"""Canonicalise a Havok packfile XML (hkpackfile, hk_2010.2.0-r1) for semantic comparison.

Two XMLs of the same object graph can differ in object order and in the "#NNNN" names
(hkxcmd, HavokBehaviorPostProcess and serde-hkx all number differently). This walks the
graph depth-first from `toplevelobject`, renames every object reference to the order it was
first reached, and prints one line per object with its class, signature and params, with
whitespace collapsed and floats normalised to %.6f. Equal output == same graph.

Usage:  python3 -I hkx_xml_canon.py FILE.xml            # canonical text on stdout
        python3 -I hkx_xml_canon.py --cmp A.xml B.xml   # exit 0 if semantically equal
Options: --keep-negzero  keep "-0.000000" distinct from "0.000000" (default folds them)
"""
import re
import sys
import hashlib
import xml.etree.ElementTree as ET

REF = re.compile(r"#\d+")
FLOAT = re.compile(r"^-?\d+\.\d+(e[-+]?\d+)?$", re.I)


def canon(path, keep_negzero=False):
    root = ET.parse(path).getroot()
    if root.tag != "hkpackfile":
        raise SystemExit(f"{path}: root is <{root.tag}>, not <hkpackfile>")
    objs = {}
    for sec in root.findall("hksection"):
        for o in sec.findall("hkobject"):
            objs[o.get("name")] = o
    ids, order, out = {}, [], []

    def ref(name):
        if name not in objs:
            return "?" + name  # dangling reference
        if name not in ids:
            ids[name] = f"@{len(ids)}"
            order.append(name)
        return ids[name]

    def flags(t):
        # "A|B|0x1680" (hkxcmd) vs "B|A|5760" (serde-hkx): sort the names, sum the numbers
        names, num = set(), 0
        for p in t.split("|"):
            if re.fullmatch(r"-?(0x[0-9a-f]+|\d+)", p, re.I):
                num += int(p, 0)
            elif p and not p.endswith("_NONE"):  # *_NONE is 0
                names.add(p)
        return "|".join(sorted(names) + ([str(num)] if num else [])) or "0"

    def tok(t):
        if "|" in t:
            return flags(t)
        if REF.fullmatch(t):
            return ref(t)
        if FLOAT.match(t):
            s = "%.6f" % float(t)
            if not keep_negzero and s == "-0.000000":
                s = "0.000000"
            return s
        return t

    def text(s):
        s = (s or "").strip()
        if not s:
            return ""
        # vectors "(x y z)" and arrays of ints/floats/refs: tokenise on whitespace and parens
        return " ".join(tok(p) for p in s.replace("(", " ( ").replace(")", " ) ").split())

    def body(el, depth):
        lines = []
        for c in el:
            if c.tag == "hkparam":
                n = c.get("numelements")
                head = f"{'  '*depth}{c.get('name')}" + (f"[{n}]" if n is not None else "")
                if len(c):  # struct array / inline struct / cstring array
                    lines.append(head + ":")
                    for sub in c:
                        if sub.tag == "hkobject":
                            lines.append(f"{'  '*(depth+1)}{{")
                            lines.extend(body(sub, depth + 2))
                            lines.append(f"{'  '*(depth+1)}}}")
                        else:
                            lines.append(f"{'  '*(depth+1)}<{sub.tag}>{text(sub.text)}")
                else:
                    lines.append(f"{head}={text(c.text)}")
        return lines

    ref(root.get("toplevelobject"))
    i = 0
    while i < len(order):
        name = order[i]
        o = objs[name]
        out.append(f"{ids[name]} {o.get('class')} {o.get('signature')}")
        out.extend(body(o, 1))
        i += 1
    unreached = sorted(set(objs) - set(ids))
    out.append(f"# objects={len(objs)} reached={len(ids)} unreached={len(unreached)}")
    for u in unreached:
        out.append(f"# unreached {objs[u].get('class')}")
    return "\n".join(out) + "\n"


def main(argv):
    keep = "--keep-negzero" in argv
    argv = [a for a in argv if a != "--keep-negzero"]
    if argv and argv[0] == "--cmp":
        a, b = canon(argv[1], keep), canon(argv[2], keep)
        ha, hb = (hashlib.sha256(x.encode()).hexdigest()[:16] for x in (a, b))
        if a == b:
            print(f"EQUAL {ha} ({a.count(chr(10))} lines)")
            return 0
        al, bl = a.splitlines(), b.splitlines()
        for k, (x, y) in enumerate(zip(al, bl)):
            if x != y:
                print(f"DIFF at canonical line {k+1}:\n  A: {x}\n  B: {y}")
                break
        else:
            print(f"DIFF length {len(al)} vs {len(bl)}")
        return 1
    sys.stdout.write(canon(argv[0], keep))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
