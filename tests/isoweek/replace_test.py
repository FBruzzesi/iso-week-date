from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("year", "week", "expected"),
    [
        (2022, None, "2022-W01"),
        (None, 2, "2023-W02"),
        (2022, 52, "2022-W52"),
        (2024, 1, "2024-W01"),
    ],
)
def test_replace(isoweek_constructor: type[IsoWeek], year: int | None, week: int | None, expected: str) -> None:
    """Tests replace method of IsoWeek class"""
    obj = isoweek_constructor(value)
    expected_obj = isoweek_constructor(expected)

    assert obj.replace(year=year, week=week) == expected_obj
