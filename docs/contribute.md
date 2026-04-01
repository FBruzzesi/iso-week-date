# Contributing

We welcome contributions to the library!

If you have a new feature and/or a bug fix that you would like to contribute, please follow the steps below.

## Prerequisites

The following tools are needed as a one time setup:

* [uv](https://docs.astral.sh/uv/getting-started/installation/) for dependency management.
* [prek](https://github.com/j178/prek?tab=readme-ov-file#installation) for pre-commit hooks.

## Getting started

1. Fork and clone the repository:

    ```terminal
    git clone git@github.com:<your-github-handle>/iso-week-date.git
    cd iso-week-date
    ```

2. Install dependencies (including all optional and development groups):

    ```terminal
    uv sync --all-extras --group local-dev
    ```

3. Install the pre-commit hooks:

    ```terminal
    prek install
    prek run --all-files
    ```

    This installs git hooks under the `.git/hooks/` directory and runs them on all files to verify the setup.

## Development workflow

1. Create a new branch for your bug fix or feature.
2. Make your changes and test them thoroughly, making sure that all existing tests still pass.
3. Commit your changes and push the branch to your fork.
4. Open a pull request on the main repository.

## Code and Markdown formatting

**iso-week-date** uses [ruff](https://docs.astral.sh/ruff/) as linter and formatter, and
[rumdl](https://github.com/ssgier/rumdl) as markdown linter:

=== "with make"

    ```bash
    make lint
    ```

=== "without make"

    ```bash
    uvx ruff format src tests
    uvx ruff check src tests --fix
    uvx rumdl check .
    ```

## Testing

Once you are done with changes, you should:

* Add tests for the new features in the `tests/` folder.
* Make sure that new features do not break existing codebase by running tests:

    === "with make"

        ```bash
        make test
        ```

    === "without make"

        ```bash
        uv run --group tests pytest src tests --cov=src --cov=tests --cov-fail-under=95 --doctest-modules --cache-clear
        ```

## Type checking

The project uses both [mypy](https://mypy-lang.org/) and [pyright](https://github.com/microsoft/pyright) for static
type checking:

=== "with make"

    ```bash
    make typing
    ```

=== "without make"

    ```bash
    uv run --group typing mypy src tests
    uv run --group typing pyright src tests
    ```

## Running all checks

To run linting, tests, type checking, and more in one go:

```bash
make check
```

## Docs

The documentation is generated using [zensical](https://zensical.org/), the API part uses
[mkdocstrings](https://mkdocstrings.github.io/).

If a breaking feature is developed, then we suggest to update the documentation in the `docs/` folder as well, in order
to describe how this can be used from a user perspective.

To serve it locally:

```bash
uv run --group docs zensical serve -a localhost:<port-number>
```

## Reporting bugs

If you find a bug in the library, please report it by opening an [issue on GitHub](https://github.com/FBruzzesi/iso-week-date/issues).
Be sure to include the version of the library you're using, as well as any error messages or tracebacks and a
reproducible example.

## Requesting features

If you have a suggestion for a new feature, please open an [issue on GitHub](https://github.com/FBruzzesi/iso-week-date/issues).
Be sure to explain the problem that you're trying to solve and how you think the feature would solve it.

## Code of conduct

All contributors are expected to follow the project's code of conduct, which is based on the
[Contributor Covenant](https://www.contributor-covenant.org/).
