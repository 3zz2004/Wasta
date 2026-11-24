from __future__ import annotations

import dataclasses

import pytest
from conftest import load_spec

from wasta import GOVERNORATES, find_governorate, get_governorate

SPEC = load_spec("governorates")


def test_lists_all_27_governorates() -> None:
    assert len(GOVERNORATES) == 27
    assert len({g.code for g in GOVERNORATES}) == 27
    assert len({g.slug for g in GOVERNORATES}) == 27


def test_governorates_are_immutable() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        GOVERNORATES[0].name_en = "Somewhere"  # type: ignore[misc]


def test_get_governorate() -> None:
    governorate = get_governorate("15")
    assert governorate is not None
    assert governorate.name_en == "Kafr El Sheikh"
    assert get_governorate("88") is None


def test_no_two_governorates_claim_the_same_spelling() -> None:
    for g in GOVERNORATES:
        for name in (g.name_ar, g.name_en, g.slug, *g.aliases):
            found = find_governorate(name)
            assert found is not None and found.code == g.code, name


@pytest.mark.parametrize("case", SPEC["find"], ids=lambda c: c["input"])
def test_find_governorate(case: dict[str, str]) -> None:
    found = find_governorate(case["input"])
    assert found is not None
    assert found.code == case["code"]


@pytest.mark.parametrize("name", SPEC["notFound"])
def test_find_governorate_misses(name: str) -> None:
    assert find_governorate(name) is None
