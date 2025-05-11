from __future__ import annotations

from contextlib import AbstractContextManager
from contextlib import nullcontext as do_not_raise
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Generator
from typing import Literal
from typing import Sequence

import pytest

from iso_week_date import IsoWeek


class CustomWeek(IsoWeek):
    """Custom IsoWeek class with offset of 1 day"""

    offset_ = timedelta(days=1)


isoweek = IsoWeek("2023-W01")
customweek = CustomWeek("2023-W01")


@pytest.mark.parametrize(
    ("value", "context"),
    [
        ("2023-W01", do_not_raise()),
        ("abcd-xyz", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("0000-W01", pytest.raises(ValueError, match="Invalid isoweek date format")),
        ("2023-W54", pytest.raises(ValueError, match="Invalid isoweek date format")),
    ],
)
def test_init(value: str, context: AbstractContextManager) -> None:
    """Tests __init__ and _validate methods of IsoWeek class"""
    with context:
        IsoWeek(value)


def test_properties() -> None:
    """Tests properties of IsoWeek class, namely year, week, quarter and days"""
    min_year, max_year = 0, 9999
    min_week, max_week = 1, 53
    n_days = 7

    days = isoweek.days

    assert min_year <= isoweek.year <= max_year
    assert min_week <= isoweek.week <= max_week
    assert len(days) == n_days
    assert all(isinstance(day, date) for day in days)


@pytest.mark.parametrize(
    ("n", "context"),
    [
        (1, do_not_raise()),
        (1.0, pytest.raises(TypeError, match="`n` must be an integer")),
        (-1, pytest.raises(ValueError, match="`n` must be between 1 and 7")),
        (8, pytest.raises(ValueError, match="`n` must be between 1 and 7")),
    ],
)
def test_nth(n: int, context: AbstractContextManager) -> None:
    """Tests nth method of IsoWeek class"""
    with context:
        isoweek.nth(n)


def test_hash() -> None:
    """Tests __hash__ method of IsoWeek class"""
    assert hash(isoweek) != hash(customweek)


def test_next() -> None:
    """Tests next method of IsoWeek class"""
    assert isoweek.next() == isoweek + 1 == IsoWeek("2023-W02")
    assert customweek.next() == customweek + 1 == CustomWeek("2023-W02")


def test_prev() -> None:
    """Tests prev method of IsoWeek class"""
    assert isoweek.previous() == isoweek - 1 == IsoWeek("2022-W52")
    assert customweek.previous() == customweek - 1 == CustomWeek("2022-W52")


@pytest.mark.parametrize(
    ("weekday", "context"),
    [
        (1, do_not_raise()),
        (1.0, pytest.raises(TypeError, match="`weekday` must be an integer")),
        (-1, pytest.raises(ValueError, match="Weekday must be between 1 and 7")),
        (8, pytest.raises(ValueError, match="Weekday must be between 1 and 7")),
    ],
)
def test_to_datetime_raise(weekday: int, context: AbstractContextManager) -> None:
    """Tests to_datetime method of IsoWeek class"""
    with context:
        isoweek.to_datetime(weekday)


@pytest.mark.parametrize(
    ("value", "context"),
    [
        (1, do_not_raise()),
        ((1, 2, 3), do_not_raise()),
        ([1, 2, 3], do_not_raise()),
        (timedelta(weeks=2), pytest.raises(TypeError, match="Cannot add type")),
        ((1, 2, timedelta(weeks=2)), pytest.raises(TypeError, match="Cannot add type")),
        (1.0, pytest.raises(TypeError, match="Cannot add type")),
        ("1", pytest.raises(TypeError, match="Cannot add type")),
        (("1", 2), pytest.raises(TypeError, match="Cannot add type")),
    ],
)
def test_addition(value: int | timedelta | str, context: AbstractContextManager) -> None:
    """Tests addition operator of IsoWeek class"""
    with context:
        isoweek + value  # type: ignore[operator]

    with context:
        isoweek.add(value)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("value", "context"),
    [
        (1, do_not_raise()),
        (-1, do_not_raise()),
        ((1, 2, isoweek - 3), do_not_raise()),
        ([1, 2, isoweek - 3], do_not_raise()),
        (timedelta(weeks=2), pytest.raises(TypeError, match="Cannot subtract type")),
        (IsoWeek("2023-W01"), do_not_raise()),
        (IsoWeek("2023-W02"), do_not_raise()),
        (IsoWeek("2022-W52"), do_not_raise()),
        ((1, timedelta(weeks=2), IsoWeek("2022-W52")), pytest.raises(TypeError, match="Cannot subtract type")),
        (customweek, pytest.raises(TypeError, match="Cannot subtract type")),
        ("1", pytest.raises(TypeError, match="Cannot subtract type")),
        (("1", 2), pytest.raises(TypeError, match="Cannot subtract type")),
    ],
)
def test_subtraction(value: int | timedelta | IsoWeek | str, context: AbstractContextManager) -> None:
    """Tests subtraction operator of IsoWeek class"""
    with context:
        isoweek - value  # type: ignore[operator]

    with context:
        isoweek.sub(value)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("value", "return_type"),
    [
        (1, IsoWeek),
        (IsoWeek("2023-W01"), int),
    ],
)
def test_subtraction_return_type(value: int | IsoWeek, return_type: type) -> None:
    """Tests subtraction operator of IsoWeek class"""
    assert isinstance(isoweek - value, return_type)


