// Runs the built package with no dev dependencies, so older Node versions can be
// checked even though the test tooling itself needs a recent one.
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import * as esm from "../dist/index.js";

const cjs = createRequire(import.meta.url)("../dist/index.cjs");

for (const w of [esm, cjs]) {
  assert.equal(w.tafqeet(1500.25), "فقط ألف وخمسمائة جنيه وخمسة وعشرون قرشًا لا غير");
  assert.equal(w.parsePhone("+20 100 123 4567").value.e164, "+201001234567");
  assert.equal(w.parseNationalId("29905211201538").value.birthDate, "1999-05-21");
  assert.equal(w.findGovernorate("كفرالشيخ").code, "15");
  assert.equal(w.normalizeArabic("مُدرسـة"), "مدرسه");
}

console.log(`ok on Node ${process.version}`);
