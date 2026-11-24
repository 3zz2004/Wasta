from __future__ import annotations

from decimal import Decimal
from typing import Any

import pytest
from conftest import load_spec

from wasta import MAX_AMOUNT, TafqeetError, number_to_arabic_words, tafqeet

SPEC = load_spec("tafqeet")


@pytest.mark.parametrize("case", SPEC["words"], ids=lambda c: str(c["input"]))
def test_number_to_arabic_words(case: dict[str, Any]) -> None:
    assert number_to_arabic_words(case["input"]) == case["output"]


@pytest.mark.parametrize("value", [1.5, -3, MAX_AMOUNT + 1, True, "5"])
def test_number_to_arabic_words_rejects(value: Any) -> None:
    with pytest.raises(TafqeetError):
        number_to_arabic_words(value)


@pytest.mark.parametrize("case", SPEC["money"], ids=lambda c: repr(c["input"]))
def test_tafqeet(case: dict[str, Any]) -> None:
    assert tafqeet(case["input"]) == case["output"]


@pytest.mark.parametrize("case", SPEC["unwrapped"], ids=lambda c: repr(c["input"]))
def test_tafqeet_unwrapped(case: dict[str, Any]) -> None:
    assert tafqeet(case["input"], wrap=False) == case["output"]


@pytest.mark.parametrize("case", SPEC["errors"], ids=lambda c: repr(c["input"]))
def test_tafqeet_errors(case: dict[str, Any]) -> None:
    with pytest.raises(TafqeetError) as info:
        tafqeet(case["input"])
    assert info.value.code == case["error"]


def test_accepts_decimal() -> None:
    assert tafqeet(Decimal("1500.25")) == tafqeet("1500.25")


@pytest.mark.parametrize("value", [float("inf"), float("nan"), Decimal("NaN"), True, None])
def test_rejects_non_numbers(value: Any) -> None:
    with pytest.raises(TafqeetError) as info:
        tafqeet(value)
    assert info.value.code == "INVALID_NUMBER"
