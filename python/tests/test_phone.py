from __future__ import annotations

import pytest
from conftest import load_spec

from wasta import InvalidPhoneError, MobileNumber, WastaError, is_valid_phone, parse_phone

SPEC = load_spec("phone")


@pytest.mark.parametrize("case", SPEC["valid"], ids=lambda c: repr(c["input"]))
def test_parses_valid_numbers(case: dict[str, str]) -> None:
    assert parse_phone(case["input"]) == MobileNumber(
        national=case["national"],
        e164=case["e164"],
        prefix=case["national"][:3],
        operator=case["operator"],
    )
    assert is_valid_phone(case["input"])


@pytest.mark.parametrize("case", SPEC["invalid"], ids=lambda c: repr(c["input"]))
def test_rejects_invalid_numbers(case: dict[str, str]) -> None:
    with pytest.raises(InvalidPhoneError) as info:
        parse_phone(case["input"])
    assert info.value.code == case["error"]
    assert not is_valid_phone(case["input"])


def test_errors_share_a_base_class() -> None:
    with pytest.raises(WastaError):
        parse_phone("")
    with pytest.raises(ValueError):
        parse_phone("")
