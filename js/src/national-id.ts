import { WHITESPACE } from "./chars.js";
import { toWesternDigits } from "./digits.js";
import { getGovernorate, type Governorate } from "./governorates.js";
import { err, ok, type Result } from "./result.js";

export interface NationalIdInfo {
  /** ISO date, e.g. `1999-05-21`. A string, so no time zone can shift it. */
  readonly birthDate: string;
  /** `null` when the holder was born outside Egypt (code 88). */
  readonly governorate: Governorate | null;
  readonly governorateCode: string;
  readonly bornAbroad: boolean;
  readonly gender: "male" | "female";
}

export type NationalIdError =
  | "INVALID_FORMAT"
  | "INVALID_CENTURY"
  | "INVALID_BIRTH_DATE"
  | "FUTURE_BIRTH_DATE"
  | "UNKNOWN_GOVERNORATE";

export interface NationalIdOptions {
  /** The date to compare the birth date against. Defaults to today. */
  today?: Date;
}

const BORN_ABROAD = "88";
const SPACES = new RegExp(`[${WHITESPACE}]`, "g");
const CENTURIES: Record<string, number> = { "2": 1900, "3": 2000 };

/**
 * Reads the information encoded in a 14-digit Egyptian national ID.
 *
 * Layout: century (1) · YYMMDD (6) · governorate (2) · serial (4) · check (1).
 * The second-to-last digit of the serial is odd for men and even for women.
 *
 * The check digit is not verified: its algorithm has never been published, so
 * any implementation of it would be a guess.
 */
export function parseNationalId(
  input: string,
  options: NationalIdOptions = {},
): Result<NationalIdInfo, NationalIdError> {
  const id = toWesternDigits(input).replace(SPACES, "");
  if (!/^\d{14}$/.test(id)) return err("INVALID_FORMAT");

  const century = CENTURIES[id[0]!];
  if (century === undefined) return err("INVALID_CENTURY");

  const year = century + Number(id.slice(1, 3));
  const month = Number(id.slice(3, 5));
  const day = Number(id.slice(5, 7));
  if (!isRealDate(year, month, day)) return err("INVALID_BIRTH_DATE");

  const birthDate = `${year}-${pad(month)}-${pad(day)}`;
  if (birthDate > isoDate(options.today ?? new Date())) return err("FUTURE_BIRTH_DATE");

  const governorateCode = id.slice(7, 9);
  const bornAbroad = governorateCode === BORN_ABROAD;
  const governorate = bornAbroad ? null : getGovernorate(governorateCode);
  if (governorate === undefined) return err("UNKNOWN_GOVERNORATE");

  const gender = Number(id[12]) % 2 === 1 ? "male" : "female";

  return ok({ birthDate, governorate, governorateCode, bornAbroad, gender });
}

export function isValidNationalId(input: string, options?: NationalIdOptions): boolean {
  return parseNationalId(input, options).ok;
}

function isRealDate(year: number, month: number, day: number): boolean {
  if (month < 1 || month > 12 || day < 1) return false;
  const daysInMonth = new Date(Date.UTC(year, month, 0)).getUTCDate();
  return day <= daysInMonth;
}

const pad = (n: number) => String(n).padStart(2, "0");

// Local calendar date: someone born "today" in Cairo is valid even when UTC is still yesterday.
const isoDate = (d: Date) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
