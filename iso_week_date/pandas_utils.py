from __future__ import annotations

import sys
from typing import TYPE_CHECKING
from typing import Union

from iso_week_date._patterns import ISOWEEK__DATE_FORMAT
from iso_week_date._patterns import ISOWEEK_PATTERN
from iso_week_date._patterns import ISOWEEKDATE__DATE_FORMAT
from iso_week_date._patterns import ISOWEEKDATE_PATTERN
from iso_week_date._utils import parse_version

if sys.version_info >= (3, 10):  # pragma: no cover
    from typing import TypeAlias
else:  # pragma: no cover
    from typing_extensions import TypeAlias

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self
else:  # pragma: no cover
    from typing_extensions import Self

if parse_version("pandas") < (1, 0, 0):  # pragma: no cover
    raise ImportError(
        "pandas>=1.0.0 is required for this module, install it with `python -m pip install pandas>=1.0.0`"
        " or `python -m pip install iso-week-date[pandas]`",
    )
else:  # pragma: no cover
    import pandas as pd
    from pandas.api.types import is_datetime64_any_dtype as is_datetime

if TYPE_CHECKING:
    from typing import Literal

    ErrorT = Literal["coerce", "raise"]

OffsetType: TypeAlias = Union[int, pd.Timedelta]


def _datetime_to_format(
    series: pd.Series[pd.Timestamp],
    offset: OffsetType,
    _format: str,
) -> pd.Series[str]:
    """Converts series of `date` or `datetime` values to series of `str` values in `_format` format.

    Arguments:
        series: series of `date` or `datetime` values
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting to
            ISO Week, it can be negative
        _format: format to use for conversion

    Returns:
        Series converted to given format

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pd.Series`
            - series values are not `datetime`
            - `offset` is not of type `pd.Timedelta` or `int`
    """
    if not isinstance(series, pd.Series):
        msg = f"`series` must be of type `pd.Series`, found {type(series)}"
        raise TypeError(msg)

    if not is_datetime(series):
        msg = f"`series` values must be of type `datetime`, found {series.dtype}"
        raise TypeError(msg)

    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (series - _offset).dt.strftime(_format)


def datetime_to_isoweek(series: pd.Series[pd.Timestamp], offset: OffsetType = 0) -> pd.Series[str]:
    """Converts series of `date` or `datetime` values to `str` values representing ISO Week format YYYY-WNN.

    Arguments:
        series: series of `date` or `datetime` values
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting to
            ISO Week, it can be negative

    Returns:
        Series with converted ISO Week values (in format YYYY-WNN)

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pd.Series`
            - `series` values are not `datetime`-like
            - `offset` is not of type `pd.Timedelta` or `int`

    Examples:
    ```py
    from datetime import date
    import pandas as pd
    from iso_week_date.pandas_utils import datetime_to_isoweek

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    datetime_to_isoweek(series=s, offset=pd.Timedelta(days=1)).to_list()
    # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    ```
    """
    return _datetime_to_format(series, offset, ISOWEEK__DATE_FORMAT)


def datetime_to_isoweekdate(series: pd.Series, offset: OffsetType = 0) -> pd.Series:
    """Converts series of `date` or `datetime` values to `str` values representing ISO Week date format YYYY-WNN-D.

    Arguments:
        series: series of `date` or `datetime` values
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting to
            ISO Week, it can be negative

    Returns:
        Series with converted ISO Week date values (in format YYYY-WNN-D)

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pd.Series`
            - `series` values are not `datetime`-like
            - `offset` is not of type `pd.Timedelta` or `int`

    Examples:
    ```py
    from datetime import date
    import pandas as pd
    from iso_week_date.pandas_utils import datetime_to_isoweekdate

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    datetime_to_isoweekdate(series=s, offset=pd.Timedelta(days=1)).to_list()
    # ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']
    ```
    """
    return _datetime_to_format(series, offset, ISOWEEKDATE__DATE_FORMAT)


