<img src="img/iso-week-date-logo.svg" width=160 height=160 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="img/interrogate-shield.svg">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
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

[Documentation](https://fbruzzesi.github.io/iso-week-date) | [Source Code](https://github.com/fbruzzesi/iso-week-date)

---

## Installation

**iso-week-date** is published as a Python package on [pypi](https://pypi.org/project/iso-week-date/), and it can be installed with pip, or directly from source using git, or with a local clone:

=== "pip (pypi)"

    ```bash
    python -m pip install iso-week-date
    ```

=== "source/git"

    ```bash
    python -m pip install git+https://github.com/FBruzzesi/iso-week-date.git
    ```

=== "local clone"

    ```bash
    git clone https://github.com/FBruzzesi/iso-week-date.git
    cd iso-week-date
    python -m pip install .
    ```

### Dependencies

- To work with `IsoWeek` and `IsoWeekDate` classes, no additional dependency is required
- _pandas_ and _polars_ functionalities require the installation of the respective libraries

## Usage

To get started with `IsoWeek` and `IsoWeekDate` classes please refer to the [quickstart](getting-started/quickstart.md) section.

To check examples on how to work with _pandas_ and _polars_ functionalities please refer to the [dataframe modules](getting-started/dataframe-modules.md) section.

## Contributing

Please read the [contributing guidelines](contribute.md) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/deczoo/blob/main/LICENSE).
