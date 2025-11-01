from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("other_value", "expected", "exc_type", "exc_match"),
    [
        ("2023-W01", True, None, None),
        ("2023-W02", False, None, None),
        (date(2023, 1, 4), True, None, None),
        (date(2023, 1, 1), False, None, None),
        (datetime(2023, 1, 4, tzinfo=timezone.utc), True, None, None),
        (datetime(2023, 1, 1, tzinfo=timezone.utc), False, None, None),
        ((), None, TypeError, "Cannot compare type"),
        (123, None, TypeError, "Cannot compare type"),
    ],
)
def test__contains__(
    isoweek_constructor: type[IsoWeek],
    other_value: str | date | datetime | tuple[Any, ...] | int,
    expected: bool | None,
    exc_type: type[Exception] | None,
    exc_match: str | None,
) -> None:
    """Tests __contains__ method of IsoWeek class"""
    obj = isoweek_constructor(value)

    context = pytest.raises(exc_type, match=exc_match) if exc_type else do_not_raise()

    # Convert string to actual IsoWeek object for certain tests
    if isinstance(other_value, str) and other_value.startswith("202"):
        week_obj = isoweek_constructor(other_value)
        with context:
            r = week_obj in obj
            assert r == expected
    else:
        with context:
            r = other_value in obj
            assert r == expected


@pytest.mark.parametrize(
    ("other_value", "expected", "exc_type", "exc_match"),
    [
        (date(2023, 1, 4), True, None, None),
        (date(2023, 1, 1) + timedelta(weeks=52), False, None, None),
        ((1, 2, 3), None, TypeError, "Cannot compare type"),
        (123, None, TypeError, "Cannot compare type"),
    ],
)
def test_contains_method(
    isoweek_constructor: type[IsoWeek],
    other_value: Sequence[date] | date | tuple[int, ...] | int,
    expected: Sequence[bool] | bool | None,
    exc_type: type[Exception] | None,
    exc_match: str | None,
) -> None:
    """Tests contains method of IsoWeek class"""
    obj = isoweek_constructor(value)

    context = pytest.raises(exc_type, match=exc_match) if exc_type else do_not_raise()

    with context:
        if isinstance(other_value, (date, datetime, str)):
            r = obj.contains(other_value)
            assert isinstance(r, bool)
            assert r == expected
        else:
            # For invalid types, this will raise an error
            obj.contains(other_value)  # type: ignore[arg-type]


def test_contains_method_with_days(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests contains method with the days property"""
    obj = isoweek_constructor(value)
    days = obj.days

    result = obj.contains(days)
    expected = tuple(True for _ in days)

    assert result == expected


def test_contains_method_with_single_day(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests contains method with a single day"""
    obj = isoweek_constructor(value)
    day = obj.days[0]

    assert obj.contains(day) is True
