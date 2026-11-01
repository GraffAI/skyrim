# tools/slice — the first slice's names, measured (006 M44)

Measurement scripts behind `docs/design/evidence/006-m44-slice-names.md`: which graph variables
and events the player's locomotion and one-handed light attack touch, read from the stock
behaviour graphs' XML (the serde-hkx conversion, `TOOLCHAIN.md`). Standard library only, run with
`python3 -I`. They read `~/skyrim-data-extracted/xml/meshes/actors/character/behaviors/` (I152: the
data never enters git; names and counts do) — on 2026-10-19 that tree existed on `aubron-mini`
only, so each script was piped over ssh:

```sh
cd projects/skyrim/tools/slice
(cat lib.py; echo "sys.argv=['x','<file>.xml','<args>']"; cat <script>.py) | ssh mini python3 -I -
(cat lib.py; echo "SPEC=[]"; cat slice.py comps.py) | ssh mini python3 -I - | tail -1 > comps.json
python3 -I final.py     # the unions, the counts and the classification columns
```

`final.py` also reads `cls.json` and `contract_min.json`, cut from `semantics/`'s output JSON
on mini (DIRTY-SIDE: the engine-input / engine-sent classes); without them it still prints the
names. These are one night's measurement scripts, kept so the numbers in the record can be
re-derived, not a maintained tool. `names.json` (the 53 variables and 88 events, the exit's
coverage list; written 2026-11-01 in M44 Part 3 from a fresh `comps.json` on mini and
`final.py`'s `collect()`, names only — its `_source` says how) is what the coverage report reads.
