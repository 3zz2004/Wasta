from __future__ import annotations

from datetime import date
from typing import Any

import pytest
from conftest import load_spec

from wasta import InvalidNationalIdError, NationalIdInfo, get_governorate, is_valid_national_id, parse_national_id

SPEC = load_spec("national-id")
TODAY = date.fromisoformat(SPEC["today"])


@pytest.mark.parametrize("case", SPEC["valid"], ids=lambda c: repr(c["input"]))
def test_parses_valid_ids(case: dict[str, Any]) -> None:
    assert parse_national_id(case["input"], today=TODAY) == NationalIdInfo(
        birth_date=date.fromisoformat(case["birthDate"]),
        governorate=None if case["bornAbroad"] else get_governorate(case["governorateCode"]),
        governorate_code=case["governorateCode"],
        born_abroad=case["bornAbroad"],
        gender=case["gender"],
    )
    assert is_valid_national_id(case["input"], today=TODAY)


@pytest.mark.parametrize("case", SPEC["invalid"], ids=lambda c: repr(c["input"]))
def test_rejects_invalid_ids(case: dict[str, str]) -> None:
    with pytest.raises(InvalidNationalIdError) as info:
        parse_national_id(case["input"], today=TODAY)
    assert info.value.code == case["error"]
    assert not is_valid_national_id(case["input"], today=TODAY)


def test_uses_the_current_date_by_default() -> None:
    with pytest.raises(InvalidNationalIdError) as info:
        parse_national_id("39912311201538")
    assert info.value.code == "FUTURE_BIRTH_DATE"
