import { WHITESPACE } from "./chars.js";
import { toWesternDigits } from "./digits.js";

export type TafqeetErrorCode = "INVALID_NUMBER" | "NEGATIVE" | "TOO_MANY_DECIMALS" | "OUT_OF_RANGE";

export class TafqeetError extends RangeError {
  readonly code: TafqeetErrorCode;

  constructor(code: TafqeetErrorCode, message: string) {
    super(message);
    this.name = "TafqeetError";
    this.code = code;
  }
}

export interface TafqeetOptions {
  /** Wrap the result in «فقط … لا غير», as invoices and cheques expect. Default `true`. */
  wrap?: boolean;
}

/** Largest supported value: 999,999,999,999 (just under a trillion). */
export const MAX_AMOUNT = 999_999_999_999;

const ONES = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"];
const TENS = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"];
const EDGE_SPACES = new RegExp(`^[${WHITESPACE}]+|[${WHITESPACE}]+$`, "g");

const HUNDREDS = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"];

interface Noun {
  singular: string;
  dual: string;
  /** The dual before another noun: «ألفا جنيه», not «ألفان جنيه». */
  dualConstruct: string;
  plural: string;
  /** Singular with tanween fath, used after 11–99: «أحد عشر ألفًا». */
  accusative: string;
}

const noun = (singular: string, dual: string, plural: string): Noun => ({
  singular,
  dual,
  dualConstruct: dual.slice(0, -1),
  plural,
  accusative: `${singular}\u064bا`,
});

const SCALES = [noun("ألف", "ألفان", "آلاف"), noun("مليون", "مليونان", "ملايين"), noun("مليار", "ملياران", "مليارات")];
const POUND = noun("جنيه", "جنيهان", "جنيهات");
const PIASTER = noun("قرش", "قرشان", "قروش");

function belowHundred(n: number): string {
  if (n < 10) return ONES[n]!;
  if (n === 10) return TENS[1]!;
  if (n === 11) return "أحد عشر";
  if (n === 12) return "اثنا عشر";
  if (n < 20) return `${ONES[n - 10]} عشر`;
  const unit = n % 10;
  const ten = TENS[Math.floor(n / 10)]!;
  return unit === 0 ? ten : `${ONES[unit]} و${ten}`;
}

/** 1–999. `construct` is true when a noun directly follows, which turns «مائتان» into «مائتا». */
function group(n: number, construct: boolean): string {
  const h = Math.floor(n / 100);
  const rest = n % 100;
  const hundred = h === 2 && rest === 0 && construct ? "مائتا" : HUNDREDS[h]!;
  return [hundred, belowHundred(rest)].filter(Boolean).join(" و");
}

/** The form a counted noun takes after a number, following the rules of تمييز العدد. */
function counted(n: number, item: Noun, followedByNoun: boolean): string {
  if (n === 1) return item.singular;
  if (n === 2) return followedByNoun ? item.dualConstruct : item.dual;
  const lastTwo = n % 100;
  const count = group(n, lastTwo === 0);
  if (lastTwo >= 3 && lastTwo <= 10) return `${count} ${item.plural}`;
  if (lastTwo >= 11) return `${count} ${followedByNoun ? item.singular : item.accusative}`;
  return `${count} ${item.singular}`;
}

/** `followedByNoun` means a currency word comes right after the number. */
function integerWords(n: number, followedByNoun: boolean): string {
  if (n === 0) return "صفر";

  const groups: number[] = [];
  for (let rest = n; rest > 0; rest = Math.floor(rest / 1000)) groups.push(rest % 1000);
  const last = groups.findIndex((g) => g !== 0);

  const parts: string[] = [];
  for (let i = groups.length - 1; i >= 0; i--) {
    const g = groups[i]!;
    if (g === 0) continue;
    const nounFollows = followedByNoun && i === last;
    parts.push(i === 0 ? group(g, nounFollows) : counted(g, SCALES[i - 1]!, nounFollows));
  }
  return parts.join(" و");
}

function amountOf(n: number, item: Noun): string {
  if (n === 1) return `${item.singular} واحد`;
  if (n === 2) return item.dual;
  const lastTwo = n % 100;
  const words = integerWords(n, true);
  if (lastTwo >= 3 && lastTwo <= 10) return `${words} ${item.plural}`;
  if (lastTwo >= 11) return `${words} ${item.accusative}`;
  return `${words} ${item.singular}`;
}

/** Spells out a whole number in Arabic: `1500` → «ألف وخمسمائة». */
export function numberToArabicWords(value: number): string {
  if (!Number.isSafeInteger(value)) throw new TafqeetError("INVALID_NUMBER", `Expected an integer, got ${value}`);
  if (value < 0) throw new TafqeetError("NEGATIVE", "Negative numbers are not supported");
  if (value > MAX_AMOUNT) throw new TafqeetError("OUT_OF_RANGE", `Numbers above ${MAX_AMOUNT} are not supported`);
  return integerWords(value, false);
}

/**
 * Writes an amount of Egyptian pounds in words, the way it appears on invoices:
 * `1500.25` → «فقط ألف وخمسمائة جنيه وخمسة وعشرون قرشًا لا غير».
 *
 * Amounts with more than two decimal places are rejected rather than rounded:
 * silently changing a sum of money is worse than an error.
 */
export function tafqeet(amount: number | string, options: TafqeetOptions = {}): string {
  const { pounds, piasters } = splitAmount(amount);

  let text: string;
  if (pounds === 0 && piasters === 0) text = `صفر ${POUND.singular}`;
  else if (piasters === 0) text = amountOf(pounds, POUND);
  else if (pounds === 0) text = amountOf(piasters, PIASTER);
  else text = `${amountOf(pounds, POUND)} و${amountOf(piasters, PIASTER)}`;

  return options.wrap === false ? text : `فقط ${text} لا غير`;
}

function splitAmount(amount: number | string): { pounds: number; piasters: number } {
  let text: string;
  if (typeof amount === "number") {
    if (!Number.isFinite(amount)) throw new TafqeetError("INVALID_NUMBER", `Not a finite number: ${amount}`);
    if (amount < 0) throw new TafqeetError("NEGATIVE", "Negative amounts are not supported");
    text = String(amount);
  } else {
    text = toWesternDigits(amount).replace(EDGE_SPACES, "").replace(/[,٬]/g, "").replace(/٫/g, ".");
  }

  if (text.startsWith("-")) throw new TafqeetError("NEGATIVE", "Negative amounts are not supported");
  const match = /^(\d+)(?:\.(\d+))?$/.exec(text);
  if (!match) {
    if (/^\d+(\.\d+)?e[+-]?\d+$/i.test(text)) {
      throw new TafqeetError("OUT_OF_RANGE", `Amounts must be between 0.01 and ${MAX_AMOUNT}`);
    }
    throw new TafqeetError("INVALID_NUMBER", `Not a valid amount: "${amount}"`);
  }

  const [, whole, fraction = ""] = match;
  const significant = fraction.replace(/0+$/, "");
  if (significant.length > 2) {
    throw new TafqeetError("TOO_MANY_DECIMALS", `Amounts can have at most two decimal places, got "${amount}"`);
  }

  const pounds = Number(whole);
  if (pounds > MAX_AMOUNT) throw new TafqeetError("OUT_OF_RANGE", `Amounts above ${MAX_AMOUNT} are not supported`);

  return { pounds, piasters: Number(significant.padEnd(2, "0")) };
}
