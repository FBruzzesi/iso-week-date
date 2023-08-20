# Features

This is a high level view of the features provided by the `iso-week` package.

## [`IsoWeek` class](../../api/isoweek/)

The `IsoWeek` class provides the following functionalities:

- Parsing from string, date and datetime objects
- Conversion to string, date and datetime objects
- Comparison operations between `IsoWeek` objects
- Addition with `int` and `timedelta` types
- Subtraction with `int`, `timedelta` and `IsoWeek` types
- Range between (iso)weeks
- Weeksout generation
- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value

## pandas & polars utils

[`pandas_utils`](../../api/pandas/) and [`polars_utils`](../../api/polars/) modules provide functionalities to work with and move back and forth with series of Iso Week dates in _YYYY-WNN_ format.

In specific both modules implements the following functionalities:

- `datetime_to_isoweek` to convert a series of datetime objects to a series of Iso Week strings
- `isoweek_to_datetime` to convert a series of Iso Week strings to a series of datetime objects
