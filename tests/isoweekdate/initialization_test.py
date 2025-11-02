from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate


@pytest.mark.parametrize("value", ["0001-W01-1", "2000-W01-2", "2020-W53-3", "9999-W52-7"])
def test_valid_value(isoweekdate_constructor: type[IsoWeekDate], value: str) -> None:
    assert isoweekdate_constructor(value) is not None


@pytest.mark.parametrize(
    ("value", "err_msg"),
    [
        ("2025-W53-5", "Invalid week number"),
        ("abcd-xyz-1", "Invalid isoweek date format"),
        ("0000-W01-1", "Invalid isoweek date format"),
        ("2023-W00-1", "Invalid isoweek date format"),
        ("2023-W54-1", "Invalid isoweek date format"),
        ("2023-W01-0", "Invalid isoweek date format"),
        ("2023-W01-8", "Invalid isoweek date format"),
        ("abcd-xyz", "Invalid isoweek date format"),
        ("0000-W01", "Invalid isoweek date format"),
    ],
)
def test_invalid_value(isoweekdate_constructor: type[IsoWeekDate], value: str, err_msg: str) -> None:
    with pytest.raises(ValueError, match=err_msg):
        isoweekdate_constructor(value)
