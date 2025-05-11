from __future__ import annotations

from contextlib import AbstractContextManager
from contextlib import nullcontext as do_not_raise
from datetime import timedelta
from typing import Generator
from typing import Literal

import pytest

from iso_week_date import IsoWeekDate

isoweekdate = IsoWeekDate("2023-W01-1")


class CustomWeekDate(IsoWeekDate):
    """Custom IsoWeekDate class with offset of 1 day"""

    offset_ = timedelta(days=1)


customweekdate = CustomWeekDate("2023-W01-1")


@pytest.mark.parametrize("isoweek", ("2023-W01", "2023-W02", "2023-W52"))
@pytest.mark.parametrize("weekday", range(1, 8))
def test_property(isoweek: str, weekday: int) -> None:
    """Tests properties unique of IsoWeekDate class, namely day and isoweek"""
    iwd = IsoWeekDate(f"{isoweek}-{weekday}")
    assert iwd.day == weekday
    assert iwd.isoweek == isoweek


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
def test_addition(value: timedelta | float | str | tuple, context: AbstractContextManager) -> None:
    """Tests addition operator of IsoWeek class"""
    with context:
        isoweekdate + value  # type: ignore[operator]

    with context:
        isoweekdate.add(value)  # type: ignore[operator]


@pytest.mark.parametrize(
    ("value", "context"),
    [
        (1, do_not_raise()),
        (-1, do_not_raise()),
        ((1, 2, isoweekdate - 3), do_not_raise()),
        ([1, 2, isoweekdate - 3], do_not_raise()),
        (timedelta(days=2), pytest.raises(TypeError, match="Cannot subtract type")),
        (IsoWeekDate("2023-W01-2"), do_not_raise()),
        (IsoWeekDate("2023-W02-1"), do_not_raise()),
        (IsoWeekDate("2022-W52-1"), do_not_raise()),
        ((1, timedelta(weeks=2), IsoWeekDate("2022-W52-1")), pytest.raises(TypeError, match="Cannot subtract type")),
        (customweekdate, pytest.raises(TypeError, match="Cannot subtract type")),
        ("1", pytest.raises(TypeError, match="Cannot subtract type")),
        (("1", 2), pytest.raises(TypeError, match="Cannot subtract type")),
    ],
)
def test_subtraction(
    value: int | timedelta | IsoWeekDate | str | tuple,
    context: AbstractContextManager,
) -> None:
    """Tests subtraction operator of IsoWeek class"""
    with context:
        isoweekdate - value  # type: ignore[operator]

    with context:
        isoweekdate.sub(value)  # type: ignore[operator]


def test_sub_isoweekdate() -> None:
    """Tests subtraction of IsoWeekDate with IsoWeekDate"""
    assert isoweekdate - IsoWeekDate("2023-W01-2") == -1
    assert customweekdate - CustomWeekDate("2023-W01-2") == -1

    assert IsoWeekDate("2023-W01-2") - isoweekdate == 1
    assert CustomWeekDate("2023-W01-2") - customweekdate == 1


@pytest.mark.parametrize(
    ("n_days", "step", "context"),
    [
        (1, 1, do_not_raise()),
        (1, 2, do_not_raise()),
        (10, 1, do_not_raise()),
        (1.0, 1, pytest.raises(TypeError, match="`n_weeks` must be integer")),
        (0, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
        (-2, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
    ],
)
def test_daysout(
    n_days: int,
    step: int,
    context: AbstractContextManager,
) -> None:
    """Tests daysout method of IsoWeekDate class"""
    with context:
        r = isoweekdate.daysout(n_days, step=step)
        assert isinstance(r, Generator)


def test_hash() -> None:
    """Tests __hash__ method of IsoWeek class"""
    assert hash(isoweekdate) != hash(customweekdate)


def test_next() -> None:
    """Tests next method of IsoWeek class"""
    assert isoweekdate.next() == isoweekdate + 1 == IsoWeekDate("2023-W01-2")
    assert customweekdate.next() == customweekdate + 1 == CustomWeekDate("2023-W01-2")


def test_prev() -> None:
    """Tests prev method of IsoWeek class"""
    assert isoweekdate.previous() == isoweekdate - 1 == IsoWeekDate("2022-W52-7")
    assert customweekdate.previous() == customweekdate - 1 == CustomWeekDate("2022-W52-7")


@pytest.mark.parametrize(
    ("lower_bound", "upper_bound", "inclusive", "expected"),
    [
        (isoweekdate, isoweekdate + 1, "both", True),
        (isoweekdate, isoweekdate + 1, "right", False),
        (isoweekdate, isoweekdate + 1, "left", True),
        (isoweekdate, isoweekdate + 1, "neither", False),
    ],
)
def test_is_between(
    lower_bound: IsoWeekDate,
    upper_bound: IsoWeekDate,
    inclusive: Literal["both", "left", "right", "neither"],
    expected: bool,
) -> None:
    """Tests is_between method of IsoWeekDate class"""
    assert isoweekdate.is_between(lower_bound, upper_bound, inclusive=inclusive) == expected


@pytest.mark.parametrize(
    ("year", "week", "weekday", "expected"),
    [
        (2022, 1, 1, CustomWeekDate("2022-W01-1")),
        (2022, 1, 7, CustomWeekDate("2022-W01-7")),
        (2023, None, 2, CustomWeekDate("2023-W01-2")),
        (2023, 1, 7, CustomWeekDate("2023-W01-7")),
        (None, None, None, CustomWeekDate("2023-W01-1")),
        (None, None, 7, CustomWeekDate("2023-W01-7")),
    ],
)
def test_replace(year: int | None, week: int | None, weekday: int | None, expected: CustomWeekDate) -> None:
    """Tests replace method of IsoWeekDate class"""
    assert customweekdate.replace(year=year, week=week, weekday=weekday) == expected
