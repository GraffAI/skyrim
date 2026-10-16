# census — Skyrim SE behavior census (006 M35)

Counts what the Havok behavior data in `Skyrim - Animations.bsa` uses, so the clean-room
engine knows which classes, variables, events and annotations it must support, and in what
proportion. Output is aggregate statistics plus identifier strings only — no game data:

- `projects/skyrim/census/census.json` — everything, machine-readable
- `projects/skyrim/census/CENSUS.md` — tables, rendered from the JSON

## Rerun

From the worktree root, after `tools/hkx/bulk_convert.sh graph` and `bulk_convert.sh anim 200`:

```sh
python3 -I projects/skyrim/tools/census/test_census.py      # unit tests, hand-made packfiles
python3 -I projects/skyrim/tools/census/census.py           # ~7 s on the M1 Max with the full animation set
python3 -I projects/skyrim/tools/census/render_md.py
```

Stdlib only (`xml.etree`, `json`). Flags: `--xml` (default `~/skyrim-data-extracted/xml`),
`--anim-xml` (`~/skyrim-data-extracted/xml-anim`, every animation, from `bulk_convert.sh anim-all`;
when absent §4b falls back to the sample), `--anim-sample-xml` (`~/skyrim-data-extracted/xml-anim-sample`), `--raw`
(`~/skyrim-data-extracted/raw`), `--out` (`projects/skyrim/census`). Inputs are extracted
game data and are treated as untrusted: run with `-I`, never from inside the data dirs.

## What it reads

- hkxc's hkpackfile XML (`<hksection name="__data__">`, top-level `<hkobject name="#NNNN"
  class=...>`, references as `#NNNN` tokens in `hkparam` text). Every class-bearing object
  in hkxc output is top-level (`grep -rho 'class="' xml | wc -l` equals the count of
  two-tab-indented `<hkobject name=... class=` lines, 86,411), so nested `<hkobject>`s are
  structs, not class instances.
- `meshes/animationdatasinglefile.txt`: `N`, `N` project names, then per project `L` and `L`
  lines; when the project block's flag (line `2 + paths`) is `1`, `M` and `M` lines of motion
  data follow. Framing check:

  ```sh
  python3 -I -c "
  L=open('$HOME/skyrim-data-extracted/raw/meshes/animationdatasinglefile.txt',encoding='latin-1').read().split('\n')
  n=int(L[0]); i=1+n
  for _ in range(n):
      c=int(L[i]); b=L[i+1:i+1+c]; i+=1+c
      if b[2+int(b[1])].strip()=='1': i+=1+int(L[i])
  print(n, i, len(L))"      # 429 170724 170725 (last element is the trailing newline)
  ```

## Definitions

- **node** = generator (class ends in `Generator`, or `hkbStateMachine`), modifier (ends in
  `Modifier`, or `hkbModifierList`), or state (`hkbStateMachineStateInfo`). See `role()`.
- **max_sm_depth** = most `hkbStateMachine`s on one reference path from `rootGenerator`,
  following every `#NNNN` reference in the file; **max_sm_depth_through_references** also
  descends through `hkbBehaviorReferenceGenerator.behaviorName`, resolved against the
  project dir (parent of the graph's directory).
- **actor group** = `meshes/actors/<dir>` (`ambient`, `dlc01`, `dlc02` one level deeper).
