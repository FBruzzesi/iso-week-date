# Quickstart

In this section we will see how to work with the different modules of the library.

For a high level overview of the features provided by the `iso-week-date` package, see the [features](../features) section.

For a detailed description of the API, see the API Reference section.

## Shared functionalities

As mentioned in the [features](../features) section, the [`IsoWeek`](../../api/isoweek) and [`IsoWeekDate`](../../api/isoweekdate) classes share a lot of functionalities and methods, since they both inherit from an abstract base class, namely [`BaseIsoWeek`](../../api/baseisoweek).

Therefore we will focus first on the shared functionalities, and then showcase the unique features of each class.

Both these classes are available from the top-level module:

```py title="imports"
from iso_week_date import IsoWeek, IsoWeekDate
from datetime import date, datetime, timedelta
```

### Parsing from types

An instance can be initialized from parsing multiple types:

=== "directly"

    ```py
    iw = IsoWeek("2023-W01")  # IsoWeek("2023-W01")
    iwd = IsoWeekDate("2023-W01-1")  # IsoWeekDate("2023-W01-1")
    ```
=== "`from_string`"

    ```py
    iw = IsoWeek.from_string("2023-W01")  # IsoWeek("2023-W01")
    iwd = IsoWeekDate.from_string("2023-W01-1")  # IsoWeekDate("2023-W01-1")
    ```

=== "`from_compact`"

    ```py
    iw = IsoWeek.from_compact("2023W01")  # IsoWeek("2023-W01")
    iwd = IsoWeekDate.from_compact("2023W01-1")  # IsoWeekDate("2023-W01-1")
    ```

=== "`from_date`"

    ```py
    iw = IsoWeek.from_date(date(2023, 1, 2))  # IsoWeek("2023-W01")
    iwd = IsoWeekDate.from_date(date(2023, 1, 2))  # IsoWeekDate("2023-W01-1")
    ```

=== "`from_datetime`"

    ```py
    iw = IsoWeek.from_datetime(datetime(2023, 1, 2, 12))  # IsoWeek("2023-W01")
    iwd = IsoWeekDate.from_datetime(datetime(2023, 1, 2, 12))  # IsoWeekDate("2023-W01-1")
    ```

### Conversion to types

On the "opposite" direction, an instance can be converted to multiple types:

=== "`to_string`"

    ```py
    iw.to_string()  # "2023-W01"
    iwd.to_string()  # "2023-W01-1"
    ```

=== "`to_compact`"

    ```py
    iw.to_compact()  # "2023W01"
    iwd.to_compact()  # "2023W011"
    ```

=== "`to_date`"

    ```py
    iw.to_date()  # date(2023, 1, 2)
    iwd.to_date()  # date(2023, 1, 2)
    ```

=== "`to_datetime`"

    ```py
    iw.to_datetime()  # datetime(2023, 1, 2, 0, 0)
    iwd.to_datetime()  # datetime(2023, 1, 2, 0, 0)
    ```

!!! warning "IsoWeek to date/datetime"
    Remark that [`IsoWeek.to_date`](../../api/isoweek/#iso_week_date.isoweek.IsoWeek.to_date) and [`IsoWeek.to_datetime`](../../api/isoweek/#iso_week_date.isoweek.IsoWeek.to_datetime) methods accept an optional `weekday` argument, which defaults to `1` (first weekday), and can be used to get the date of a specific day of the week:

    ```py title="specific weekday"
    iw.to_date(2)  # date(2023, 1, 3)
    iw.to_datetime(3)  # datetime(2023, 1, 4, 0, 0)
    ```

### Comparison operations

Both classes inherit all the comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`), which can be used to compare two instances of the same class:

```py
iw == IsoWeek("2023-W01") # True
iw == iwd # False
iw < IsoWeek("2023-W02") # True
iwd > IsoWeekDate("2023-W02-2") # False
iw < iwd # TypeError
```

To compare two instances we first check that they have the same parent class, then check they share the same offset value, and
finally we compare their string value exploiting the lexical order of the ISO Week date format.

### Properties

=== "`year`"

    ```py
    iw.year  # 2023
    iwd.year  # 2023
    ```

=== "`week`"

    ```py
    iw.week  # 1
    iwd.week  # 1
    ```

### Range method

`BaseIsoWeek` implements a classmethod to create range between two "ISO Week"-like objects that inherit from it and
implement addition with `int` and subtraction between ISO Week objects.

```py title="range classmethod"
tuple(IsoWeek.range(start="2023-W01", end="2023-W07", step=2, inclusive="both", as_str=True))
# ('2023-W01', '2023-W03', '2023-W05', '2023-W07')

tuple(IsoWeekDate.range(start="2023-W01-1", end="2023-W03-3", step=3, inclusive="left", as_str=True))
# ('2023-W01-1', '2023-W01-4', '2023-W01-7', '2023-W02-3', '2023-W02-6', '2023-W03-2')
```

## [`IsoWeek`](../../api/isoweek) specific

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

## [`IsoWeekDate`](../../api/isoweekdate) specific

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
