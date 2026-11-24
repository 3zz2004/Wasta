from __future__ import annotations

import re
from dataclasses import dataclass

from ._data import load
from .normalize import normalize_arabic


@dataclass(frozen=True)
class Governorate:
    code: str
    """The two-digit code used in national ID numbers."""
    slug: str
    name_ar: str
    name_en: str
    aliases: tuple[str, ...]


GOVERNORATES: tuple[Governorate, ...] = tuple(
    Governorate(
        code=g["code"],
        slug=g["slug"],
        name_ar=g["nameAr"],
        name_en=g["nameEn"],
        aliases=tuple(g["aliases"]),
    )
    for g in load("governorates.json")
)

_BY_CODE = {g.code: g for g in GOVERNORATES}

_ARABIC = re.compile("[\u0600-\u06ff]")
_PUNCTUATION = re.compile("[-_'’.,]")
_ARABIC_FILLERS = {"محافظه"}
_ENGLISH_FILLERS = {"governorate", "gov", "el", "al"}


def get_governorate(code: str) -> Governorate | None:
    return _BY_CODE.get(code)


def _keys_of(name: str) -> list[str]:
    """Every spelling of a name collapses to a small set of keys, so "كفرالشيخ",
    "محافظة كفر الشيخ" and "Kafr-El-Sheikh" all meet in the same place."""
    text = _PUNCTUATION.sub(" ", normalize_arabic(name).lower())
    words = [w for w in text.split(" ") if w]

    if _ARABIC.search(text):
        kept = [w for w in words if w not in _ARABIC_FILLERS]
        without_article = [w[2:] if w.startswith("ال") and len(w) > 3 else w for w in kept]
        keys = ["".join(kept), "".join(without_article)]
    else:
        keys = ["".join(w for w in words if w != "governorate"), "".join(w for w in words if w not in _ENGLISH_FILLERS)]

    return [k for k in dict.fromkeys(keys) if k]


_BY_KEY: dict[str, Governorate] = {
    key: g for g in GOVERNORATES for name in (g.name_ar, g.name_en, g.slug, *g.aliases) for key in _keys_of(name)
}


def find_governorate(name: str) -> Governorate | None:
    """Find a governorate by its Arabic or English name, tolerating common spelling variants."""
    for key in _keys_of(name):
        match = _BY_KEY.get(key)
        if match is not None:
            return match
    return None
