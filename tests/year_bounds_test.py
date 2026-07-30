"""Behaviour at the documented `0001`-`9999` ISO year bounds.

`IsoWeek` and `IsoWeekDate` are backed by `datetime.date`, so the first and last representable weeks
sit next to an edge that arithmetic can fall off. Stepping over it surfaces the standard library's own
error, which is a documented limitation rather than a bug: guarding every operation would cost every
caller something to protect a range essentially nobody reaches. These tests pin which error each path
produces, so the documentation cannot drift from the behaviour.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Any

import pytest

from iso_week_date import IsoWeek, IsoWeekDate

if TYPE_CHECKING:
    from collections.abc import Callable

FIRST_WEEK = "0001-W01"
LAST_WEEK = "9999-W52"
FIRST_WEEK_DATE = "0001-W01-1"
#: The last ISO week date that `datetime.date` can hold. `9999-W52-6` and `-7` are well-formed and
#: constructible, but fall in year 10000, so they cannot be converted at all.
LAST_WEEK_DATE = "9999-W52-5"
UNREPRESENTABLE_WEEK_DATE = "9999-W52-7"


@pytest.mark.parametrize(
    ("operation", "expected_exception"),
    [
        # `timedelta` arithmetic overflows...
        pytest.param(lambda: IsoWeek(LAST_WEEK).next(), OverflowError, id="isoweek-next"),
        pytest.param(lambda: IsoWeek(FIRST_WEEK).previous(), OverflowError, id="isoweek-previous"),
        pytest.param(lambda: IsoWeek(LAST_WEEK) + 1, OverflowError, id="isoweek-add"),
        pytest.param(lambda: IsoWeek(FIRST_WEEK) - 1, OverflowError, id="isoweek-sub"),
        pytest.param(lambda: tuple(IsoWeek(LAST_WEEK).add((1,))), OverflowError, id="isoweek-add-iterable"),
        pytest.param(lambda: tuple(IsoWeek(FIRST_WEEK).sub((1,))), OverflowError, id="isoweek-sub-iterable"),
        pytest.param(lambda: tuple(IsoWeek(LAST_WEEK).weeksout(2)), OverflowError, id="isoweek-weeksout"),
        pytest.param(lambda: IsoWeekDate(LAST_WEEK_DATE) + 1, OverflowError, id="isoweekdate-add"),
        pytest.param(lambda: IsoWeekDate(FIRST_WEEK_DATE) - 1, OverflowError, id="isoweekdate-sub"),
        pytest.param(lambda: tuple(IsoWeekDate(LAST_WEEK_DATE).daysout(2)), OverflowError, id="isoweekdate-daysout"),
        # ...while `strptime` rejects the year, so the two halves of the API disagree on the type.
        pytest.param(lambda: IsoWeek(LAST_WEEK).days, ValueError, id="isoweek-days"),
        pytest.param(lambda: IsoWeek(LAST_WEEK).nth(7), ValueError, id="isoweek-nth"),
        pytest.param(lambda: IsoWeek(LAST_WEEK).to_date(7), ValueError, id="isoweek-to-date"),
        pytest.param(lambda: IsoWeek(LAST_WEEK).to_datetime(7), ValueError, id="isoweek-to-datetime"),
        pytest.param(lambda: IsoWeekDate(LAST_WEEK_DATE).next(), OverflowError, id="isoweekdate-next"),
        pytest.param(lambda: IsoWeekDate(FIRST_WEEK_DATE).previous(), OverflowError, id="isoweekdate-previous"),
        # Constructible but not representable: the conversion fails before any arithmetic happens.
        pytest.param(lambda: IsoWeekDate(UNREPRESENTABLE_WEEK_DATE).to_date(), ValueError, id="isoweekdate-unrepr"),
        pytest.param(lambda: IsoWeekDate(UNREPRESENTABLE_WEEK_DATE) + 1, ValueError, id="isoweekdate-unrepr-add"),
    ],
)
def test_crossing_the_year_bounds_raises(
    operation: Callable[[], Any],
    expected_exception: type[Exception],
) -> None:
    """Which error each path produces is a documented limitation, so it is pinned rather than fixed.

    `except (OverflowError, ValueError)` is what the docs tell callers near the bounds to write, and
    that advice only holds while every path here raises one of the two.
    """
    with pytest.raises(expected_exception):
        operation()

    with pytest.raises((OverflowError, ValueError)):
        operation()


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (IsoWeek(FIRST_WEEK), date(1, 1, 1)),
        (IsoWeekDate(FIRST_WEEK_DATE), date(1, 1, 1)),
        (IsoWeek(LAST_WEEK), date(9999, 12, 27)),
        (IsoWeekDate(LAST_WEEK_DATE), date(9999, 12, 31)),
    ],
)
def test_the_bounds_themselves_are_representable(value: IsoWeek | IsoWeekDate, expected: date) -> None:
    """The extreme values that *do* fit still convert; only stepping past them fails."""
    assert value.to_date() == expected
    assert value.to_datetime() == datetime(expected.year, expected.month, expected.day)


@pytest.mark.parametrize(("weekday", "expected"), [(1, date(9999, 12, 27)), (5, date(9999, 12, 31))])
def test_the_last_week_resolves_the_weekdays_that_fit(weekday: int, expected: date) -> None:
    """`9999-W52` spills into year 10000 only from its sixth day on.

    `nth` reached these through `self.days`, which materialises the whole week, so every weekday
    raised even when the requested one was well inside range.
    """
    assert IsoWeek(LAST_WEEK).nth(weekday) == expected
    assert IsoWeek(LAST_WEEK).to_date(weekday) == expected


@pytest.mark.parametrize("value", [FIRST_WEEK, LAST_WEEK])
def test_in_range_operations_at_the_bounds_still_work(value: str) -> None:
    """Only the operations that actually cross the edge raise; the rest are unaffected."""
    week = IsoWeek(value)

    assert week.year in {1, 9999}
    assert week.week == int(value[-2:])
    assert week.to_compact() == value.replace("-", "")
    assert IsoWeek.from_compact(value.replace("-", "")) == week
