// Loads project -> character -> behavior graphs, resolving file references by path.
//
// Paths inside the data are Windows-style and relative to the *project* directory:
//   hkbProjectStringData.characterFilenames   "Characters\DefaultMale.hkx"
//   hkbCharacterStringData.behaviorFilename   "Behaviors\0_Master.hkx"
//   hkbBehaviorReferenceGenerator.behaviorName "Behaviors\MT_Behavior.hkx"
// The converted tree is lower-case with `.xml` for `.hkx`, so references are normalised to that.

import { readFileSync, existsSync } from "node:fs";
import { join, posix } from "node:path";
import { readPackfile, rootVariant, objectsOf } from "./packfile.ts";
import type { Packfile, Diagnostic } from "./packfile.ts";
import type {
  hkbBehaviorGraph,
  hkbBehaviorGraphData,
  hkbBehaviorReferenceGenerator,
  hkbCharacterData,
  hkbCharacterStringData,
  hkbProjectData,
} from "./generated/classes.ts";

export interface BehaviorReference {
  readonly node: hkbBehaviorReferenceGenerator;
  /** Normalised path of the referenced file. */
  readonly path: string;
  /** The loaded graph, or undefined when the file is missing or failed to load. */
  target: BehaviorFile | undefined;
}

export interface BehaviorFile {
  readonly kind: "behavior";
  readonly path: string;
  readonly projectDir: string;
  readonly packfile: Packfile;
  readonly graph: hkbBehaviorGraph;
  readonly data: hkbBehaviorGraphData | undefined;
  readonly references: BehaviorReference[];
}

export interface CharacterFile {
  readonly kind: "character";
  readonly path: string;
  readonly projectDir: string;
  readonly packfile: Packfile;
  readonly data: hkbCharacterData;
  readonly strings: hkbCharacterStringData;
  readonly behaviorPath: string | undefined;
  readonly behavior: BehaviorFile | undefined;
  /** Normalised path of the rig (skeleton) file; not loaded by this package. */
  readonly rigPath: string | undefined;
}

export interface ProjectFile {
  readonly kind: "project";
  readonly path: string;
  readonly packfile: Packfile;
  readonly data: hkbProjectData;
  readonly characters: CharacterFile[];
}

export interface LoaderOptions {
  /** Read a file given its absolute path; defaults to fs (latin1, the files are ASCII). */
  readonly read?: (absPath: string) => string;
  readonly exists?: (absPath: string) => boolean;
}

