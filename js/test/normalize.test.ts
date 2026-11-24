import { describe, expect, it } from "vitest";
import { normalizeArabic, toArabicDigits, toWesternDigits, type NormalizeOptions } from "../src/index.js";
import { loadSpec } from "./spec.js";

type Case = { input: string; output: string };

const spec = loadSpec<{
  default: Case[];
  options: (Case & { options: NormalizeOptions })[];
  toWesternDigits: Case[];
  toArabicDigits: Case[];
}>("normalize");

describe("normalizeArabic", () => {
  it.each(spec.default)("$input → $output", ({ input, output }) => {
    expect(normalizeArabic(input)).toBe(output);
  });

  it.each(spec.options)("$input with $options → $output", ({ input, options, output }) => {
    expect(normalizeArabic(input, options)).toBe(output);
  });

  it("is idempotent", () => {
    for (const { input } of spec.default) {
      const once = normalizeArabic(input);
      expect(normalizeArabic(once)).toBe(once);
    }
  });
});

describe("digits", () => {
  it.each(spec.toWesternDigits)("toWesternDigits($input)", ({ input, output }) => {
    expect(toWesternDigits(input)).toBe(output);
  });

  it.each(spec.toArabicDigits)("toArabicDigits($input)", ({ input, output }) => {
    expect(toArabicDigits(input)).toBe(output);
  });
});
