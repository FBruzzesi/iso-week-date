from __future__ import annotations

import re
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest

pytest.importorskip("pandas")

import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.testing import assert_series_equal

from iso_week_date import IsoWeek, IsoWeekDate
from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEKDATE__DATE_FORMAT
from iso_week_date.pandas_utils import (
    SeriesIsoWeek,  # noqa: F401
    _datetime_to_format,
    datetime_to_isoweek,
    datetime_to_isoweekdate,
    is_isoweek_series,
    is_isoweekdate_series,
    isoweek_to_datetime,
    isoweekdate_to_datetime,
)

pytestmark = pytest.mark.pandas

start = date(2023, 1, 1)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_datetime_to(periods: int, offset: int) -> None:
    """Tests datetime_to_isoweek with different offsets"""
    dt_series: pd.Series = pd.Series(pd.date_range(start, periods=periods, freq="W"))

    to_isoweek_g = _datetime_to_format(dt_series, offset=offset, _format=ISOWEEK__DATE_FORMAT)  # from generic function
    to_isoweek_f = datetime_to_isoweek(dt_series, offset=offset)  # from function
    to_isoweek_m = dt_series.iwd.datetime_to_isoweek(offset=offset)  # from method extension

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
    to_isoweekdate_m = dt_series.iwd.datetime_to_isoweekdate(offset=offset)  # from method extension

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

    iso_series = pd.Series(list(CustomWeek.from_date(start - timedelta(weeks=1)).weeksout(periods)))
    assert_series_equal(to_isoweek_f, iso_series)


