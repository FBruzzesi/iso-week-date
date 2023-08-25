# Quickstart

In this section we will see how to work with the different modules of the library.

For a high level overview of the features provided by the `iso-week-date` package, see [Features](../features) sections.

For a detailed description of the API, see the API Reference section.

## [`BaseIsoWeek`](../../api/baseisoweek)

`BaseIsoWeek` is an abstract class that provides the base functionalities to work with ISO Week date in different formats.

It is not meant to be used directly, but it is the base class for both [`IsoWeek`](../../api/isoweek) and [`IsoWeekDate`](../../api/isoweekdate) classes.

The functionalities provided by the `BaseIsoWeek` class are:

- Validation method to check if a string matches a certain format/pattern
- `range` method to generate a range between a start and end isoweek(date)s.
- Properties such as `year` and `week` to access the year and week of the instance.

- All the comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`)
- Conversion methods (`to_string`, `to_compact`, `to_date`, `to_datetime`)
- Parsing methods (`from_string`, `from_compact`, `from_date`, `from_datetime`)

To exemplify these functionalities, check the next section where we showcase them within the `IsoWeek` class, yet they are available in the `IsoWeekDate` class as well.

## [`IsoWeek`](../../api/isoweek)

The `IsoWeek` class is accessible from the top-level module:

```py
from datetime import date, datetime, timedelta
from iso_week_date import IsoWeek
```

An instance can be initialized from parsing multiple types:

- `str` in _YYYY-WNN_ format

    ```py
    iw = IsoWeek("2023-W01")
    iw.value, iw.offset # "2023-W01", datetime.timedelta(0)
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
    iw.to_string() # "2023-W01"
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

- Addition with `int` (interpreted as weeks) and `timedelta` types:

    ```py
    iw + 1 # IsoWeek("2023-W02")
    iw + timedelta(weeks=2) # IsoWeek("2023-W03")
    ```

- Subtraction with `int` (interpreted as weeks), `timedelta` and `IsoWeek` (difference in weeks):

    ```py
    iw - 1 # IsoWeek("2022-W52")
    iw - timedelta(weeks=2) # IsoWeek("2022-W51")
    iw - IsoWeek("2022-W52") # 1
    ```

- Range between isoweeks:

    ```py
    tuple(IsoWeek.range(start="2023-W01", end="2023-W07", step=2, inclusive="both", as_str=True))
    # ('2023-W01', '2023-W03', '2023-W05', '2023-W07')
    ```

- **Weeksout** generator:

    ```py
    tuple(iw.weeksout(3)) # ('2023-W02', '2023-W03', '2023-W04')
    ```

- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value:

    ```py
    date(2023, 1, 1) in iw # False
    date(2023, 1, 2) in iw # True

    iw.contains((IsoWeek("2023-W01"), date(2023, 1, 1), date(2023, 1, 2))) # (True, False, True)
    ```

## [`IsoWeekDate`](../../api/isoweekdate)

Similarly, the `IsoWeekDate` class is accessible from the top-level module:

```py
from iso_week_date import IsoWeekDate
```

and an instance can be initialized from parsing multiple types using the same methods as the `IsoWeek` class:

- `str` in _YYYY-WNN-D_ format
- `str` in compact format _YYYYWNND_
- `date` or `datetime` objects

Once initialized, the instance provides the following methods:

- _properties_ to access year, week and days of the week:

    ```py
    iwd = IsoWeekDate("2023-W01-1")
    iwd.year # 2023
    iwd.week # 1
    iwd.day # 1
    iwd.isoweek # "2023-W01"
    ```

- Conversion to multiple types (same as `IsoWeek`)
- Comparison operations (same as `IsoWeek` due to `BaseIsoWeek` inheritance):

    ```py
    iwd == IsoWeekDate("2023-W01-1") # True
    iwd == IsoWeekDate("2023-W01-2") # False
    iwd < IsoWeekDate("2023-W02-3") # True
    iw > IsoWeekDate("2023-W02-4") # False
    ```

- Addition with `int` (interpreted as days) and `timedelta` types:

    ```py
    iwd + 1 # IsoWeekDate("2023-W01-2")
    iwd + timedelta(weeks=2) # IsoWeekDate("2023-W03-1")
    ```

- Subtraction with `int` (interpreted as days), `timedelta` and `IsoWeek` (difference in days) types:

    ```py
    iwd - 1 # IsoWeekDate("2022-W52-1")
    iwd - timedelta(weeks=2) # IsoWeekDate("2022-W51-1")
    iwd - IsoWeekDate("2022-W52-3") # 5
    ```

- Range between (iso)weekdates:

    ```py
    tuple(IsoWeekDate.range(start="2023-W01-1", end="2023-W02-7", step=3, inclusive="both", as_str=True))  # ('2023-W01-1', '2023-W01-4', '2023-W01-7', '2023-W02-3', '2023-W02-6')

    ```

- **Daysout** generator:

    ```py
    tuple(iwd.daysout(3)) # ('2023-W01-2', '2023-W01-3', '2023-W01-4')
    ```

## Working with _custom offset_

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
from iso_week_date.pandas_utils import datetime_to_isoweek, isoweek_to_datetime, is_isoweek_series

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

is_isoweek_series(s_iso)  # True
is_isoweek_series(s_iso + "abc")  # False
```

```py title="polars"
import polars as pl
from datetime import date, timedelta
from iso_week_date.polars_utils import datetime_to_isoweek, isoweek_to_datetime, is_isoweek_series

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

is_isoweek_series(s_iso)  # True
is_isoweek_series(s_iso + "abc")  # False
```
