from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Any

import pytest

pytest.importorskip("polars")

import polars as pl
from polars.exceptions import InvalidOperationError
from polars.testing import assert_series_equal
from typing_extensions import assert_type

from iso_week_date import IsoWeek, IsoWeekDate
from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEKDATE__DATE_FORMAT
from iso_week_date.polars_utils import (
    SeriesIsoWeek,
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
        # A null is missing data, not a malformed value, so it is skipped.
        (pl.Series(["2023-W01", None]), True),
        (pl.Series([None, None], dtype=pl.String), True),
        (pl.Series([], dtype=pl.String), True),
        # A null does not excuse a genuine non-match elsewhere in the series.
        (pl.Series(["nope", None]), False),
        (pl.Series([None, "2023-W00"]), False),
        (pl.Series(["2023-W01\n", "2023-W02"]), False),
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
        (pl.Series(["2023-W01-1", None]), True),
        (pl.Series([None, None], dtype=pl.String), True),
        (pl.Series(["nope", None]), False),
        (pl.Series(["2023-W01-1\n", "2023-W02-1"]), False),
    ],
)
def test_is_isoweekdate_series(series: pl.Series, expected: bool) -> None:
    """Test is_isoweek_series function"""
    assert is_isoweekdate_series(series) == expected


@pytest.mark.parametrize("_date", [date(1, 1, 1), date(9, 3, 2), date(999, 6, 1), date(1000, 1, 3)])
def test_datetime_to_isoweek_zero_pads_the_iso_year(_date: date) -> None:
    """polars must zero-pad the ISO year exactly as `IsoWeek.from_date` does.

    `%G` padding is platform dependent (see `BaseIsoWeek._format_isocalendar`), and polars formats
    through Rust chrono rather than the scalar path, so anchoring on the scalar class means any
    divergence shows up here rather than as a corrupt string in a user's dataframe.

    There is no pandas equivalent: `datetime64[ns]` cannot represent a year before 1677, and the
    non-nanosecond units that can need pandas >= 2.0, above this project's declared floor.
    """
    expected = IsoWeek.from_date(_date).value_
    result = datetime_to_isoweek(pl.Series([_date])).item()

    assert result == expected, f"polars produced {result!r}, scalar class gives {expected!r}"


def test_conversions_propagate_nulls() -> None:
    """Nulls flow through the conversions instead of raising or becoming a bogus value."""
    dt_series = pl.Series([date(2023, 1, 2), None, date(2023, 1, 9)])

    isoweek = datetime_to_isoweek(dt_series)
    assert isoweek.to_list() == ["2023-W01", None, "2023-W02"]

    isoweekdate = datetime_to_isoweekdate(dt_series)
    assert isoweekdate.to_list() == ["2023-W01-1", None, "2023-W02-1"]

    # strict=True must not treat a null as an unparsable value.
    assert isoweek_to_datetime(pl.Series(["2023-W01", None]), strict=True).to_list() == [date(2023, 1, 2), None]
    assert isoweekdate_to_datetime(pl.Series(["2023-W01-1", None]), strict=True).to_list() == [date(2023, 1, 2), None]


def test_null_round_trip_is_null_preserving() -> None:
    """date -> ISO Week str -> date keeps the null in place, with strict=True."""
    dt_series = pl.Series([date(2023, 1, 2), None])

    round_tripped = isoweekdate_to_datetime(datetime_to_isoweekdate(dt_series), strict=True)
    assert round_tripped.to_list() == [date(2023, 1, 2), None]


def test_conversions_propagate_nulls_in_expr_context() -> None:
    """The same holds for the Expr / namespace API used inside `select`."""
    df = pl.DataFrame({"date": pl.Series([date(2023, 1, 2), None])})

    result = df.select(
        isoweek=datetime_to_isoweek(pl.col("date")),
        isoweekdate=pl.col("date").iwd.datetime_to_isoweekdate(),  # type: ignore[attr-defined]
    )
    assert result["isoweek"].to_list() == ["2023-W01", None]
    assert result["isoweekdate"].to_list() == ["2023-W01-1", None]


def test_is_isoweek_series_raise() -> None:
    """Test is_isoweek_series function with invalid type"""
    series = pl.DataFrame({"isoweek": ["2023-W01", "2023-W02"]})
    with pytest.raises(TypeError):
        is_isoweek_series(series)  # type: ignore[call-overload]


@pytest.mark.parametrize("weekday", [1.0, True, False, "1", Decimal(1)])
def test_isoweek_to_datetime_rejects_non_int_weekday(weekday: Any) -> None:
    """A non-`int` `weekday` must fail as a `TypeError` before it reaches the parser.

    Left unguarded, each of these is concatenated into the value and surfaces as an
    `InvalidOperationError` about the data rather than about the argument. `bool` is the sharp edge:
    `isinstance(True, int)` holds and `True in range(1, 8)` holds, so `True` used to be interpolated
    as the literal string "True", producing `"2023-W01-True"`.
    """
    with pytest.raises(TypeError, match="`weekday` must be an integer between 1 and 7"):
        isoweek_to_datetime(pl.Series(["2023-W01", "2023-W02"]), weekday=weekday)


