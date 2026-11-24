import { BIDI_MARKS, WHITESPACE } from "./chars.js";
import { toWesternDigits } from "./digits.js";
import { MOBILE_PREFIX_DATA } from "./generated/data.js";
import { err, ok, type Result } from "./result.js";

export type MobileOperator = (typeof MOBILE_PREFIX_DATA)[number]["operator"];

export interface MobileNumber {
  /** Local format, e.g. `01001234567`. */
  readonly national: string;
  /** E.164 format, e.g. `+201001234567`. */
  readonly e164: string;
  /** e.g. `010`. */
  readonly prefix: string;
  /**
   * The operator that owns the prefix. Egypt has number portability, so a
   * subscriber may have moved to another network since the number was issued.
   */
  readonly operator: MobileOperator;
}

export type PhoneError =
  | "EMPTY"
  | "INVALID_CHARACTERS"
  | "NOT_EGYPTIAN"
  | "NOT_MOBILE"
  | "INVALID_LENGTH"
  | "UNKNOWN_PREFIX";

const OPERATOR_BY_PREFIX: ReadonlyMap<string, MobileOperator> = new Map(
  MOBILE_PREFIX_DATA.map((p) => [p.prefix, p.operator]),
);

// Separators people actually type, plus the invisible direction marks that
// sneak in when a number is copied out of Arabic text.
const SEPARATORS = new RegExp(`[${WHITESPACE}${BIDI_MARKS}().-]`, "g");

/**
 * Parses an Egyptian mobile number written in any common format:
 * `01001234567`, `+20 100 123 4567`, `0020…`, `٠١٠٠١٢٣٤٥٦٧`.
 */
export function parsePhone(input: string): Result<MobileNumber, PhoneError> {
  const cleaned = toWesternDigits(input).replace(SEPARATORS, "");
  if (cleaned === "") return err("EMPTY");
  if (!/^\+?\d+$/.test(cleaned)) return err("INVALID_CHARACTERS");

  const hasPlus = cleaned.startsWith("+");
  const digits = hasPlus ? cleaned.slice(1) : cleaned;

  let subscriber: string;
  if (hasPlus) {
    if (!digits.startsWith("20")) return err("NOT_EGYPTIAN");
    subscriber = digits.slice(2);
  } else if (digits.startsWith("00")) {
    if (!digits.startsWith("0020")) return err("NOT_EGYPTIAN");
    subscriber = digits.slice(4);
  } else if (digits.startsWith("20") && digits.length === 12) {
    subscriber = digits.slice(2);
  } else if (digits.startsWith("0")) {
    subscriber = digits.slice(1);
  } else {
    subscriber = digits;
  }

  if (subscriber === "") return err("INVALID_LENGTH");
  if (!subscriber.startsWith("1")) return err("NOT_MOBILE");
  if (subscriber.length !== 10) return err("INVALID_LENGTH");

  const prefix = `0${subscriber.slice(0, 2)}`;
  const operator = OPERATOR_BY_PREFIX.get(prefix);
  if (!operator) return err("UNKNOWN_PREFIX");

  return ok({ national: `0${subscriber}`, e164: `+20${subscriber}`, prefix, operator });
}

export function isValidPhone(input: string): boolean {
  return parsePhone(input).ok;
}
