from datetime import timedelta
from typing import TypeVar, Union

try:
    import polars as pl
except ImportError:  # pragma: no cover
    raise ImportError("polars is required for this module")

T = TypeVar("T", pl.Series, pl.Expr)


def datetime_to_isoweek(
    series: T, offset: Union[timedelta, int] = timedelta(days=0)
) -> T:
    """
    Convert date or datetime polars series or expr to IsoWeek series or expr

    Arguments:
        series: date or datetime series or expr
        offset: offset in days or timedelta. It represents how many days to add to the
            date before converting to IsoWeek, it can be negative

    Returns:
        IsoWeek series or expr

    Raises:
        TypeError: if series is not of type pl.Series or pl.Expr
        TypeError: if offset is not of type timedelta or int

    Usage:
    ```py
    import polars as pl
    from datetime import date, timedelta
    from iso_week.polars_utils import datetime_to_isoweek

    s = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
    datetime_to_isoweek(s, offset=timedelta(days=1))

    df = pl.DataFrame({"date": s})
    df.select(datetime_to_isoweek(pl.col("date"), offset=1))
    ```
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        raise TypeError(
            f"series must be of type pl.Series or pl.Expr, found {type(series)}"
        )

    if not isinstance(offset, (timedelta, int)):
        raise TypeError(f"offset must be of type timedelta or int, found {type(offset)}")

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.strftime("%G-W%V")


def isoweek_to_datetime(
    series: T,
    offset: Union[timedelta, int] = timedelta(days=0),
    weekday: int = 1,
) -> T:
    """
    Convert IsoWeek series or expr to date series or expr

    Arguments:
        series: IsoWeek series or expr
        offset: offset in days or timedelta. It represents how many days to add to the
            date before converting to IsoWeek, it can be negative
        weekday: weekday to use for conversion (1-7)

    Returns:
        date series

    Raises:
        TypeError: if series is not of type pl.Series or pl.Expr
        TypeError: if offset is not of type timedelta or int
        ValueError: if weekday is not an integer between 1 and 7
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        raise TypeError(
            f"series must be of type pl.Series or pl.Expr, found {type(series)}"
        )

    if not isinstance(offset, (timedelta, int)):
        raise TypeError(f"offset must be of type timedelta or int, found {type(offset)}")

    if weekday not in range(1, 8):
        raise ValueError(
            f"weekday value must be an integer between 1 and 7, found {weekday}"
        )

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return (series + f"-{weekday}").str.strptime(pl.Date, "%G-W%V-%u") + _offset
