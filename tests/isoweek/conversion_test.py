from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING
from typing import Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("weekday", "exc_type", "exc_match"),
    [
        (1, None, None),
        (1.0, TypeError, "`weekday` must be an integer"),
        (-1, ValueError, "Weekday must be between 1 and 7"),
        (8, ValueError, "Weekday must be between 1 and 7"),
    ],
)
def test_to_datetime_raise(
    isoweek_constructor: type[IsoWeek],
    weekday: int,
    exc_type: type[Exception] | None,
    exc_match: str | None,
) -> None:
    """Tests to_datetime method of IsoWeek class"""
    obj = isoweek_constructor(value)
    context = pytest.raises(exc_type, match=exc_match) if exc_type else do_not_raise()
    with context:
        obj.to_datetime(weekday)
