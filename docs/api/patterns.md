# Patterns

Compiled regex patterns for the two supported formats, exported from the top level module.

They validate the _shape_ of a string, not whether the week really existed: `2023-W53` matches `ISOWEEK_PATTERN` even
though 2023 had only 52 weeks. See
[why validation is stricter than the regex](../user-guide/why-iso-week-date.md#why-validation-is-stricter-than-the-regex)
for the reasoning, and [working with Pydantic](../user-guide/pydantic.md) for how to choose between the two.

```python exec="true" source="material-block" session="patterns" result="python"
from iso_week_date import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN

print(bool(ISOWEEK_PATTERN.match("2023-W01")))
print(bool(ISOWEEK_PATTERN.match("2023-W01-1")))  # a week date, not a week
print(bool(ISOWEEKDATE_PATTERN.match("2023-W01-1")))
print(bool(ISOWEEK_PATTERN.match("2023-W53")))  # shape is valid, the week is not
```

Each pattern captures its components as groups:

```python exec="true" source="material-block" session="patterns" result="python"
match = ISOWEEKDATE_PATTERN.match("2023-W01-1")

print(match.groups())
```

::: iso_week_date.ISOWEEK_PATTERN
    options:
        show_root_full_path: true
        show_root_heading: true

::: iso_week_date.ISOWEEKDATE_PATTERN
    options:
        show_root_full_path: true
        show_root_heading: true
