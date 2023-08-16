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
    Convert datetime series to IsoWeek series

    Arguments:
        series: datetime series
        offset: offset in days or pd.Timedelta

    Returns:
        IsoWeek series
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"series must be of type pd.Series, found {type(series)}")

    if not is_datetime(series):
        raise TypeError(f"series must be of type datetime, found {series.dtype}")

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
    Convert IsoWeek series to datetime series

    Arguments:
        series: IsoWeek series
        offset: offset in days or pd.Timedelta
        weekday: weekday to use for conversion

    Returns:
        datetime series
    """
    if not isinstance(series, pd.Series):
        raise TypeError(f"series must be of type pd.Series, found {type(series)}")

    if not isinstance(offset, (pd.Timedelta, int)):
        raise TypeError(
            f"offset must be of type pd.Timedelta or int, found {type(offset)}"
        )

    if weekday not in range(1, 8):
        raise ValueError(f"weekday value must be between 1 and 7, found {weekday}")

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return pd.to_datetime(series + "-" + f"{weekday}", format="%G-W%V-%u") + _offset
