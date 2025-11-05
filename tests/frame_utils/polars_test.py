from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import pytest

pytest.importorskip("polars")

import polars as pl
from polars.exceptions import InvalidOperationError
from polars.testing import assert_series_equal

from iso_week_date import IsoWeek, IsoWeekDate
from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEKDATE__DATE_FORMAT
from iso_week_date.polars_utils import (
    SeriesIsoWeek,  # noqa: F401
    _datetime_to_format,
    datetime_to_isoweek,
    datetime_to_isoweekdate,
    is_isoweek_series,
    is_isoweekdate_series,
    isoweek_to_datetime,
    isoweekdate_to_datetime,
)

pytestmark = pytest.mark.polars

start = date(2023, 1, 1)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_datetime_to_isoweek(periods: int, offset: int) -> None:
    """Tests datetime_to_isoweek with different offsets"""
    dt_series = pl.date_range(start, start + timedelta(weeks=periods - 1), interval="1w", eager=True)

    to_isoweek_g = _datetime_to_format(dt_series, offset=offset, _format=ISOWEEK__DATE_FORMAT)  # from generic function
    to_isoweek_f = datetime_to_isoweek(dt_series, offset=offset)  # from function
    to_isoweek_m = dt_series.iwd.datetime_to_isoweek(offset=offset)  # type: ignore[attr-defined]

    assert_series_equal(to_isoweek_g, to_isoweek_f)
    assert_series_equal(to_isoweek_g, to_isoweek_m)

    assert all([is_isoweek_series(to_isoweek_g), is_isoweek_series(to_isoweek_f), is_isoweek_series(to_isoweek_m)])
    assert all([to_isoweek_g.iwd.is_isoweek(), to_isoweek_f.iwd.is_isoweek(), to_isoweek_m.iwd.is_isoweek()])  # type: ignore[attr-defined]

    to_isoweekdate_g = _datetime_to_format(
        dt_series,
        offset=offset,
        _format=ISOWEEKDATE__DATE_FORMAT,
    )  # from generic function
    to_isoweekdate_f = datetime_to_isoweekdate(dt_series, offset=offset)  # from function
    to_isoweekdate_m = dt_series.iwd.datetime_to_isoweekdate(offset=offset)  # type: ignore[attr-defined]

    assert_series_equal(to_isoweekdate_g, to_isoweekdate_f)
    assert_series_equal(to_isoweekdate_g, to_isoweekdate_m)

    assert all(
        [
            is_isoweekdate_series(to_isoweekdate_g),
            is_isoweekdate_series(to_isoweekdate_f),
            is_isoweekdate_series(to_isoweekdate_m),
        ],
    )
    assert all(
        [
            to_isoweekdate_g.iwd.is_isoweekdate(),  # type: ignore[attr-defined]
            to_isoweekdate_f.iwd.is_isoweekdate(),  # type: ignore[attr-defined]
            to_isoweekdate_m.iwd.is_isoweekdate(),
        ],
    )

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pl.Series(CustomWeek.from_date(start - timedelta(weeks=1)).weeksout(periods))
    assert_series_equal(to_isoweek_f, iso_series, check_names=False)


