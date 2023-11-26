# Dataframe modules

The [`pandas_utils`](../api/pandas.md) and [`polars_utils`](../api/polars.md) modules provide the same API to work with `pandas.Series` and `polars.Series`/`polars.Expr` respectively.

The utilities come in two _flavors_: [functions](#functions) and [extensions](#extensions).

## Functions

The functions approach takes the series/expr as an argument and returns a new series/expr.

Available functions are:

- `datetime_to_isoweek` and `datetime_to_isoweekdate`: converts a `datetime` series to an ISO week (date) series.
- `isoweek_to_datetime` and `isoweekdate_to_datetime`: converts an ISO week date series to a `datetime` series.
- `is_isoweek_series` and `is_isoweekdate_series`: checks if a series is an ISO week (date) series.

```py title="pandas"
import pandas as pd
from datetime import date, timedelta
from iso_week_date.pandas_utils import datetime_to_isoweek, isoweek_to_datetime, is_isoweek_series

s_date = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
datetime_to_isoweek(series=s_date, offset=pd.Timedelta(days=1)).to_list()
# ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']

s_iso = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
isoweek_to_datetime(series=s_iso, offset=pd.Timedelta(days=1))
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
from iso_week_date.polars_utils import datetime_to_isoweekdate, isoweekdate_to_datetime, is_isoweekdate_series

s_date = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d", eager=True)
datetime_to_isoweekdate(s_date, offset=timedelta(days=1)).to_list()
# ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']

s_iso = pl.Series(["2022-W52-1", "2023-W01-2", "2023-W02-7"])
isoweekdate_to_datetime(series=s_iso,offset=timedelta(days=1))
'''
date
2022-12-27
2023-01-04
2023-01-16
'''

is_isoweekdate_series(s_iso)  # True
is_isoweekdate_series(s_iso + "abc")  # False
```

## Extensions

On the other hand the extensions[^1] approach extends the `pandas.Series` and `polars.Series`/`polars.Expr` classes with new methods.

The extensions are available through the `iwd` (isoweekdate) namespace, and the methods available are the same as the functions.

"Translating" the previous examples to extensions:

```py title="pandas"
import pandas as pd
from iso_week_date.pandas_utils import SeriesIsoWeek  # noqa: F401 (1)

s_date = pd.Series(pd.date_range(date(2023, 1, 1), date(2023, 1, 10), freq="1d"))
s_date.iwd.datetime_to_isoweek(offset=pd.Timedelta(days=1)).to_list()
# ['2022-W52', '2022-W52', '2023-W01',..., '2023-W01', '2023-W02']

s_iso = pd.Series(["2022-W52", "2023-W01", "2023-W02"])
s_iso.iwd.isoweek_to_datetime(offset=pd.Timedelta(days=1))
'''
0   2022-12-27
1   2023-01-03
2   2023-01-10
dtype: datetime64[ns]
'''

s_iso.iwd.is_isoweek(s_iso)  # True
s_iso.iwd.is_isoweek(s_iso + "abc")  # False
```

1. The import of `SeriesIsoWeek` is needed to register the extensions.

    _noqa: F401_ is added to avoid the linter(s) warning about the unused import.

```py title="polars"
import polars as pl
from iso_week_date.polars_utils import SeriesIsoWeek  # noqa: F401 (1)

s_date = pl.date_range(date(2023, 1, 1), date(2023, 1, 10), interval="1d")
s_date.iwd.datetime_to_isoweekdate(offset=timedelta(days=1)).to_list()
# ['2022-W52-6', '2022-W52-7', '2023-W01-1',..., '2023-W01-7', '2023-W02-1']

s_iso = pl.Series(["2022-W52-1", "2023-W01-2", "2023-W02-7"])
s_iso.iwd.isoweekdate_to_datetime(offset=timedelta(days=1))
'''
date
2022-12-27
2023-01-04
2023-01-16
'''

s_iso.iwd.is_isoweekdate()  # True
(s_iso + "abc").iwd.is_isoweekdate_series()  # False
```

1. The import of `SeriesIsoWeek` is needed to register the extensions.

    _noqa: F401_ is added to avoid the linter(s) warning about the unused import.

!!! note
    Polars extension is valid for both `Series` and `Expr` classes.

    This means that it is possible to use the extension in any [polars context](https://pola-rs.github.io/polars/user-guide/concepts/contexts/) in which it would be possible to use an expression.

[^1]: Extending [pandas](https://pandas.pydata.org/docs/development/extending.html) and [polars](https://pola-rs.github.io/polars/py-polars/html/reference/api.html)