def isoweek_to_datetime(
    series: pd.Series[str],
    offset: OffsetType = 0,
    weekday: int = 1,
    *,
    strict: bool = True,
) -> pd.Series[pd.Timestamp]:
    """Converts series of `str` values in ISO Week format to a series of `datetime` values.

    `offset` represents how many days to add to the date before converting to datetime and it can be negative.

    `weekday` represents the weekday to use for conversion in ISO Week format (1-7), where 1 is the first day of the
    week, 7 is the last one.

    Arguments:
        series: Series of `str` values in ISO Week format.
        offset: Offset in days or pd.Timedelta. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative.
        weekday: Weekday to use for conversion (1-7).
        strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

    Returns:
        Series of converted datetime values

    Raises:
        TypeError: If any of the following condition is met:

            - `series` is not of type `pd.Series`
            - `offset` is not of type `pd.Timedelta` or `int`
        ValueError: If `weekday` is not an integer between 1 and 7

    Examples:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import isoweek_to_datetime

    s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
    isoweek_to_datetime(series=s, offset=pd.Timedelta(days=1))
    '''
    0   2022-12-27
    1   2023-01-03
    2   2023-01-10
    dtype: datetime64[ns]
    '''
    ```
    """
    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    if weekday not in range(1, 8):
        msg = f"`weekday` value must be an integer between 1 and 7, found {weekday}"
        raise ValueError(msg)

    _offset: pd.Timedelta = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    errors: ErrorT = "raise" if strict else "coerce"
    return pd.to_datetime(series + "-" + f"{weekday}", errors=errors, format=ISOWEEKDATE__DATE_FORMAT) + _offset


def isoweekdate_to_datetime(
    series: pd.Series[str],
    offset: OffsetType = 0,
    *,
    strict: bool = True,
) -> pd.Series[pd.Timestamp]:
    """Converts series of `str` values in ISO Week date format to a series of `datetime` values.

    `offset` represents how many days to add to the date before converting to datetime and it can be negative.

    Arguments:
        series: series of `str` in ISO Week date format.
        offset: offset in days or pd.Timedelta. It represents how many days to add to the date before converting to
            IsoWeek, it can be negative.
        strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

    Returns:
        Series of converted datetime values

    Raises:
        TypeError: If one of the following condition is met:

            - `series` is not of type `pd.Series`
            - `offset` is not of type `pd.Timedelta` or `int`

    Examples:
    ```py
    import pandas as pd
    from iso_week_date.pandas_utils import isoweekdate_to_datetime

    s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
    isoweekdate_to_datetime(series=s, offset=pd.Timedelta(days=1))
    '''
    0   2022-12-27
    1   2023-01-03
    2   2023-01-10
    dtype: datetime64[ns]
    '''
    ```
    """
    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset: pd.Timedelta = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    errors: ErrorT = "raise" if strict else "coerce"
    return pd.to_datetime(series, errors=errors, format=ISOWEEKDATE__DATE_FORMAT) + _offset


def _match_series(series: pd.Series, pattern: str) -> bool:
    """Checks if a `series` contains only values matching `pattern`.

    Arguments:
        series: Series of `str` values
        pattern: pattern to match

    Returns:
        `True` if all values match `pattern`, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pd.Series`
    """
    if not isinstance(series, pd.Series):
        msg = f"`series` must be of type `pd.Series`, found {type(series)}"
        raise TypeError(msg)

    try:
        return series.str.match(pattern).all()
    except AttributeError:
        return False


def is_isoweek_series(series: pd.Series) -> bool:
    """Checks if `series` contains only values in ISO Week format.

    Arguments:
        series: series of `str` values to check against "YYYY-WNN" pattern

    Returns:
        `True` if all values match ISO Week format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pd.Series`

    Examples:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import is_isoweek_series

    s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
    is_isoweek_series(series=s)  # True
    ```
    """
    return _match_series(series, ISOWEEK_PATTERN.pattern)


def is_isoweekdate_series(series: pd.Series) -> bool:
    """Checks if `series` contains only values in ISO Week date format.

    Arguments:
        series: series of `str` values to check against "YYYY-WNN-D" pattern

    Returns:
        `True` if all values match ISO Week date format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pd.Series`

    Examples:
    ```py
    import pandas as pd

    from iso_week_date.pandas_utils import is_isoweekdate_series

    s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
    is_isoweekdate_series(series=s)  # True
    ```
    """
    return _match_series(series, ISOWEEKDATE_PATTERN.pattern)


