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
- _pandas_, _polars_  and/or _pydantic_ functionalities require the installation of the respective libraries.

    === "pandas"

        ```bash
        python -m pip install "pandas>=1.0.0"
        python -m pip install "iso-week-date[pandas]"
        ```

    === "polars"

        ```bash
        python pip install "polars>=0.18.0"
        python pip install "iso-week-date[polars]"
        ```

    === "pydantic"

        ```bash
        python pip install "pydantic>=2.4.0"
        python pip install "iso-week-date[pydantic]"
        ```
