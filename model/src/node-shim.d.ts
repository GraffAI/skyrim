// Minimal ambient declarations for the Node APIs this package uses, so it type-checks with no
// @types/node installed (zero dependencies). Only the signatures actually called are declared.

declare module "node:fs" {
  export function readFileSync(path: string, encoding: "utf8" | "latin1"): string;
  export function writeFileSync(path: string, data: string): void;
  export function existsSync(path: string): boolean;
  export function readdirSync(path: string): string[];
}

declare module "node:path" {
  interface PathApi {
    join(...parts: string[]): string;
    dirname(p: string): string;
    basename(p: string, ext?: string): string;
    normalize(p: string): string;
    resolve(...parts: string[]): string;
    relative(from: string, to: string): string;
  }
  export const posix: PathApi;
  export function join(...parts: string[]): string;
  export function dirname(p: string): string;
  export function basename(p: string, ext?: string): string;
  export function resolve(...parts: string[]): string;
  export function relative(from: string, to: string): string;
}

declare module "node:url" {
  export function fileURLToPath(url: string): string;
}

declare module "node:os" {
  export function homedir(): string;
}

declare module "node:test" {
  interface TestOptions {
    skip?: boolean | string;
  }
  type TestFn = () => void | Promise<void>;
  export function test(name: string, fn: TestFn): Promise<void>;
  export function test(name: string, options: TestOptions, fn: TestFn): Promise<void>;
  export function describe(name: string, fn: () => void): Promise<void>;
  export function describe(name: string, options: TestOptions, fn: () => void): Promise<void>;
}

declare module "node:assert/strict" {
  interface Assert {
    (value: unknown, message?: string): asserts value;
    ok(value: unknown, message?: string): asserts value;
    equal<T>(actual: unknown, expected: T, message?: string): asserts actual is T;
    deepEqual(actual: unknown, expected: unknown, message?: string): void;
    notEqual(actual: unknown, expected: unknown, message?: string): void;
    throws(fn: () => unknown, expected?: RegExp, message?: string): void;
    match(value: string, re: RegExp, message?: string): void;
  }
  const assert: Assert;
  export default assert;
}

interface ImportMeta {
  readonly url: string;
}

declare const process: {
  readonly argv: string[];
  exit(code?: number): never;
  memoryUsage(): { rss: number; heapUsed: number; heapTotal: number; external: number; arrayBuffers: number };
};

declare const console: {
  log(...args: unknown[]): void;
  error(...args: unknown[]): void;
};

declare const performance: { now(): number };
