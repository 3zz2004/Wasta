from __future__ import annotations

import math
import re
from dataclasses import dataclass
from decimal import Decimal

from ._chars import WHITESPACE
from ._errors import TafqeetError
from .digits import to_western_digits

MAX_AMOUNT = 999_999_999_999
"""Largest supported value: 999,999,999,999 (just under a trillion)."""

Amount = int | float | str | Decimal

_ONES = ["", "واحد", "اثنان", "ثلاثة", "أربعة", "خمسة", "ستة", "سبعة", "ثمانية", "تسعة"]
_TENS = ["", "عشرة", "عشرون", "ثلاثون", "أربعون", "خمسون", "ستون", "سبعون", "ثمانون", "تسعون"]
_HUNDREDS = ["", "مائة", "مائتان", "ثلاثمائة", "أربعمائة", "خمسمائة", "ستمائة", "سبعمائة", "ثمانمائة", "تسعمائة"]

_EDGE_SPACES = re.compile(f"^[{WHITESPACE}]+|[{WHITESPACE}]+$")
_AMOUNT = re.compile(r"([0-9]+)(?:\.([0-9]+))?")
_EXPONENT = re.compile(r"[0-9]+(\.[0-9]+)?e[+-]?[0-9]+", re.IGNORECASE)


@dataclass(frozen=True)
class _Noun:
    singular: str
    dual: str
    plural: str

    @property
    def dual_construct(self) -> str:
        """The dual before another noun: «ألفا جنيه», not «ألفان جنيه»."""
        return self.dual[:-1]

    @property
    def accusative(self) -> str:
        """Singular with tanween fath, used after 11–99: «أحد عشر ألفًا»."""
        return self.singular + "\u064bا"


_SCALES = [_Noun("ألف", "ألفان", "آلاف"), _Noun("مليون", "مليونان", "ملايين"), _Noun("مليار", "ملياران", "مليارات")]
_POUND = _Noun("جنيه", "جنيهان", "جنيهات")
_PIASTER = _Noun("قرش", "قرشان", "قروش")


