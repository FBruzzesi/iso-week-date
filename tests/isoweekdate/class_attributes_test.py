from __future__ import annotations

from datetime import timedelta
from typing import Final

from iso_week_date import IsoWeekDate
from iso_week_date._patterns import ISOWEEKDATE__DATE_FORMAT, ISOWEEKDATE__FORMAT, ISOWEEKDATE_PATTERN

value: Final[str] = "2025-W02-1"


def test_class_attributes(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    assert isoweekdate_constructor._pattern == ISOWEEKDATE_PATTERN
    assert isoweekdate_constructor._format == ISOWEEKDATE__FORMAT
    assert isoweekdate_constructor._date_format == ISOWEEKDATE__DATE_FORMAT

    obj = isoweekdate_constructor(value)

    assert obj._pattern == ISOWEEKDATE_PATTERN
    assert obj._format == ISOWEEKDATE__FORMAT
    assert obj._date_format == ISOWEEKDATE__DATE_FORMAT


def test_offset(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    offset = timedelta(0) if isoweekdate_constructor is IsoWeekDate else timedelta(days=1)
    assert isoweekdate_constructor.offset_ == offset

    obj = isoweekdate_constructor(value)

    assert obj.offset_ == offset
