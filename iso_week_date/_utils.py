from typing import Any, Callable, Type, TypeVar

try:
    from typing import Self  # type: ignore[attr-defined]
except ImportError:
    from typing_extensions import Self  # type: ignore[attr-defined]


T = TypeVar("T")


class classproperty:
    """
    Decorator to create a class level property. It allows to define a property at the
    class level, which can be accessed without creating an instance of the class.

    Arguments:
        f: function to be decorated

    Usage:
    ```python
    class CustomClass:

        @classproperty
        def my_property(cls: Type):
            return "This is a class property."

    # Access the class property without creating an instance
    print(CustomClass.my_property)  # "This is a class property."
    ```
    """

    def __init__(self: Self, f: Callable[[Type[T]], Any]):
        """Initialize classproperty."""
        self.f = f

    def __get__(self: Self, obj: T, owner: Type[T]) -> Any:
        """
        Get the value of the class property.

        Arguments:
            obj: The instance of the class (ignored)
            owner: The class that owns the property
        """
        return self.f(owner)


def format_err_msg(_fmt: str, _value: str) -> str:  # pragma: no cover
    """Format error message given a format and a value."""

    return (
        "Invalid isoweek date format. "
        f"Format must match the '{_fmt}' pattern, "
        "where:"
        "\n- YYYY is a year between 0001 and 9999"
        "\n- W is a literal character"
        "\n- NN is a week number between 1 and 53"
        "\n- D is a day number between 1 and 7"
        f"\n but found {_value}"
    )


def p_of_year(year: int) -> int:
    """Returns the day of the week of 31 December"""
    return (year + year // 4 - year // 100 + year // 400) % 7


def weeks_of_year(year: int) -> int:
    """
    Returns the max number of weeks in a year.

    From wikipedia section on
    [weeks per year](https://en.wikipedia.org/wiki/ISO_week_date#Weeks_per_year):

    If p(y) = (y + y//4 - y//100 + y//400) % 7 then
    weeks(y) = 52 + (p(y) ==4 or p(y-1) == 3)

    Arguments:
        year: Ordinal year number

    Returns:
        Number of weeks in the year (either 52 or 53)
    """
    return 52 + (p_of_year(year) == 4 or p_of_year(year - 1) == 3)
