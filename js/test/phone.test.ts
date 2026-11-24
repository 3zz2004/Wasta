import { describe, expect, it } from "vitest";
import { isValidPhone, parsePhone, type PhoneError } from "../src/index.js";
import { loadSpec } from "./spec.js";

const spec = loadSpec<{
  valid: { input: string; national: string; e164: string; operator: string }[];
  invalid: { input: string; error: PhoneError }[];
}>("phone");

describe("parsePhone", () => {
  it.each(spec.valid)("parses $input", ({ input, national, e164, operator }) => {
    const result = parsePhone(input);
    expect(result).toEqual({
      ok: true,
      value: { national, e164, prefix: national.slice(0, 3), operator },
    });
    expect(isValidPhone(input)).toBe(true);
  });

  it.each(spec.invalid)("rejects $input with $error", ({ input, error }) => {
    expect(parsePhone(input)).toEqual({ ok: false, error });
    expect(isValidPhone(input)).toBe(false);
  });
});