@pytest.mark.parametrize(
    ("value", "context"),
    [
        (customweek, do_not_raise()),
        ("2023-W01", do_not_raise()),
        (date(2023, 1, 1), do_not_raise()),
        (datetime(2023, 1, 1, tzinfo=timezone.utc), do_not_raise()),
        (1, pytest.raises(NotImplementedError, match="Cannot cast type")),
    ],
)
def test_automatic_cast(value: IsoWeek | str | date | datetime | int, context: AbstractContextManager) -> None:
    """Tests automatic casting of IsoWeek class"""
    with context:
        _ = IsoWeek._cast(value)  # type: ignore[type-var]


@pytest.mark.parametrize(
    ("n_weeks", "step", "context"),
    [
        (1, 1, do_not_raise()),
        (1, 2, do_not_raise()),
        (10, 1, do_not_raise()),
        (1.0, 1, pytest.raises(TypeError, match="`n_weeks` must be an integer")),
        (0, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
        (-2, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
    ],
)
def test_weeksout(n_weeks: float, step: int, context: AbstractContextManager) -> None:
    """Tests weeksout method of IsoWeek class"""
    with context:
        r = isoweek.weeksout(n_weeks, step=step)  # type: ignore[call-overload]
        assert isinstance(r, Generator)


@pytest.mark.parametrize(
    ("other", "expected", "context"),
    [
        (IsoWeek("2023-W01"), True, do_not_raise()),
        (IsoWeek("2023-W02"), False, do_not_raise()),
        ("2023-W01", True, do_not_raise()),
        ("2023-W02", False, do_not_raise()),
        (date(2023, 1, 4), True, do_not_raise()),
        (date(2023, 1, 1), False, do_not_raise()),
        (datetime(2023, 1, 4, tzinfo=timezone.utc), True, do_not_raise()),
        (datetime(2023, 1, 1, tzinfo=timezone.utc), False, do_not_raise()),
        ((), None, pytest.raises(TypeError, match="Cannot compare type")),
        (123, None, pytest.raises(TypeError, match="Cannot compare type")),
    ],
)
def test__contains__(
    other: IsoWeek | str | date | datetime | tuple | int, expected: bool | None, context: AbstractContextManager
) -> None:
    """Tests __contains__ method of IsoWeek class"""
    with context:
        r = other in isoweek
        assert r == expected


@pytest.mark.parametrize(
    ("other", "expected", "context"),
    [
        (isoweek.days, tuple(True for _ in isoweek.days), do_not_raise()),
        (isoweek.days[0], True, do_not_raise()),
        (isoweek.days[1] + timedelta(weeks=52), False, do_not_raise()),
        ((1, 2, 3), None, pytest.raises(TypeError, match="Cannot compare type")),
        (123, None, pytest.raises(TypeError, match="Cannot compare type")),
    ],
)
def test_contains_method(
    other: Sequence[date] | date | Sequence[int] | int, expected: Sequence[bool] | bool, context: AbstractContextManager
) -> None:
    """Tests contains method of IsoWeek class"""
    with context:
        r = isoweek.contains(other)

        if isinstance(other, (date, datetime, str, IsoWeek)):
            assert isinstance(r, bool)
            assert r == expected

        elif isinstance(other, Sequence):
            assert len(other) == len(r)  # type: ignore[arg-type]
            assert all(isinstance(v, bool) for v in r)  # type: ignore[union-attr]
            assert r == expected


@pytest.mark.parametrize(
    ("lower_bound", "upper_bound", "inclusive", "expected"),
    [
        (isoweek, isoweek + 1, "both", True),
        (isoweek, isoweek + 1, "right", False),
        (isoweek, isoweek + 1, "left", True),
        (isoweek, isoweek + 1, "neither", False),
    ],
)
def test_is_between(
    lower_bound: IsoWeek, upper_bound: IsoWeek, inclusive: Literal["both", "left", "right", "neither"], expected: bool
) -> None:
    """Tests is_between method of IsoWeek class"""
    assert isoweek.is_between(lower_bound, upper_bound, inclusive=inclusive) == expected


@pytest.mark.parametrize(
    ("year", "week", "expected"),
    [
        (2022, None, IsoWeek("2022-W01")),
        (None, 2, IsoWeek("2023-W02")),
        (2022, 52, IsoWeek("2022-W52")),
        (2024, 1, IsoWeek("2024-W01")),
    ],
)
def test_replace(year: int | None, week: int | None, expected: IsoWeek) -> None:
    """Tests replace method of IsoWeek class"""
    assert isoweek.replace(year=year, week=week) == expected
