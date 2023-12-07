<img src="img/iso-week-date-logo.svg" width=160 height=160 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="img/interrogate-shield.svg">
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
<img src="img/coverage.svg">
<img src="https://img.shields.io/pypi/pyversions/iso-week-date">

# ISO Week Date

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in two formats, namely:

- Week format **YYYY-WNN** (corresponding to the date format **%Y-W%V**)
- Week date format **YYYY-WNN-D** (corresponding to the date format **%Y-W%V-%u**)

(where YYYY represents the year, W is a literal, NN represents the week number, and D represents the day of the week)

In a nutshell it provides:

- [`IsoWeek`](api/isoweek.md) and [`IsoWeekDate`](api/isoweekdate.md) classes implementing a series of methods to work with ISO Week (Date) formats and avoiding the pitfalls of going back and forth between string, date and datetime python objects
- [pandas](api/pandas.md) and [polars](api/polars.md) functionalities to work with series of ISO Week dates

---

[Documentation](https://fbruzzesi.github.io/iso-week-date/) | [Source Code](https://github.com/fbruzzesi/iso-week-date/)

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
