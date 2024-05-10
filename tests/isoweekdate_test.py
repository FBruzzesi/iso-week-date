from contextlib import nullcontext as do_not_raise
from datetime import timedelta
from typing import Generator

import pytest

from iso_week_date import IsoWeekDate

isoweekdate = IsoWeekDate("2023-W01-1")


class CustomWeekDate(IsoWeekDate):
    """Custom IsoWeekDate class with offset of 1 day"""

    offset_ = timedelta(days=1)


customweekdate = CustomWeekDate("2023-W01-1")


@pytest.mark.parametrize("isoweek", ("2023-W01", "2023-W02", "2023-W52"))
@pytest.mark.parametrize("weekday", range(1, 8))
def test_property(isoweek, weekday):
    """Tests properties unique of IsoWeekDate class, namely day and isoweek"""
    iwd = IsoWeekDate(f"{isoweek}-{weekday}")
    assert iwd.day == weekday
    assert iwd.isoweek == isoweek


@pytest.mark.parametrize(
    "value, context",
    [
        (1, do_not_raise()),
        (timedelta(weeks=2), do_not_raise()),
        ((1, 2, timedelta(weeks=2)), do_not_raise()),
        (1.0, pytest.raises(TypeError, match="Cannot add type")),
        ("1", pytest.raises(TypeError, match="Cannot add type")),
        (("1", 2), pytest.raises(TypeError, match="Cannot add type")),
    ],
)
def test_addition(value, context):
    """Tests addition operator of IsoWeek class"""
    with context:
        isoweekdate + value


@pytest.mark.parametrize(
    "value, context",
    [
        (1, do_not_raise()),
        (-1, do_not_raise()),
        (timedelta(days=2), do_not_raise()),
        (IsoWeekDate("2023-W01-2"), do_not_raise()),
        (IsoWeekDate("2023-W02-1"), do_not_raise()),
        (IsoWeekDate("2022-W52-1"), do_not_raise()),
        ((1, timedelta(weeks=2), IsoWeekDate("2022-W52-1")), do_not_raise()),
        (customweekdate, pytest.raises(TypeError, match="Cannot subtract type")),
        ("1", pytest.raises(TypeError, match="Cannot subtract type")),
        (("1", 2), pytest.raises(TypeError, match="Cannot subtract type")),
    ],
)
def test_subtraction(
    value,
    context,
):
    """Tests subtraction operator of IsoWeek class"""
    with context:
        isoweekdate - value


def test_sub_isoweekdate():
    """Tests subtraction of IsoWeekDate with IsoWeekDate"""
    assert isoweekdate - IsoWeekDate("2023-W01-2") == -1
    assert customweekdate - CustomWeekDate("2023-W01-2") == -1

    assert IsoWeekDate("2023-W01-2") - isoweekdate == 1
    assert CustomWeekDate("2023-W01-2") - customweekdate == 1


@pytest.mark.parametrize(
    "n_days, step, context",
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
    n_days,
    step,
    context,
):
    """Tests daysout method of IsoWeekDate class"""
    with context:
        r = isoweekdate.daysout(n_days, step=step)
        assert isinstance(r, Generator)
