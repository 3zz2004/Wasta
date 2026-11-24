import { describe, expect, it } from "vitest";
import { getGovernorate, isValidNationalId, parseNationalId, type NationalIdError } from "../src/index.js";
import { loadSpec } from "./spec.js";

const spec = loadSpec<{
  today: string;
  valid: { input: string; birthDate: string; governorateCode: string; bornAbroad: boolean; gender: string }[];
  invalid: { input: string; error: NationalIdError }[];
}>("national-id");

const [year, month, day] = spec.today.split("-").map(Number) as [number, number, number];
const today = new Date(year, month - 1, day, 12);

describe("parseNationalId", () => {
  it.each(spec.valid)("parses $input", ({ input, birthDate, governorateCode, bornAbroad, gender }) => {
    expect(parseNationalId(input, { today })).toEqual({
      ok: true,
      value: {
        birthDate,
        governorate: bornAbroad ? null : getGovernorate(governorateCode),
        governorateCode,
        bornAbroad,
        gender,
      },
    });
    expect(isValidNationalId(input, { today })).toBe(true);
  });

  it.each(spec.invalid)("rejects $input with $error", ({ input, error }) => {
    expect(parseNationalId(input, { today })).toEqual({ ok: false, error });
    expect(isValidNationalId(input, { today })).toBe(false);
  });

  it("uses the current date by default", () => {
    expect(parseNationalId("39912311201538")).toEqual({ ok: false, error: "FUTURE_BIRTH_DATE" });
  });
});
