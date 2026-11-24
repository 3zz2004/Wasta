import { BIDI_MARKS, WHITESPACE } from "./chars.js";
import { toWesternDigits } from "./digits.js";

export interface NormalizeOptions {
  /** Strip tashkeel and Quranic marks. Default `true`. */
  diacritics?: boolean;
  /** Remove tatweel (ـ). Default `true`. */
  tatweel?: boolean;
  /** أ إ آ ٱ → ا. Default `true`. */
  alef?: boolean;
  /** ى → ي. Default `true`. */
  alefMaqsura?: boolean;
  /** ة → ه. Default `true`. */
  taMarbuta?: boolean;
  /** ؤ → و and ئ → ي. Default `false`. */
  hamza?: boolean;
  /** Arabic-Indic and Persian digits → 0-9. Default `true`. */
  digits?: boolean;
  /** Collapse runs of whitespace into one space and trim. Default `true`. */
  whitespace?: boolean;
}

const DIACRITICS = /[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06dc\u06df-\u06e8\u06ea-\u06ed]/g;
const BIDI = new RegExp(`[${BIDI_MARKS}]`, "g");
const SPACES = new RegExp(`[${WHITESPACE}]+`, "g");
const TATWEEL = /\u0640/g;
const ALEF_VARIANTS = /[\u0622\u0623\u0625\u0671]/g;

/**
 * Normalizes Arabic text for comparison and search.
 *
 * This is lossy on purpose: "مدرسة" and "مدرسه" become equal. Use it for keys,
 * indexes and matching, never for text you display back to users.
 */
export function normalizeArabic(text: string, options: NormalizeOptions = {}): string {
  const {
    diacritics = true,
    tatweel = true,
    alef = true,
    alefMaqsura = true,
    taMarbuta = true,
    hamza = false,
    digits = true,
    whitespace = true,
  } = options;

  let out = text.replace(BIDI, "");
  if (diacritics) out = out.replace(DIACRITICS, "");
  if (tatweel) out = out.replace(TATWEEL, "");
  if (alef) out = out.replace(ALEF_VARIANTS, "\u0627");
  if (alefMaqsura) out = out.replace(/\u0649/g, "\u064a");
  if (taMarbuta) out = out.replace(/\u0629/g, "\u0647");
  if (hamza) out = out.replace(/\u0624/g, "\u0648").replace(/\u0626/g, "\u064a");
  if (digits) out = toWesternDigits(out);
  if (whitespace) out = out.replace(SPACES, " ").replace(/^ | $/g, "");
  return out;
}