/** Normalise a data path ("Behaviors\\0_Master.hkx") against a directory, to the converted tree's form. */
export function normalizeRef(dir: string, ref: string): string {
  const rel = ref.replace(/\\/g, "/").toLowerCase().replace(/\.hkx$/, ".xml");
  return posix.normalize(dir.length > 0 ? posix.join(dir, rel) : rel).replace(/^\.\//, "");
}

export class Loader {
  readonly root: string;
  private readonly read: (p: string) => string;
  private readonly exists: (p: string) => boolean;
  private readonly packfiles = new Map<string, Packfile>();
  private readonly behaviors = new Map<string, BehaviorFile>();
  private readonly characters = new Map<string, CharacterFile>();
  private readonly projects = new Map<string, ProjectFile>();
  /** Files a reference named that do not exist (path -> who referenced it). */
  readonly missing = new Map<string, string>();
  /** Files that exist but failed to parse or had the wrong root. */
  readonly failures = new Map<string, string>();

  constructor(root: string, opts: LoaderOptions = {}) {
    this.root = root;
    this.read = opts.read ?? ((p) => readFileSync(p, "latin1"));
    this.exists = opts.exists ?? existsSync;
  }

  /** Load (or return the cached) packfile at a root-relative path. */
  packfile(path: string): Packfile {
    let pf = this.packfiles.get(path);
    if (pf === undefined) {
      pf = readPackfile(this.read(join(this.root, path)), path);
      this.packfiles.set(path, pf);
    }
    return pf;
  }

  private tryPackfile(path: string, referrer: string): Packfile | undefined {
    if (!this.packfiles.has(path) && !this.exists(join(this.root, path))) {
      this.missing.set(path, referrer);
      return undefined;
    }
    try {
      return this.packfile(path);
    } catch (e) {
      this.failures.set(path, e instanceof Error ? e.message : String(e));
      return undefined;
    }
  }

  /**
   * Load a behavior graph and, transitively, every graph its hkbBehaviorReferenceGenerators name.
   * `projectDir` is the directory references resolve against; by default the parent of the
   * file's own directory (vanilla graphs live in `<project>/behaviors/`).
   */
  behavior(path: string, projectDir: string = posix.dirname(posix.dirname(path)), referrer = "(caller)"): BehaviorFile | undefined {
    const cached = this.behaviors.get(path);
    if (cached !== undefined) return cached;
    const pf = this.tryPackfile(path, referrer);
    if (pf === undefined) return undefined;
    const graph = rootVariant(pf, "hkbBehaviorGraph");
    if (graph === undefined) {
      this.failures.set(path, "root has no hkbBehaviorGraph");
      return undefined;
    }
    const bf: BehaviorFile = { kind: "behavior", path, projectDir, packfile: pf, graph, data: graph.data ?? undefined, references: [] };
    this.behaviors.set(path, bf); // before recursing: graphs may reference each other
    for (const node of objectsOf(pf, "hkbBehaviorReferenceGenerator")) {
      const ref: BehaviorReference = { node, path: normalizeRef(projectDir, node.behaviorName), target: undefined };
      bf.references.push(ref);
    }
    for (const ref of bf.references) ref.target = this.behavior(ref.path, projectDir, path);
    return bf;
  }

  character(path: string, projectDir: string, referrer = "(caller)"): CharacterFile | undefined {
    const cached = this.characters.get(path);
    if (cached !== undefined) return cached;
    const pf = this.tryPackfile(path, referrer);
    if (pf === undefined) return undefined;
    const data = rootVariant(pf, "hkbCharacterData");
    if (data === undefined) {
      this.failures.set(path, "root has no hkbCharacterData");
      return undefined;
    }
    const strings = data.stringData;
    const behaviorPath = strings.behaviorFilename ? normalizeRef(projectDir, strings.behaviorFilename) : undefined;
    const rigPath = strings.rigName ? normalizeRef(projectDir, strings.rigName) : undefined;
    const behavior = behaviorPath === undefined ? undefined : this.behavior(behaviorPath, projectDir, path);
    const cf: CharacterFile = { kind: "character", path, projectDir, packfile: pf, data, strings, behaviorPath, behavior, rigPath };
    this.characters.set(path, cf);
    return cf;
  }

  project(path: string): ProjectFile | undefined {
    const cached = this.projects.get(path);
    if (cached !== undefined) return cached;
    const pf = this.tryPackfile(path, "(caller)");
    if (pf === undefined) return undefined;
    const data = rootVariant(pf, "hkbProjectData");
    if (data === undefined) {
      this.failures.set(path, "root has no hkbProjectData");
      return undefined;
    }
    const dir = posix.dirname(path) === "." ? "" : posix.dirname(path);
    const characters: CharacterFile[] = [];
    for (const c of data.stringData.characterFilenames) {
      if (c === null) continue;
      const cf = this.character(normalizeRef(dir, c), dir, path);
      if (cf !== undefined) characters.push(cf);
    }
    const pr: ProjectFile = { kind: "project", path, packfile: pf, data, characters };
    this.projects.set(path, pr);
    return pr;
  }

  loadedPackfiles(): IterableIterator<Packfile> {
    return this.packfiles.values();
  }

  loadedBehaviors(): IterableIterator<BehaviorFile> {
    return this.behaviors.values();
  }

  loadedCharacters(): IterableIterator<CharacterFile> {
    return this.characters.values();
  }

  loadedProjects(): IterableIterator<ProjectFile> {
    return this.projects.values();
  }

  diagnostics(): Diagnostic[] {
    const out: Diagnostic[] = [];
    for (const pf of this.packfiles.values()) out.push(...pf.diagnostics);
    return out;
  }
}
