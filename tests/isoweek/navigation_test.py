from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


def test_next(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests next method of IsoWeek class"""
    obj = isoweek_constructor(value)
    expected = isoweek_constructor("2023-W02")

    assert obj.next() == obj + 1 == expected


def test_prev(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests prev method of IsoWeek class"""
    obj = isoweek_constructor(value)
    expected = isoweek_constructor("2022-W52")

    assert obj.previous() == obj - 1 == expected
