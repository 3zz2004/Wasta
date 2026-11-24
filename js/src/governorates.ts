import { GOVERNORATE_DATA } from "./generated/data.js";
import { normalizeArabic } from "./normalize.js";

export type GovernorateCode = (typeof GOVERNORATE_DATA)[number]["code"];

export interface Governorate {
  /** The two-digit code used in national ID numbers. */
  readonly code: GovernorateCode;
  readonly slug: string;
  readonly nameAr: string;
  readonly nameEn: string;
  readonly aliases: readonly string[];
}

export const governorates: readonly Governorate[] = Object.freeze(
  GOVERNORATE_DATA.map((g) => Object.freeze({ ...g, aliases: Object.freeze([...g.aliases]) })),
);

const BY_CODE: ReadonlyMap<string, Governorate> = new Map(governorates.map((g) => [g.code, g]));

export function getGovernorate(code: string): Governorate | undefined {
  return BY_CODE.get(code);
}

const ARABIC_FILLERS = new Set(["محافظه"]);
const ENGLISH_FILLERS = new Set(["governorate", "gov", "el", "al"]);

/**
 * Every spelling of a name collapses to a small set of keys, so "كفرالشيخ",
 * "محافظة كفر الشيخ" and "Kafr-El-Sheikh" all meet in the same place.
 */
function keysOf(name: string): string[] {
  const text = normalizeArabic(name).toLowerCase().replace(/[-_'’.,]/g, " ");
  const words = text.split(" ").filter(Boolean);

  if (/[\u0600-\u06ff]/.test(text)) {
    const kept = words.filter((w) => !ARABIC_FILLERS.has(w));
    const withoutArticle = kept.map((w) => (w.startsWith("ال") && w.length > 3 ? w.slice(2) : w));
    return unique([kept.join(""), withoutArticle.join("")]);
  }

  const kept = words.filter((w) => !ENGLISH_FILLERS.has(w));
  return unique([words.filter((w) => w !== "governorate").join(""), kept.join("")]);
}

const unique = (keys: string[]) => [...new Set(keys.filter(Boolean))];

const BY_KEY: ReadonlyMap<string, Governorate> = (() => {
  const index = new Map<string, Governorate>();
  for (const g of governorates) {
    for (const name of [g.nameAr, g.nameEn, g.slug, ...g.aliases]) {
      for (const key of keysOf(name)) index.set(key, g);
    }
  }
  return index;
})();

/** Finds a governorate by its Arabic or English name, tolerating common spelling variants. */
export function findGovernorate(name: string): Governorate | undefined {
  for (const key of keysOf(name)) {
    const match = BY_KEY.get(key);
    if (match) return match;
  }
  return undefined;
}