@pytest.mark.parametrize(
    ("kwargs", "err_msg"),
    [
        (
            {"series": pd.DataFrame()},
            "`series` must be of type `pd.Series`",
        ),
        (
            {"series": pd.Series([1, 2, 3])},
            "`series` values must be of type `datetime`",
        ),
        (
            {"series": pd.Series(pd.date_range(start, periods=5)), "offset": "abc"},
            "`offset` must be of type `pd.Timedelta` or `int`",
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

    iso_series = pd.Series(list(CustomWeek.from_date(_start - timedelta(weeks=1)).weeksout(periods)))

    dt_series_f = isoweek_to_datetime(iso_series, offset=offset, weekday=weekday)
    dt_series_m = iso_series.iwd.isoweek_to_datetime(offset=offset, weekday=weekday)
    assert all([is_datetime(dt_series_f), is_datetime(dt_series_m)])

    assert_series_equal(dt_series_f.iwd.datetime_to_isoweek(offset=offset), iso_series)  # type: ignore[attr-defined]


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_isoweekdate_to_datetime(periods: int, offset: int) -> None:
    """Tests isoweekdate_to_datetime with different offsets"""
    _start = start + timedelta(days=offset)

    class CustomWeekDate(IsoWeekDate):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pd.Series(list(CustomWeekDate.from_date(_start - timedelta(days=1)).daysout(periods)))

    dt_series_f = isoweekdate_to_datetime(iso_series, offset=offset)
    dt_series_m = iso_series.iwd.isoweekdate_to_datetime(offset=offset)
    assert all([is_datetime(dt_series_f), is_datetime(dt_series_m)])

    assert_series_equal(datetime_to_isoweekdate(dt_series_f, offset=offset), iso_series)


@pytest.mark.parametrize(
    ("kwargs", "expected_exception", "err_msg"),
    [
        (
            {"series": pd.Series(["2023-W01", "2023-W02"]), "offset": "abc"},
            TypeError,
            re.escape("`offset` must be of type `pd.Timedelta` or `int`"),
        ),
        (
            {"series": pd.Series(["2023-W01", "2023-W02"]), "weekday": 0},
            ValueError,
            "`weekday` value must be an integer between 1 and 7",
        ),
        (
            {"series": pd.Series(["2023-Wab", "2023-W02"]), "weekday": 1},
            ValueError,
            'time data "2023-Wab-1" doesn\'t match format',
        ),
    ],
)
def test_isoweek_to_datetime_raise(kwargs: dict[str, Any], expected_exception: type[Exception], err_msg: str) -> None:
    """Test isoweek_to_datetime with invalid arguments"""
    with pytest.raises(expected_exception=expected_exception, match=err_msg):
        isoweek_to_datetime(**kwargs)


@pytest.mark.parametrize(
    ("kwargs", "expected_exception", "err_msg"),
    [
        (
            {"series": pd.Series(["2023-W01-1", "2023-W02-1"]), "offset": "abc"},
            TypeError,
            re.escape("`offset` must be of type `pd.Timedelta` or `int`"),
        ),
        (
            {"series": pd.Series(["2023-W01-a", "2023-W02-b"]), "offset": 1},
            ValueError,
            'time data "2023-W01-a" doesn\'t match format',
        ),
    ],
)
def test_isoweekdate_to_datetime_raise(
    kwargs: dict[str, Any], expected_exception: type[Exception], err_msg: str
) -> None:
    """Test isoweekdate_to_datetime with invalid arguments.

    This called `isoweek_to_datetime` until the `offset` guard here showed up as the only uncovered
    branch in the module, so the sibling function was being tested twice and this one not at all.
    """
    with pytest.raises(expected_exception=expected_exception, match=err_msg):
        isoweekdate_to_datetime(**kwargs)


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        (pd.Series(["2023-W01", "2023-W02"]), True),
        (pd.Series(["abcd-Wxy", "2023-W02"]), False),
        (pd.Series(["0000-W01", "2023-W02"]), False),
        (pd.Series(["2023-W00", "2023-W02"]), False),
        (pd.Series([1, 2, 3]), False),
        # A null is missing data, not a malformed value, so it is skipped. The answer must not
        # depend on the dtype used to hold it: under `str` dtype `str.fullmatch` collapses nulls to
        # False before we can see them, so they are located via the input's own null mask.
        (pd.Series(["2023-W01", None]), True),
        (pd.Series(["2023-W01", None], dtype="object"), True),
        (pd.Series(["2023-W01", None], dtype="string"), True),
        (pd.Series([None, None], dtype="object"), True),
        (pd.Series([], dtype="object"), True),
        # A null does not excuse a genuine non-match elsewhere in the series.
        (pd.Series(["nope", None]), False),
        (pd.Series([None, "2023-W00"]), False),
        # `str.match` anchors at the start only, and `$` matches before a trailing newline, so these
        # used to report True here while polars reported False.
        (pd.Series(["2023-W01\n", "2023-W02"]), False),
        (pd.Series(["2023-W01 extra", "2023-W02"]), False),
    ],
)
def test_is_isoweek_series(series: pd.Series, expected: bool) -> None:
    """Test is_isoweek_series function"""
    assert is_isoweek_series(series) == expected


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        (pd.Series(["2023-W01-1", "2023-W02-1"]), True),
        (pd.Series(["abcd-Wxy-1", "2023-W02-1"]), False),
        (pd.Series(["0000-W01-1", "2023-W02-1"]), False),
        (pd.Series(["2023-W00-1", "2023-W02-1"]), False),
        (pd.Series([1, 2, 3]), False),
        (pd.Series(["2023-W01-1", None]), True),
        (pd.Series(["2023-W01-1", None], dtype="object"), True),
        (pd.Series(["2023-W01-1", None], dtype="string"), True),
        (pd.Series([None, None], dtype="object"), True),
        (pd.Series(["nope", None]), False),
        (pd.Series(["2023-W01-1\n", "2023-W02-1"]), False),
    ],
)
def test_is_isoweekdate_series(series: pd.Series, expected: bool) -> None:
    """Test is_isoweek_series function"""
    assert is_isoweekdate_series(series) == expected


