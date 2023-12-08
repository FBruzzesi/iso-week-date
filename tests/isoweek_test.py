from contextlib import nullcontext as do_not_raise
from datetime import date, datetime, timedelta
from typing import Generator, Iterable

import pytest

from iso_week_date import IsoWeek

isoweek = IsoWeek("2023-W01")


class CustomWeek(IsoWeek):
    """Custom IsoWeek class with offset of 1 day"""

    offset_ = timedelta(days=1)


customweek = CustomWeek("2023-W01")


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        ("2023-W01", do_not_raise(), ""),
        ("abcd-xyz", pytest.raises(ValueError), "Invalid isoweek date format"),
        ("0000-W01", pytest.raises(ValueError), "Invalid isoweek date format"),
        ("2023-W54", pytest.raises(ValueError), "Invalid isoweek date format"),
    ],
)
def test_init(value, context, err_msg):
    """Tests __init__ and _validate methods of IsoWeek class"""

    with context as exc_info:
        IsoWeek(value)
    if exc_info:
        assert err_msg in str(exc_info.value)


def test_properties():
    """Tests properties of IsoWeek class, namely year, week, quarter and days"""

    assert isoweek.year == 2023
    assert isoweek.week == 1
    assert isoweek.quarter == 1

    days = isoweek.days
    assert len(days) == 7
    assert all([isinstance(day, date) for day in days])


def test_quarters():
    """Tests quarter property of IsoWeek class"""

    assert all(1 <= w.quarter <= 4 for w in IsoWeek.range("2020-W01", "2025-W52", step=1, as_str=False))


@pytest.mark.parametrize(
    "n, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "`n` must be an integer"),
        (-1, pytest.raises(ValueError), "`n` must be between 1 and 7"),
        (8, pytest.raises(ValueError), "`n` must be between 1 and 7"),
    ],
)
def test_nth(n, context, err_msg):
    """Tests nth method of IsoWeek class"""
    with context as exc_info:
        isoweek.nth(n)

    if exc_info:
        assert err_msg in str(exc_info.value)


def test_str_repr():
    """Tests __repr__ and __str__ methods of IsoWeek class"""
    assert isoweek.__repr__() == f"IsoWeek({isoweek.value_}) with offset {isoweek.offset_}"
    assert str(isoweek) == isoweek.value_


@pytest.mark.parametrize(
    "weekday, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "`weekday` must be an integer"),
        (-1, pytest.raises(ValueError), "Weekday must be between 1 and 7"),
        (8, pytest.raises(ValueError), "Weekday must be between 1 and 7"),
    ],
)
def test_to_datetime_raise(weekday, context, err_msg):
    """Tests to_datetime method of IsoWeek class"""
    with context as exc_info:
        isoweek.to_datetime(weekday)

    if exc_info:
        assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (timedelta(weeks=2), do_not_raise(), ""),
        ((1, 2, timedelta(weeks=2)), do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "Cannot add type"),
        ("1", pytest.raises(TypeError), "Cannot add type"),
        (("1", 2), pytest.raises(TypeError), "Cannot add type"),
    ],
)
def test_addition(value, context, err_msg):
    """Tests addition operator of IsoWeek class"""
    with context as exc_info:
        isoweek + value

    if exc_info:
        assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (-1, do_not_raise(), ""),
        (timedelta(weeks=2), do_not_raise(), ""),
        (IsoWeek("2023-W01"), do_not_raise(), ""),
        (IsoWeek("2023-W02"), do_not_raise(), ""),
        (IsoWeek("2022-W52"), do_not_raise(), ""),
        ((1, timedelta(weeks=2), IsoWeek("2022-W52")), do_not_raise(), ""),
        (customweek, pytest.raises(TypeError), "Cannot subtract type"),
        ("1", pytest.raises(TypeError), "Cannot subtract type"),
        (("1", 2), pytest.raises(TypeError), "Cannot subtract type"),
    ],
)
def test_subtraction(value, context, err_msg):
    """Tests subtraction operator of IsoWeek class"""
    with context as exc_info:
        isoweek - value

    if exc_info:
        assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "value, return_type",
    [
        (1, IsoWeek),
        (IsoWeek("2023-W01"), int),
    ],
)
def test_subtraction_return_type(value, return_type):
    """Tests subtraction operator of IsoWeek class"""
    assert isinstance(isoweek - value, return_type)


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (customweek, do_not_raise(), ""),
        ("2023-W01", do_not_raise(), ""),
        (date(2023, 1, 1), do_not_raise(), ""),
        (datetime(2023, 1, 1), do_not_raise(), ""),
        (1, pytest.raises(NotImplementedError), "Cannot cast type"),
    ],
)
def test_automatic_cast(value, context, err_msg):
    """Tests automatic casting of IsoWeek class"""

    with context as exc_info:
        _ = IsoWeek._cast(value)

    if exc_info:
        assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "n_weeks, step, context, err_msg",
    [
        (1, 1, do_not_raise(), ""),
        (1, 2, do_not_raise(), ""),
        (10, 1, do_not_raise(), ""),
        (1.0, 1, pytest.raises(TypeError), "`n_weeks` must be an integer"),
        (0, 1, pytest.raises(ValueError), "`n_weeks` must be strictly positive"),
        (-2, 1, pytest.raises(ValueError), "`n_weeks` must be strictly positive"),
    ],
)
def test_weeksout(n_weeks, step, context, err_msg):
    """Tests weeksout method of IsoWeek class"""

    with context as exc_info:
        r = isoweek.weeksout(n_weeks, step)

    if exc_info:
        assert err_msg in str(exc_info.value)
    else:
        assert isinstance(r, Generator)


@pytest.mark.parametrize(
    "other, expected, context, err_msg",
    [
        (IsoWeek("2023-W01"), True, do_not_raise(), ""),
        (IsoWeek("2023-W02"), False, do_not_raise(), ""),
        ("2023-W01", True, do_not_raise(), ""),
        ("2023-W02", False, do_not_raise(), ""),
        (date(2023, 1, 4), True, do_not_raise(), ""),
        (date(2023, 1, 1), False, do_not_raise(), ""),
        (datetime(2023, 1, 4), True, do_not_raise(), ""),
        (datetime(2023, 1, 1), False, do_not_raise(), ""),
        (tuple(), None, pytest.raises(TypeError), "Cannot compare type"),
        (123, None, pytest.raises(TypeError), "Cannot compare type"),
    ],
)
def test__contains__(other, expected, context, err_msg):
    """Tests __contains__ method of IsoWeek class"""

    with context as exc_info:
        r = other in isoweek

    if exc_info:
        assert err_msg in str(exc_info.value)
    else:
        assert r == expected


@pytest.mark.parametrize(
    "other, expected, context, err_msg",
    [
        (isoweek.days, tuple(True for _ in isoweek.days), do_not_raise(), ""),
        (isoweek.days[0], True, do_not_raise(), ""),
        (isoweek.days[1] + timedelta(weeks=52), False, do_not_raise(), ""),
        ((1, 2, 3), None, pytest.raises(TypeError), "Cannot compare type"),
        (123, None, pytest.raises(TypeError), "Cannot compare type"),
    ],
)
def test_contains_method(other, expected, context, err_msg):
    """Tests contains method of IsoWeek class"""

    with context as exc_info:
        r = isoweek.contains(other)

        if isinstance(other, (date, datetime, str, IsoWeek)):
            assert isinstance(r, bool)
            assert r == expected

        elif isinstance(other, Iterable):
            len(other) == len(r)
            assert all(isinstance(v, bool) for v in r)
            assert r == expected

    if exc_info:
        assert err_msg in str(exc_info.value)