@pd.api.extensions.register_series_accessor("iwd")
class SeriesIsoWeek:
    """Pandas Series extension that provides methods for working with ISO weeks and dates.

    Instead of importing and working with single functions from the `pandas_utils` module, it is possible to import the
    Series [extension class](https://pandas.pydata.org/docs/development/extending.html) to be able to use the functions
    as methods on Series objects.

    To accomplish this, it is enough to load `SeriesIsoWeek` into scope:

    ```python hl_lines="3 6"
    from datetime import date
    import pandas as pd
    from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
    s.iwd.datetime_to_isoweek(offset=pd.Timedelta(days=1)).to_list()
    # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    ```
    Parameters:
        series: The pandas Series object the extension is attached to.

    Attributes:
        _series: The pandas Series object the extension is attached to.
    """

    def __init__(self: Self, series: pd.Series) -> None:
        self._series: pd.Series = series

    def datetime_to_isoweek(self: Self, offset: OffsetType = 0) -> pd.Series:
        """Converts series of `date` or `datetime` values to `str` values representing ISO Week format YYYY-WNN.

        Arguments:
            offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting
                to ISO Week, it can be negative

        Returns:
            ISO Week pandas series in format YYYY-WNN

        Raises:
            TypeError: If series values are not `datetime`, or if `offset` is not of type `pd.Timedelta` or `int`

        Examples:
        ```py
        from datetime import date
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
        s.iwd.datetime_to_isoweek(offset=pd.Timedelta(days=1)).to_list()
        # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
        ```
        """
        return datetime_to_isoweek(self._series, offset=offset)

    def datetime_to_isoweekdate(self: Self, offset: OffsetType = 0) -> pd.Series:
        """Converts series of `date` or `datetime` values to `str` values representing ISO Week date format YYYY-WNN-D.

        Arguments:
            offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting
                to ISO Week, it can be negative

        Returns:
            ISO Week date pandas series in format YYYY-WNN-D

        Raises:
            TypeError: If series values are not `datetime`, or if `offset` is not of type `pd.Timedelta` or `int`

        Examples:
        ```py
        from datetime import date
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
        s.iwd.datetime_to_isoweekdate(offset=pd.Timedelta(days=1)).to_list()
        # ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']
        ```
        """
        return datetime_to_isoweekdate(self._series, offset=offset)

    def isoweek_to_datetime(
        self: Self,
        offset: OffsetType = 0,
        weekday: int = 1,
        *,
        strict: bool = True,
    ) -> pd.Series:
        """Converts series of `str` values in ISO Week format to a series of `datetime` values.

        `offset` represents how many days to add to the date before converting to datetime and it can be negative.

        `weekday` represents the weekday to use for conversion in ISO Week format (1-7), where 1 is the first day of the
        week, 7 is the last one.

        Arguments:
            offset: Offset in days or pd.Timedelta. It represents how many days to add to the date before converting to
                IsoWeek, it can be negative.
            weekday: Weekday to use for conversion (1-7).
            strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

        Returns:
            Series of converted datetime values

        Raises:
            TypeError: If `offset` is not of type `pd.Timedelta` or `int`
            ValueError: If `weekday` is not an integer between 1 and 7

        Examples:
        ```py
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
        s.iwd.isoweek_to_datetime(offset=pd.Timedelta(days=1))
        '''
        0   2022-12-27
        1   2023-01-03
        2   2023-01-10
        dtype: datetime64[ns]
        '''
        ```
        """
        return isoweek_to_datetime(self._series, offset=offset, weekday=weekday, strict=strict)

    def isoweekdate_to_datetime(self: Self, offset: OffsetType = 0, *, strict: bool = True) -> pd.Series:
        """Converts series of `str` values in ISO Week date format to a series of `datetime` values.

        `offset` represents how many days to add to the date before converting to datetime and it can be negative.

        Arguments:
            offset: Offset in days or pd.Timedelta. It represents how many days to add to the date before converting to
                IsoWeek, it can be negative.
            strict: Raise an error if the values cannot be converted to datetime. Otherwise mask out with a null value.

        Returns:
            Series of converted datetime values

        Raises:
            TypeError: If `offset` is not of type `pd.Timedelta` or `int`
            ValueError: If `weekday` is not an integer between 1 and 7

        Examples:
        ```py
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
        s.iwd.isoweekdate_to_datetime(offset=pd.Timedelta(days=1))
        '''
        0   2022-12-27
        1   2023-01-03
        2   2023-01-10
        dtype: datetime64[ns]
        '''
        ```
        """
        return isoweekdate_to_datetime(self._series, offset=offset, strict=strict)

    def is_isoweek(self: Self) -> bool:
        """Checks if series contains only values in ISO Week format.

        Returns:
            `True` if all values match ISO Week format, `False` otherwise

        Examples:
        ```py
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
        s.iwd.is_isoweek()  # True
        ```
        """
        return is_isoweek_series(self._series)

    def is_isoweekdate(self: Self) -> bool:
        """Checks if series contains only values in ISO Week date format.

        Returns:
            `True` if all values match ISO Week date format, `False` otherwise

        Examples:
        ```py
        import pandas as pd
        from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401

        s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
        s.iwd.is_isoweekdate()  # True
        ```
        """
        return is_isoweekdate_series(self._series)
