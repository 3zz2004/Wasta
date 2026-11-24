from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Literal

from ._chars import WHITESPACE
from ._errors import InvalidNationalIdError
from .digits import to_western_digits
from .governorates import Governorate, get_governorate

_BORN_ABROAD = "88"
_CENTURIES = {"2": 1900, "3": 2000}
_FOURTEEN_DIGITS = re.compile(r"[0-9]{14}")
_SPACES = re.compile(f"[{WHITESPACE}]")


@dataclass(frozen=True)
class NationalIdInfo:
    birth_date: date
    governorate: Governorate | None
    """``None`` when the holder was born outside Egypt (code 88)."""
    governorate_code: str
    born_abroad: bool
    gender: Literal["male", "female"]


def parse_national_id(value: str, *, today: date | None = None) -> NationalIdInfo:
    """Read the information encoded in a 14-digit Egyptian national ID.

    Layout: century (1) · YYMMDD (6) · governorate (2) · serial (4) · check (1).
    The second-to-last digit of the serial is odd for men and even for women.

    The check digit is not verified: its algorithm has never been published, so
    any implementation of it would be a guess.

    Raises :class:`InvalidNationalIdError` with one of these codes:
    ``INVALID_FORMAT``, ``INVALID_CENTURY``, ``INVALID_BIRTH_DATE``,
    ``FUTURE_BIRTH_DATE``, ``UNKNOWN_GOVERNORATE``.
    """
    national_id = _SPACES.sub("", to_western_digits(value))
    if not _FOURTEEN_DIGITS.fullmatch(national_id):
        raise InvalidNationalIdError("INVALID_FORMAT", "A national ID has exactly 14 digits")

    century = _CENTURIES.get(national_id[0])
    if century is None:
        raise InvalidNationalIdError("INVALID_CENTURY", f"Unknown century digit {national_id[0]}")

    try:
        birth_date = date(century + int(national_id[1:3]), int(national_id[3:5]), int(national_id[5:7]))
    except ValueError:
        raise InvalidNationalIdError("INVALID_BIRTH_DATE", "The encoded birth date does not exist") from None

    if birth_date > (today or date.today()):
        raise InvalidNationalIdError("FUTURE_BIRTH_DATE", "The encoded birth date is in the future")

    governorate_code = national_id[7:9]
    born_abroad = governorate_code == _BORN_ABROAD
    governorate = None if born_abroad else get_governorate(governorate_code)
    if not born_abroad and governorate is None:
        raise InvalidNationalIdError("UNKNOWN_GOVERNORATE", f"Unknown governorate code {governorate_code}")

    return NationalIdInfo(
        birth_date=birth_date,
        governorate=governorate,
        governorate_code=governorate_code,
        born_abroad=born_abroad,
        gender="male" if int(national_id[12]) % 2 == 1 else "female",
    )


def is_valid_national_id(value: str, *, today: date | None = None) -> bool:
    try:
        parse_national_id(value, today=today)
    except InvalidNationalIdError:
        return False
    return True