@pytest.mark.parametrize("dtype", ["object", "str", "string"])
def test_datetime_to_isoweek_propagates_nulls(dtype: str) -> None:
    """Nulls flow through the conversions instead of raising or becoming a bogus value."""
    dt_series = pd.Series([pd.Timestamp("2023-01-02"), pd.NaT, pd.Timestamp("2023-01-09")])

    isoweek = datetime_to_isoweek(dt_series)
    assert isoweek.isna().tolist() == [False, True, False]
    assert isoweek.dropna().tolist() == ["2023-W01", "2023-W02"]

    isoweekdate = datetime_to_isoweekdate(dt_series)
    assert isoweekdate.isna().tolist() == [False, True, False]
    assert isoweekdate.dropna().tolist() == ["2023-W01-1", "2023-W02-1"]

    # And a null survives the whole round trip, still as a null.
    assert isoweek_to_datetime(pd.Series(["2023-W01", None], dtype=dtype)).isna().tolist() == [False, True]
    assert isoweekdate_to_datetime(pd.Series(["2023-W01-1", None], dtype=dtype)).isna().tolist() == [False, True]


def test_null_round_trip_is_null_preserving() -> None:
    """date -> ISO Week str -> date keeps the null in place, with strict=True."""
    dt_series = pd.Series([pd.Timestamp("2023-01-02"), pd.NaT])

    round_tripped = isoweekdate_to_datetime(datetime_to_isoweekdate(dt_series), strict=True)
    assert round_tripped.isna().tolist() == [False, True]
    assert round_tripped.dropna().tolist() == [pd.Timestamp("2023-01-02")]


def test_is_isoweek_series_raise() -> None:
    """Test is_isoweek_series function with invalid type"""
    series = pd.DataFrame({"isoweek": ["2023-W01", "2023-W02"]})
    with pytest.raises(TypeError):
        is_isoweek_series(series)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        # A `category` column holds ordinary strings and is read on its content, as in polars.
        (pd.Series(["2023-W01"], dtype="category"), True),
        (pd.Series(["2023-W01", None], dtype="category"), True),
        (pd.Series(["nope"], dtype="category"), False),
        # A non-null value that is not a `str` is malformed data. `str.fullmatch` yields `NaN` for
        # those and `NaN` is truthy, so an unfilled `all()` used to call them correctly formatted.
        (pd.Series([["2023-W01"], ["2023-W02"]], dtype="object"), False),
        (pd.Series([{"a": 1}], dtype="object"), False),
        (pd.Series(["2023-W01", 1], dtype="object"), False),
        # The dangerous one: a real ISO Week string beside a value that is not a string at all.
        (pd.Series([["2023-W01"], "2023-W01"], dtype="object"), False),
        # `bytes` has a `.str` accessor that cannot match, raising `TypeError` rather than
        # `AttributeError`; the only `TypeError` these functions raise is for a non-`pd.Series`.
        (pd.Series([b"2023-W01"], dtype="object"), False),
        # No `.str` accessor at all.
        (pd.Series([1, 2, 3]), False),
        (pd.Series([1.5]), False),
        (pd.Series([True, False]), False),
    ],
)
def test_is_isoweek_series_answers_on_content_not_dtype(series: pd.Series, expected: bool) -> None:
    """Both checks share `_match_series`, so dtype handling is exercised through one of them."""
    assert is_isoweek_series(series) is expected


@pytest.mark.parametrize("weekday", [1.0, True, False, "1", Decimal(1)])
def test_isoweek_to_datetime_rejects_non_int_weekday(weekday: Any) -> None:
    """A non-`int` `weekday` must fail as a `TypeError` before it reaches the parser.

    Left unguarded, each of these is concatenated into the value and surfaces as an opaque pandas
    parse error about the data rather than about the argument. `bool` is the sharp edge:
    `isinstance(True, int)` holds and `True in range(1, 8)` holds, so `True` used to be interpolated
    as the literal string "True", producing `"2023-W01-True"`.
    """
    with pytest.raises(TypeError, match=re.escape("`weekday` must be an integer between 1 and 7")):
        isoweek_to_datetime(pd.Series(["2023-W01", "2023-W02"]), weekday=weekday)
