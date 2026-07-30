from __future__ import annotations

from typing import TYPE_CHECKING, Any, Final, Generic, Protocol, TypeVar

if TYPE_CHECKING:
    import re
    from collections.abc import Callable

    from typing_extensions import Self, TypeIs


T = TypeVar("T")
R = TypeVar("R")


class SupportsYearArithmetic(Protocol):  # noqa: PLW1641
    """Whatever `is_long_year` needs from a year: integer arithmetic and boolean combination.

    Operands and results are `Any` because neither can be pinned down. `Series == 4` is a *boolean*
    Series rather than a `Series[int]`, so the intermediate types do not follow the input type; and
    pandas-stubs declares each of these as a large overload set that no single exact signature can
    satisfy. Narrowing any of them silently drops a backend from the bound instead of checking it
    more strictly: `polars.Expr.__eq__` accepts only what polars can compare against, so demanding
    the `object` that `object.__eq__` declares excludes `Expr` outright.
    """

    # Positional-only, as every dunder is: `int.__add__` takes no keyword, so a protocol that allowed
    # one would not be satisfied by `int` at all.
    def __add__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401
    def __sub__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401
    def __floordiv__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401
    def __mod__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401
    def __or__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401
    def __eq__(self: Self, other: Any, /) -> Any: ...  # noqa: ANN401


#: A year, or a column of them: anything `is_long_year` can compute over.
YearsT = TypeVar("YearsT", bound=SupportsYearArithmetic)

SHORT_YEAR_WEEKS: Final = 52
LONG_YEAR_WEEKS: Final = 53


class classproperty(Generic[T, R]):  # noqa: N801
    """Decorator to create a class level property.

    It allows to define a property at the class level, which can be accessed without creating an instance of the class.

    Arguments:
        func: Function to be decorated.

    Examples:
        >>> class CustomClass:
        ...     @classproperty
        ...     def my_class_property(cls: Type):
        ...         return "This is a class property."

        Then access the class property without creating an instance

        >>> CustomClass.my_class_property
        'This is a class property.'
    """

    def __init__(self: Self, func: Callable[[type[T]], R], /) -> None:
        """Initialize classproperty."""
        self.func = func
        self.__doc__ = func.__doc__
        self.__name__ = func.__name__
        self.__qualname__ = func.__qualname__

    def __get__(self: Self, instance: object, owner: type[Any], /) -> R:
        """Get the value of the class property.

        `owner` is deliberately not tied to `T`. The decorated functions annotate their first
        parameter as `type[Self]`, so binding `T` to that made `T` resolve to `Never` for anything
        outside the defining class, and every access from elsewhere needed a `type: ignore`. `T` is
        only ever used to call `self.func`, which the descriptor protocol already guarantees is
        called with its own class.

        Arguments:
            instance: The instance of the class (ignored)
            owner: The class that owns the property
        """
        value: R = self.func(owner)
        return value


def is_int(value: object) -> TypeIs[int]:
    """Checks that `value` is an integer, excluding `bool`."""
    return isinstance(value, int) and not isinstance(value, bool)


def format_err_msg(_fmt: str, _value: str) -> str:
    """Format error message given a format and a value."""
    return (
        f"Invalid isoweek date format. Format must match the '{_fmt}' pattern, where:"
        "\n* YYYY is a year between 0001 and 9999"
        "\n* W is a literal character"
        "\n* NN is a week number between 1 and 53"
        "\n* D is a day number between 1 and 7"
        f"\n but found {_value}"
    )


def match_isoweek(pattern: re.Pattern[str], value: str) -> tuple[int, int] | None:
    r"""Matches `value` against `pattern` and extracts its year and week numbers.

    `re.fullmatch` is used on purpose, and every caller must go through this function rather than
    matching directly: the patterns in `iso_week_date._patterns` are `$`-anchored, and in Python
    `$` also matches immediately *before* a trailing newline. `pattern.match("2024-W01\n")`
    therefore succeeds and lets a malformed value reach `value_`, where it survives `year`, `week`
    and `to_values()` before finally breaking `to_compact()` and `to_date()`.

    Arguments:
        pattern: Compiled pattern to match `value` against. Its first group must be the year and
            its second group the (`W`-prefixed) week number.
        value: String to match against `pattern`.

    Returns:
        Tuple of `(year, week)` numbers, or `None` when `value` does not match `pattern`.
    """
    if (_match := pattern.fullmatch(value)) is None:
        return None
    return int(_match.group(1)), int(_match.group(2)[1:])


