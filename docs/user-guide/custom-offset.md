# Weeks that do not start on Monday

The "standard" ISO week starts on Monday and ends on Sunday. Retail, payroll and reporting calendars often do not: a
week may start on Saturday, or on Sunday, or on whatever day the business decided years ago.

This page shows how to shift the start of the week with a custom offset. For the reasoning behind the design, see
[why iso-week-date?](why-iso-week-date.md).

## Shift the start of an `IsoWeek`

Subclass [`IsoWeek`](../api/isoweek.md) and set the `offset_` class attribute to a `timedelta`:

```python exec="true" source="material-block" session="offset" result="python"
from datetime import date, timedelta

from iso_week_date import IsoWeek


class SaturdayWeek(IsoWeek):
    """An IsoWeek whose weeks start on the Saturday before the standard ISO week."""

    offset_ = timedelta(days=-2)
```

That is all that is required. A negative offset moves the start of the week _earlier_, a positive one moves it _later_.

The same date now maps to a different week depending on which class you ask:

```python exec="true" source="material-block" session="offset" result="python"
reference_day = date(2023, 1, 1)  # a Sunday

print(IsoWeek.from_date(reference_day))
print(SaturdayWeek.from_date(reference_day))
```

And the same week label now starts on a different date:

```python exec="true" source="material-block" session="offset" result="python"
print(IsoWeek("2023-W01").nth(1))
print(SaturdayWeek("2023-W01").nth(1))
```

Everything else keeps working as before, offset included:

```python exec="true" source="material-block" session="offset" result="python"
print(SaturdayWeek("2023-W01").days)
```

## Shift the start of an `IsoWeekDate`

[`IsoWeekDate`](../api/isoweekdate.md) works the same way:

```python exec="true" source="material-block" session="offset" result="python"
from iso_week_date import IsoWeekDate


class SaturdayWeekDate(IsoWeekDate):
    """An IsoWeekDate whose weeks start on the Saturday before the standard ISO week."""

    offset_ = timedelta(days=-2)


print(SaturdayWeekDate.from_date(date(2023, 1, 1)))
```

## Operations stay within a class

Comparisons and arithmetic require both operands to be instances of the **same class**. Since `offset_` is a class
attribute, this also guarantees they share the same offset, so you cannot accidentally compare two weeks that mean
different spans of days:

```python exec="true" source="material-block" result="python" session="offset" result="python"
try:
    SaturdayWeek("2023-W01") < IsoWeek("2023-W02")
except TypeError as e:
    print(f"TypeError: {e}")
```

Equality returns `False` rather than raising:

```python exec="true" source="material-block" session="offset" result="python"
print(SaturdayWeek("2023-W01") == IsoWeek("2023-W01"))
```

!!! warning "Same offset is not enough"
    Two _different_ classes that happen to share the same `offset_` value still refuse to be compared: the check is on
    the class, not on the offset value. Define one class per business calendar and reuse it.

## Offsets on dataframe series

The dataframe helpers take the offset as a plain `offset` argument instead of a subclass, using the same sign
convention:

```python exec="true" source="material-block" session="offset" result="python"
import polars as pl

from iso_week_date.polars_utils import datetime_to_isoweek

series = pl.date_range(date(2023, 1, 1), date(2023, 1, 3), interval="1d", eager=True)

print(datetime_to_isoweek(series).to_list())
print(datetime_to_isoweek(series, offset=timedelta(days=-2)).to_list())
```

See [working with dataframes](dataframe-modules.md) for the full set of series helpers.
