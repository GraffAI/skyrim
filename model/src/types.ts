// Hand-written base types the generated classes build on.

/**
 * A resolved pointer. The loader replaces every `#NNNN` reference with the object it names,
 * so a `Ref<T>` *is* the target object (cycles are possible in memory). `T` is the union of
 * the classes the generator observed as targets of that field in the vanilla corpus.
 */
export type Ref<T> = T;

/** Fields every top-level packfile object carries in the model, beside its hkparams. */
export interface HkObjectBase<C extends string> {
  /** The Havok class name (the discriminant: `if (o.$class === "hkbStateMachine")` narrows). */
  readonly $class: C;
  /** The object's name in its packfile, e.g. `#0042`. Unique per file only. */
  readonly $id: string;
  /** The packfile the object came from, relative to the loader's root (lower-case, `/`). */
  readonly $file: string;
}

export type Vec3 = [number, number, number];
export type Vec4 = [number, number, number, number];

/**
 * The runtime schema emitted next to the interfaces. A field kind is one of
 * `num` `bool` `str` `enum` `flags` `ref` `vec:<group sizes>` `struct:<name>` `unknown`,
 * optionally prefixed `[]` for arrays.
 */
export interface FieldSchema {
  readonly name: string;
  readonly kind: string;
  /** Ever written as null (pointer `null`, string `␀`, or a null array element). */
  readonly null: boolean;
  /** Ever written empty (`""` or `numelements="0"`). */
  readonly empty: boolean;
  /** Missing from some instances. */
  readonly optional: boolean;
  /** For refs: the classes observed as targets. */
  readonly targets?: readonly string[];
}

export interface StructSchema {
  readonly fields: readonly FieldSchema[];
}

export interface ClassSchema extends StructSchema {
  readonly signatures: readonly string[];
  readonly instances: number;
  readonly files: number;
}

export interface Schema {
  readonly corpus: { readonly files: number; readonly objects: number };
  readonly classes: Readonly<Record<string, ClassSchema>>;
  readonly structs: Readonly<Record<string, StructSchema>>;
}
