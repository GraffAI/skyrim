# model: a typed in-memory model of converted behavior graphs

This TypeScript package (006 M35) loads Havok packfile XML into typed objects with every
reference resolved. It reads the serde-hkx 2.0.0 output under `~/skyrim-data-extracted/xml`
(`tools/hkx/RESULT.md` describes it) and covers behavior graphs, character files and project
files. It is clean side: the code was written from the structure of the XML, and the types are
generated from the vanilla corpus. The package has no runtime dependencies and no install step,
because Node runs the `.ts` files directly through type stripping. The code therefore uses
erasable syntax only: no enums, namespaces or parameter properties, `import type` for types,
and `.ts` extensions in imports. Node 24.11.1 is what was measured here (`node --version`).

## Gates (run from `projects/skyrim`)

```sh
nix shell --inputs-from ../.. nixpkgs#typescript -c tsc -p model   # typecheck: tsc 7.0.2 (world's flake.lock nixpkgs)
(cd model && node --test 'test/*.test.ts')                         # tests: corpus tests skip without ~/skyrim-data-extracted/xml
(cd model && node gen/generate.ts --check)                         # generated files match the corpus (exits 0 when the corpus is absent)
```

`tsc -p model` type-checks `src/`, `gen/` and `test/` using the tree's `tsconfig.base.json`
(`strict`, `noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`, `erasableSyntaxOnly`,
`verbatimModuleSyntax`), with `noUnusedLocals` and `noUnusedParameters` added on top. Since
`@types/node` is not installed, `src/node-shim.d.ts` declares the few `node:` APIs the code calls.
The root `node_modules` does not exist in this worktree (`ls ../../node_modules` fails), so `tsc` comes from Nix.
This directory sits outside the root npm workspace globs, and it has no lockfile.

## Layout

| path | what |
|---|---|
| `gen/generate.ts` | Scans every file whose root class is `hkbBehaviorGraph`, `hkbCharacterData` or `hkbProjectData` (1,238 files, classified with `_manifest.tsv`) and writes `src/generated/*` |
| `src/generated/classes.ts` | **Generated.** One interface per class (72) and per anonymous struct (49), the `HkObject` union and `HkClassMap` |
| `src/generated/schema.ts` | **Generated.** The runtime schema. For each field it records the kind, whether it was ever null, ever empty or absent in some instance, and its ref targets |
| `src/xml.ts` | The XML tokenizer, plus the raw packfile reader for objects, params, `hkcstring`s and nested structs |
| `src/values.ts` | Scalar classification and parsing for numbers, NaN, flags and `( … )` vectors |
| `src/packfile.ts` | The object table: two passes (create the shells, then fill the fields), decoding each value by schema kind, with `#NNNN` replaced by the target object |
| `src/loader.ts` | `Loader`: project → character → behavior → referenced behaviors, resolved by path and cached. Cycles are safe |
| `src/query.ts` | `references`, `reachable`, `graphNodes`, `graphClosure`, `stateMachineTree`/`formatTree`, `variables`, `events` |
| `src/cli.ts` | Prints the counts for a project closure or for the whole corpus |
| `test/fixtures/tiny/` | A hand-written two-graph project (not game data), used by tests that always run |

## Types

- `Ref<T>` is the resolved target object. `T` is the union of the classes observed as targets.
  A field that was observed null is typed `Ref<…> | null`. A pointer that was **never** observed
  non-null is typed `Ref<HkObject> | null`.
- Numbers map to `number`, `true`/`false` to `boolean`, and strings to `string`. The `␀` marker
  becomes `null`, so a string observed null is typed `string | null`.
- Enums become a string union of the values observed. Flag fields (`A|B`, `0`, `FLAG_*`) become
  arrays of observed flag names. A numeric remainder such as `…|5760` becomes `` `${number}` ``.
- `(x y z w)` becomes `Vec4`. A multi-group value becomes a tuple of tuples, e.g. `[Vec3, Vec4, Vec3]`.
- Arrays map to `T[]`. An array that was never observed non-empty is `unknown[]`.
- The XML does not name anonymous structs, so they are named `<owner>__<field>`, e.g.
  `hkbStateMachineTransitionInfoArray__transitions`.
- Each field's JSDoc gives its kind and notes whether it was observed null, observed empty, or
  absent in some instances. Absent fields are also marked optional with `?`.
- `$class` is the discriminant (`is(o, "hkbStateMachine")` narrows on it). `$id` and `$file` are
  also present (`$file` is not enumerable).

The loader does not validate that fields are present. An object missing a field gets
`undefined` there, whatever its type says. Unknown classes and fields are decoded heuristically
and reported in `Loader.diagnostics()`. On the vanilla corpus there are none.

## Measured (aubron-mini, Mac mini M4 Pro, Node 24.11.1, 2026-10-15)

| run | command | result |
|---|---|---|
| tests | `node --test 'test/*.test.ts'` | 10 pass (7 fixture, 3 corpus). With `HOME=/tmp/nonexistent-home`: 7 pass, 3 skipped |
| census cross-check | `test/corpus.test.ts` | All 428 graphs match `census/census.json`: nodes, state machines, clips, variables, events and distinct references |
| 0_master closure | `node --expose-gc src/cli.ts` | 2 projects, 2 characters, 17 graphs, 21 packfiles, 19,410 objects, 32/32 refs resolved. 0.20 s load, 0.29 s wall, peak RSS 264 MB, heap after GC 24 MB |
| whole corpus | `node --expose-gc src/cli.ts --all` | 457 projects, 353 characters, 428 graphs, 1,238 packfiles, 71,336 objects, 33,630 nodes, 97/97 refs. 0.62–0.67 s load, 0.77–0.81 s wall, peak RSS ≈ 400 MB (`/usr/bin/time -l`), heap after GC 95 MB |
| generator | `node gen/generate.ts` | 1,238 files → 72 classes, 49 structs in 0.6 s |

The `--all` run reports one missing file. `meshes/magic/summonhandfx01.xml` names a character
(`…/fireball01handeffects.xml`) that is not in the converted tree. That is a gap in the data,
not a loader failure.

## Not done

- Skeletons (`hkaSkeleton`), animations and ragdolls are not in the schema. The generator only
  scans the three root classes above, but the reader parses them, decoding heuristically and
  reporting diagnostics.
- Nothing uses the field semantics yet. For example, nothing maps `variableIndex` to a variable,
  `eventId` to an event, or a binding's `memberPath` to the field it binds.
- The model has no writer back to XML.
