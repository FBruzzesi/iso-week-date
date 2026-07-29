# Installation

**iso-week-date** requires Python 3.10 or above. It is published as a Python package on
[pypi](https://pypi.org/project/iso-week-date/), and it can be installed with pip, or directly from source using git,
or with a local clone:

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

## Optional dependencies

The [`IsoWeek`](api/isoweek.md) and [`IsoWeekDate`](api/isoweekdate.md) classes have no third party dependency: a plain
install is all they need.

The dataframe and pydantic integrations are opt-in extras, each of which installs the corresponding library at a
supported version:

=== "pandas"

    ```bash
    python -m pip install "iso-week-date[pandas]"
    ```

    Installs `pandas>=1.0.0`.

=== "polars"

    ```bash
    python -m pip install "iso-week-date[polars]"
    ```

    Installs `polars>=0.18.0`.

=== "pydantic"

    ```bash
    python -m pip install "iso-week-date[pydantic]"
    ```

    Installs `pydantic>=2.4.0`.

=== "all"

    ```bash
    python -m pip install "iso-week-date[all]"
    ```

    Installs all of the above.

!!! tip
    Extras are additive, so they can be combined: `python -m pip install "iso-week-date[pandas,pydantic]"`.
