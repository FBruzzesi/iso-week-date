# ISO Week Date

[![PyPI version](https://badge.fury.io/py/iso-week-date.svg)](https://badge.fury.io/py/iso-week-date)
![license-shield](https://img.shields.io/github/license/FBruzzesi/iso-week-date)
![pypi-versions](https://img.shields.io/pypi/pyversions/iso-week-date)
[![Trusted publishing](https://img.shields.io/badge/Trusted_publishing-Provides_attestations-bright_green)](https://peps.python.org/pep-0740/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![interrogate-shield](docs/img/interrogate-shield.svg)
[![PYPI - Types](https://img.shields.io/pypi/types/iso-week-date)](https://pypi.org/project/iso-week-date)

<img src="docs/img/iso-week-date-logo.svg" width=160 height=160 align="right">

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date)
in two formats, namely:

* Week format **YYYY-WNN** (date format **%G-W%V**)
* Week date format **YYYY-WNN-D** (date format **%G-W%V-%u**)

where _YYYY_ represents the year, _W_ is a string literal, _NN_ represents the week number, and _D_ represents the day
of the week.

In a nutshell it provides:

* [`IsoWeek`](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) and [`IsoWeekDate`](https://fbruzzesi.github.io/iso-week-date/api/isoweekdate/)
    classes that implement a series of methods to work with ISO Week (Date) formats directly, avoiding the pitfalls of
    going back and forth between string, date and datetime python objects.
* [pandas](https://fbruzzesi.github.io/iso-week-date/api/pandas/) and [polars](https://fbruzzesi.github.io/iso-week-date/api/polars/)
    functionalities (and namespaces) to work with series of ISO Week dates.
* [pydantic](https://fbruzzesi.github.io/iso-week-date/user-guide/pydantic/) compatible types, as described in their
    docs section on how to [customize validation with `__get_pydantic_core_schema__`](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__)

---

[Documentation](https://fbruzzesi.github.io/iso-week-date/) | [Source Code](https://github.com/fbruzzesi/iso-week-date/) | [Issue Tracker](https://github.com/fbruzzesi/iso-week-date/issues)

---

## Installation

**iso-week-date** is published as a Python package on [pypi](https://pypi.org/project/iso-week-date/), and it can be
installed with pip, or directly from source using git, or with a local clone:

* **pip** (suggested):

    ```bash
    python -m pip install iso-week-date
    ```

* **pip + source/git**:

    ```bash
    python -m pip install git+https://github.com/FBruzzesi/iso-week-date.git
    ```

* **local clone**:

    ```bash
    git clone https://github.com/FBruzzesi/iso-week-date.git
    cd iso-week-date
    python -m pip install .
    ```

### Dependencies

* To work with `IsoWeek` and `IsoWeekDate` classes, the only dependency is [`packaging`](https://packaging.pypa.io/),
    which is used to compare the versions of the optional dependencies below.
* _pandas_ and _polars_ functionalities require the installation of the respective libraries
    (`pandas>=1.1.0`, `polars>=0.18.0`).
* _pydantic_ integration requires `pydantic>=2.4.0`.

## Getting Started

```python
from datetime import date

from iso_week_date import IsoWeek

week = IsoWeek.from_date(date(2026, 3, 10))

week  # IsoWeek(2026-W11)
week.year, week.week  # (2026, 11)
week.nth(1), week.nth(7)  # (date(2026, 3, 9), date(2026, 3, 15))
week + 1  # IsoWeek(2026-W12)
week - 13  # IsoWeek(2025-W50), year boundary handled
date(2026, 3, 12) in week  # True

tuple(IsoWeek.range(start=week - 2, end=week, inclusive="both", as_str=True))
# ('2026-W09', '2026-W10', '2026-W11')
```

Work through the [quickstart](https://fbruzzesi.github.io/iso-week-date/user-guide/quickstart/) to build something
end to end, or jump to the [API tour](https://fbruzzesi.github.io/iso-week-date/user-guide/api-tour/) for every
available parsing, conversion, comparison and arithmetic option.

### Documentation

| If you want to... | Go to |
| --- | --- |
| learn the library by building something | [Quickstart](https://fbruzzesi.github.io/iso-week-date/user-guide/quickstart/) |
| look up a specific method and see it used | [API tour](https://fbruzzesi.github.io/iso-week-date/user-guide/api-tour/) |
| apply this to a _pandas_ or _polars_ series | [Working with dataframes](https://fbruzzesi.github.io/iso-week-date/user-guide/dataframe-modules/) |
| validate ISO week strings on a model field | [Working with Pydantic](https://fbruzzesi.github.io/iso-week-date/user-guide/pydantic/) |
| have weeks start on a day other than Monday | [Weeks not starting on Monday](https://fbruzzesi.github.io/iso-week-date/user-guide/custom-offset/) |
| understand why the library works this way | [Why iso-week-date?](https://fbruzzesi.github.io/iso-week-date/user-guide/why-iso-week-date/) |
| read exact signatures and exceptions | [API Reference](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) |

### Custom offset

One of the main reasons for this library to exist is the flexibility to work with custom offsets, i.e. to add/subtract a
custom offset (as `timedelta`) to the default ISO Week start, and get a "shifted" week. This is available both in the
`IsoWeek`/`IsoWeekDate` classes and in the dataframe functionalities: see
[weeks not starting on Monday](https://fbruzzesi.github.io/iso-week-date/user-guide/custom-offset/).

## Contributing

Please read the [contributing guidelines](https://fbruzzesi.github.io/iso-week-date/contribute/) in the documentation
site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/iso-week-date/blob/main/LICENSE).
