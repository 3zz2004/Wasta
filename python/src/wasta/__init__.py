"""The Egyptian utilities every app ends up rewriting."""

from ._errors import InvalidNationalIdError, InvalidPhoneError, TafqeetError, WastaError
from .digits import to_arabic_digits, to_western_digits
from .governorates import GOVERNORATES, Governorate, find_governorate, get_governorate
from .national_id import NationalIdInfo, is_valid_national_id, parse_national_id
from .normalize import normalize_arabic
from .phone import MobileNumber, is_valid_phone, parse_phone
from .tafqeet import MAX_AMOUNT, number_to_arabic_words, tafqeet

__version__ = "0.1.0"

__all__ = [
    "GOVERNORATES",
    "MAX_AMOUNT",
    "Governorate",
    "InvalidNationalIdError",
    "InvalidPhoneError",
    "MobileNumber",
    "NationalIdInfo",
    "TafqeetError",
    "WastaError",
    "find_governorate",
    "get_governorate",
    "is_valid_national_id",
    "is_valid_phone",
    "normalize_arabic",
    "number_to_arabic_words",
    "parse_national_id",
    "parse_phone",
    "tafqeet",
    "to_arabic_digits",
    "to_western_digits",
]
