from datetime import date, timedelta

import pandas as pd
import pytest
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.testing import assert_series_equal

from iso_week import IsoWeek
from iso_week.pandas_utils import datetime_to_isoweek, isoweek_to_datetime

start = date(2023, 1, 1)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_datetime_to_isoweek(periods, offset):
    """Tests datetime_to_isoweek with different offsets"""

    dt_series = pd.Series(pd.date_range(start, periods=periods, freq="W"))
    converted_series = datetime_to_isoweek(dt_series, offset=offset)

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        _offset = timedelta(days=offset)

    iso_series = pd.Series(
        CustomWeek.from_date(start).weeksout(periods, inclusive="left")
    )

    assert_series_equal(converted_series, iso_series)


@pytest.mark.parametrize("periods", [5, 10, 52])
@pytest.mark.parametrize("offset", [-7, -2, 0, 1, 5])
def test_isoweek_to_datetime(periods, offset):
    """Tests isoweek_to_datetime with different offsets"""

    _start = start + timedelta(days=offset)
    weekday = _start.isocalendar().weekday

    class CustomWeek(IsoWeek):
        """Custom week class with offset"""

        _offset = timedelta(days=offset)

    iso_series = pd.Series(
        CustomWeek.from_date(_start).weeksout(periods, inclusive="left")
    )

    dt_series = isoweek_to_datetime(iso_series, offset=offset, weekday=weekday)
    assert is_datetime(dt_series)

    assert_series_equal(datetime_to_isoweek(dt_series, offset=offset), iso_series)
