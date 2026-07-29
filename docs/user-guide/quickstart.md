# Quickstart

This is a hands-on lesson: by the end of it you will have written a small helper that turns any date into an ISO week
label and builds the rolling window of weeks a weekly report needs.

Follow the steps in order and run every snippet. Each one builds on the previous one, and every output on this page is
produced by actually running the code.

If you already know the library and are looking for a specific method, go to the [API tour](api-tour.md) instead.

## What you will build

A `report_weeks` helper that answers: _"which ISO weeks does my 4-week report cover, and which calendar dates fall in
each of them?"_

## Step 1: install the library

```bash
python -m pip install iso-week-date
```

Nothing else is needed for this lesson. See [installation](../installation.md) for the optional extras.

## Step 2: turn a date into a week

Import [`IsoWeek`](../api/isoweek.md) and build one from a date:

```python exec="true" source="material-block" session="quickstart" result="python"
from datetime import date

from iso_week_date import IsoWeek

reference_day = date(2026, 3, 10)
week = IsoWeek.from_date(reference_day)

print(week)
```

`week` is now an object, not a string, but it carries the canonical **YYYY-WNN** label. Its parts are available as
integers:

```python exec="true" source="material-block" session="quickstart" result="python"
print(week.year, week.week, week.quarter)
```

!!! tip "Why not `strftime`?"
    You may be used to writing `some_date.strftime("%Y-W%V")`. That is subtly wrong at year boundaries: `%Y` is the
    calendar year while `%V` is the _ISO_ week number, and the two disagree during the last and first days of a year.
    [Why iso-week-date?](why-iso-week-date.md) shows the failure and explains it.

## Step 3: ask the week which dates it covers

A week knows the seven dates it spans:

```python exec="true" source="material-block" session="quickstart" result="python"
for day in week.days:
    print(day)
```

If you only want the boundaries, ask for the _nth_ day (`1` is Monday, `7` is Sunday):

```python exec="true" source="material-block" session="quickstart" result="python"
print(week.nth(1), "->", week.nth(7))
```

And you can test membership with the `in` operator:

```python exec="true" source="material-block" session="quickstart" result="python"
print(reference_day in week)
print(date(2026, 3, 16) in week)
```

## Step 4: move between weeks

Adding an `int` to an `IsoWeek` moves it by that many weeks, and the year boundary is handled for you:

```python exec="true" source="material-block" session="quickstart" result="python"
print(week + 1)
print(week - 13)
```

Subtracting two weeks gives you the distance between them as an `int`:

```python exec="true" source="material-block" session="quickstart" result="python"
print(week - IsoWeek("2026-W08"))
```

This is the reason to use objects rather than strings: no conversion to `date` and back, and no arithmetic on the week
number that breaks when a year has 53 weeks.

## Step 5: build the report window

[`IsoWeek.range`](../api/isoweek.md#iso_week_date.isoweek.IsoWeek.range) generates every week between two endpoints.
Combine it with what you learned in step 4 to get the last four weeks:

```python exec="true" source="material-block" session="quickstart" result="python"
window = tuple(IsoWeek.range(start=week - 3, end=week, inclusive="both", as_str=True))

print(window)
```

`as_str=True` gives you plain strings, which is what you usually want for a report label or a dataframe column.

## Step 6: go down to the day

When a week is too coarse, [`IsoWeekDate`](../api/isoweekdate.md) works the same way but with a weekday component,
and `int` arithmetic moves it by **days** instead of weeks:

```python exec="true" source="material-block" session="quickstart" result="python"
from iso_week_date import IsoWeekDate

day = IsoWeekDate.from_date(reference_day)

print(day, "| weekday:", day.weekday, "| its week:", day.isoweek)
print(day + 1)
```

## Step 7: put it together

```python exec="true" source="material-block" session="quickstart" result="python"
def report_weeks(reference: date, n_weeks: int = 4) -> dict[str, tuple[date, date]]:
    """Map each ISO week label in the report window to its first and last calendar day."""
    last_week = IsoWeek.from_date(reference)
    weeks = IsoWeek.range(
        start=last_week - (n_weeks - 1), end=last_week, inclusive="both", as_str=False
    )
    return {w.to_string(): (w.nth(1), w.nth(7)) for w in weeks}


for label, (first, last) in report_weeks(date(2026, 3, 10)).items():
    print(f"{label}: {first} -> {last}")
```

That is a complete, correct weekly-report window in a handful of lines, with no `strftime` format strings and no manual
year-boundary handling.

## What you learned

* `IsoWeek.from_date` and `IsoWeekDate.from_date` build objects from dates.
* `.year`, `.week`, `.quarter`, `.weekday` and `.isoweek` expose the parts.
* `.days`, `.nth()` and the `in` operator relate a week back to calendar dates.
* `int` arithmetic moves by weeks on `IsoWeek` and by days on `IsoWeekDate`.
* `.range()` generates windows, with `as_str` choosing between objects and strings.

## Next steps

* [API tour](api-tour.md): every parsing, conversion, comparison and arithmetic option, with examples.
* [Working with dataframes](dataframe-modules.md): the same operations on whole _pandas_ and _polars_ series.
* [Working with Pydantic](pydantic.md): validate ISO week strings on your model fields.
* [Weeks that do not start on Monday](custom-offset.md): shift the start of the week with a custom offset.
* [Why iso-week-date?](why-iso-week-date.md): the reasoning behind the design.
