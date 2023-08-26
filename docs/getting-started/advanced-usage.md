# Advanced usage

## [`BaseIsoWeek`](../api/baseisoweek.md)

`BaseIsoWeek` is an abstract base class that provides:

- Template for functionalities that need to be implemented the shared functionalities to work with ISO Week date in different formats.

It is not meant to be used directly, but it is the base class for both [`IsoWeek`](../api/isoweek.md) and [`IsoWeekDate`](../api/isoweekdate.md) classes.

The functionalities provided by the `BaseIsoWeek` class directly are:

- Validation method(s) to check if a string matches a certain format/pattern
- `range` method to generate a range between a start and end isoweek(date)s.
- Properties such as `year` and `week` to access the year and week of the instance.


- All the comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`)
- Conversion methods (`to_string`, `to_compact`, `to_date`, `to_datetime`)
- Parsing methods (`from_string`, `from_compact`, `from_date`, `from_datetime`)
