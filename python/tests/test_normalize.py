from __future__ import annotations

import re
from typing import Any

import pytest
from conftest import load_spec

from wasta import normalize_arabic, to_arabic_digits, to_western_digits

SPEC = load_spec("normalize")


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


@pytest.mark.parametrize("case", SPEC["default"], ids=lambda c: repr(c["input"]))
def test_normalize_defaults(case: dict[str, str]) -> None:
    assert normalize_arabic(case["input"]) == case["output"]


@pytest.mark.parametrize("case", SPEC["options"], ids=lambda c: repr(c["options"]))
def test_normalize_options(case: dict[str, Any]) -> None:
    options = {snake_case(k): v for k, v in case["options"].items()}
    assert normalize_arabic(case["input"], **options) == case["output"]


def test_normalize_is_idempotent() -> None:
    for case in SPEC["default"]:
        once = normalize_arabic(case["input"])
        assert normalize_arabic(once) == once


@pytest.mark.parametrize("case", SPEC["toWesternDigits"], ids=lambda c: c["input"])
def test_to_western_digits(case: dict[str, str]) -> None:
    assert to_western_digits(case["input"]) == case["output"]


@pytest.mark.parametrize("case", SPEC["toArabicDigits"], ids=lambda c: c["input"])
def test_to_arabic_digits(case: dict[str, str]) -> None:
    assert to_arabic_digits(case["input"]) == case["output"]
