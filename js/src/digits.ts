const ARABIC_INDIC_ZERO = 0x0660;
const EXTENDED_ARABIC_INDIC_ZERO = 0x06f0;

/** Converts Arabic-Indic (٠-٩) and Persian (۰-۹) digits to 0-9. Everything else is left untouched. */
export function toWesternDigits(text: string): string {
  return text.replace(/[\u0660-\u0669\u06f0-\u06f9]/g, (d) => {
    const code = d.charCodeAt(0);
    const base = code >= EXTENDED_ARABIC_INDIC_ZERO ? EXTENDED_ARABIC_INDIC_ZERO : ARABIC_INDIC_ZERO;
    return String(code - base);
  });
}

/** Converts 0-9 to Arabic-Indic digits (٠-٩). */
export function toArabicDigits(text: string): string {
  return text.replace(/[0-9]/g, (d) => String.fromCharCode(ARABIC_INDIC_ZERO + Number(d)));
}
