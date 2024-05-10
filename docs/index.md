# ISO Week Date

![license-shield](https://img.shields.io/github/license/FBruzzesi/iso-week-date)
![interrogate-shield](img/interrogate-shield.svg)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![coverage](img/coverage.svg)
![pypi-versions](https://img.shields.io/pypi/pyversions/iso-week-date)

<img src="img/iso-week-date-logo.svg" width=160 height=160 align="right">

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in two formats, namely:

- Week format **YYYY-WNN** (date format **%Y-W%V**)
- Week date format **YYYY-WNN-D** (date format **%Y-W%V-%u**)

where _YYYY_ represents the year, _W_ is a literal, _NN_ represents the week number, and _D_ represents the day of the week.

In a nutshell it provides:

- [`IsoWeek`](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) and [`IsoWeekDate`](https://fbruzzesi.github.io/iso-week-date/api/isoweekdate/) classes that implement a series of methods to work with ISO Week (Date) formats directly, avoiding the pitfalls of going back and forth between string, date and datetime python objects.
- [pandas](https://fbruzzesi.github.io/iso-week-date/api/pandas/) and [polars](https://fbruzzesi.github.io/iso-week-date/api/polars/) functionalities (and namespaces) to work with series of ISO Week dates.
- [pydantic](https://fbruzzesi.github.io/iso-week-date/user-guide/pydantic/) compatible types, as described in their docs section on how to [customize validation with `__get_pydantic_core_schema__`](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__)

---

[Documentation](https://fbruzzesi.github.io/iso-week-date/) | [Source Code](https://github.com/fbruzzesi/iso-week-date/) | [Issue Tracker](https://github.com/fbruzzesi/iso-week-date/issues)

---

## Installation

TL;DR: you can install the package with pip:

```bash
python -m pip install iso-week-date
```

For more information please refer to the [installation](installation.md) section.

## Usage

To get started with `IsoWeek` and `IsoWeekDate` classes please refer to the [quickstart](user-guide/quickstart.md) section.

To check examples on how to work with _pandas_ and _polars_ functionalities please refer to the [dataframe modules](user-guide/dataframe-modules.md) section.

## Contributing

Please read the [contributing guidelines](contribute.md) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/iso-week-date/blob/main/LICENSE).
