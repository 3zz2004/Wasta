// The two packages ship together, so their versions must never drift apart.
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (file) => readFileSync(join(root, file), "utf8");

const versions = {
  "js/package.json": JSON.parse(read("js/package.json")).version,
  "python/pyproject.toml": read("python/pyproject.toml").match(/^version = "(.+)"$/m)?.[1],
  "python/src/wasta/__init__.py": read("python/src/wasta/__init__.py").match(/^__version__ = "(.+)"$/m)?.[1],
};

if (new Set(Object.values(versions)).size !== 1) {
  console.error("Package versions disagree:");
  for (const [file, version] of Object.entries(versions)) console.error(`  ${file}: ${version}`);
  process.exit(1);
}
