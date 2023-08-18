<img src="docs/img/iso-week-logo.svg" width=185 height=185 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="docs/img/interrogate-shield.svg">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
<img src="docs/img/coverage.svg">

# iso-week

**iso-week** is a toolkit to work with str representing ISO Week date format _YYYY-WXY_.

In a nutshell it provides:

- a `IsoWeek` class implementing a series of functionalities and methods to work with ISO Week date format and avoiding the pitfalls of going back and forth between Iso Week, string and date/datetime object.
- [pandas](https://pandas.pydata.org/) and [polars](https://www.pola.rs/) functionalities to work with series of Iso Week dates.

---

**Documentation**: https://fbruzzesi.github.io/iso-week

**Source Code**: https://github.com/fbruzzesi/iso-week

---

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

```python
from datetime import date, datetime, timedelta
from iso_week import IsoWeek

# Initialize from string
iw = IsoWeek("2023-W01")
iw.value, iw._offset # "2023-W01", datetime.timedelta(0)

# Initialize from date
iw = IsoWeek.from_date(date(2023, 1, 2))
iw.year, iw.week, iw.days # 2023, 1, (date(2023, 1, 2),..., date(2023, 1, 8))

# Addition
iw + 1 # IsoWeek("2023-W02")
iw + timedelta(weeks=2) # IsoWeek("2023-W03")

# Subtraction
iw - 1 # IsoWeek("2022-W52")
iw - timedelta(weeks=2) # IsoWeek("2022-W51")
iw - IsoWeek("2022-W52") # 1

# Comparisons
iw == IsoWeek("2023-W01") # True
iw == IsoWeek("2023-W02") # False
iw < IsoWeek("2023-W02") # True
iw > IsoWeek("2023-W02") # False

# Contains
iw.contains((IsoWeek("2023-W01"), date(2023, 1, 1), date(2023, 1, 2))) # (True, False, True)

# Weeksout
tuple(iw.weeksout(3)) # ('2023-W02', '2023-W03', '2023-W04')

# Range
tuple(IsoWeek.range(start="2023-W01", end="2023-W07", step=2, inclusive="both", as_str=True))  # ('2023-W01', '2023-W03', '2023-W05', '2023-W07')

# Custom offset
class CustomWeek(IsoWeek):
    """
    Custom week class with offset of -2 days.
    CustomWeek week starts the Saturday before the "standard" ISO week.
    """
    _offset = timedelta(days=-2)
```

## Installation

**iso-week** is published as a Python package on [pypi](https://pypi.org/), and it can be installed with pip, or directly from source using git, or with a local clone:

- **pip** (suggested):

    ```bash
    python -m pip install iso-week
    ```

- **pip + source/git**:

    ```bash
    python -m pip install git+https://github.com/FBruzzesi/iso-week.git
    ```

- **local clone**:

    ```bash
    git clone https://github.com/FBruzzesi/iso-week.git
    cd iso-week
    python -m pip install .
    ```

### Dependencies

- To work with `IsoWeek` class, no additional dependency is required.
- pandas and polars functionalities require the installation of the respective libraries.

## Contributing

Please read the [Contributing guidelines](https://fbruzzesi.github.io/iso-week/contribute/) in the documentation site.

## License

The project has a [MIT Licence](https://github.com/FBruzzesi/deczoo/blob/main/LICENSE)
