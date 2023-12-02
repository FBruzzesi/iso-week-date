# Working with Pydantic

If you want to work with ISO Week (date) format within [pydantic v2](https://docs.pydantic.dev/), i.e. create a model with a string field representing an ISO Week (date) format, there are two options: [the easy way](#the-easy-way) and [the hard way](#the-hard-way).

## The easy way

For me the easy way to achieve this is via [`Annotated`](https://docs.python.org/3/library/typing.html#typing.Annotated) and [`StringConstraints`](https://docs.pydantic.dev/api/types/#pydantic.types.StringConstraints) with custom regex patterns.

The regex patterns are available in the top level module of **iso-week-date**, therefore it is possible to use them directly:

```py
from typing import Annotated

from iso_week_date import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
from pydantic import BaseModel, StringConstraints

T_ISOWeek = Annotated[str, StringConstraints(pattern=ISOWEEK_PATTERN.pattern)]
T_ISOWeekDate = Annotated[str, StringConstraints(pattern=ISOWEEKDATE_PATTERN.pattern)]

class MyModel(BaseModel):
    week: T_ISOWeek
    week_date: T_ISOWeekDate

m1 = MyModel(week='2023-W01', week_date='2023-W01-1')
m2 = MyModel(week='2023-W53', week_date='2023-W01-1')
```

### Caveat

The caveat of this approach can be seen in the second instance in the example above. Namely the regex patterns could be not _strict_ enough for your purpouses, i.e. they allow for some combinations that are not valid ISO Week (date) formats.

In fact not every combination of year and week number should be possible (not every year has 53 weeks!), but this is not enforced by the regex patterns.

!!! note
    Remark that actual validation happens when instantiating [`IsoWeek`](../api/isoweek.md) and [`IsoWeekDate`](../api/isoweekdate.md) classes.

On the positive side, python [datetime module](https://docs.python.org/3/library/datetime.html) deals with that automagically:

```py
from datetime import datetime

# 2023 has 52 weeks
datetime.strptime("2023-W53-1", "%G-W%V-%u")  # datetime(2024, 1, 1, 0, 0)
datetime.strptime("2024-W01-1", "%G-W%V-%u")  # datetime(2024, 1, 1, 0, 0)
```

As we can see the datetime module is able to parse both `2023-W53-1` and `2024-W01-1` as the same datetime object (`datetime(2024, 1, 1, 0, 0)`).

## The hard way

The _hard_ (yet arguably the proper) _way_ to do it is to implement (and maintain[^1]) a custom type using [custom validation with `__get_pydantic_core_schema__`](https://docs.pydantic.dev/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__).

There are multiple examples of this approach in [pydantic-extra-types](https://github.com/pydantic/pydantic-extra-types).

[^1]: As this approach uses Pydantic v2 and [pydantic-core](https://github.com/pydantic/pydantic-core) features, which are both under fast and active development, it is likely that the implementation will need to be updated in the future.

## Compact formats

The compact formats (**YYYYWNN**, **YYYYWNND**) are not directly available in the module. However if needed it is possible to composed them with some gymnastic:

```py
from typing import Final
from iso_week_date._patterns import YEAR_MATCH, WEEK_MATCH, WEEKDAY_MATCH  # These are strings, not regex patterns

ISOWEEK_COMPACT_PATTERN: Final[str] = r"^{}{}$".format(YEAR_MATCH, WEEK_MATCH)
ISOWEEKDATE_COMPACT_PATTERN: Final[str] = r"^{}{}{}$".format(YEAR_MATCH, WEEK_MATCH, WEEK_DAY_MATCH)

T_ISOWeekCompact = Annotated[str, StringConstraints(pattern=ISOWEEK_COMPACT_PATTERN)]
T_ISOWeekDateCompact = Annotated[str, StringConstraints(pattern=ISOWEEKDATE_COMPACT_PATTERN)]
```
