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
    Converts polars `series` (or `expr`) with `date` (or `datetime`) values to `str`
    values representing ISO Week date format YYYY-WNN.

    Arguments:
        series: `date` or `datetime` polars `series` or `expr`
        offset: offset in days or `timedelta`. It represents how many days to add to the
            date before converting to ISO Week, it can be negative

    Returns:
        ISO Week polars series or expr

    Raises:
        TypeError: if series is not of type pl.Series or pl.Expr
        TypeError: if offset is not of type timedelta or int

    Usage:
    ```py
    import polars as pl
    from datetime import date, timedelta
    from iso_week_date.polars_utils import datetime_to_isoweek

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
    Converts polars `series` or `expr` of `str` in ISO Week date format to a `series` or
    `expr` of `pl.Date` type.

    `offset` represents how many days to add to the date before converting to `pl.Date`,
        and it can be negative.

    `weekday` represents the weekday to use for conversion in ISO Week format (1-7),
        where 1 is the first day of the week, 7 is the last one.

    Arguments:
        series: series or expr of `str` in ISO Week date format
        offset: offset in days or `timedelta`. It represents how many days to add to the
            date before converting to IsoWeek, it can be negative
        weekday: weekday to use for conversion (1-7)

    Returns:
        date series or expr

    Raises:
        TypeError: if series is not of type pl.Series or pl.Expr
        TypeError: if offset is not of type timedelta or int
        ValueError: if weekday is not an integer between 1 and 7

    Usage:
    ```py
    import polars as pl
    from datetime import timedelta
    from iso_week_date.polars_utils import isoweek_to_datetime

    s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
    isoweek_to_datetime(
        series=s,
        offset=timedelta(days=1)
        )
    '''
    date
    2022-12-27
    2023-01-03
    2023-01-10
    '''
    ```
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        raise TypeError(
            f"series must be of type pl.Series or pl.Expr, found {type(series)}"
        )

    if not is_isoweek_series(series):
        raise ValueError("series values must match ISO Week date format YYYY-WNN")

    if not isinstance(offset, (timedelta, int)):
        raise TypeError(f"offset must be of type timedelta or int, found {type(offset)}")

    if weekday not in range(1, 8):
        raise ValueError(
            f"weekday value must be an integer between 1 and 7, found {weekday}"
        )

    _offset = timedelta(days=offset) if isinstance(offset, int) else offset

    return (series + f"-{weekday}").str.strptime(pl.Date, "%G-W%V-%u") + _offset


def is_isoweek_series(series: T) -> bool:
    """
    Checks if a polars `series` of `str` represents a valid ISO Week date format.

    Arguments:
        series: series of `str` in ISO Week date format

    Returns:
        bool

    Usage:
    ```py
    import polars as pl
    from iso_week_date.polars_utils import is_isoweek_series

    s = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
    is_isoweek_series(s)
    '''
    True
    '''
    ```
    """
    if not isinstance(series, (pl.Series, pl.Expr)):
        raise TypeError(
            f"series must be of type pl.Series or pl.Expr, found {type(series)}"
        )

    return (
        pl.DataFrame(
            {
                "grps": series.str.extract_groups(
                    r"^(\d{4})-W(\d{2})$"
                ).struct.rename_fields(["year", "week"])
            }
        )
        .unnest("grps")
        .with_columns(
            year=pl.col("year").cast(pl.Int32),
            week=pl.col("week").cast(pl.Int32),
        )
        .with_columns(
            valid_year=pl.col("year").ge(1) & pl.col("year").le(9999),
            valid_week=pl.col("week").ge(1) & pl.col("week").le(53),
        )
        .select(pl.all_horizontal("valid_year", "valid_week").all().alias("is_valid"))
        .frame_equal(pl.DataFrame({"is_valid": (True,)}))
    )
