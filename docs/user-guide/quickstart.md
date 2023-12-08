# Quickstart

In this section we will see how to work with the different modules of the library.

For a high level overview of the features provided by the `iso-week-date` package, see the [features](features.md) section.

For a detailed description of the API, see the API Reference section.

## Common functionalities

As mentioned in the [features](features.md) section, the [`IsoWeek`](../api/isoweek.md) and [`IsoWeekDate`](../api/isoweekdate.md) classes share a lot of functionalities and methods, since they both inherit from the same abstract base class, namely [`BaseIsoWeek`](../api/baseisoweek.md).

Therefore we will focus first on the common functionalities, and then showcase the unique features of each class.

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

=== "`from_values`"

    ```py
    iw = IsoWeek.from_values(year=2023, week=1)  # IsoWeek("2023-W01")
    iwd = IsoWeekDate.from_values(2023, 1, weekday=1)  # IsoWeekDate("2023-W01-1")
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

=== "`to_values`"

    ```py
    iw.to_values()  # (2023, 1)  # (year, weeknumber)
    iwd.to_values()  # (2023, 1, 1)  # (year, weeknumber, weekday)
    ```

!!! warning "IsoWeek to date/datetime"
    Remark that [`IsoWeek.to_date`](../api/isoweek.md#iso_week_date.isoweek.IsoWeek.to_date) and [`IsoWeek.to_datetime`](../api/isoweek.md#iso_week_date.isoweek.IsoWeek.to_datetime) methods accept an optional `weekday` argument, which defaults to `1` (first weekday), and can be used to get the date of a specific day of the week:

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

### Addition and subtraction

Classes inheriting from `BaseIsoWeek` have to implement:

- addition with `int` and `timedelta` types
- subtraction with `int`, `timedelta` and `Self` types (1)
{ .annotate }

    1. The `Self` type is the class itself, i.e. `IsoWeek` for `IsoWeek` and `IsoWeekDate` for `IsoWeekDate`.

!!! danger "operation with `int`s"
    The two classes treat `int` type differently when performing addition and subtraction operations.
    Namely:

    - For `IsoWeek` it is interpreted as **weeks**
    - For `IsoWeekDate` it is interpreted as **days**

=== "Addition `+`"

    ```py
    iw + 1  # IsoWeek("2023-W02")
    iw + timedelta(weeks=2)  # IsoWeek("2023-W03")

    tuple(iw + (1,2,3))  # (IsoWeek("2023-W02"), IsoWeek("2023-W03"), IsoWeek("2023-W04"))

    iwd + 1  # IsoWeekDate("2023-W01-2")
    iwd + timedelta(days=2)  # IsoWeekDate("2023-W01-3")
    ```

=== "Subtraction `-`"

    ```py
    iw - 1  # IsoWeek("2022-W52")
    iw - timedelta(weeks=2)  # IsoWeek("2022-W51")
    iw - IsoWeek("2022-W52")  # 1

    tuple(iw - (1,2,3))  # (IsoWeek("2022-W52"), IsoWeek("2022-W51"), IsoWeek("2022-W50"))

    iwd - 1 # IsoWeekDate("2022-W52-7")
    iwd - timedelta(days=2) # IsoWeekDate("2022-W52-6")
    iwd - IsoWeekDate("2022-W52-3") # 5
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

## [`IsoWeek`](../api/isoweek.md) specific

In addition to the common functionalities, the `IsoWeek` class provides additional properties and methods.

### Days property

The `days` property returns a tuple of `date`s in the given week:

```py
iw.days # (date(2023, 1, 2), date(2023, 1, 3), ..., date(2023, 1, 8))
```

### Weeksout method

The `weeksout` method generates a list of weeks that are _n\_weeks_ after the given week:

```py
tuple(iw.weeksout(3)) # ('2023-W02', '2023-W03', '2023-W04')
tuple(iw.weeksout(6, step=2, as_str=False)) # (IsoWeek('2023-W02'), IsoWeek('2023-W04'), IsoWeek('2023-W06'))
```

### Contains method

The `contains` method checks if a (iterable of) week(s), string(s) and/or date(s) is contained in the given week:

```py
iw.contains("2023-W01") # True
iw.contains(date(2023, 1, 1)) # False

iw.contains((IsoWeek("2023-W01"), date(2023, 1, 1), date(2023, 1, 2))) # (True, False, True)
```

This is achieved by implementing the `__contains__` method, which is called when using the `in` operator:

```py
date(2023, 1, 1) in iw # False
date(2023, 1, 2) in iw # True
```

## [`IsoWeekDate`](../api/isoweekdate.md) specific

In a similar fashion, `IsoWeekDate` class provides additional properties and methods.

### Properties

We have two additional properties:

- `isoweek` returns the ISO Week of the given date (as string)
- `day`: returns the weekday as integer

=== "`isoweek`"

    ```py
    iwd.isoweek  # "2023-W01"
    ```

=== "`day`"

    ```py
    iwd.day  # 1
    ```

### Daysout method

The `daysout` method generates a list of dates that are _n\_days_ after the given date:

```py
tuple(iwd.daysout(3)) # ('2023-W01-2', '2023-W01-3', '2023-W01-4')
tuple(iwd.daysout(6, step=3, as_str=False))
# (IsoWeekDate('2023-W01-2'), IsoWeekDate('2023-W01-5'), IsoWeekDate('2023-W02-1'))
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

Now the same date may be "mapped" to different ISO Weeks depending on the offset:

```py
_date = date(2023, 1, 1)
IsoWeek.from_date(_date)  # IsoWeek(2022-W52)
MyWeek.from_date(_date)  # MyWeek(2023-W01)
```

Or we can see that the same week starts on different dates:

```py
IsoWeek("2023-W01").nth(1)  # date(2023, 1, 2)
MyWeek("2023-W01").nth(1)  # date(2022, 12, 31)
```

Similarly we can define a custom offset for the `IsoWeekDate` class:

```py title="custom offset"
class MyWeekDate(IsoWeekDate):
    """
    MyWeekDate class is a IsoWeekDate with custom offset of -2 days.
    Therefore MyWeekDate starts the Saturday before the "standard" ISO week.
    """
    offset_ = timedelta(days=-2)
```

All the functionalities still work as expected, just keep in mind that comparisons and arithmetic operations will be available only on instances with the same offset.
