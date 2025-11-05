from __future__ import annotations

from datetime import timedelta
from typing import Final

from iso_week_date import IsoWeek
from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEK__FORMAT, ISOWEEK_PATTERN

value: Final[str] = "2025-W02"


def test_class_attributes(isoweek_constructor: type[IsoWeek]) -> None:
    assert isoweek_constructor._pattern == ISOWEEK_PATTERN
    assert isoweek_constructor._format == ISOWEEK__FORMAT
    assert isoweek_constructor._date_format == ISOWEEK__DATE_FORMAT

    obj = isoweek_constructor(value)

    assert obj._pattern == ISOWEEK_PATTERN
    assert obj._format == ISOWEEK__FORMAT
    assert obj._date_format == ISOWEEK__DATE_FORMAT


def test_offset(isoweek_constructor: type[IsoWeek]) -> None:
    offset = timedelta(0) if isoweek_constructor is IsoWeek else timedelta(days=1)
    assert isoweek_constructor.offset_ == offset

    obj = isoweek_constructor(value)

    assert obj.offset_ == offset
