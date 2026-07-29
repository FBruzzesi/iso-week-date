# Why iso-week-date?

This page explains the reasoning behind the library: which problem it solves, why it represents weeks the way it does,
and where its design draws its boundaries. It is background reading rather than instructions. If you want to get
something working, start with the [quickstart](quickstart.md).

## The problem: ISO week strings are everywhere and easy to get wrong

Weekly is the natural grain for a lot of reporting: sales, planning, forecasting, payroll. So ISO week labels such as
`2023-W01` end up as keys in data warehouses, as column values in dataframes, as identifiers in APIs. They are strings,
and they look harmless.

The standard library can produce them, and this is where the first trap is:

```python exec="true" source="material-block" session="why" result="python"
from datetime import date

boundary = date(2025, 12, 29)  # a Monday

print(boundary.strftime("%Y-W%V"))  # looks right, is wrong
print(boundary.strftime("%G-W%V"))  # correct
```

`%Y` is the **calendar** year while `%V` is the **ISO** week number, and the two disagree for the handful of days where
an ISO week straddles New Year. December 29th 2025 belongs to the first ISO week of 2026, so `%Y-W%V` reports it as week
1 of 2025: a label that is a full year away from the truth, produced by code that passes every test not run in late
December.

The correct directive is `%G`, the ISO year. It is one character away from the wrong answer, and the wrong answer is the
one that looks familiar.

## Why not just use `date`?

Because a week is a **span**, not a point. Representing `2023-W01` as `date(2023, 1, 2)` silently answers a different
question, and the code that does the round trip has to keep re-deciding which day stands for the week, whether the
boundaries are inclusive, and what happens at year ends. Those decisions get re-made, differently, at each call site.

There is a second reason: the labels are already strings in the systems you are integrating with. Parsing them to
`date`, computing, and formatting back means every operation pays for two conversions and two chances to use the wrong
format directive.

So `IsoWeek` and `IsoWeekDate` keep the string as the canonical value and put the calendar logic behind methods.
Conversion to `date` and `datetime` is available when you need it, and explicit about which day it means.

## Why arithmetic on the objects rather than on the number

The other tempting shortcut is to treat the week number as an integer and add to it. This breaks because years do not
all have the same number of weeks: 2015, 2020, 2026 and 2032 have 53, most others have 52.

```python exec="true" source="material-block" session="why" result="python"
from iso_week_date import IsoWeek

print(IsoWeek("2020-W52") + 1)  # 2020 has 53 weeks
print(IsoWeek("2021-W52") + 1)  # 2021 has 52, so this rolls over
```

Naive `week + 1` arithmetic would produce `2021-W53`, a week that does not exist. The classes route arithmetic through
the calendar, so the rollover is handled once, in one place.

## Why string comparison is enough for ordering

Ordering compares the string values directly, which is not a shortcut but a property of the format: the fields run from
most to least significant, each is zero-padded to a fixed width, and the literal `W` is constant. Lexicographic order
and chronological order therefore coincide, for every year the format admits (`0001` to `9999`).

This is why comparison is cheap and why sorting a column of ISO week strings in a dataframe, with no parsing at all,
gives the right answer.

## Why the offset is a class attribute

Business calendars often shift the start of the week. The library models that with the `offset_` **class** attribute,
which means you declare a subclass per calendar rather than passing an offset to each call.

The reason is type safety. A week starting on Saturday and a week starting on Monday are not interchangeable, even when
they carry the same label: `2023-W01` means a different span of days in each. Making the offset part of the type turns
mixing them into a `TypeError` at the point of use, instead of a plausible-looking number in a report:

```python exec="true" source="material-block" result="python" session="why" result="python"
from datetime import timedelta


class SaturdayWeek(IsoWeek):
    offset_ = timedelta(days=-2)


try:
    SaturdayWeek("2023-W01") < IsoWeek("2023-W02")
except TypeError as e:
    print(f"TypeError: {e}")
```

The cost of this choice is that you cannot vary the offset per call on the class API, and that two classes sharing an
offset value still will not compare. That is deliberate: the class _is_ the calendar. The dataframe helpers, which
operate on values rather than on typed objects, do take a per-call `offset` argument instead.

See [weeks that do not start on Monday](custom-offset.md) for how to use this.

## Why validation is stricter than the regex

The package exposes regex patterns (`ISOWEEK_PATTERN`, `ISOWEEKDATE_PATTERN`) and also does real validation when you
instantiate a class. These are not the same check, and the difference matters.

A regex can confirm the _shape_ **YYYY-WNN**, and can constrain the week number to `01`-`53`. It cannot know that 2023
had only 52 weeks, because that depends on the year. So `2023-W53` matches the pattern and is still not a real week.

```python exec="true" source="material-block" result="python" session="why" result="python"
from iso_week_date import ISOWEEK_PATTERN

print(bool(ISOWEEK_PATTERN.match("2023-W53")))  # shape is fine

try:
    IsoWeek("2023-W53")
except ValueError as e:
    print(f"ValueError: {e}")
```

Use the patterns for cheap shape checks on large volumes of strings; instantiate the classes when you need the label to
be a week that actually existed. [Working with Pydantic](pydantic.md) shows both, and when each is the right trade.

## When this library is not the right tool

* **You need general calendar arithmetic.** Months, quarters as first-class objects, business days, holidays: use
    `dateutil`, `pandas` offsets, or a dedicated business-calendar library.
* **You need timezone-aware instants.** These classes model dates, not moments. Convert at the edges.
* **Your weeks are not ISO weeks at all.** A "week 1 starts on January 1st" convention is a different scheme, not an
    offset of this one.

## Further reading

* [ISO week date on Wikipedia](https://en.wikipedia.org/wiki/ISO_week_date)
* [`strftime` format codes](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes), where
    `%G`, `%V` and `%u` are documented