@pytest.mark.parametrize(
    ("kwargs", "err_msg"),
    [
        (
            {"series": pl.DataFrame()},
            "`series` must be of type `pl.Series` or `pl.Expr`",
        ),
        (
            {
                "series": pl.date_range(start, start + timedelta(weeks=5), interval="1w", eager=True),
                "offset": "abc",
            },
            "`offset` must be of type `timedelta` or `int`",
        ),
    ],
)
def test_datetime_to_isoweek_raise(kwargs: dict[str, Any], err_msg: str) -> None:
    """Test datetime_to_isoweek with invalid arguments"""
    with pytest.raises(TypeError, match=err_msg):
        datetime_to_isoweek(**kwargs)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_isoweek_to_datetime(periods: int, offset: int) -> None:
    """Tests isoweek_to_datetime with different offsets"""
    _start = start + timedelta(days=offset)
    _, _, weekday = _start.isocalendar()

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pl.Series(CustomWeek.from_date(_start - timedelta(weeks=1)).weeksout(periods))

    dt_series_f = isoweek_to_datetime(iso_series, offset=offset, weekday=weekday)
    dt_series_m = iso_series.iwd.isoweek_to_datetime(offset=offset, weekday=weekday)  # type: ignore[attr-defined]

    assert_series_equal(dt_series_f.iwd.datetime_to_isoweek(offset=offset), iso_series, check_names=False)  # type: ignore[attr-defined]
    assert_series_equal(dt_series_m.iwd.datetime_to_isoweek(offset=offset), iso_series, check_names=False)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_isoweekdate_to_datetime(periods: int, offset: int) -> None:
    """Tests isoweekdate_to_datetime with different offsets"""
    _start = start + timedelta(days=offset)

    class CustomWeekDate(IsoWeekDate):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pl.Series(CustomWeekDate.from_date(_start - timedelta(days=1)).daysout(periods))

    dt_series_f = isoweekdate_to_datetime(iso_series, offset=offset)
    dt_series_m = iso_series.iwd.isoweekdate_to_datetime(offset=offset)  # type: ignore[attr-defined]

    assert_series_equal(datetime_to_isoweekdate(dt_series_f, offset=offset), iso_series, check_names=False)
    assert_series_equal(dt_series_m.iwd.datetime_to_isoweekdate(offset=offset), iso_series, check_names=False)


@pytest.mark.parametrize(
    ("kwargs", "expected_exception", "err_msg"),
    [
        (
            {"series": pl.Series(["2023-W01", "2023-W02"]), "offset": "abc"},
            TypeError,
            "`offset` must be of type `timedelta` or `int`",
        ),
        (
            {"series": pl.Series(["2023-W01", "2023-W02"]), "weekday": 0},
            ValueError,
            "`weekday` value must be an integer between 1 and 7",
        ),
        (
            {"series": pl.Series(["2023-Wab", "2023-W02"]), "weekday": 1},
            InvalidOperationError,
            "conversion from `str` to `date` failed in column",
        ),
    ],
)
def test_isoweek_to_datetime_raise(kwargs: dict[str, Any], expected_exception: type[Exception], err_msg: str) -> None:
    """Test isoweek_to_datetime with invalid arguments"""
    with pytest.raises(expected_exception, match=err_msg):
        isoweek_to_datetime(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "expected_exception", "err_msg"),
    [
        (
            {"series": pl.Series(["2023-W01-a", "2023-W02-b"]), "offset": 1},
            InvalidOperationError,
            "conversion from `str` to `date` failed in column ''",
        ),
        (
            {"series": pl.Series(["2023-W01-1", "2023-W02-1"]), "offset": "abc"},
            TypeError,
            "`offset` must be of type `timedelta` or `int`",
        ),
    ],
)
def test_isoweekdate_to_datetime_raise(
    kwargs: dict[str, Any], expected_exception: type[Exception], err_msg: str
) -> None:
    """Test isoweekdate_to_datetime with invalid arguments"""
    with pytest.raises(expected_exception=expected_exception, match=err_msg):
        isoweekdate_to_datetime(**kwargs)


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        (pl.Series(["2023-W01", "2023-W02"]), True),
        (pl.Series(["abcd-Wxy", "2023-W02"]), False),
        (pl.Series(["0000-W01", "2023-W02"]), False),
        (pl.Series(["2023-W00", "2023-W02"]), False),
        (pl.Series([1, 2, 3]), False),
    ],
)
def test_is_isoweek_series(series: pl.Series, expected: bool) -> None:
    """Test is_isoweek_series function"""
    assert is_isoweek_series(series) == expected


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        (pl.Series(["2023-W01-1", "2023-W02-1"]), True),
        (pl.Series(["abcd-Wxy-1", "2023-W02-1"]), False),
        (pl.Series(["0000-W01-1", "2023-W02-1"]), False),
        (pl.Series(["2023-W00-1", "2023-W02-1"]), False),
        (pl.Series([1, 2, 3]), False),
    ],
)
def test_is_isoweekdate_series(series: pl.Series, expected: bool) -> None:
    """Test is_isoweek_series function"""
    assert is_isoweekdate_series(series) == expected


def test_is_isoweek_series_raise() -> None:
    """Test is_isoweek_series function with invalid type"""
    series = pl.DataFrame({"isoweek": ["2023-W01", "2023-W02"]})
    with pytest.raises(TypeError):
        is_isoweek_series(series)  # type: ignore[type-var]
