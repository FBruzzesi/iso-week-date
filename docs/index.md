# ISO Week Date

[![PyPI version](https://badge.fury.io/py/iso-week-date.svg)](https://badge.fury.io/py/iso-week-date)
![license-shield](https://img.shields.io/github/license/FBruzzesi/iso-week-date)
![pypi-versions](https://img.shields.io/pypi/pyversions/iso-week-date)
[![Trusted publishing](https://img.shields.io/badge/Trusted_publishing-Provides_attestations-bright_green)](https://peps.python.org/pep-0740/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![interrogate-shield](img/interrogate-shield.svg)
[![PYPI - Types](https://img.shields.io/pypi/types/iso-week-date)](https://pypi.org/project/iso-week-date)

<img src="img/iso-week-date-logo.svg" width=160 height=160 align="right">

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date)
in two formats, namely:

* Week format **YYYY-WNN** (date format **%G-W%V**)
* Week date format **YYYY-WNN-D** (date format **%G-W%V-%u**)

where _YYYY_ represents the year, _W_ is a string literal, _NN_ represents the week number, and _D_ represents the day
of the week.

In a nutshell it provides:

* [`IsoWeek`](api/isoweek.md) and [`IsoWeekDate`](api/isoweekdate.md) classes that implement a series of methods to work
    with ISO Week (Date) formats directly, avoiding the pitfalls of going back and forth between string, date and
    datetime python objects.
* [pandas](api/pandas.md) and [polars](api/polars.md) functionalities (and namespaces) to work with series of ISO Week
    dates.
* [pydantic](user-guide/pydantic.md) compatible types.

---

[Documentation](https://fbruzzesi.github.io/iso-week-date/) | [Source Code](https://github.com/fbruzzesi/iso-week-date/) | [Issue Tracker](https://github.com/fbruzzesi/iso-week-date/issues)

---

## Installation

TL;DR: you can install the package with pip:

```bash
python -m pip install iso-week-date
```

For more information please refer to the [installation](installation.md) section.

## Where to start

The documentation is organized by what you are trying to do:

| If you want to... | Go to |
| --- | --- |
| learn the library by building something | [Quickstart](user-guide/quickstart.md) |
| look up a specific method and see it used | [API tour](user-guide/api-tour.md) |
| apply this to a _pandas_ or _polars_ series | [Working with dataframes](user-guide/dataframe-modules.md) |
| validate ISO week strings on a model field | [Working with Pydantic](user-guide/pydantic.md) |
| have weeks start on a day other than Monday | [Weeks not starting on Monday](user-guide/custom-offset.md) |
| understand why the library works this way | [Why iso-week-date?](user-guide/why-iso-week-date.md) |
| read exact signatures and exceptions | [API Reference](api/isoweek.md) |

## Contributing

Please read the [contributing guidelines](contribute.md) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/iso-week-date/blob/main/LICENSE).
