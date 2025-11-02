from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek


@pytest.mark.parametrize("value", ["0001-W01", "2000-W01", "2020-W53", "9999-W52"])
def test_valid_value(isoweek_constructor: type[IsoWeek], value: str) -> None:
    assert isoweek_constructor(value) is not None


@pytest.mark.parametrize(
    ("value", "err_msg"),
    [
        ("2025-W53", "Invalid week number"),
        ("abcd-xyz", "Invalid isoweek date format"),
        ("0000-W01", "Invalid isoweek date format"),
        ("2025-W00", "Invalid isoweek date format"),
        ("2025-W54", "Invalid isoweek date format"),
        ("2025-W54-1", "Invalid isoweek date format"),
    ],
)
def test_invalid_value(isoweek_constructor: type[IsoWeek], value: str, err_msg: str) -> None:
    with pytest.raises(ValueError, match=err_msg):
        isoweek_constructor(value)
