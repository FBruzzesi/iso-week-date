# Features

This is a high level overview of the features provided by the `iso-week-date` package.

## [`IsoWeek`](../api/isoweek.md) and [`IsoWeekDate`](../api/isoweekdate.md) classes

The `IsoWeek` and `IsoWeekDate` classes both provide the following functionalities:

- Parsing from string, date and datetime objects
- Conversion to string, date and datetime objects
- Comparison operations between `IsoWeek` (resp `IsoWeekDate`) objects
- Addition with `int`, `timedelta`, and  `Iterable[int | timedelta]` types
- Subtraction with `int`, `timedelta`, `IsoWeek` (resp `IsoWeekDate`), and `Iterable[int | timedelta | IsoWeek]` types
- Range between two `IsoWeek` (resp. `IsoWeekDate`) objects
- `__next__` method to generate the next `IsoWeek` (resp. `IsoWeekDate`) object

`IsoWeek` unique methods/features:

- `days` properties that lists the dates in the given week
- `nth` method to get the _nth_ day of the week as date
- `in` operator and `contains` method to check if a (iterable of) week(s), string(s) and/or date(s) is contained in the given week
- `weeksout` method to generate a list of weeks that are _n\_weeks_ after the given week
- Addition and subtraction with `int` defaults to adding/subtracting weeks

`IsoWeekDate` unique methods/features:

- `day` property that returns the weekday as integer
- `isoweek` property that returns the ISO Week of the given date (as string)
- `daysout` method to generate a list of dates that are _n\_days_ after the given date
- Addition and subtraction with `int` defaults to adding/subtracting days

## pandas and polars utils

[`pandas_utils`](../api/pandas.md) and [`polars_utils`](../api/polars.md) modules provide functionalities to work with and move back and forth with _series_ of ISO Week date formats.

In specific both modules implements the following functionalities:

- `datetime_to_isoweek` and `datetime_to_isoweekdate` to convert a series of datetime objects to a series of ISO Week (date) strings
- `isoweek_to_datetime` and `isoweekdate_to_datetime` to convert a series of ISO Week (date) strings to a series of datetime objects
- `is_isoweek_series` and `is_isoweekdate_series` to check if a string series values match the ISO Week (date) format

## Custom offset

One of the main reason for this library to exist is the need and the flexibility to work with custom offsets, i.e. to be able to add/subtract a custom offset (as `timedelta`) to the default ISO Week start and given date, and get a "shifted" week.

This feature is available both in the `IsoWeek` and `IsoWeekDate` classes and the dataframe functionalities.

To check an example see the [working with custom offset](../user-guide/quickstart.md#working-with-custom-offset) section.
