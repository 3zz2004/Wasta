// Registries render the README and LICENSE that sit next to each package,
// so both packages get a copy of the root files before they are built.
// npm and PyPI can't resolve the README's relative links and images, so those
// are rewritten to point at GitHub.
import { copyFileSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const pkg = JSON.parse(readFileSync(join(root, "js", "package.json"), "utf8"));
const repo = pkg.repository.url.replace(/^git\+/, "").replace(/\.git$/, "");
// jsDelivr serves SVGs with an image content type; raw.githubusercontent.com does not.
const raw = repo.replace("https://github.com/", "https://cdn.jsdelivr.net/gh/") + "@main/";
const blob = `${repo}/blob/main/`;

const readme = readFileSync(join(root, "README.md"), "utf8")
  .replace(/(src|srcset)="(?!https?:|#)([^"]+)"/g, (_, attr, path) => `${attr}="${raw}${path}"`)
  .replace(/\]\((?!https?:|#)([^)]+)\)/g, (_, path) => `](${blob}${path})`);

for (const pkgDir of ["js", "python"]) {
  writeFileSync(join(root, pkgDir, "README.md"), readme);
  copyFileSync(join(root, "LICENSE"), join(root, pkgDir, "LICENSE"));
}
