from __future__ import annotations

import sys
from datetime import timedelta
from typing import TypeVar, Union

import narwhals.stable.v1 as nw

from iso_week_date._patterns import (
    ISOWEEK__DATE_FORMAT,
    ISOWEEK__FORMAT,
    ISOWEEK_PATTERN,
    ISOWEEKDATE__DATE_FORMAT,
    ISOWEEKDATE__FORMAT,
    ISOWEEKDATE_PATTERN,
)

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias


T = TypeVar("T", nw.Series, nw.Expr)
S = TypeVar("S")

OffsetType: TypeAlias = Union[int, timedelta]


def _datetime_to_format(
    series: T,
    offset: OffsetType,
    _format: str,
) -> T:
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

            - `series` is not of type `pl.Series` or `pl.Expr`
            - `offset` is not of type `timedelta` or `int`
    """
    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.to_string(_format)


@nw.narwhalify(series_only=True)
def datetime_to_isoweek(series: S, offset: OffsetType = timedelta(days=0)) -> S:
    """Converts `date(time)` `series/expr` to `str` values representing ISO Week format YYYY-WNN.

    Arguments:
        series: series or expr of `date` or `datetime` values
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to ISO
            Week, it can be negative

    Returns:
        Series or Expr with converted ISO Week values (in format YYYY-WNN)

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pl.Series` or `pl.Expr`
            - `offset` is not of type `timedelta` or `int`

    Examples:
    ```py
    from datetime import date, timedelta

    import polars as pl
    from iso_week_date.polars_utils import datetime_to_isoweek

    s = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
    datetime_to_isoweek(s, offset=timedelta(days=1))

    df = pl.DataFrame({"date": s})
    df.select(datetime_to_isoweek(pl.col("date"), offset=1))
    ```
    """
    return _datetime_to_format(series, offset, ISOWEEK__DATE_FORMAT)


@nw.narwhalify(series_only=True)
def datetime_to_isoweekdate(series: S, offset: OffsetType = timedelta(days=0)) -> S:
    """Converts `date(time)` `series/expr`  to `str` values representing ISO Week date format YYYY-WNN-D.

    Arguments:
        series: series or expr of `date` or `datetime` values
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to ISO
            Week, it can be negative

    Returns:
        Series or Expr with converted ISO Week values (in format YYYY-WNN-D)

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pl.Series` or `pl.Expr`
            - `offset` is not of type `timedelta` or `int`

    Examples:
    ```py
    from datetime import date, timedelta

    import polars as pl
    from iso_week_date.polars_utils import datetime_to_isoweekdate

    s = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
    datetime_to_isoweekdate(s, offset=timedelta(days=1))

    df = pl.DataFrame({"date": s})
    df.select(datetime_to_isoweekdate(pl.col("date"), offset=1))
    ```
    """
    return _datetime_to_format(series, offset, ISOWEEKDATE__DATE_FORMAT)


@nw.narwhalify(series_only=True)
def isoweek_to_datetime(
    series: T,
    offset: OffsetType = timedelta(days=0),
    weekday: int = 1,
) -> T:
    """Converts series or expr of `str` values in ISO Week format YYYY-WNN to a series or expr of `pl.Date` values.

    `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

    `weekday` represents the weekday to use for conversion in ISO Week format (1-7), where 1 is the first day of the
    week, 7 is the last one.

    Arguments:
        series: series or expr of `str` values in ISO Week format
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative
        weekday: weekday to use for conversion (1-7)

    Returns:
        Series or Expr of converted date values

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pl.Series` or `pl.Expr`
            - `offset` is not of type `timedelta` or `int`
        ValueError: If `weekday` is not an integer between 1 and 7

    Examples:
    ```py
    from datetime import timedelta

    import polars as pl
    from iso_week_date.polars_utils import isoweek_to_datetime

    s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
    isoweek_to_datetime(series=s, offset=timedelta(days=1))
    '''
    date
    2022-12-27
    2023-01-03
    2023-01-10
    '''
    ```
    """
    if not is_isoweek_series(series):
        msg = f"`series` values must match ISO Week format {ISOWEEK__FORMAT}"
        raise ValueError(msg)

    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    if weekday not in range(1, 8):
        msg = f"`weekday` value must be an integer between 1 and 7, found {weekday}"
        raise ValueError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return (series + f"-{weekday}").str.strptime(nw.Date, ISOWEEKDATE__DATE_FORMAT) + _offset


@nw.narwhalify(series_only=True)
def isoweekdate_to_datetime(
    series: T,
    offset: OffsetType = timedelta(days=0),
) -> T:
    """Converts `series/expr` of values in ISO Week date format YYYY-WNN-D to a series or expr of `pl.Date` values.

    `offset` represents how many days to add to the date before converting to `pl.Date`, and it can be negative.

    Arguments:
        series: series or expr of `str` values in ISO Week date format
        offset: offset in days or `timedelta`. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative

    Returns:
        Series or Expr of converted date values

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pl.Series` or `pl.Expr`
            - `offset` is not of type `timedelta` or `int`

    Examples:
    ```py
    from datetime import timedelta

    import polars as pl
    from iso_week_date.polars_utils import isoweekdate_to_datetime

    s = pl.Series(["2022-W52-7", "2023-W01-1", "2023-W02-1"])
    isoweekdate_to_datetime(series=s, offset=timedelta(days=1))
    '''
    date
    2022-01-02
    2023-01-03
    2023-01-10
    '''
    ```
    """
    if not is_isoweekdate_series(series):
        msg = f"`series` values must match ISO Week date format {ISOWEEKDATE__FORMAT}"
        raise ValueError(msg)

    if not isinstance(offset, (timedelta, int)):
        msg = f"`offset` must be of type `timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return series.str.strptime(nw.Date, ISOWEEKDATE__DATE_FORMAT) + _offset


def _match_series(series: T, pattern: str) -> bool:
    """Checks if a `Series` or `Expr` contains only values matching `pattern`.

    Arguments:
        series: Series or Expr of `str` values
        pattern: pattern to match

    Returns:
        `True` if all values match `pattern`, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`
    """
    if not isinstance(series, (nw.Series, nw.Expr)):
        msg = f"`series` must be of type `pl.Series` or `pl.Expr`, found {type(series)}"
        raise TypeError(msg)

    try:
        return series.str.extract(pattern).is_not_null().all()  # type: ignore[return-value]
    except Exception:  # noqa: BLE001
        return False


def is_isoweek_series(series: T) -> bool:
    """Checks if a series or expr contains only values in ISO Week format.

    Arguments:
        series: series or expr of `str` values to check against "YYYY-WNN" pattern

    Returns:
        `True` if all values match ISO Week format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`

    Examples:
    ```py
    import polars as pl
    from iso_week_date.polars_utils import is_isoweek_series

    s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
    is_isoweek_series(s) # True
    ```
    """
    return _match_series(series, ISOWEEK_PATTERN.pattern)


def is_isoweekdate_series(series: T) -> bool:
    """Checks if a series or expr contains only values in ISO Week date format.

    Arguments:
        series: series or expr of `str` values to check against "YYYY-WNN-D" pattern

    Returns:
        `True` if all values match ISO Week date format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pl.Series` or `pl.Expr`

    Examples:
    ```py
    import polars as pl
    from iso_week_date.polars_utils import is_isoweekdate_series

    s = pl.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
    is_isoweekdate_series(series=s)  # True
    ```
    """
    return _match_series(series, ISOWEEKDATE_PATTERN.pattern)
