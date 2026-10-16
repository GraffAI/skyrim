# HKX → XML on macOS arm64: result

Recon for the clean-room engine (2026-10-15, aubron-roam, M1 Max, Darwin 25.5.0). The priority
was behavior graphs, not animation decompression. All measurements below came from commands
run on this machine; the commands are given beside the numbers.

## Verdict

| candidate | verdict | evidence |
|---|---|---|
| **serde-hkx 2.0.0** (`hkxc`, Rust) | **works**: behaviors, characters, projects, skeletons, animations | Built from source here. All 1,763 non-animation game `.hkx` files convert to XML (1763 ok, 0 fail). `hkxc verify` (binary → Rust → binary) reproduces all 7,699 game `.hkx` byte for byte. Every XML output parses back into a fully reachable object graph. |
| HKX2Library (.NET) | not tried | The brief said to try it only if serde-hkx failed, and serde-hkx did not fail. |
| HavokLib (PredatorCZ, C++) | **fails for behaviors** (judged from the source, not built) | At `ef5d5c6f5ab8d7f32cb4e8983300b8db61e4dc6b`, the README's "Supported classes" lists only `hka*` animation/skeleton classes, and `grep -rhoE '\bhk[bp][A-Z]…'` finds no `hkb*` class anywhere in the tree. It is an animation and skeleton library. |

## Versions

- serde-hkx: tag `2.0.0` = commit `2b684a347375adc82be733e3d85077adbcec873a` (2026-07-27).
  `main` was at `3f53c05…` (2026-08-11) and was not used.
- Toolchain: `nix shell github:NixOS/nixpkgs/494ce7fd23ff6a5dff39e1fb11e9b6f2ac74bf25#{cargo,rustc}`
  → rustc 1.98.1 (`nix eval --raw nixpkgs#rustc.version`). The crate needs ≥ 1.95 and edition 2024.
- The source build reports `hkxc 2.0.0`. Cold build: 2m51s (`cargo build --release -p hkxc --features extra_fmt`).
- Upstream also publishes a macOS arm64 release binary, `serde-hkx-cli-aarch64-apple-darwin-extra_fmt.tar.gz`,
  sha256 `a4a3bfde…7837c6`. On the game's `0_master.hkx` its XML is byte-identical to the source build's (`cmp`).

## Files in this directory (ours; no third-party source)

- `build_serde_hkx.sh`: the pinned recipe. It clones the repo into `~/skyrim-data-extracted/_toolsrc/serde-hkx`,
  checks out the commit above, verifies it, and builds in the pinned Nix shell with `--locked`.
  `--release` downloads the upstream binary and checks its sha256 instead.
- `bulk_convert.sh graph|anim N`: the bulk HKX → XML conversion, output mirroring the input paths.
  It writes `_manifest.tsv` (status, directory category, root classes, sizes, relpath) and `_errors.log`.
- `roundtrip_check.sh xml|json`: XML/JSON → hkx, then a byte comparison with the original.
- `hkx_xml_canon.py`: canonicalises a packfile XML so two files can be compared semantically. It walks
  the graph depth-first from `toplevelobject`, renumbers references, folds flag and float spellings,
  and reports unreached objects. Its comparison is also a small reference parser. It collapses whitespace
  inside values, so it ignores a leading space in a string.

**Trap:** `hkxc convert` **exits 0 when a conversion fails** (measured: a Nemesis template with `%n`
placeholders printed `XML Deserialize Error` and returned `$?`=0). The scripts here count success
only when a non-empty `<?xml` file was written. Do not trust the exit code.

## Run

```sh
tools/hkx/build_serde_hkx.sh                       # → ~/skyrim-data-extracted/_toolsrc/serde-hkx/target/release/hkxc
H=~/skyrim-data-extracted/_toolsrc/serde-hkx/target/release/hkxc
$H convert -i in.hkx -o out.xml -v xml             # also: -v json|yaml|toml|amd64|win32
$H convert -i out.xml -o back.hkx -v amd64         # SE is 64-bit (amd64); LE is win32
$H verify <file-or-dir>                            # binary→Rust→binary byte check (dir: silent on success;
                                                   #   add --stdout --log-level info to see "Passed Reproduction")
tools/hkx/bulk_convert.sh graph                    # raw → ~/skyrim-data-extracted/xml
tools/hkx/bulk_convert.sh anim 200                 # raw → ~/skyrim-data-extracted/xml-anim-sample
tools/hkx/bulk_convert.sh anim-all                  # raw → ~/skyrim-data-extracted/xml-anim (every animations/*.hkx)
```

## Results on the real data (`~/skyrim-data-extracted/raw`, from `Skyrim - Animations.bsa`)

The extracted tree holds 7,699 `.hkx` files. All are 64-bit (byte 0x10 = 08), and 5,936 sit under an `animations/` directory.

**Bulk conversion** (`bulk_convert.sh graph`, 8.6 s wall time, 12 jobs). It took every `.hkx` that is
**not** under `animations/`. That is a superset of what was asked: it also includes paired killmoves,
furniture, traps and other misc graphs.

