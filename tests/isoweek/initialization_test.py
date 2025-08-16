from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING
from typing import Any

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek


@pytest.mark.parametrize("value", ["0001-W01", "2000-W01", "2020-W53", "9999-W52"])
def test_valid_value(isoweek_constructor: type[IsoWeek], value: str) -> None:
    assert isoweek_constructor(value) is not None


@pytest.mark.parametrize(
    ("value", "context"),
    [
        ("2025-W53", pytest.raises(ValueError, match="Invalid week number")),
        ("abcd-xyz", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("0000-W01", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2025-W00", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2025-W54", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2025-W54-1", pytest.raises(ValueError, match="Invalid isoweek date format")),
    ],
)
def test_invalid_value(isoweek_constructor: type[IsoWeek], value: str, context: Any) -> None:
    with deepcopy(context):
        isoweek_constructor(value)
