from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


def test_properties(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests properties of IsoWeek class, namely year, week, quarter and days"""
    obj = isoweek_constructor(value)

    min_year, max_year = 0, 9999
    min_week, max_week = 1, 53
    n_days = 7

    days = obj.days

    assert min_year <= obj.year <= max_year
    assert min_week <= obj.week <= max_week
    assert len(days) == n_days
    assert all(isinstance(day, date) for day in days)


@pytest.mark.parametrize(
    ("n", "expected_exception", "err_msg"),
    [
        (1, None, None),
        (1.0, TypeError, "`n` must be an integer"),
        (-1, ValueError, "`n` must be between 1 and 7"),
        (8, ValueError, "`n` must be between 1 and 7"),
        # `bool` is rejected here as well, so that the weekday-shaped arguments across the class
        # agree on what an integer is. `nth(True)` used to silently mean `nth(1)`.
        (True, TypeError, "`n` must be an integer"),
        (False, TypeError, "`n` must be an integer"),
        ("1", TypeError, "`n` must be an integer"),
        (Decimal(1), TypeError, "`n` must be an integer"),
    ],
)
def test_nth(
    isoweek_constructor: type[IsoWeek],
    n: Any,
    expected_exception: type[Exception] | None,
    err_msg: str | None,
) -> None:
    """Tests nth method of IsoWeek class"""
    obj = isoweek_constructor(value)
    context = pytest.raises(expected_exception, match=err_msg) if expected_exception else do_not_raise()
    with context:
        obj.nth(n)
