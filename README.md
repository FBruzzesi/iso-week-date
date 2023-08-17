<!-- <img src="docs/img/iso-week-logo.png" width=185 height=185 align="right">

![](https://img.shields.io/github/license/FBruzzesi/iso-week)
<img src ="docs/img/interrogate-shield.svg">
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) -->
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

## Getting started

In short a python decorator is a way to modify or enhance the behavior of a function or a class without actually modifying the source code of the function or class.

Decorators are implemented as functions (or classes) that take a function or a class as input and return a new function or class that has some additional functionality.

To have a more in-depth explanation you can check the [decorators docs page](https://fbruzzesi.github.io/deczoo/decorators/intro/).

### Features


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
