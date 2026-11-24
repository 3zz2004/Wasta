import { describe, expect, it } from "vitest";
import { MAX_AMOUNT, TafqeetError, numberToArabicWords, tafqeet, type TafqeetErrorCode } from "../src/index.js";
import { loadSpec } from "./spec.js";

type Case = { input: number | string; output: string };

const spec = loadSpec<{
  words: { input: number; output: string }[];
  money: Case[];
  unwrapped: Case[];
  errors: { input: number | string; error: TafqeetErrorCode }[];
}>("tafqeet");

describe("numberToArabicWords", () => {
  it.each(spec.words)("$input → $output", ({ input, output }) => {
    expect(numberToArabicWords(input)).toBe(output);
  });

  it.each([1.5, -3, MAX_AMOUNT + 1, Number.NaN])("rejects %s", (value) => {
    expect(() => numberToArabicWords(value)).toThrow(TafqeetError);
  });
});

describe("tafqeet", () => {
  it.each(spec.money)("$input → $output", ({ input, output }) => {
    expect(tafqeet(input)).toBe(output);
  });

  it.each(spec.unwrapped)("$input without wrapping", ({ input, output }) => {
    expect(tafqeet(input, { wrap: false })).toBe(output);
  });

  it.each(spec.errors)("rejects $input with $error", ({ input, error }) => {
    expect(() => tafqeet(input)).toThrow(expect.objectContaining({ name: "TafqeetError", code: error }));
  });

  it("rejects non-finite numbers", () => {
    expect(() => tafqeet(Number.POSITIVE_INFINITY)).toThrow(expect.objectContaining({ code: "INVALID_NUMBER" }));
  });

  it("errors are RangeErrors", () => {
    expect(() => tafqeet(-1)).toThrow(RangeError);
  });
});
