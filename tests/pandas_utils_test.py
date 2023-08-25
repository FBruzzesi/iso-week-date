from datetime import date, timedelta

import pandas as pd
import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.testing import assert_series_equal

from iso_week_date import IsoWeek
from iso_week_date.pandas_utils import (
    datetime_to_isoweek,
    is_isoweek_series,
    is_isoweekdate_series,
    isoweek_to_datetime,
)

start = date(2023, 1, 1)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_datetime_to_isoweek(periods, offset):
    """Tests datetime_to_isoweek with different offsets"""

    dt_series = pd.Series(pd.date_range(start, periods=periods, freq="W"))
    converted_series = datetime_to_isoweek(dt_series, offset=offset)

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pd.Series(
        CustomWeek.from_date(start - timedelta(weeks=1)).weeksout(periods)
    )

    assert_series_equal(converted_series, iso_series)


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"series": pd.DataFrame()},
            pytest.raises(TypeError),
            "series must be of type pd.Series",
        ),
        (
            {"series": pd.Series([1, 2, 3])},
            pytest.raises(TypeError),
            "series values must be of type datetime",
        ),
        (
            {"series": pd.Series(pd.date_range(start, periods=5)), "offset": "abc"},
            pytest.raises(TypeError),
            "offset must be of type pd.Timedelta or int",
        ),
    ],
)
def test_datetime_to_isoweek_raise(capsys, kwargs, context, err_msg):
    """Test datetime_to_isoweek with invalid arguments"""
    with context:
        datetime_to_isoweek(**kwargs)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_isoweek_to_datetime(periods, offset):
    """Tests isoweek_to_datetime with different offsets"""

    _start = start + timedelta(days=offset)
    _, _, weekday = _start.isocalendar()

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        offset_ = timedelta(days=offset)

    iso_series = pd.Series(
        CustomWeek.from_date(_start - timedelta(weeks=1)).weeksout(periods)
    )

    dt_series = isoweek_to_datetime(iso_series, offset=offset, weekday=weekday)
    assert is_datetime(dt_series)

    assert_series_equal(datetime_to_isoweek(dt_series, offset=offset), iso_series)


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"series": pd.DataFrame()},
            pytest.raises(TypeError),
            "series must be of type pd.Series",
        ),
        (
            {"series": pd.Series(["2023-W01", "2023-W02"]), "offset": "abc"},
            pytest.raises(TypeError),
            "offset must be of type pd.Timedelta or int",
        ),
        (
            {"series": pd.Series(["2023-W01", "2023-W02"]), "weekday": 0},
            pytest.raises(ValueError),
            "weekday value must be an integer between 1 and 7",
        ),
        (
            {"series": pd.Series(["2023-Wab", "2023-W02"]), "weekday": 1},
            pytest.raises(ValueError),
            "series values must match ISO Week date format YYYY-WNN",
        ),
    ],
)
def test_isoweek_to_datetime_raise(capsys, kwargs, context, err_msg):
    """Test isoweek_to_datetime with invalid arguments"""
    with context:
        isoweek_to_datetime(**kwargs)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize(
    "series, expected",
    [
        (pd.Series(["2023-W01", "2023-W02"]), True),
        (pd.Series(["abcd-Wxy", "2023-W02"]), False),
        (pd.Series(["0000-W01", "2023-W02"]), False),
        (pd.Series(["2023-W00", "2023-W02"]), False),
    ],
)
def test_is_isoweek_series(series, expected):
    """Test is_isoweek_series function"""
    assert is_isoweek_series(series) == expected


@pytest.mark.parametrize(
    "series, expected",
    [
        (pd.Series(["2023-W01-1", "2023-W02-1"]), True),
        (pd.Series(["abcd-Wxy-1", "2023-W02-1"]), False),
        (pd.Series(["0000-W01-1", "2023-W02-1"]), False),
        (pd.Series(["2023-W00-1", "2023-W02-1"]), False),
    ],
)
def test_is_isoweek_series(series, expected):
    """Test is_isoweek_series function"""
    assert is_isoweekdate_series(series) == expected


def test_is_isoweek_series_raise():
    """Test is_isoweek_series function with invalid type"""
    series = pd.DataFrame({"isoweek": ["2023-W01", "2023-W02"]})
    with pytest.raises(TypeError):
        is_isoweek_series(series)
