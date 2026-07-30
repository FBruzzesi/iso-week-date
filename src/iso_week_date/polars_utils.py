from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Generic, TypeVar, overload

from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEK_PATTERN, ISOWEEKDATE__DATE_FORMAT, ISOWEEKDATE_PATTERN
from iso_week_date._utils import LONG_YEAR_WEEKS, is_long_year, require_version

require_version("polars", minimum="0.18.0", extra="polars")

import polars as pl  # noqa: E402
from polars.exceptions import ComputeError, InvalidOperationError, SchemaError  # noqa: E402

if TYPE_CHECKING:
    from typing import TypeAlias

    from typing_extensions import Self

    OffsetType: TypeAlias = int | timedelta

ExprOrSeries = TypeVar("ExprOrSeries", pl.Series, pl.Expr)

__all__ = (
    "SeriesIsoWeek",
    "datetime_to_isoweek",
    "datetime_to_isoweekdate",
    "is_isoweek_series",
    "is_isoweekdate_series",
    "isoweek_to_datetime",
    "isoweekdate_to_datetime",
)


def _datetime_to_format(
    series: ExprOrSeries,
    offset: OffsetType,
    _format: str,
) -> ExprOrSeries:
    """Converts series or expr of `date` or `datetime` values to series or expr of `str` values in `_format` format.

    Arguments:
        series: series or expr of `date` or `datetime` values
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to ISO
            Week, it can be negative
        _format: format to use for conversion

    Returns:
        Series or Expr converted to given format

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pl.Series` or `pl.Expr`
            * `offset` is not of type `timedelta` or `int`
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        msg = f"`series` must be of type `pl.Series` or `pl.Expr`, found {type(series)}"
        raise TypeError(msg)

    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.strftime(_format)


def datetime_to_isoweek(series: ExprOrSeries, offset: OffsetType = timedelta(days=0)) -> ExprOrSeries:
    """Converts `date(time)` `series/expr` to `str` values representing ISO Week format YYYY-WNN.

    Arguments:
        series: series or expr of `date` or `datetime` values
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to ISO
            Week, it can be negative

    Returns:
        Series or Expr with converted ISO Week values (in format YYYY-WNN)

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pl.Series` or `pl.Expr`
            * `offset` is not of type `timedelta` or `int`

    Examples:
        >>> from datetime import date, timedelta
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import datetime_to_isoweek
        >>>
        >>> s = pl.date_range(date(2023, 1, 1), date(2023, 1, 5), interval="1d", eager=True)
        >>> datetime_to_isoweek(s, offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
        shape: (5,)
        Series: 'literal' [str]
        [
           "2022-W52"
           "2022-W52"
           "2023-W01"
           "2023-W01"
           "2023-W01"
        ]
        >>> df = pl.DataFrame({"date": s})
        >>> df.select(datetime_to_isoweek(pl.col("date"), offset=1))
        shape: (5, 1)
        ┌──────────┐
        │ date     │
        │ ---      │
        │ str      │
        ╞══════════╡
        │ 2022-W52 │
        │ 2022-W52 │
        │ 2023-W01 │
        │ 2023-W01 │
        │ 2023-W01 │
        └──────────┘
    """
    return _datetime_to_format(series, offset, ISOWEEK__DATE_FORMAT)


def datetime_to_isoweekdate(series: ExprOrSeries, offset: OffsetType = timedelta(days=0)) -> ExprOrSeries:
    """Converts `date(time)` `series/expr`  to `str` values representing ISO Week date format YYYY-WNN-D.

    Arguments:
        series: series or expr of `date` or `datetime` values
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to ISO
            Week, it can be negative

    Returns:
        Series or Expr with converted ISO Week values (in format YYYY-WNN-D)

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pl.Series` or `pl.Expr`
            * `offset` is not of type `timedelta` or `int`

    Examples:
        >>> from datetime import date, timedelta
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import datetime_to_isoweekdate
        >>>
        >>> s = pl.date_range(date(2023, 1, 1), date(2023, 1, 5), interval="1d", eager=True)
        >>> datetime_to_isoweekdate(s, offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
        shape: (5,)
        Series: 'literal' [str]
        [
           "2022-W52-6"
           "2022-W52-7"
           "2023-W01-1"
           "2023-W01-2"
           "2023-W01-3"
        ]
        >>> df = pl.DataFrame({"date": s})
        >>> df.select(datetime_to_isoweekdate(pl.col("date"), offset=1))
        shape: (5, 1)
        ┌────────────┐
        │ date       │
        │ ---        │
        │ str        │
        ╞════════════╡
        │ 2022-W52-6 │
        │ 2022-W52-7 │
        │ 2023-W01-1 │
        │ 2023-W01-2 │
        │ 2023-W01-3 │
        └────────────┘
    """
    return _datetime_to_format(series, offset, ISOWEEKDATE__DATE_FORMAT)


def isoweek_to_datetime(
    series: ExprOrSeries,
    offset: OffsetType = timedelta(days=0),
    weekday: int = 1,
    *,
    strict: bool = True,
) -> ExprOrSeries:
    """Converts series or expr of `str` values in ISO Week format YYYY-WNN to a series or expr of `pl.Date` values.

    `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

    `weekday` represents the weekday to use for conversion in ISO Week format (1-7), where 1 is the first day of the
    week, 7 is the last one.

    Arguments:
        series: Series or Expr of `str` values in ISO Week format.
        offset: Offset in days or `timedelta`. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative.
        weekday: Weekday to use for conversion (1-7)
        strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

    Returns:
        Series or Expr of converted date values

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pl.Series` or `pl.Expr`
            * `offset` is not of type `timedelta` or `int`
            * `weekday` is not of type `int` (`bool` is not accepted)
        ValueError: If `weekday` is not an integer between 1 and 7

    Examples:
        >>> from datetime import timedelta
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import isoweek_to_datetime
        >>>
        >>> s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
        >>> isoweek_to_datetime(series=s, offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
        shape: (3,)
        Series: '' [date]
        [
            2022-12-27
            2023-01-03
            2023-01-10
        ]
    """
    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    # `bool` is excluded explicitly: `isinstance(True, int)` and `True in range(1, 8)` both hold, so
    # a bare range check would interpolate the literal string "True" into the value being parsed.
    if not isinstance(weekday, int) or isinstance(weekday, bool):
        msg = f"`weekday` must be an integer between 1 and 7, found {type(weekday)}"
        raise TypeError(msg)

    if weekday not in range(1, 8):
        msg = f"`weekday` value must be an integer between 1 and 7, found {weekday}"
        raise ValueError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return (series + f"-{weekday}").str.strptime(pl.Date, ISOWEEKDATE__DATE_FORMAT, strict=strict) + _offset


def isoweekdate_to_datetime(
    series: ExprOrSeries,
    offset: OffsetType = timedelta(days=0),
    *,
    strict: bool = True,
) -> ExprOrSeries:
    """Converts `series/expr` of values in ISO Week date format YYYY-WNN-D to a series or expr of `pl.Date` values.

    `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

    Arguments:
        series: Series or Expr of `str` values in ISO Week date format
        offset: Offset in days or `timedelta`. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative
        strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

    Returns:
        Series or Expr of converted date values

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pl.Series` or `pl.Expr`
            * `offset` is not of type `timedelta` or `int`

    Examples:
        >>> from datetime import timedelta
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import isoweekdate_to_datetime
        >>>
        >>> s = pl.Series(["2022-W52-7", "2023-W01-1", "2023-W02-1"])
        >>> isoweekdate_to_datetime(series=s, offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
        shape: (3,)
        Series: '' [date]
        [
            2023-01-02
            2023-01-03
            2023-01-10
        ]
    """
    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return series.str.strptime(pl.Date, ISOWEEKDATE__DATE_FORMAT, strict=strict) + _offset


@overload
def _match_series(series: pl.Series, pattern: str) -> bool: ...


@overload
def _match_series(series: pl.Expr, pattern: str) -> pl.Expr: ...


def _match_series(series: pl.Series | pl.Expr, pattern: str) -> bool | pl.Expr:
    """Checks if a `Series` or `Expr` contains only values matching `pattern`.

    A `pl.Series` is evaluated eagerly and gives back a `bool`. A `pl.Expr` cannot be: it describes a
    computation with no data attached yet, so it gives back a boolean `Expr` to be evaluated by
    whatever `select` / `filter` / `with_columns` it is handed to.

    Null values are skipped rather than counted as non-matching, so a series of
    `["2024-W01", None]` returns `True`. A null is missing data, not a malformed ISO Week string,
    and this is the convention the rest of the module follows: the conversion functions propagate
    nulls through instead of raising on them. `pandas_utils._match_series` behaves identically.

    `fill_null(True)` states that intent rather than leaning on `all()` ignoring nulls by default,
    so the behaviour cannot silently flip if that default ever changes.

    The cast to `String` is what lets `Categorical` and `Enum` columns be checked: they hold genuine
    ISO Week strings, but `str.contains` refuses to look at them and raises. It also settles the
    `Null` dtype, where an all-null series is missing data rather than malformed data. For any dtype
    that is not string-like the cast either fails or yields values that cannot match, so the answer
    stays `False` either way.

    Matching the format is necessary but not sufficient: weeks `01` to `53` are all well-formed, yet
    only long ISO years have a week 53. The week number is therefore checked against its year through
    the very same `is_long_year` helper `IsoWeek._validate` uses, so this answers the same question as
    `IsoWeek(value)` and stays a usable precondition for `isoweek_to_datetime`, which rejects
    `"2023-W53"` outright.

    The whole answer is built as one expression, because the `Expr` path has no data to inspect and
    cannot branch. A malformed value makes the week comparison null, and polars' Kleene logic keeps
    `False & null` at `False`, so the format verdict still wins. A null *input* leaves both operands
    null, which `fill_null` then excuses.

    Arguments:
        series: Series or Expr of `str` values
        pattern: pattern to match. It is already anchored by `iso_week_date._patterns`.

    Returns:
        For a `pl.Series`, `True` if all non-null values match `pattern` and name a week that exists
            in their year, `False` otherwise; an empty or all-null series returns `True`, since it
            contains nothing that violates the format. For a `pl.Expr`, a boolean `Expr` computing
            the same answer.

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        msg = f"`series` must be of type `pl.Series` or `pl.Expr`, found {type(series)}"
        raise TypeError(msg)

    try:
        values = series.cast(pl.String())
        # Every well-formed value has the same fixed-width layout, so year and week are readable by
        # position. A malformed value yields null here instead of failing the cast.
        year = values.str.slice(0, 4).cast(pl.Int32, strict=False)
        week = values.str.slice(6, 2).cast(pl.Int32, strict=False)
        # Weeks 01 to 52 exist in every year, so only a week 53 has anything left to prove.
        # `is_long_year` is the same helper `IsoWeek._validate` uses, applied to a column.
        in_calendar = (week != LONG_YEAR_WEEKS) | is_long_year(year)
        matches = values.str.contains(pattern) & in_calendar
        return matches.fill_null(value=True).all()
    except (InvalidOperationError, SchemaError, ComputeError):
        # A dtype that is neither string-like nor castable to one (nested types, for instance) holds
        # nothing in ISO Week format, so it is a plain `False` rather than an error. Narrowed to the
        # dtype and compute failures on purpose: a bare `except` here would report a genuine bug in
        # this function as "not ISO Week format". Only the eager path can reach this at all; for an
        # `Expr` nothing is evaluated yet, so the equivalent failure surfaces from the frame.
        return False


@overload
def is_isoweek_series(series: pl.Series) -> bool: ...


@overload
def is_isoweek_series(series: pl.Expr) -> pl.Expr: ...


def is_isoweek_series(series: pl.Series | pl.Expr) -> bool | pl.Expr:
    """Checks if a series or expr contains only values in ISO Week format.

    Arguments:
        series: series or expr of `str` values to check against "YYYY-WNN" pattern

    Returns:
        For a `pl.Series`, `True` if all values match ISO Week format and `False` otherwise. For a
            `pl.Expr`, a boolean `Expr` computing the same answer, to be used inside `select` /
            `filter`. An `Expr` is not a `bool`, so `if is_isoweek_series(expr):` raises on its
            ambiguous truth value.

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`

    Examples:
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import is_isoweek_series
        >>>
        >>> s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
        >>> is_isoweek_series(s)
        True

        The `Expr` form answers inside a frame:

        >>> df = pl.DataFrame({"isoweek": ["2022-W52", "2023-W01"]})
        >>> df.select(is_isoweek=is_isoweek_series(pl.col("isoweek")))["is_isoweek"].item()
        True
    """
    return _match_series(series, ISOWEEK_PATTERN.pattern)


@overload
def is_isoweekdate_series(series: pl.Series) -> bool: ...


@overload
def is_isoweekdate_series(series: pl.Expr) -> pl.Expr: ...


def is_isoweekdate_series(series: pl.Series | pl.Expr) -> bool | pl.Expr:
    """Checks if a series or expr contains only values in ISO Week date format.

    Arguments:
        series: series or expr of `str` values to check against "YYYY-WNN-D" pattern

    Returns:
        For a `pl.Series`, `True` if all values match ISO Week date format and `False` otherwise. For
            a `pl.Expr`, a boolean `Expr` computing the same answer, to be used inside `select` /
            `filter`. An `Expr` is not a `bool`, so `if is_isoweekdate_series(expr):` raises on its
            ambiguous truth value.

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`

    Examples:
        >>> import polars as pl
        >>> from iso_week_date.polars_utils import is_isoweekdate_series
        >>>
        >>> s = pl.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
        >>> is_isoweekdate_series(series=s)
        True

        The `Expr` form answers inside a frame:

        >>> df = pl.DataFrame({"isoweekdate": ["2022-W52-1", "2023-W01-1"]})
        >>> df.select(check=is_isoweekdate_series(pl.col("isoweekdate")))["check"].item()
        True
    """
    return _match_series(series, ISOWEEKDATE_PATTERN.pattern)


@pl.api.register_series_namespace("iwd")
@pl.api.register_expr_namespace("iwd")
class SeriesIsoWeek(Generic[ExprOrSeries]):
    """Polars Series and Expr extension that provides methods for working with ISO weeks and dates.

    Instead of importing and working with single functions from the `polars_utils` module, it is possible to import the
    Series and Expr [extension class](https://pola-rs.github.io/polars/py-polars/html/reference/api.html) to be able to
    use the functions as methods on Series and Expr objects.

    To accomplish this, it is enough to load `SeriesIsoWeek` into scope:

    ```python hl_lines="3 6 9"
    from datetime import date, timedelta
    import polars as pl
    from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401

    s = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
    s.iwd.datetime_to_isoweek(offset=timedelta(days=1))

    df = pl.DataFrame({"date": s})
    df.select(pl.col("date").iwd.datetime_to_isoweek(offset=1))
    ```

    Arguments:
        series: ExprOrSerieshe pandas Series object the extension is attached to.

    Attributes:
        _series: ExprOrSerieshe pandas Series object the extension is attached to.
    """

    def __init__(self: Self, series: ExprOrSeries) -> None:
        self._series: ExprOrSeries = series

    def datetime_to_isoweek(self: Self, offset: OffsetType = timedelta(0)) -> ExprOrSeries:
        """Converts `date(time)` `series/expr` to `str` values representing ISO Week format YYYY-WNN.

        Arguments:
            offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to
                ISO Week, it can be negative

        Returns:
            Series or Expr with converted ISO Week values (in format YYYY-WNN)

        Raises:
            TypeError: If `offset` is not of type `timedelta` or `int`

        Examples:
            >>> from datetime import date, timedelta
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.date_range(date(2023, 1, 1), date(2023, 1, 5), interval="1d", eager=True)
            >>> s.iwd.datetime_to_isoweek(offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
            shape: (5,)
            Series: 'literal' [str]
            [
                "2022-W52"
                "2022-W52"
                "2023-W01"
                "2023-W01"
                "2023-W01"
            ]
            >>> df = pl.DataFrame({"date": s})
            >>> df.select(pl.col("date").iwd.datetime_to_isoweek(offset=1))
            shape: (5, 1)
            ┌──────────┐
            │ date     │
            │ ---      │
            │ str      │
            ╞══════════╡
            │ 2022-W52 │
            │ 2022-W52 │
            │ 2023-W01 │
            │ 2023-W01 │
            │ 2023-W01 │
            └──────────┘
        """
        return datetime_to_isoweek(self._series, offset=offset)

    def datetime_to_isoweekdate(self: Self, offset: OffsetType = timedelta(0)) -> ExprOrSeries:
        """Converts `date(time)` `series/expr` to `str` values representing ISO Week date format YYYY-WNN-D.

        Arguments:
            offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to
                ISO Week, it can be negative

        Returns:
            Series or Expr with converted ISO Week values (in format YYYY-WNN-D)

        Raises:
            TypeError: If `offset` is not of type `timedelta` or `int`

        Examples:
            >>> from datetime import date, timedelta
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.date_range(date(2023, 1, 1), date(2023, 1, 5), interval="1d", eager=True)
            >>> s.iwd.datetime_to_isoweekdate(offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
            shape: (5,)
            Series: 'literal' [str]
            [
                "2022-W52-6"
                "2022-W52-7"
                "2023-W01-1"
                "2023-W01-2"
                "2023-W01-3"
            ]
            >>> df = pl.DataFrame({"date": s})
            >>> df.select(pl.col("date").iwd.datetime_to_isoweekdate(offset=1))
            shape: (5, 1)
            ┌────────────┐
            │ date       │
            │ ---        │
            │ str        │
            ╞════════════╡
            │ 2022-W52-6 │
            │ 2022-W52-7 │
            │ 2023-W01-1 │
            │ 2023-W01-2 │
            │ 2023-W01-3 │
            └────────────┘
        """
        return datetime_to_isoweekdate(self._series, offset=offset)

    def isoweek_to_datetime(
        self: Self,
        offset: OffsetType = timedelta(0),
        weekday: int = 1,
        *,
        strict: bool = True,
    ) -> ExprOrSeries:
        """Converts series or expr of `str` values in ISO Week format YYYY-WNN to a series or expr of `pl.Date` values.

        `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

        `weekday` represents the weekday to use for conversion in ISO Week format (1-7), where 1 is the first day of the
        week, 7 is the last one.

        Arguments:
            offset: Offset in days or `timedelta`. It represents how many days to add to the date before converting to
                IsoWeek, it can be negative.
            weekday: Weekday to use for conversion (1-7).
            strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

        Returns:
            Series or Expr of converted date values

        Raises:
            TypeError: If `offset` is not of type `timedelta` or `int`
            ValueError: If `weekday` is not an integer between 1 and 7

        Examples:
            >>> from datetime import timedelta
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
            >>> s.iwd.isoweek_to_datetime(offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
            shape: (3,)
            Series: '' [date]
            [
                2022-12-27
                2023-01-03
                2023-01-10
            ]
        """
        return isoweek_to_datetime(self._series, offset=offset, weekday=weekday, strict=strict)

    def isoweekdate_to_datetime(self: Self, offset: OffsetType = timedelta(0), *, strict: bool = True) -> ExprOrSeries:
        """Converts `str` series or expr of ISO Week date format YYYY-WNN-D to a series or expr of `pl.Date` values.

        `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

        Arguments:
            offset: Offset in days or `timedelta`. It represents how many days to add to the date before converting to
                IsoWeek, it can be negative.
            strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

        Returns:
            Series or Expr of converted date values

        Raises:
            TypeError: If `offset` is not of type `timedelta` or `int`

        Examples:
            >>> from datetime import timedelta
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.Series(["2022-W52-7", "2023-W01-1", "2023-W02-1"])
            >>> s.iwd.isoweekdate_to_datetime(offset=timedelta(days=1))  # doctest: +NORMALIZE_WHITESPACE
            shape: (3,)
            Series: '' [date]
            [
                2023-01-02
                2023-01-03
                2023-01-10
            ]
        """
        return isoweekdate_to_datetime(self._series, offset=offset, strict=strict)

    @overload
    def is_isoweek(self: SeriesIsoWeek[pl.Series]) -> bool: ...

    @overload
    def is_isoweek(self: SeriesIsoWeek[pl.Expr]) -> pl.Expr: ...

    def is_isoweek(self: Self) -> bool | pl.Expr:
        """Checks if a series or expr contains only values in ISO Week format.

        Returns:
            For a `pl.Series`, `True` if all values match ISO Week format and `False` otherwise. For
                a `pl.Expr`, a boolean `Expr` computing the same answer, to be used inside `select` /
                `filter`.

        Examples:
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
            >>> s.iwd.is_isoweek()
            True

            >>> df = pl.DataFrame({"isoweek": ["2022-W52", "2023-W01"]})
            >>> df.select(check=pl.col("isoweek").iwd.is_isoweek())["check"].item()
            True
        """
        return is_isoweek_series(self._series)

    @overload
    def is_isoweekdate(self: SeriesIsoWeek[pl.Series]) -> bool: ...

    @overload
    def is_isoweekdate(self: SeriesIsoWeek[pl.Expr]) -> pl.Expr: ...

    def is_isoweekdate(self: Self) -> bool | pl.Expr:
        """Checks if a series or expr contains only values in ISO Week date format.

        Returns:
            For a `pl.Series`, `True` if all values match ISO Week date format and `False` otherwise.
                For a `pl.Expr`, a boolean `Expr` computing the same answer, to be used inside
                `select` / `filter`.

        Examples:
            >>> import polars as pl
            >>> from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pl.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
            >>> s.iwd.is_isoweekdate()
            True

            >>> df = pl.DataFrame({"isoweekdate": ["2022-W52-1", "2023-W01-1"]})
            >>> df.select(check=pl.col("isoweekdate").iwd.is_isoweekdate())["check"].item()
            True
        """
        return is_isoweekdate_series(self._series)
