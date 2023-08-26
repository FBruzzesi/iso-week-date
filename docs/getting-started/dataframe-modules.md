# Dataframe modules

[`pandas_utils`](../api/pandas.md) and [`polars_utils`](../api/polars.md) modules provide the same API to work with `pandas.Series` and `polars.Series`/`polars.Expr` respectively.

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
