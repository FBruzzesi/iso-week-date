from __future__ import annotations

from typing import TYPE_CHECKING, Any

from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEK_PATTERN, ISOWEEKDATE__DATE_FORMAT, ISOWEEKDATE_PATTERN
from iso_week_date._utils import LONG_YEAR_WEEKS, is_long_year, require_version

require_version("pandas", minimum="1.1.0", extra="pandas")

import pandas as pd  # noqa: E402
from pandas.api.types import is_datetime64_any_dtype as is_datetime  # noqa: E402

if TYPE_CHECKING:
    from typing import Literal, TypeAlias

    from typing_extensions import Self

    ErrorT = Literal["coerce", "raise"]

    OffsetType: TypeAlias = int | pd.Timedelta


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
    series: pd.Series[pd.Timestamp],
    offset: OffsetType,
    _format: str,
) -> pd.Series[str]:
    """Converts series of `date` or `datetime` values to series of `str` values in `_format` format.

    The value is assembled from `Series.dt.isocalendar()` rather than rendered with
    `Series.dt.strftime(_format)`. `strftime` delegates to the platform C library, whose `%G` padding
    is not portable: on glibc with Python < 3.14 an ISO year below 1000 renders unpadded, so
    `date(1, 1, 1)` becomes `"1-W01"` instead of `"0001-W01"`. That is the same defect
    `BaseIsoWeek._format_isocalendar` fixes for the scalar path, and this is its vectorised
    counterpart, so both paths now zero-pad in Python and agree on every platform.

    Arguments:
        series: series of `date` or `datetime` values
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting to
            ISO Week, it can be negative
        _format: format to use for conversion

    Returns:
        Series converted to given format

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pd.Series`
            * series values are not `datetime`
            * `offset` is not of type `pd.Timedelta` or `int`
    """
    if not isinstance(series, pd.Series):
        msg = f"`series` must be of type `pd.Series`, found {type(series).__qualname__}"
        raise TypeError(msg)

    if not is_datetime(series):
        msg = f"`series` values must be of type `datetime`, found {series.dtype}"
        raise TypeError(msg)

    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    shifted = series - _offset
    isocalendar = shifted.dt.isocalendar()

    formatted = isocalendar["year"].astype(str).str.zfill(4) + "-W" + isocalendar["week"].astype(str).str.zfill(2)
    if "%u" in _format:
        formatted = formatted + "-" + isocalendar["day"].astype(str)

    # Nulls are restored from the input rather than left to propagate: on pandas < 3 `astype(str)`
    # renders a missing `UInt32` as the literal string "<NA>", which would concatenate into
    # "<NA>-W<NA>" instead of staying null the way `strftime` did.
    return formatted.where(shifted.notna())


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

            * `series` is not of type `pd.Series`
            * `series` values are not `datetime`-like
            * `offset` is not of type `pd.Timedelta` or `int`

    Examples:
        >>> from datetime import date
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import datetime_to_isoweek
        >>>
        >>> s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1D"))
        >>> datetime_to_isoweek(series=s, offset=pd.Timedelta(days=1)).to_list()
        ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    """
    return _datetime_to_format(series, offset, ISOWEEK__DATE_FORMAT)


def datetime_to_isoweekdate(series: pd.Series[pd.Timestamp], offset: OffsetType = 0) -> pd.Series[str]:
    """Converts series of `date` or `datetime` values to `str` values representing ISO Week date format YYYY-WNN-D.

    Arguments:
        series: series of `date` or `datetime` values
        offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting to
            ISO Week, it can be negative

    Returns:
        Series with converted ISO Week date values (in format YYYY-WNN-D)

    Raises:
        TypeError: If any of the following condition is met:

            * `series` is not of type `pd.Series`
            * `series` values are not `datetime`-like
            * `offset` is not of type `pd.Timedelta` or `int`

    Examples:
        >>> from datetime import date
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import datetime_to_isoweekdate
        >>>
        >>> s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1D"))
        >>> datetime_to_isoweekdate(series=s, offset=pd.Timedelta(days=1)).to_list()
        ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']
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

            * `series` is not of type `pd.Series`
            * `offset` is not of type `pd.Timedelta` or `int`
            * `weekday` is not of type `int` (`bool` is not accepted)
        ValueError: If `weekday` is not an integer between 1 and 7

    Examples:
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import isoweek_to_datetime
        >>>
        >>> s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
        >>> isoweek_to_datetime(series=s, offset=pd.Timedelta(days=1))  # doctest: +ELLIPSIS
        0   2022-12-27
        1   2023-01-03
        2   2023-01-10
        dtype: datetime64[...]
    """
    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    # `bool` is excluded explicitly: `isinstance(True, int)` and `True in range(1, 8)` both hold, so
    # a bare range check would interpolate the literal string "True" into the value being parsed.
    if not isinstance(weekday, int) or isinstance(weekday, bool):
        msg = f"`weekday` must be an integer between 1 and 7, found {type(weekday)}"
        raise TypeError(msg)

    if weekday not in range(1, 8):
        msg = f"`weekday` value must be an integer between 1 and 7, found {weekday}"
        raise ValueError(msg)

    _offset: pd.Timedelta = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    errors: ErrorT = "raise" if strict else "coerce"
    return pd.to_datetime(series + f"-{weekday}", errors=errors, format=ISOWEEKDATE__DATE_FORMAT) + _offset  # pyrefly: ignore[unsupported-operation]


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

            * `series` is not of type `pd.Series`
            * `offset` is not of type `pd.Timedelta` or `int`

    Examples:
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import isoweekdate_to_datetime
        >>>
        >>> s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
        >>> isoweekdate_to_datetime(series=s, offset=pd.Timedelta(days=1))  # doctest: +ELLIPSIS
        0   2022-12-27
        1   2023-01-03
        2   2023-01-10
        dtype: datetime64[...]
    """
    if not isinstance(offset, (pd.Timedelta, int)):
        msg = f"`offset` must be of type `pd.Timedelta` or `int`, found {type(offset)}"
        raise TypeError(msg)

    _offset: pd.Timedelta = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    errors: ErrorT = "raise" if strict else "coerce"
    return pd.to_datetime(series, errors=errors, format=ISOWEEKDATE__DATE_FORMAT) + _offset


