from __future__ import annotations

from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate

value: Final[str] = "2023-W01-1"


@pytest.mark.parametrize(
    ("year", "week", "weekday", "expected"),
    [
        (2022, 1, 1, "2022-W01-1"),
        (2022, 1, 7, "2022-W01-7"),
        (2023, None, 2, "2023-W01-2"),
        (2023, 1, 7, "2023-W01-7"),
        (None, None, None, "2023-W01-1"),
        (None, None, 7, "2023-W01-7"),
    ],
)
def test_replace(
    isoweekdate_constructor: type[IsoWeekDate], year: int | None, week: int | None, weekday: int | None, expected: str
) -> None:
    """Tests replace method of IsoWeekDate class"""
    obj = isoweekdate_constructor(value)
    expected_obj = isoweekdate_constructor(expected)

    assert obj.replace(year=year, week=week, weekday=weekday) == expected_obj
