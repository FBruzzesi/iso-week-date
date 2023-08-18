from typing import Union

try:
    import pandas as pd
    from pandas.api.types import is_datetime64_any_dtype as is_datetime
except ImportError:  # pragma: no cover
    raise ImportError("pandas is required for this module")


def datetime_to_isoweek(
    series: pd.Series, offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0)
) -> pd.Series:
    """
    Converts pandas `series` with `date` (or `datetime`) values to `str` values
    representing ISO Week date format YYYY-WNN.

    Arguments:
        series: `date` or `datetime` pandas `series`
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to
            the date before converting to ISO Week, it can be negative

    Returns:
        ISO Week pandas series

    Raises:
        TypeError: if series is not of type pd.Series
        TypeError: if offset is not of type pd.Timedelta or int

    Usage:
    ```py
    import pandas as pd
    from datetime import date, timedelta
    from iso_week.pandas_utils import datetime_to_isoweek

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    datetime_to_isoweek(
        series=s,
        offset=pd.Timedelta(days=1)
        ).to_list()  # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    ```
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"series must be of type pd.Series, found {type(series)}")

    if not is_datetime(series):
        raise TypeError(f"series values must be of type datetime, found {series.dtype}")

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"offset must be of type pd.Timedelta or int, found {type(offset)}"
        )
    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.strftime("%G-W%V")


def isoweek_to_datetime(
    series: pd.Series,
    offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0),
    weekday: int = 1,
) -> pd.Series:
    """
    Converts pandas `series` of `str` in ISO Week date format to a `series` of
    `datetime` object.

    `offset` represents how many days to add to the date before converting to datetime
        and it can be negative.

    `weekday` represents the weekday to use for conversion in ISO Week format (1-7),
        where 1 is the first day of the week, 7 is the last one.

    Arguments:
        series: series of `str` in ISO Week date format
        offset: offset in days or pd.Timedelta. It represents how many days to add to the
            date before converting to IsoWeek, it can be negative
        weekday: weekday to use for conversion (1-7)

    Returns:
        datetime series

    Raises:
        TypeError: if series is not of type pd.Series
        TypeError: if offset is not of type pd.Timedelta or int
        ValueError: if weekday is not an integer between 1 and 7

    Usage:
    ```py
    import pandas as pd

    from iso_week.pandas_utils import isoweek_to_datetime

    s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
    isoweek_to_datetime(
        series=s,
        offset=pd.Timedelta(days=1)
        )
    '''
    0   2022-12-27
    1   2023-01-03
    2   2023-01-10
    dtype: datetime64[ns]
    '''
    ```
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"series must be of type pd.Series, found {type(series)}")

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"offset must be of type pd.Timedelta or int, found {type(offset)}"
        )

    if weekday not in range(1, 8):
        raise ValueError(
            f"weekday value must be an integer between 1 and 7, found {weekday}"
        )

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return pd.to_datetime(series + "-" + f"{weekday}", format="%G-W%V-%u") + _offset