@pytest.mark.parametrize("check", [is_isoweek_series, is_isoweekdate_series])
@pytest.mark.parametrize(
    "series",
    [
        pl.Series(["2023-W01", "2023-W02"], dtype=pl.String),
        pl.Series(["2023-W01-1", "2023-W02-1"], dtype=pl.String),
        pl.Series(["nope", "2023-W02"], dtype=pl.String),
        pl.Series(["2023-W01", None], dtype=pl.String),
        pl.Series([None, None], dtype=pl.String),
        pl.Series([], dtype=pl.String),
        # The dtypes the cast exists for must answer the same way lazily.
        pl.Series(["2023-W01", "2023-W02"], dtype=pl.Categorical),
        pl.Series([None, None]),
        pl.Series([1, 2, 3]),
    ],
)
def test_is_isoweek_checks_accept_an_expr(check: Any, series: pl.Series) -> None:
    """An `Expr` in gives a boolean `Expr` out, computing exactly what the eager path computes."""
    expr = check(pl.col("a"))
    assert isinstance(expr, pl.Expr), "an Expr is not a bool: `if check(expr):` would raise"

    assert pl.DataFrame({"a": series}).select(result=expr)["result"].item() == check(series)


@pytest.mark.parametrize(
    ("series", "expected"),
    [
        # Dictionary-encoded strings are still strings: `str.contains` rejects the dtype and used to
        # be swallowed into `False`, a wrong answer for a valid column.
        (pl.Series(["2023-W01", "2023-W02"], dtype=pl.Categorical), True),
        (pl.Series(["2023-W01", None], dtype=pl.Categorical), True),
        (pl.Series(["nope"], dtype=pl.Categorical), False),
        (pl.Series(["2023-W01"], dtype=pl.Enum(["2023-W01"])), True),
        (pl.Series(["2023-W01", None], dtype=pl.Enum(["2023-W01"])), True),
        (pl.Series([], dtype=pl.Categorical), True),
        # `Null`, not `String`: an all-null column needs no explicit string dtype to be recognised
        # as containing nothing that violates the format.
        (pl.Series([None, None]), True),
        (pl.Series([]), True),
        # Not string-like: malformed data, so `False` rather than an error. Three different routes
        # get there: the cast succeeds but nothing matches, the cast raises `InvalidOperationError`
        # (nested types), or the cast raises `ComputeError` (`Object`).
        (pl.Series([1, 2, 3]), False),
        (pl.Series([1.5]), False),
        (pl.Series([True, False]), False),
        (pl.Series([date(2023, 1, 2)]), False),
        (pl.Series([{"a": 1}]), False),
        (pl.Series([["2023-W01"]]), False),
        (pl.Series([["2023-W01"]], dtype=pl.Array(pl.String, 1)), False),
        (pl.Series([object()], dtype=pl.Object), False),
        # `Binary` is the one dtype the cast decodes into a matching string, so bytes spelling an ISO
        # week read as `True` here while pandas answers `False`. Restricting the cast per dtype would
        # fix the asymmetry but is impossible for an `Expr`, whose dtype is unknown until collection,
        # and an eager/lazy split inside one backend is the worse trade.
        (pl.Series([b"2023-W01"]), True),
    ],
)
def test_is_isoweek_series_answers_on_content_not_dtype(series: pl.Series, expected: bool) -> None:
    """Both checks share `_match_series`, so dtype handling is exercised through one of them."""
    assert is_isoweek_series(series) is expected


def test_is_isoweek_series_nested_dtype_is_eager_only() -> None:
    """The `except` cannot fire for an `Expr`, so a nested column is `False` eagerly and raises lazily."""
    series = pl.Series([["2023-W01"]])

    assert is_isoweek_series(series) is False
    with pytest.raises(InvalidOperationError, match="cannot cast List type"):
        pl.DataFrame({"a": series}).select(check=is_isoweek_series(pl.col("a")))


def test_is_isoweek_checks_are_typed_per_input_kind() -> None:
    """`assert_type` is checked by mypy and pyright, both of which run over `tests/`."""
    series, expr = pl.Series(["2023-W01"]), pl.col("isoweek")

    assert_type(is_isoweek_series(series), bool)
    assert_type(is_isoweek_series(expr), pl.Expr)
    assert_type(is_isoweekdate_series(series), bool)
    assert_type(is_isoweekdate_series(expr), pl.Expr)

    # Through the class rather than the `.iwd` accessor: polars registers the namespace at runtime,
    # so the accessor is `Any` to a type checker and would assert nothing.
    assert_type(SeriesIsoWeek(series).is_isoweek(), bool)
    assert_type(SeriesIsoWeek(expr).is_isoweek(), pl.Expr)
    assert_type(SeriesIsoWeek(series).is_isoweekdate(), bool)
    assert_type(SeriesIsoWeek(expr).is_isoweekdate(), pl.Expr)


def test_is_isoweek_checks_via_expr_namespace() -> None:
    """The registered `iwd` namespace behaves the same on the `Expr` side."""
    df = pl.DataFrame({"isoweek": ["2023-W01", "2023-W02"], "other": ["nope", "2023-W02"]})

    result = df.select(
        good=pl.col("isoweek").iwd.is_isoweek(),  # type: ignore[attr-defined]
        bad=pl.col("other").iwd.is_isoweek(),  # type: ignore[attr-defined]
    )
    assert result["good"].item() is True
    assert result["bad"].item() is False