- **1763 ok / 0 FAIL** → `~/skyrim-data-extracted/xml/` (134 MB, 1,763 `.xml`).
- By directory: 390 `behaviors*/`, 314 `characters*/`, 333 `character assets*` / `characterassets/`, 726 others.
- By the root container's variant classes (`cut -f1,3 _manifest.tsv | sort | uniq -c`):
  - 457 `hkbProjectData`
  - 428 `hkbBehaviorGraph`
  - 353 `hkbCharacterData`
  - 475 `hkaAnimationContainer+hkMemoryResourceContainer`
  - 48 skeletons with ragdoll/mapper (`…+hkpPhysicsData+hkaRagdollInstance+hkaSkeletonMapper…`)
  - 2 with the order swapped
  - The directory name is a weak signal: e.g. the 726 "other" include project files and behaviors outside `behaviors/`.
    **Classify by root class, not by path.**

**Animation sample** (`bulk_convert.sh anim 200`, every 29th animation in sorted order): **200 ok / 0 FAIL**
→ `~/skyrim-data-extracted/xml-anim-sample/` (9.4 MB). Annotation text and times are plain params, so they
can be read directly.

**All animations** (`JOBS=12 bulk_convert.sh anim-all`, 2026-10-15, 25.5 s wall time by `time`): **5936 ok / 0 FAIL**
(`cut -f1 _manifest.tsv | sort | uniq -c`; `_errors.log` 0 bytes) → `~/skyrim-data-extracted/xml-anim/`
(263 MB by `du -sh`). The XML is kept; the census reads it directly (`census/CENSUS.md` §4b).

**Byte-level reproduction:**

| test | command | result |
|---|---|---|
| binary → Rust → binary, all 7,699 | `hkxc verify meshes --stdout --log-level info \| grep -c 'Passed Reproduction'` | **7699 / 7699 byte-identical** |
| hkx → XML → hkx, 1,763 graph files | `roundtrip_check.sh xml` | 1174 identical, 589 differ (0 fail) |
| hkx → JSON → hkx, 1,763 graph files | `roundtrip_check.sh json` | 1341 identical, 408 differ, **14 fail** |
| hkx → XML → hkx, 200 animations | `roundtrip_check.sh xml … xml-anim-sample …` | 0 identical, 200 differ (floats) |
| XML semantic parse, 1,763 | `hkx_xml_canon.py` on each | 1763 parse, `unreached=0` in every file |

The XML differences were classified word by word (scratch script, not kept):

- **Float rounding:** 162,367 words. XML prints floats as `%.6f`, so the low bits are lost.
- **Dropped `w` lanes:** 24,369 words, almost all in skeletons (`character assets*`: ~24.3k). The original
  has non-zero bytes in the 4th lane of `hkQsTransform` translation/scale vectors. XML writes 3 components,
  following Havok's convention, so the lane comes back as 0. It is padding, not data.
- **Leading spaces in strings:** about 44 words in 5 behavior files. The XML **writer keeps** a string's
  leading space (`<hkcstring> iState_…`); the serde-hkx **XML reader trims it** on the way back to hkx.
  So hkx → XML is faithful for strings, and only XML → hkx loses the space.
- **NaN:** 15 words. Written as `NaN`, read back with a different payload.

JSON keeps full float precision and has its own failures:

- It writes NaN/Inf as `null` and then refuses to read them back (`invalid type: null, expected f32`).
  The 14 failures are all `quadrupedbehavior.hkx` and similar files.
- It loses the sign of `-0.0` in a few places.

**Use XML for reading.** For a byte-exact copy, keep the `.hkx`. `hkxc verify` shows that the binary
path is exact.

**Independent cross-check:**

- The serde-hkx fixtures `docs/handson_hex_dump/defaultmale/defaultmale.hkx` and `wisp_skeleton/skeleton.hkx`
  are byte-identical to the game's `meshes/actors/character/defaultmale.hkx` and
  `meshes/actors/wisp/character assets/skeleton.hkx` (`cmp`).
- Before the game data arrived, the same tests ran on third-party samples under `~/skyrim-data-extracted/_samples/`:
  - Nemesis `test environment/cached_behaviors`, 76 LE/SE binaries: `verify` passed on all of them.
  - SOBA hkxcmd-made XML: 42 / 44 converted. The 2 failures are `%n` template files, which are not valid XML.
  - Canonical comparisons: LE `0_master` = SE `0_master` = SOBA's hkxcmd XML. hkxcmd and serde-hkx XML
    therefore describe the same graph with different object order and numbering.
- Pandora's 276 "template" `.hkx` files **fail** in serde-hkx with `expected Skip x64 ptr size(0 fill 8bytes)`.
  They are not game bytes: Pandora's serializer writes non-zero values into pointer slots, which serde-hkx
  checks strictly. Expect the same failure on any mod output written by a non-Havok serializer.

## Output format (for the census parser)

Havok 2010 "packfile XML", ASCII:

