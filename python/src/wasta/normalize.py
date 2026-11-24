from __future__ import annotations

import re

from ._chars import BIDI_MARKS, WHITESPACE
from .digits import to_western_digits

_DIACRITICS = re.compile("[\u0610-\u061a\u064b-\u065f\u0670\u06d6-\u06dc\u06df-\u06e8\u06ea-\u06ed]")
_BIDI = re.compile(f"[{BIDI_MARKS}]")
_ALEF_VARIANTS = re.compile("[\u0622\u0623\u0625\u0671]")
_SPACES = re.compile(f"[{WHITESPACE}]+")


def normalize_arabic(
    text: str,
    *,
    diacritics: bool = True,
    tatweel: bool = True,
    alef: bool = True,
    alef_maqsura: bool = True,
    ta_marbuta: bool = True,
    hamza: bool = False,
    digits: bool = True,
    whitespace: bool = True,
) -> str:
    """Normalize Arabic text for comparison and search.

    This is lossy on purpose: "مدرسة" and "مدرسه" become equal. Use it for keys,
    indexes and matching, never for text you display back to users.
    """
    out = _BIDI.sub("", text)
    if diacritics:
        out = _DIACRITICS.sub("", out)
    if tatweel:
        out = out.replace("\u0640", "")
    if alef:
        out = _ALEF_VARIANTS.sub("\u0627", out)
    if alef_maqsura:
        out = out.replace("\u0649", "\u064a")
    if ta_marbuta:
        out = out.replace("\u0629", "\u0647")
    if hamza:
        out = out.replace("\u0624", "\u0648").replace("\u0626", "\u064a")
    if digits:
        out = to_western_digits(out)
    if whitespace:
        out = _SPACES.sub(" ", out).strip(" ")
    return out
