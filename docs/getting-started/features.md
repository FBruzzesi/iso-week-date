# Features

This is a high level view of the features provided by the `iso-week-date` package.

## [`IsoWeek``](../../api/isoweek/) and [`IsoWeekDate`](../../api/isoweekdate/) classes

The `IsoWeek` and `IsoWeekDate` classes both provide the following functionalities:

- Parsing from string, date and datetime objects
- Conversion to string, date and datetime objects
- Comparison operations between `IsoWeek` (resp `IsoWeekDate`) objects
- Addition with `int` and `timedelta` types
- Subtraction with `int`, `timedelta` and `IsoWeek` (resp `IsoWeekDate`) types
- Range between two `IsoWeek` (resp `IsoWeekDate`) objects

In addition, the `IsoWeek` class provides the following functionalities:

- Weeksout generation
- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value

while the `IsoWeekDate` class provides the following functionalities:

- Daysout generation

## pandas & polars utils

[`pandas_utils`](../../api/pandas/) and [`polars_utils`](../../api/polars/) modules provide functionalities to work with and move back and forth with series of Iso Week dates in _YYYY-WNN_ format.

In specific both modules implements the following functionalities:

- `datetime_to_isoweek` to convert a series of datetime objects to a series of Iso Week strings
- `isoweek_to_datetime` to convert a series of Iso Week strings to a series of datetime objects
- `is_isoweek_series` to check if a string series values match the ISO Week format
