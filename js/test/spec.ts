import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

/** Shared test vectors live in /spec so the JS and Python packages are held to the same answers. */
export function loadSpec<T>(name: string): T {
  const url = new URL(`../../spec/${name}.json`, import.meta.url);
  return JSON.parse(readFileSync(fileURLToPath(url), "utf8")) as T;
}