def _below_hundred(n: int) -> str:
    if n < 10:
        return _ONES[n]
    if n == 10:
        return _TENS[1]
    if n == 11:
        return "أحد عشر"
    if n == 12:
        return "اثنا عشر"
    if n < 20:
        return f"{_ONES[n - 10]} عشر"
    unit, ten = n % 10, _TENS[n // 10]
    return ten if unit == 0 else f"{_ONES[unit]} و{ten}"


def _group(n: int, construct: bool) -> str:
    """1–999. ``construct`` is true when a noun directly follows, which turns «مائتان» into «مائتا»."""
    h, rest = divmod(n, 100)
    hundred = "مائتا" if h == 2 and rest == 0 and construct else _HUNDREDS[h]
    return " و".join(part for part in (hundred, _below_hundred(rest)) if part)


def _counted(n: int, item: _Noun, followed_by_noun: bool) -> str:
    """The form a counted noun takes after a number, following the rules of تمييز العدد."""
    if n == 1:
        return item.singular
    if n == 2:
        return item.dual_construct if followed_by_noun else item.dual
    last_two = n % 100
    count = _group(n, last_two == 0)
    if 3 <= last_two <= 10:
        return f"{count} {item.plural}"
    if last_two >= 11:
        return f"{count} {item.singular if followed_by_noun else item.accusative}"
    return f"{count} {item.singular}"


def _integer_words(n: int, followed_by_noun: bool) -> str:
    """``followed_by_noun`` means a currency word comes right after the number."""
    if n == 0:
        return "صفر"

    groups: list[int] = []
    while n > 0:
        n, g = divmod(n, 1000)
        groups.append(g)
    last = next(i for i, g in enumerate(groups) if g)

    parts = []
    for i in range(len(groups) - 1, -1, -1):
        g = groups[i]
        if g == 0:
            continue
        noun_follows = followed_by_noun and i == last
        parts.append(_group(g, noun_follows) if i == 0 else _counted(g, _SCALES[i - 1], noun_follows))
    return " و".join(parts)


def _amount_of(n: int, item: _Noun) -> str:
    if n == 1:
        return f"{item.singular} واحد"
    if n == 2:
        return item.dual
    last_two = n % 100
    words = _integer_words(n, True)
    if 3 <= last_two <= 10:
        return f"{words} {item.plural}"
    if last_two >= 11:
        return f"{words} {item.accusative}"
    return f"{words} {item.singular}"


def number_to_arabic_words(value: int) -> str:
    """Spell out a whole number in Arabic: ``1500`` → «ألف وخمسمائة»."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise TafqeetError("INVALID_NUMBER", f"Expected an integer, got {value!r}")
    if value < 0:
        raise TafqeetError("NEGATIVE", "Negative numbers are not supported")
    if value > MAX_AMOUNT:
        raise TafqeetError("OUT_OF_RANGE", f"Numbers above {MAX_AMOUNT} are not supported")
    return _integer_words(value, False)


def tafqeet(amount: Amount, *, wrap: bool = True) -> str:
    """Write an amount of Egyptian pounds in words, the way it appears on invoices:
    ``1500.25`` → «فقط ألف وخمسمائة جنيه وخمسة وعشرون قرشًا لا غير».

    Amounts with more than two decimal places are rejected rather than rounded:
    silently changing a sum of money is worse than an error.
    """
    pounds, piasters = _split_amount(amount)

    if pounds == 0 and piasters == 0:
        text = f"صفر {_POUND.singular}"
    elif piasters == 0:
        text = _amount_of(pounds, _POUND)
    elif pounds == 0:
        text = _amount_of(piasters, _PIASTER)
    else:
        text = f"{_amount_of(pounds, _POUND)} و{_amount_of(piasters, _PIASTER)}"

    return f"فقط {text} لا غير" if wrap else text


def _split_amount(amount: Amount) -> tuple[int, int]:
    if isinstance(amount, bool):
        raise TafqeetError("INVALID_NUMBER", f"Not a valid amount: {amount!r}")
    if isinstance(amount, (int, float, Decimal)):
        if isinstance(amount, float) and not math.isfinite(amount):
            raise TafqeetError("INVALID_NUMBER", f"Not a finite number: {amount!r}")
        if isinstance(amount, Decimal) and not amount.is_finite():
            raise TafqeetError("INVALID_NUMBER", f"Not a finite number: {amount!r}")
        if amount < 0:
            raise TafqeetError("NEGATIVE", "Negative amounts are not supported")
        text = format(amount, "f") if isinstance(amount, Decimal) else repr(amount)
    elif isinstance(amount, str):
        text = _EDGE_SPACES.sub("", to_western_digits(amount)).replace(",", "").replace("٬", "").replace("٫", ".")
    else:
        raise TafqeetError("INVALID_NUMBER", f"Not a valid amount: {amount!r}")

    if text.startswith("-"):
        raise TafqeetError("NEGATIVE", "Negative amounts are not supported")
    match = _AMOUNT.fullmatch(text)
    if match is None:
        if _EXPONENT.fullmatch(text):
            raise TafqeetError("OUT_OF_RANGE", f"Amounts must be between 0.01 and {MAX_AMOUNT}")
        raise TafqeetError("INVALID_NUMBER", f"Not a valid amount: {amount!r}")

    whole, fraction = match.group(1), (match.group(2) or "").rstrip("0")
    if len(fraction) > 2:
        raise TafqeetError("TOO_MANY_DECIMALS", f"Amounts can have at most two decimal places, got {amount!r}")

    pounds = int(whole)
    if pounds > MAX_AMOUNT:
        raise TafqeetError("OUT_OF_RANGE", f"Amounts above {MAX_AMOUNT} are not supported")

    return pounds, int(fraction.ljust(2, "0"))
