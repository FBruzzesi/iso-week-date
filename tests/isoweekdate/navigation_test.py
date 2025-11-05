from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate

value: Final[str] = "2023-W01-1"


def test_next(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    """Tests next method of IsoWeekDate class"""
    obj = isoweekdate_constructor(value)
    expected = isoweekdate_constructor("2023-W01-2")

    assert obj.next() == obj + 1 == expected


def test_prev(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    """Tests prev method of IsoWeekDate class"""
    obj = isoweekdate_constructor(value)
    expected = isoweekdate_constructor("2022-W52-7")

    assert obj.previous() == obj - 1 == expected
