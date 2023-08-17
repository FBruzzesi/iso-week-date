from datetime import date, timedelta

import polars as pl
import pytest
from polars.testing import assert_series_equal

from iso_week import IsoWeek
from iso_week.polars_utils import datetime_to_isoweek, isoweek_to_datetime

start = date(2023, 1, 1)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_datetime_to_isoweek(periods, offset):
    """Tests datetime_to_isoweek with different offsets"""

    dt_series = pl.date_range(
        start, start + timedelta(weeks=periods - 1), interval="1w", eager=True
    )

    converted_series = datetime_to_isoweek(dt_series, offset=offset)

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        _offset = timedelta(days=offset)

    iso_series = pl.Series(
        CustomWeek.from_date(start - timedelta(weeks=1)).weeksout(periods)
    )

    assert_series_equal(converted_series, iso_series, check_names=False)


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"series": pl.DataFrame()},
            pytest.raises(TypeError),
            "series must be of type pl.Series or pl.Expr",
        ),
        (
            {
                "series": pl.date_range(
                    start, start + timedelta(weeks=5), interval="1w", eager=True
                ),
                "offset": "abc",
            },
            pytest.raises(TypeError),
            "offset must be of type timedelta or int",
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

        _offset = timedelta(days=offset)

    iso_series = pl.Series(
        CustomWeek.from_date(_start - timedelta(weeks=1)).weeksout(periods)
    )

    dt_series = isoweek_to_datetime(iso_series, offset=offset, weekday=weekday)

    assert_series_equal(
        datetime_to_isoweek(dt_series, offset=offset), iso_series, check_names=False
    )


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"series": pl.DataFrame()},
            pytest.raises(TypeError),
            "series must be of type pl.Series or pl.Expr",
        ),
        (
            {"series": pl.Series(["2023-W01", "2023-W02"]), "offset": "abc"},
            pytest.raises(TypeError),
            "offset must be of type timedelta or int",
        ),
        (
            {"series": pl.Series(["2023-W01", "2023-W02"]), "weekday": 0},
            pytest.raises(ValueError),
            "weekday value must be an integer between 1 and 7",
        ),
    ],
)
def test_isoweek_to_datetime_raise(capsys, kwargs, context, err_msg):
    """Test isoweek_to_datetime with invalid arguments"""
    with context:
        isoweek_to_datetime(**kwargs)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out
