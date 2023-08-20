# Quickstart

In this section we will see how to work with the different modules of the library.

For a high level overview of the features provided by the `iso-week` package, see [Features](../features) sections.

For a detailed description of the API, see [API Reference](../../api/isoweek) section.

## `IsoWeek`

The `IsoWeek` class is accessible from the top-level module:

```py
from datetime import date, datetime, timedelta
from iso_week import IsoWeek
```

An instance can be initialized from parsing multiple types:

- `str` in _YYYY-WNN_ format

    ```py
    iw = IsoWeek("2023-W01")
    iw.value, iw._offset # "2023-W01", datetime.timedelta(0)
    ```

- `str` in compact format _YYYYWNN_

    ```py
    IsoWeek.from_compact("2023W01")
    ```

- `date` or `datetime` objects

    ```py
    IsoWeek.from_date(date(2023, 1, 2))
    IsoWeek.from_datetime(datetime(2023, 1, 2, 12, 0, 0))
    ```

Once initialized, the instance provides the following methods:

- _properties_ to access year, week and days of the week:

    ```py
    iw.year # 2023
    iw.week # 1
    iw.days # (date(2023, 1, 2),..., date(2023, 1, 8))
    ```

- Conversion to multiple types:

    ```py
    iw.to_str() # "2023-W01"
    iw.to_compact() # "2023W01"
    iw.to_date() # date(2023, 1, 2)
    iw.to_date(weekday=2) # date(2023, 1, 3)
    iw.to_datetime() # datetime(2023, 1, 2, 0, 0)
    ```

- Comparison operations:

    ```py
    iw == IsoWeek("2023-W01") # True
    iw == IsoWeek("2023-W02") # False
    iw < IsoWeek("2023-W02") # True
    iw > IsoWeek("2023-W02") # False
    ```

- Addition with `int` and `timedelta` types:

    ```py
    iw + 1 # IsoWeek("2023-W02")
    iw + timedelta(weeks=2) # IsoWeek("2023-W03")
    ```

- Subtraction with `int`, `timedelta` and `IsoWeek` types:

    ```py
    iw - 1 # IsoWeek("2022-W52")
    iw - timedelta(weeks=2) # IsoWeek("2022-W51")
    iw - IsoWeek("2022-W52") # 1
    ```

- Range between (iso)weeks:

    ```py
    tuple(IsoWeek.range(start="2023-W01", end="2023-W07", step=2, inclusive="both", as_str=True))  # ('2023-W01', '2023-W03', '2023-W05', '2023-W07')
    ```

- Weeksout generator:

    ```py
    tuple(iw.weeksout(3)) # ('2023-W02', '2023-W03', '2023-W04')
    ```

- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value:

    ```py
    date(2023, 1, 1) in iw # False
    date(2023, 1, 2) in iw # True

    iw.contains((IsoWeek("2023-W01"), date(2023, 1, 1), date(2023, 1, 2))) # (True, False, True)
    ```

### Working with _custom offset_

The "standard" ISO Week starts on Monday and end on Sunday. However there are cases in which one may require a _shift_ in the starting day of a week.

The `IsoWeek` class has one class attribute called `offset_` which can be used to define a custom offset for the week.

```py title="custom offset"
class MyWeek(IsoWeek):
    """
    MyWeek class is a IsoWeek with custom offset of -2 days.
    Therefore MyWeek starts the Saturday before the "standard" ISO week.
    """
    offset_ = timedelta(days=-2)
```

This is all that is required to work with a custom shifted week.

## pandas & polars utils

[`pandas_utils`](../../api/pandas/) and [`polars_utils`](../../api/polars/) modules provide the same API to work with `pandas.Series` and `polars.Series`/`polars.Expr` respectively.

```py title="pandas"
import pandas as pd
from datetime import date, timedelta
from iso_week.pandas_utils import datetime_to_isoweek, isoweek_to_datetime

s_date = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
datetime_to_isoweek(
    series=s_date,
    offset=pd.Timedelta(days=1)
    ).to_list()  # ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']

s_iso = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
isoweek_to_datetime(
    series=s_iso,
    offset=pd.Timedelta(days=1)
    )
'''
0   2022-12-27
1   2023-01-03
2   2023-01-10
dtype: datetime64[ns]
'''
```

```py title="polars"
import polars as pl
from datetime import date, timedelta
from iso_week.polars_utils import datetime_to_isoweek, isoweek_to_datetime

s_date = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
datetime_to_isoweek(s_date, offset=timedelta(days=1))
# ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']

s_iso = pl.Series(["2022-W52", "2023-W01", "2023-W02"])
isoweek_to_datetime(
    series=s_iso,
    offset=timedelta(days=1)
    )
'''
date
2022-12-27
2023-01-03
2023-01-10
'''
```
