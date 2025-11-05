from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from datetime import date, datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("other_value", "expected", "expected_exception", "err_msg"),
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
    expected_exception: type[Exception] | None,
    err_msg: str | None,
) -> None:
    """Tests __contains__ method of IsoWeek class"""
    context = pytest.raises(expected_exception, match=err_msg) if expected_exception else do_not_raise()
    obj = isoweek_constructor(value)

    other = isoweek_constructor(other_value) if isinstance(other_value, str) else other_value
    with context:
        r = other in obj
        assert r == expected


@pytest.mark.parametrize(
    ("other_value", "expected", "expected_exception", "err_msg"),
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
    expected_exception: type[Exception] | None,
    err_msg: str | None,
) -> None:
    """Tests contains method of IsoWeek class"""
    obj = isoweek_constructor(value)

    context = pytest.raises(expected_exception, match=err_msg) if expected_exception else do_not_raise()
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
