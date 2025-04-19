# ISO Week Date

[![PyPI version](https://badge.fury.io/py/iso-week-date.svg)](https://badge.fury.io/py/iso-week-date)
![license-shield](https://img.shields.io/github/license/FBruzzesi/iso-week-date)
![pypi-versions](https://img.shields.io/pypi/pyversions/iso-week-date)
[![Trusted publishing](https://img.shields.io/badge/Trusted_publishing-Provides_attestations-bright_green)](https://peps.python.org/pep-0740/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
![coverage](docs/img/coverage.svg)
![interrogate-shield](docs/img/interrogate-shield.svg)
[![PYPI - Types](https://img.shields.io/pypi/types/iso-week-date)](https://pypi.org/project/iso-week-date)

<img src="docs/img/iso-week-date-logo.svg" width=160 height=160 align="right">

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in two formats, namely:

- Week format **YYYY-WNN** (date format **%Y-W%V**)
- Week date format **YYYY-WNN-D** (date format **%Y-W%V-%u**)

where _YYYY_ represents the year, _W_ is a string literal, _NN_ represents the week number, and _D_ represents the day of the week.

In a nutshell it provides:

- [`IsoWeek`](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) and [`IsoWeekDate`](https://fbruzzesi.github.io/iso-week-date/api/isoweekdate/) classes that implement a series of methods to work with ISO Week (Date) formats directly, avoiding the pitfalls of going back and forth between string, date and datetime python objects.
- [pandas](https://fbruzzesi.github.io/iso-week-date/api/pandas/) and [polars](https://fbruzzesi.github.io/iso-week-date/api/polars/) functionalities (and namespaces) to work with series of ISO Week dates.
- [pydantic](https://fbruzzesi.github.io/iso-week-date/user-guide/pydantic/) compatible types, as described in their docs section on how to [customize validation with `__get_pydantic_core_schema__`](https://docs.pydantic.dev/latest/concepts/types/#customizing-validation-with-__get_pydantic_core_schema__)

---

[Documentation](https://fbruzzesi.github.io/iso-week-date/) | [Source Code](https://github.com/fbruzzesi/iso-week-date/) | [Issue Tracker](https://github.com/fbruzzesi/iso-week-date/issues)

---

## Installation

**iso-week-date** is published as a Python package on [pypi](https://pypi.org/project/iso-week-date/), and it can be installed with pip, or directly from source using git, or with a local clone:

- **pip** (suggested):

    ```bash
    python -m pip install iso-week-date
    ```

- **pip + source/git**:

    ```bash
    python -m pip install git+https://github.com/FBruzzesi/iso-week-date.git
    ```

- **local clone**:

    ```bash
    git clone https://github.com/FBruzzesi/iso-week-date.git
    cd iso-week-date
    python -m pip install .
    ```

### Dependencies

- To work with `IsoWeek` and `IsoWeekDate` classes, no additional dependency is required.
- _pandas_ and _polars_ functionalities require the installation of the respective libraries.
- _pydantic_ integration requires `pydantic>=2.40`.

## Getting Started

### Available features

This is a high level overview of the features provided by the `iso-week-date` package.

The [`IsoWeek`](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) and [`IsoWeekDate`](https://fbruzzesi.github.io/iso-week-date/api/isoweekdate/) classes provide the following functionalities:

- **Parsing** from string, date and datetime objects.
- **Conversion** to string, date and datetime objects.
- **Comparison** operations between `IsoWeek` (resp `IsoWeekDate`) objects.
- Addition with `int` types.
- Subtraction with `int` and `IsoWeek` (resp `IsoWeekDate`) types.
- Range between two `IsoWeek` (resp. `IsoWeekDate`) objects.

`IsoWeek` unique methods/features:

- `days` properties that lists the dates in the given week
- `nth` method to get the _nth_ day of the week as date
- `in` operator and `contains` method to check if a (iterable of) week(s), string(s) and/or date(s) is contained in the given week
- `weeksout` method to generate a list of weeks that are _n\_weeks_ after the given week
- Addition and subtraction with `int` defaults to adding/subtracting weeks

`IsoWeekDate` unique methods/features:

- `day` property that returns the weekday as integer
- `isoweek` property that returns the ISO Week of the given date (as string)
- `daysout` method to generate a list of dates that are _n\_days_ after the given date
- Addition and subtraction with `int` defaults to adding/subtracting days

[`pandas_utils`](https://fbruzzesi.github.io/iso-week-date/api/pandas/) and [`polars_utils`](https://fbruzzesi.github.io/iso-week-date/api/polars/) modules provide functionalities to work with and move back and forth with _series_ of ISO Week date formats.

In specific both modules implements the following functionalities:

- `datetime_to_isoweek` and `datetime_to_isoweekdate` to convert a series of datetime objects to a series of ISO Week (date) strings
- `isoweek_to_datetime` and `isoweekdate_to_datetime` to convert a series of ISO Week (date) strings to a series of datetime objects
- `is_isoweek_series` and `is_isoweekdate_series` to check if a string series values match the ISO Week (date) format

### Quickstart

To get started with `IsoWeek` and `IsoWeekDate` classes please refer to the [quickstart](https://fbruzzesi.github.io/iso-week-date/user-guide/quickstart/) documentation section.

To check examples on how to work with _pandas_ and _polars_ functionalities please refer to the [dataframe modules](https://fbruzzesi.github.io/iso-week-date/user-guide/dataframe-modules/) documentation section.

### Custom offset

One of the main reason for this library to exist is the need and the flexibility to work with custom offsets, i.e. to be able to add/subtract a custom offset (as `timedelta`) to the default ISO Week start and given date, and get a "shifted" week.

This feature is available both in the `IsoWeek` and `IsoWeekDate` classes and the dataframe functionalities.

To check an example see the [working with custom offset](https://fbruzzesi.github.io/iso-week-date/user-guide/quickstart/#working-with-custom-offset) section.

## Contributing

Please read the [contributing guidelines](https://fbruzzesi.github.io/iso-week-date/contribute/) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/iso-week-date/blob/main/LICENSE).
