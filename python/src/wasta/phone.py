from __future__ import annotations

import re
from dataclasses import dataclass

from ._chars import BIDI_MARKS, WHITESPACE
from ._data import load
from ._errors import InvalidPhoneError
from .digits import to_western_digits

_OPERATOR_BY_PREFIX: dict[str, str] = {p["prefix"]: p["operator"] for p in load("mobile-prefixes.json")}

_SEPARATORS = re.compile(f"[{WHITESPACE}{BIDI_MARKS}().-]")
_DIGITS = re.compile(r"\+?[0-9]+")


@dataclass(frozen=True)
class MobileNumber:
    national: str
    """Local format, e.g. ``01001234567``."""
    e164: str
    """E.164 format, e.g. ``+201001234567``."""
    prefix: str
    """e.g. ``010``."""
    operator: str
    """The operator that owns the prefix. Egypt has number portability, so a
    subscriber may have moved to another network since the number was issued."""


def parse_phone(value: str) -> MobileNumber:
    """Parse an Egyptian mobile number written in any common format.

    Raises :class:`InvalidPhoneError` with one of these codes: ``EMPTY``,
    ``INVALID_CHARACTERS``, ``NOT_EGYPTIAN``, ``NOT_MOBILE``,
    ``INVALID_LENGTH``, ``UNKNOWN_PREFIX``.
    """
    cleaned = _SEPARATORS.sub("", to_western_digits(value))
    if not cleaned:
        raise InvalidPhoneError("EMPTY", "Phone number is empty")
    if not _DIGITS.fullmatch(cleaned):
        raise InvalidPhoneError("INVALID_CHARACTERS", f"Phone number contains invalid characters: {value!r}")

    has_plus = cleaned.startswith("+")
    digits = cleaned[1:] if has_plus else cleaned

    if has_plus:
        if not digits.startswith("20"):
            raise InvalidPhoneError("NOT_EGYPTIAN", f"Not an Egyptian number: {value!r}")
        subscriber = digits[2:]
    elif digits.startswith("00"):
        if not digits.startswith("0020"):
            raise InvalidPhoneError("NOT_EGYPTIAN", f"Not an Egyptian number: {value!r}")
        subscriber = digits[4:]
    elif digits.startswith("20") and len(digits) == 12:
        subscriber = digits[2:]
    elif digits.startswith("0"):
        subscriber = digits[1:]
    else:
        subscriber = digits

    if not subscriber:
        raise InvalidPhoneError("INVALID_LENGTH", f"Phone number is too short: {value!r}")
    if not subscriber.startswith("1"):
        raise InvalidPhoneError("NOT_MOBILE", f"Not a mobile number: {value!r}")
    if len(subscriber) != 10:
        raise InvalidPhoneError("INVALID_LENGTH", f"Mobile numbers have 11 digits: {value!r}")

    prefix = "0" + subscriber[:2]
    operator = _OPERATOR_BY_PREFIX.get(prefix)
    if operator is None:
        raise InvalidPhoneError("UNKNOWN_PREFIX", f"Unknown mobile prefix {prefix}: {value!r}")

    return MobileNumber(national="0" + subscriber, e164="+20" + subscriber, prefix=prefix, operator=operator)


def is_valid_phone(value: str) -> bool:
    try:
        parse_phone(value)
    except InvalidPhoneError:
        return False
    return True
