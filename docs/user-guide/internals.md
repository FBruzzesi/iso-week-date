# Internals

## [`BaseIsoWeek`](../api/baseisoweek.md)

`BaseIsoWeek` is an abstract base class that provides:

- Template for functionalities that need to be implemented the shared functionalities to work with ISO Week date in different formats.

It is not meant to be used directly, but it is the base class for both [`IsoWeek`](../api/isoweek.md) and [`IsoWeekDate`](../api/isoweekdate.md) classes.

The functionalities provided by the `BaseIsoWeek` class directly are:

- [Validation method(s)](../api/baseisoweek.md#iso_week_date.base.BaseIsoWeek.validate) to check if a string matches a certain format/pattern
- [`range`](../api/baseisoweek.md#iso_week_date.base.BaseIsoWeek.range) method to generate a range between a start and end isoweek(date)s.
- Properties such as [`year`](../api/baseisoweek.md#iso_week_date.base.BaseIsoWeek.year) and [`week`](../api/baseisoweek.md#iso_week_date.base.BaseIsoWeek.week) to access the year and week number of the instance as `int`.

Other functionalities are provided by mean of [Mixin's](../api/mixins.md):

- Parsing methods (`from_string`, `from_compact`, `from_date`, `from_datetime`) (via [`ParserMixin`](../api/mixins.md#iso_week_date.mixin.ParserMixin))
- Conversion methods (`to_string`, `to_compact`, `to_date`, `to_datetime`) (via [`ConverterMixin`](../api/mixins.md#iso_week_date.mixin.ConverterMixin))
- All the comparison operators (`==`, `!=`, `<`, `<=`, `>`, `>=`) (via [`ComparatorMixin`](../api/mixins.md#iso_week_date.mixin.ComparatorMixin))
