from typing import Union

try:
    import pandas as pd
except ImportError:
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
    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (series + _offset).dt.strftime("%G-W%V")


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

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return pd.to_datetime(series + "-" + f"{weekday}", format="%G-W%V-%w") + _offset
