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


@pytest.mark.parametrize("isoweek", ("2023-W01", "2023-W02", "2023-W53"))
@pytest.mark.parametrize("weekday", range(1, 8))
def test_property(isoweek, weekday):
    """Tests properties unique of IsoWeekDate class, namely day and isoweek"""
    iwd = IsoWeekDate(f"{isoweek}-{weekday}")
    assert iwd.day == weekday
    assert iwd.isoweek == isoweek


@pytest.mark.parametrize(
    "other, expected, context",
    [
        (1, "2023-W01-2", do_not_raise()),
        (timedelta(weeks=2), "2023-W03-1", do_not_raise()),
        (1.0, None, pytest.raises(TypeError)),
    ],
)
def test_addition(other, expected, context):
    """Tests addition of IsoWeekDate with other types"""
    with context:
        assert isoweekdate + other == IsoWeekDate(expected)
        assert customweekdate + other == CustomWeekDate(expected)


@pytest.mark.parametrize(
    "other, expected, context",
    [
        (1, "2022-W52-7", do_not_raise()),
        (timedelta(weeks=2), "2022-W51-1", do_not_raise()),
        (1.0, None, pytest.raises(TypeError)),
    ],
)
def test_subtraction(other, expected, context):
    """Tests subtraction of IsoWeekDate with other types"""
    with context:
        assert isoweekdate - other == IsoWeekDate(expected)
        assert customweekdate - other == CustomWeekDate(expected)


def test_sub_isoweekdate():
    """Tests subtraction of IsoWeekDate with IsoWeekDate"""
    assert isoweekdate - IsoWeekDate("2023-W01-2") == -1
    assert customweekdate - CustomWeekDate("2023-W01-2") == -1

    assert IsoWeekDate("2023-W01-2") - isoweekdate == 1
    assert CustomWeekDate("2023-W01-2") - customweekdate == 1


@pytest.mark.parametrize(
    "n_days, step, context, err_msg",
    [
        (1, 1, do_not_raise(), ""),
        (1, 2, do_not_raise(), ""),
        (10, 1, do_not_raise(), ""),
        (1.0, 1, pytest.raises(TypeError), "`n_weeks` must be integer"),
        (0, 1, pytest.raises(ValueError), "`n_weeks` must be strictly positive"),
        (-2, 1, pytest.raises(ValueError), "`n_weeks` must be strictly positive"),
    ],
)
def test_daysout(n_days, step, context, err_msg):
    """Tests daysout method of IsoWeekDate class"""

    with context as exc_info:
        r = isoweekdate.daysout(n_days, step)

    if exc_info:
        assert err_msg in str(exc_info.value)
    else:
        assert isinstance(r, Generator)
