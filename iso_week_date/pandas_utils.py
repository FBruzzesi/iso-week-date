from typing import Union

from iso_week_date._patterns import (
    ISOWEEK__DATE_FORMAT,
    ISOWEEK__FORMAT,
    ISOWEEK_PATTERN,
    ISOWEEKDATE__DATE_FORMAT,
    ISOWEEKDATE__FORMAT,
    ISOWEEKDATE_PATTERN,
)

try:
    import pandas as pd
    from pandas.api.types import is_datetime64_any_dtype as is_datetime
except ImportError:  # pragma: no cover
    raise ImportError(
        "pandas is required for this module, install it with `pip install pandas`"
        " or `pip install iso-week-date[pandas]`"
    )


def _datetime_to_format(
    series: pd.Series,
    offset: Union[pd.Timedelta, int],
    _format: str,
) -> pd.Series:
    """
    Converts `date` (`datetime`) pandas series to `str` series of values in `_format`
    format.

    Arguments:
        series: `date` or `datetime` pandas `series`
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to
            the date before converting to ISO Week, it can be negative
        _format: format to use for conversion

    Returns:
        pandas series in given format

    Raises:
        TypeError: if `series` is not of type `pd.Series`,its values are not `datetime`,
            or if `offset` is not of type `pd.Timedelta` or `int`
    """

    if not isinstance(series, pd.Series):
        raise TypeError(f"`series` must be of type `pd.Series`, found {type(series)}")

    if not is_datetime(series):
        raise TypeError(
            f"`series` values must be of type `datetime`, found {series.dtype}"
        )

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        )

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.strftime(_format)


def datetime_to_isoweek(
    series: pd.Series, offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0)
) -> pd.Series:
    """
    Converts pandas `series` with `date` (or `datetime`) values to `str` values
    representing ISO Week format YYYY-WNN.

    Arguments:
        series: `date` or `datetime` pandas `series`
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to
            the date before converting to ISO Week, it can be negative

    Returns:
        ISO Week pandas series in format YYYY-WNN

    Raises:
        TypeError: if `series` is not of type `pd.Series`, its values are not `datetime`,
            or if `offset` is not of type `pd.Timedelta` or `int`

    Usage:
    ```py
    from datetime import date
    import pandas as pd
    from iso_week_date.pandas_utils import datetime_to_isoweek

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    datetime_to_isoweek(
        series=s,
        offset=pd.Timedelta(days=1)
        ).to_list()
    # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    ```
    """

    return _datetime_to_format(series, offset, ISOWEEK__DATE_FORMAT)


def datetime_to_isoweekdate(
    series: pd.Series, offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0)
) -> pd.Series:
    """
    Converts pandas `series` with `date` (or `datetime`) values to `str` values
    representing ISO Week date format YYYY-WNN-D.

    Arguments:
        series: `date` or `datetime` pandas `series`
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to
            the date before converting to ISO Week, it can be negative

    Returns:
        ISO Week date pandas series in format YYYY-WNN-D

    Raises:
        TypeError: if `series` is not of type `pd.Series`,its values are not `datetime`,
            or if `offset` is not of type `pd.Timedelta` or `int`

    Usage:
    ```py
    from datetime import date
    import pandas as pd
    from iso_week_date.pandas_utils import datetime_to_isoweekdate

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    datetime_to_isoweekdate(
        series=s,
        offset=pd.Timedelta(days=1)
        ).to_list()
    # ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']
    ```
    """

    return _datetime_to_format(series, offset, ISOWEEKDATE__DATE_FORMAT)


def isoweek_to_datetime(
    series: pd.Series,
    offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0),
    weekday: int = 1,
) -> pd.Series:
    """
    Converts pandas `series` of `str` in ISO Week format to a `series` of
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
        TypeError: if `series` is not of type `pd.Series`, or if `offset` is not of type
            `pd.Timedelta` or `int`
        ValueError: if `weekday` is not an integer between 1 and 7

    Usage:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import isoweek_to_datetime

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
    if not is_isoweek_series(series):
        raise ValueError(
            f"`series` values must match ISO Week date format {ISOWEEK__FORMAT}"
        )

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        )

    if weekday not in range(1, 8):
        raise ValueError(
            f"`weekday` value must be an integer between 1 and 7, found {weekday}"
        )

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (
        pd.to_datetime(series + "-" + f"{weekday}", format=ISOWEEKDATE__DATE_FORMAT)
        + _offset
    )


def isoweekdate_to_datetime(
    series: pd.Series,
    offset: Union[pd.Timedelta, int] = pd.Timedelta(days=0),
) -> pd.Series:
    """
    Converts pandas `series` of `str` in ISO Week date format to a `series` of
    `datetime` object.

    `offset` represents how many days to add to the date before converting to datetime
        and it can be negative.

    Arguments:
        series: series of `str` in ISO Week date format
        offset: offset in days or pd.Timedelta. It represents how many days to add to the
            date before converting to IsoWeek, it can be negative

    Returns:
        datetime series

    Raises:
        TypeError: if `series` is not of type `pd.Series`, or if `offset` is not of type
            `pd.Timedelta` or `int`
        ValueError: if `weekday` is not an integer between 1 and 7

    Usage:
    ```py
    import pandas as pd
    from iso_week_date.pandas_utils import isoweekdate_to_datetime

    s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
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
    if not is_isoweekdate_series(series):
        raise ValueError(
            f"`series` values must match ISO Week date format {ISOWEEKDATE__FORMAT}"
        )

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        )

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return pd.to_datetime(series, format=ISOWEEKDATE__DATE_FORMAT) + _offset


def _match_series(series: pd.Series, pattern: str) -> bool:
    """
    Checks if a pandas `series` contains only values matching `pattern`.

    Arguments:
        series: series of `str`
        pattern: pattern to match

    Returns:
        `True` if all values match `pattern`, `False` otherwise

    Raises:
        TypeError: if `series` is not of type `pd.Series`
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"`series` must be of type `pd.Series`, found {type(series)}")

    return series.str.match(pattern).all()


def is_isoweek_series(series: pd.Series) -> bool:
    """
    Checks if a pandas `series` contains only values in ISO Week format.

    Arguments:
        series: series of `str` to check against ISOWEEK_PATTERN

    Returns:
        `True` if all values match ISO Week format, `False` otherwise

    Raises:
        TypeError: if `series` is not of type `pd.Series`

    Usage:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import is_isoweek_series

    s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
    is_isoweek_series(series=s)  # True
    ```
    """
    return _match_series(series, ISOWEEK_PATTERN.pattern)


def is_isoweekdate_series(series: pd.Series) -> bool:
    """
    Checks if a pandas `series` contains only values in ISO Week date format.

    Arguments:
        series: series of `str` to check against ISOWEEKDATE_PATTERN

    Returns:
        `True` if all values match ISO Week date format, `False` otherwise

    Raises:
        TypeError: if `series` is not of type `pd.Series`

    Usage:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import is_isoweekdate_series

    s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
    is_isoweekdate_series(series=s)  # True
    ```
    """
    return _match_series(series, ISOWEEKDATE_PATTERN.pattern)