```
<?xml version="1.0" encoding="ascii"?>
<hkpackfile classversion="8" contentsversion="hk_2010.2.0-r1" toplevelobject="#0001">
  <hksection name="__data__">
    <hkobject name="#NNNN" class="<HavokClass>" signature="0x<crc, no zero padding>">
      <!-- fieldName SERIALIZE_IGNORED -->      runtime-only members, kept as comments only
      <hkparam name="<member>">VALUE</hkparam>
      <hkparam name="<arrayMember>" numelements="K">…</hkparam>
    </hkobject> …
  </hksection>
</hkpackfile>
```

- **One section,** `__data__`. There is no `__types__` or `__classnames__` content, so there is no class
  reflection data. The schema is the class name plus its signature. serde-hkx's
  `assets/havok_class_schema.json` holds the member lists for every class.
- **Objects** are top-level `<hkobject>` elements with `name` (`#` + 4+ digits), `class` and `signature`.
  serde-hkx emits children before parents. The `hkRootLevelContainer` is `#0001` and comes **last**;
  `toplevelobject` points to it. Its `namedVariants` entries each hold `name`, `className` and `variant`
  (a reference to the real root: `hkbBehaviorGraph`, `hkbProjectData`, `hkbCharacterData`,
  `hkaAnimationContainer`, …). Numbering differs between tools, so key on graph position, never on the
  `#NNNN` text.
- **Scalar values** (`hkparam` text):
  - integers in decimal
  - floats as `%.6f` (`NaN` possible; very large values printed in full)
  - `true` / `false`
  - enums by name (`SELF_TRANSITION_MODE_…`)
  - flags as `NAME|NAME|<decimal remainder>`; hkxcmd writes `…|FLAG_NONE|0x1680` for the same value
  - strings raw. A leading space is significant; do not `strip()` string params.
  - pointers as `#NNNN` or `null`
- **Vectors:** `(x y z w)` for hkVector4/hkQuaternion, and `(x y z)(x y z w)(x y z)` for hkQsTransform.
  Matrices are several parenthesised groups.
- **Arrays:** `numelements="K"`, which can be 0 with empty text. Their contents are one of:
  - whitespace-separated scalars or `#refs`, wrapped across lines
  - one `<hkcstring>…</hkcstring>` per element (string arrays such as `eventNames`, `variableNames`,
    `characterFilenames`, `behaviorFilenames`)
  - one **anonymous** `<hkobject>` per element (no name, class or signature) for inline structs such as
    variable bindings, `wordVariableValues`, `variableInfos` and animation `annotations` (`time`, `text`)
- **Inline structs** that are not in an array are an `<hkparam>` with one anonymous `<hkobject>` inside,
  e.g. `eventToSendWhenStateOrTransitionChanges` → `{id, payload}`.
- **Edges a census will want** (behavior graphs):
  - `hkbBehaviorGraph.rootGenerator` and `.data` → `hkbBehaviorGraphData`, which holds `variableInfos`,
    `eventInfos`, `stringData` → `hkbBehaviorGraphStringData` (`eventNames`, `variableNames`, …)
  - `hkbStateMachine.states` → `hkbStateMachineStateInfo` (`generator`, `transitions`, `stateId`, `name`)
  - `variableBindingSet` → `hkbVariableBindingSet` (`bindings`: `memberPath`, `variableIndex`)
  - `hkbBehaviorReferenceGenerator.behaviorName` is a cross-file edge, a path to another behavior `.hkx`
  - `hkbProjectData` → `hkbProjectStringData`, which lists the character, behavior and animation files
  - `hkbCharacterData` → `hkbCharacterStringData` (skeleton, behavior and animation names) and `hkbMirroredSkeletonInfo`
- **Animations:** `hkaSplineCompressedAnimation` is **not decompressed**. Its `data` is a raw byte array
  (`numelements` = bytes, decimal). Block and track metadata, `annotationTracks[].annotations[]{time,text}`,
  `hkaAnimationBinding.transformTrackToBoneIndices` and `originalSkeletonName` are all plain params.
- The 1,763 bulk XMLs are 134 MB. `0_master.xml` has 2,418 objects. The largest file,
  `1hm_behavior.xml` (4,794 objects), takes 0.30 s for ElementTree plus canonicalisation (`time python3 -I hkx_xml_canon.py …`).

## Not verified

- HKX2Library was not built or run. HavokLib was not built; its verdict comes only from reading the source.
- I did not check that serde-hkx's XML → hkx output **loads in the game** (it matches Havok's bytes in
  1,174 / 1,763 cases, and the rest differ only as classified above). Only the hkx → XML direction matters
  for the census.
- The animation XML round trip was not classified word by word. All 200 differ, presumably from float
  rounding, but that was not checked. `verify` shows the binary path is exact for all 5,936 animations.
- Only the 200 sampled animations went through `convert`. The other 5,736 passed `verify` (the same
  deserializer) but were not written as XML.
- I did not check that the XML is complete against Havok's own reflection. Fields marked `SERIALIZE_IGNORED`
  are omitted by design, as in hkxcmd and Havok's own XML.
- Nothing here was committed (per the brief). Outputs live only under `~/skyrim-data-extracted/`.