def _match_series(series: pd.Series[Any], pattern: str) -> bool:
    """Checks if a `series` contains only values matching `pattern`.

    Null values are skipped rather than counted as non-matching, so a series of
    `["2024-W01", None]` returns `True`. A null is missing data, not a malformed ISO Week string,
    and this is the convention the rest of the module follows: the conversion functions propagate
    nulls through instead of raising on them. `polars_utils._match_series` behaves identically.

    Nulls have to be located through `series.notna()` rather than in the match result: under
    pandas' `str` dtype, `str.fullmatch` returns a plain `bool` Series in which nulls have already
    collapsed to `False`, so by then they are indistinguishable from genuine non-matches. Masking on
    the *input* keeps the answer the same under `object`, `str` and `string` dtypes alike.

    `str.fullmatch` is used rather than `str.match` for the reason spelled out in
    `iso_week_date._utils.match_isoweek`: `str.match` would accept a trailing newline.

    Matching the format is necessary but not sufficient: weeks `01` to `53` are all well-formed, yet
    only long ISO years have a week 53. The week number is therefore checked against its year through
    the very same `is_long_year` helper `IsoWeek._validate` uses, so this answers the same question as
    `IsoWeek(value)` and stays a usable precondition for `isoweek_to_datetime`, which rejects
    `"2023-W53"` outright.

    The match result is filled with `False` because an `object` series can hold values that are
    neither null nor `str` (a list, a dict, a number alongside strings). `str.fullmatch` returns
    `NaN` for those, and `NaN` is truthy, so an unfilled `all()` reported a series of lists as
    correctly formatted. Only nulls in the *input* are excused, and those are masked out separately.

    Arguments:
        series: Series of `str` values
        pattern: pattern to match

    Returns:
        `True` if all non-null values match `pattern` and name a week that exists in their year,
            `False` otherwise. An empty or all-null series returns `True`, since it contains nothing
            that violates the format.

    Raises:
        TypeError: If `series` is not of type `pd.Series`
    """
    if not isinstance(series, pd.Series):
        msg = f"`series` must be of type `pd.Series`, found {type(series)}"
        raise TypeError(msg)

    try:
        matches = series.str.fullmatch(pattern)
    except (AttributeError, TypeError):
        # `AttributeError` for a dtype with no `.str` accessor at all, `TypeError` for one that has
        # it but cannot match against it (`bytes` values). Neither holds ISO Week strings, so both
        # are a plain `False`: the only `TypeError` this function raises is for a non-`pd.Series`.
        return False

    present = series.notna()
    if not bool(matches[present].fillna(value=False).all()):
        return False

    # Every present value is well-formed, so the fixed-width layout makes the year and week readable
    # by position and the casts cannot fail.
    values = series[present]
    if values.empty:
        return True

    year = values.str[:4].astype(int)
    week = values.str[6:8].astype(int)

    # Weeks 01 to 52 exist in every year, so only a week 53 has anything left to prove. `is_long_year`
    # is the same helper `IsoWeek._validate` uses, applied to a column instead of a single year.
    in_calendar = (week != LONG_YEAR_WEEKS) | is_long_year(year)
    return bool(in_calendar.all())


