<img src="img/iso-week-date-logo.svg" width=185 height=185 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="img/interrogate-shield.svg">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<img src="img/coverage.svg">

# iso-week-date

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in two formats, namely:

- Week format _YYYY-WNN_ (%Y-W%V)
- Week date format _YYYY-WNN-D_ (%Y-W%V-%u)

In a nutshell it provides:

- [`IsoWeek`](api/isoweek/) and [`IsoWeekDate`](api/isoweekdate/) classes implementing a series of methods to work with ISO Week date formats and avoiding the pitfalls of going back and forth between string, date and datetime python objects.
- [pandas](api/pandas/) and [polars](api/polars/) functionalities to work with series of ISO Week dates.

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

- To work with `IsoWeek` and `IsoWeekDate` classes, no additional dependency is required.
- pandas and polars functionalities require the installation of the respective libraries.

## Usage

To see how to work with `IsoWeek`, `IsoWeekDate` and/or pandas and polars utils modules, please refer to the [getting started](getting-started/quickstart/) section.

## Contributing

Please read the [contributing guidelines](contribute/) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/deczoo/blob/main/LICENSE).