def require_version(module: str, minimum: str, extra: str) -> None:
    """Checks that `module` is installed with a version of at least `minimum`.

    Version comparison is delegated to `packaging.version.Version`, which implements PEP 440
    ordering. An unparsable installed version is treated as good enough: it carries no information
    we can act on, and refusing the import would be worse than allowing it.

    Note:
        `packaging` is imported lazily, not at module scope: this module is on the import path of the
        `IsoWeek` and `IsoWeekDate` classes, which need no third party code, so a user who never touches
        an optional integration never pays for `packaging.version` at all.

    Arguments:
        module: Distribution name of the required module, e.g. `"pandas"`.
        minimum: Minimum supported version as a PEP 440 string, e.g. `"1.1.0"`.
        extra: Name of the `iso-week-date` extra that installs `module`.

    Raises:
        ImportError: If `module` is not installed, or is installed with a version older than `minimum`.
    """
    from importlib import metadata  # noqa: PLC0415

    from packaging.version import InvalidVersion, Version  # noqa: PLC0415

    hint = (
        f"Install it with `python -m pip install '{module}>={minimum}'` "
        f"or `python -m pip install 'iso-week-date[{extra}]'`"
    )

    try:
        installed = metadata.version(module)
    except metadata.PackageNotFoundError as exc:
        msg = f"{module}>={minimum} is required for this module, but {module} is not installed.\n{hint}"
        raise ImportError(msg) from exc

    try:
        parsed = Version(installed)
    except InvalidVersion:
        return

    if parsed < Version(minimum):
        msg = f"{module}>={minimum} is required for this module, found {module}=={installed}.\n{hint}"
        raise ImportError(msg)


def p_of_year(year: YearsT) -> YearsT:
    """Returns the day of the week of 31 December.

    Elementwise integer arithmetic only, so this holds for a single `int` and for a column of them
    alike: a `pandas.Series`, a `polars.Series` or a `polars.Expr` all come back as the same type.
    """
    # Annotated locals rather than direct returns: the protocol's members are `Any`, so the computed
    # type is `Any` too, and naming it is how the identity `YearsT -> YearsT` gets stated.
    p: YearsT = (year + year // 4 - year // 100 + year // 400) % 7
    return p


def is_long_year(year: YearsT) -> YearsT:
    """Whether `year` is a long ISO year, the kind that has a week 53.

    From wikipedia section on [weeks per year](https://en.wikipedia.org/wiki/ISO_week_date#Weeks_per_year):

    If p(y) = (y + y//4 - y//100 + y//400) % 7 then
    weeks(y) = 52 + (p(y) == 4 or p(y-1) == 3)

    Written with `|` rather than `or`, which is what lets the dataframe modules reuse this instead of
    keeping their own copy: `or` needs a single truth value and raises on a column. The predicate
    rather than the count is the shared piece, because `52 + <boolean column>` is not arithmetic every
    backend allows, while `|` over comparisons is.

    Arguments:
        year: Ordinal year number, or a column of them.

    Returns:
        Whether the year has 53 weeks, elementwise for a column.
    """
    long_year: YearsT = (p_of_year(year) == 4) | (p_of_year(year - 1) == 3)  # noqa: PLR2004
    return long_year


def weeks_of_year(year: YearsT) -> YearsT:
    """Returns the max number of weeks in a year.

    Arguments:
        year: Ordinal year number

    Returns:
        Number of weeks in the year (either 52 or 53)
    """
    weeks: YearsT = is_long_year(year) + SHORT_YEAR_WEEKS
    return weeks
