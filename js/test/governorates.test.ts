import { describe, expect, it } from "vitest";
import { findGovernorate, getGovernorate, governorates } from "../src/index.js";
import { loadSpec } from "./spec.js";

const spec = loadSpec<{ find: { input: string; code: string }[]; notFound: string[] }>("governorates");

describe("governorates", () => {
  it("lists all 27 governorates with unique codes and slugs", () => {
    expect(governorates).toHaveLength(27);
    expect(new Set(governorates.map((g) => g.code)).size).toBe(27);
    expect(new Set(governorates.map((g) => g.slug)).size).toBe(27);
  });

  it("is frozen", () => {
    expect(Object.isFrozen(governorates)).toBe(true);
    expect(Object.isFrozen(governorates[0])).toBe(true);
  });

  it("looks up by code", () => {
    expect(getGovernorate("15")?.nameEn).toBe("Kafr El Sheikh");
    expect(getGovernorate("88")).toBeUndefined();
  });

  it("never lets two governorates claim the same spelling", () => {
    for (const g of governorates) {
      for (const name of [g.nameAr, g.nameEn, g.slug, ...g.aliases]) {
        expect(findGovernorate(name)?.code, name).toBe(g.code);
      }
    }
  });
});

describe("findGovernorate", () => {
  it.each(spec.find)("finds $input", ({ input, code }) => {
    expect(findGovernorate(input)?.code).toBe(code);
  });

  it.each(spec.notFound)("does not match %j", (input) => {
    expect(findGovernorate(input)).toBeUndefined();
  });
});
