from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING
from typing import Any

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate


@pytest.mark.parametrize("value", ["0001-W01-1", "2000-W01-2", "2020-W53-3", "9999-W52-7"])
def test_valid_value(isoweekdate_constructor: type[IsoWeekDate], value: str) -> None:
    assert isoweekdate_constructor(value) is not None


@pytest.mark.parametrize(
    ("value", "context"),
    [
        ("2025-W53-5", pytest.raises(ValueError, match="Invalid week number")),
        ("abcd-xyz-1", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("0000-W01-1", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2023-W00-1", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2023-W54-1", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2023-W01-0", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2023-W01-8", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("abcd-xyz", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("0000-W01", pytest.raises(ValueError, match="Invalid isoweek date format")),
    ],
)
def test_invalid_value(isoweekdate_constructor: type[IsoWeekDate], value: str, context: Any) -> None:
    with deepcopy(context):
        isoweekdate_constructor(value)
