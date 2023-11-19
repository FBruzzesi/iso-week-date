# Installation

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

## Dependencies

- To work with `IsoWeek` and `IsoWeekDate` classes, no additional dependencies are required.
- _pandas_ and _polars_ functionalities require the installation of the respective libraries.

    === "pandas"

        ```bash
        pip install pandas
        pip install iso-week-date[pandas]
        ```

    === "polars"

        ```bash
        pip install polars  # polars>=0.18.0
        pip install iso-week-date[polars]
        ```
