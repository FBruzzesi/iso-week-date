<img src="docs/img/iso-week-date-logo.svg" width=185 height=185 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="docs/img/interrogate-shield.svg">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<img src="docs/img/coverage.svg">

# iso-week-date

**iso-week-date** is a toolkit to work with strings representing [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in the  _YYYY-WNN_ format.

In a nutshell it provides:

- a [`IsoWeek` class](https://fbruzzesi.github.io/iso-week-date/api/isoweek/) implementing a series of functionalities and methods to work with ISO Week date format and avoiding the pitfalls of going back and forth between Iso Week, string and date/datetime object.
- [pandas](https://fbruzzesi.github.io/iso-week-date/api/pandas/) and [polars](https://fbruzzesi.github.io/iso-week-date/api/polars/) functionalities to work with series of Iso Week dates.

---

[Documentation](https://fbruzzesi.github.io/iso-week-date) | [Source Code](https://github.com/fbruzzesi/iso-week-date)

---

## Installation

**iso-week-date** is published as a Python package on [pypi](https://pypi.org/) with the name of `iso-week-date`, and it can be installed with pip, or directly from source using git, or with a local clone:

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

- To work with `IsoWeek` class, no additional dependency is required.
- pandas and polars functionalities require the installation of the respective libraries.

## Getting Started

### Features

`IsoWeek` class provides the following functionalities:

- Parsing from string, date and datetime objects
- Conversion to string, date and datetime objects
- Comparison between `IsoWeek` objects
- Addition with `int` and `timedelta` types
- Subtraction with `int`, `timedelta` and `IsoWeek` types
- Range between (iso)weeks
- Weeksout generation
- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value

`pandas_utils` and `polars_utils` modules provide functionalities to work with and move back and forth with series of Iso Week dates.

### Quickstart

The `IsoWeek` class is accessible from the top-level module:

```py
from datetime import date, datetime, timedelta
from iso_week_date import IsoWeek
```

An instance can be initialized from parsing multiple types:

- `str` in _YYYY-WNN_ format

    ```py
    iw = IsoWeek("2023-W01")
    iw.value, iw._offset # "2023-W01", datetime.timedelta(0)
    ```

- `str` in compact format _YYYYWNN_

    ```py
    IsoWeek.from_compact("2023W01")
    ```

- `date` or `datetime` objects

    ```py
    IsoWeek.from_date(date(2023, 1, 2))
    IsoWeek.from_datetime(datetime(2023, 1, 2, 12, 0, 0))
    ```

Once initialized, the instance provides the following methods:

- _properties_ to access year, week and days of the week:

    ```py
    iw.year # 2023
    iw.week # 1
    iw.days # (date(2023, 1, 2),..., date(2023, 1, 8))
    ```

- Conversion to multiple types:

    ```py
    iw.to_str() # "2023-W01"
    iw.to_compact() # "2023W01"
    iw.to_date() # date(2023, 1, 2)
    iw.to_date(weekday=2) # date(2023, 1, 3)
    iw.to_datetime() # datetime(2023, 1, 2, 0, 0)
    ```

- Comparison operations:

    ```py
    iw == IsoWeek("2023-W01") # True
    iw == IsoWeek("2023-W02") # False
    iw < IsoWeek("2023-W02") # True
    iw > IsoWeek("2023-W02") # False
    ```

- Addition with `int` and `timedelta` types:

    ```py
    iw + 1 # IsoWeek("2023-W02")
    iw + timedelta(weeks=2) # IsoWeek("2023-W03")
    ```

- Subtraction with `int`, `timedelta` and `IsoWeek` types:

    ```py
    iw - 1 # IsoWeek("2022-W52")
    iw - timedelta(weeks=2) # IsoWeek("2022-W51")
    iw - IsoWeek("2022-W52") # 1
    ```

- Range between (iso)weeks:

    ```py
    tuple(IsoWeek.range(start="2023-W01", end="2023-W07", step=2, inclusive="both", as_str=True))  # ('2023-W01', '2023-W03', '2023-W05', '2023-W07')
    ```

- Weeksout generator:

    ```py
    tuple(iw.weeksout(3)) # ('2023-W02', '2023-W03', '2023-W04')
    ```

- `in` operator and `contains` method to check if a (iterable of) week(s) is contained in the given week value:

    ```py
    date(2023, 1, 1) in iw # False
    date(2023, 1, 2) in iw # True

    iw.contains((IsoWeek("2023-W01"), date(2023, 1, 1), date(2023, 1, 2))) # (True, False, True)
    ```

### Working with _custom offset_

The "standard" ISO Week starts on Monday and end on Sunday. However there are cases in which one may require a _shift_ in the starting day of a week.

The `IsoWeek` class has one class attribute called `offset_` which can be used to define a custom offset for the week.

```py title="custom offset"
class MyWeek(IsoWeek):
    """
    MyWeek class is a IsoWeek with custom offset of -2 days.
    Therefore MyWeek starts the Saturday before the "standard" ISO week.
    """
    offset_ = timedelta(days=-2)
```

This is all that is required to work with a custom shifted week.

## Contributing

Please read the [Contributing guidelines](https://fbruzzesi.github.io/iso-week-date/contribute/) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/deczoo/blob/main/LICENSE)