def is_isoweek_series(series: pd.Series[Any]) -> bool:
    """Checks if `series` contains only values in ISO Week format.

    Arguments:
        series: series of `str` values to check against "YYYY-WNN" pattern

    Returns:
        `True` if all values match ISO Week format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pd.Series`

    Examples:
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import is_isoweek_series
        >>>
        >>> s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
        >>> is_isoweek_series(series=s)
        True
    """
    return _match_series(series, ISOWEEK_PATTERN.pattern)


def is_isoweekdate_series(series: pd.Series[Any]) -> bool:
    """Checks if `series` contains only values in ISO Week date format.

    Arguments:
        series: series of `str` values to check against "YYYY-WNN-D" pattern

    Returns:
        `True` if all values match ISO Week date format, `False` otherwise

    Raises:
        TypeError: If `series` is not of type `pd.Series`

    Examples:
        >>> import pandas as pd
        >>> from iso_week_date.pandas_utils import is_isoweekdate_series
        >>> s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
        >>> is_isoweekdate_series(series=s)
        True
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

    s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1D"))
    s.iwd.datetime_to_isoweek(offset=pd.Timedelta(days=1)).to_list()
    # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
    ```

    Arguments:
        series: The pandas Series object the extension is attached to.

    Attributes:
        _series: The pandas Series object the extension is attached to.
    """

    def __init__(self: Self, series: pd.Series[str] | pd.Series[pd.Timestamp]) -> None:
        self._series = series

    def datetime_to_isoweek(self: Self, offset: OffsetType = 0) -> pd.Series[str]:
        """Converts series of `date` or `datetime` values to `str` values representing ISO Week format YYYY-WNN.

        Arguments:
            offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting
                to ISO Week, it can be negative

        Returns:
            ISO Week pandas series in format YYYY-WNN

        Raises:
            TypeError: If series values are not `datetime`, or if `offset` is not of type `pd.Timedelta` or `int`

        Examples:
            >>> from datetime import date
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1D"))
            >>> s.iwd.datetime_to_isoweek(offset=pd.Timedelta(days=1)).to_list()
            ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']
        """
        return datetime_to_isoweek(self._series, offset=offset)  # type: ignore[arg-type]

    def datetime_to_isoweekdate(self: Self, offset: OffsetType = 0) -> pd.Series[str]:
        """Converts series of `date` or `datetime` values to `str` values representing ISO Week date format YYYY-WNN-D.

        Arguments:
            offset: offset in days or `pd.Timedelta`. It represents how many days to add to the date before converting
                to ISO Week, it can be negative

        Returns:
            ISO Week date pandas series in format YYYY-WNN-D

        Raises:
            TypeError: If series values are not `datetime`, or if `offset` is not of type `pd.Timedelta` or `int`

        Examples:
            >>> from datetime import date
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1D"))
            >>> s.iwd.datetime_to_isoweekdate(offset=pd.Timedelta(days=1)).to_list()
            ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']
        """
        return datetime_to_isoweekdate(self._series, offset=offset)  # type: ignore[arg-type]

    def isoweek_to_datetime(
        self: Self,
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
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
            >>> s.iwd.isoweek_to_datetime(offset=pd.Timedelta(days=1))  # doctest: +ELLIPSIS
            0   2022-12-27
            1   2023-01-03
            2   2023-01-10
            dtype: datetime64[...]
        """
        return isoweek_to_datetime(self._series, offset=offset, weekday=weekday, strict=strict)  # type: ignore[arg-type]

    def isoweekdate_to_datetime(self: Self, offset: OffsetType = 0, *, strict: bool = True) -> pd.Series[pd.Timestamp]:
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
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
            >>> s.iwd.isoweekdate_to_datetime(offset=pd.Timedelta(days=1))  # doctest: +ELLIPSIS
            0   2022-12-27
            1   2023-01-03
            2   2023-01-10
            dtype: datetime64[...]
        """
        return isoweekdate_to_datetime(self._series, offset=offset, strict=strict)  # type: ignore[arg-type]

    def is_isoweek(self: Self) -> bool:
        """Checks if series contains only values in ISO Week format.

        Returns:
            `True` if all values match ISO Week format, `False` otherwise

        Examples:
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
            >>> s.iwd.is_isoweek()
            True
        """
        return is_isoweek_series(self._series)

    def is_isoweekdate(self: Self) -> bool:
        """Checks if series contains only values in ISO Week date format.

        Returns:
            `True` if all values match ISO Week date format, `False` otherwise

        Examples:
            >>> import pandas as pd
            >>> from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401
            >>>
            >>> s = pd.Series(["2022-W52-1", "2023-W01-1", "2023-W02-1"])
            >>> s.iwd.is_isoweekdate()
            True
        """
        return is_isoweekdate_series(self._series)
