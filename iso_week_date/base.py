from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from typing import ClassVar, Generator, Literal, Type, TypeVar, Union, overload

from iso_week_date.mixin import ComparatorMixin, ConverterMixin, ParserMixin

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

BaseIsoWeek_T = TypeVar("BaseIsoWeek_T", str, date, datetime, "BaseIsoWeek")


class InclusiveEnum(str, Enum):
    """Inclusive enum"""

    both = "both"
    left = "left"
    right = "right"
    neither = "neither"


_inclusive_values = tuple(e.value for e in InclusiveEnum)
Inclusive_T = Literal[_inclusive_values]  # type: ignore


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


class BaseIsoWeek(ABC, ComparatorMixin, ConverterMixin, ParserMixin):
    """
    Base abstract class for `IsoWeek` and `IsoWeekDate` classes.

    It defines the common interface for both classes and implements the common methods
    between them.

    Attributes:
        value_: stores the string value representing the iso-week date in the
            `_format` format

        _pattern: class variable, stores the regex pattern to validate iso-week string
            format
        _format: class variable, stores the string format of the iso-week date
        _date_format: class variable, stores the string format with datetime conventions
        offset_: class variable, stores the offset to be used when converting to
            and from `datetime` and `date` objects
    """

    _pattern: ClassVar[re.Pattern]

    _format: ClassVar[str]
    _date_format: ClassVar[str]

    offset_: ClassVar[timedelta] = timedelta(days=0)

    __slots__ = ("value_",)

    def __init__(self: Self, value: str, __validate: bool = True) -> None:
        """
        Initializes `BaseIsoWeek` object from iso-week string.

        Arguments:
            value: iso-week string to initialize `BaseIsoWeek` object
            __validate: whether to validate iso-week string format or not
        """
        self.value_ = self.validate(value) if __validate else value

    @classmethod
    def validate(cls: Type[Self], value: str) -> str:
        """Validates iso-week string format."""
        _match = re.match(cls._pattern, value)

        if not _match:
            raise ValueError(format_err_msg(cls._format, value))

        return value

    @classmethod
    def validate_compact(cls: Type[Self], value: str) -> str:
        """Validates iso-week string format without dashes."""
        _compact_pattern = re.compile(cls._pattern.pattern.replace(")-(", ")("))
        _match = re.match(_compact_pattern, value)

        if not _match:
            _compact_format = cls._format.replace("-", "")
            raise ValueError(format_err_msg(_compact_format, value))

        return "-".join(_match.groups())

    def __repr__(self: Self) -> str:
        """Custom representation."""
        return f"{self.name}({self.value_}) with offset {self.offset_}"

    def __str__(self: Self) -> str:
        """String conversion operator, returns iso-week string value ignoring offset."""
        return self.value_

    @property
    def name(self: Self) -> str:
        """Returns class name."""
        return self.__class__.__name__

    @property
    def offset(self: Self) -> timedelta:
        """Returns offset."""
        return self.offset_

    @property
    def format(self: Self) -> str:
        """Returns format."""
        return self._format

    @property
    def pattern(self: Self) -> str:
        """Returns pattern as string."""
        return self._pattern.pattern

    @property
    def compact_pattern(self: Self) -> str:
        """Returns compact pattern as string."""
        return self._pattern.pattern.replace(")-(", ")(")

    @property
    def year(self: Self) -> int:
        """
        Returns year number as integer.

        Usage:
        ```py
        from iso_week_date import IsoWeek, IsoWeekDate

        IsoWeek("2023-W01").year # 2023
        IsoWeekDate("2023-W01-1").year # 2023
        ```
        """
        return int(self.value_[:4])

    @property
    def week(self: Self) -> int:
        """
        Returns week number as integer.

        Usage:
        ```py
        from iso_week_date import IsoWeek, IsoWeekDate

        IsoWeek("2023-W01").week  # 1
        IsoWeekDate("2023-W01-1").week  # 1
        ```
        """
        return int(self.value_[6:8])

    @abstractmethod
    def __add__(self: Self, other: Union[int, timedelta]) -> BaseIsoWeek:
        """Implementation of addition operator."""
        ...

    @overload
    def __sub__(
        self: Self, other: Union[int, timedelta]
    ) -> BaseIsoWeek:  # pragma: no cover
        """Annotation for subtraction with `int` and `timedelta`"""
        ...

    @overload
    def __sub__(self: Self, other: BaseIsoWeek) -> int:  # pragma: no cover
        """Annotation for subtraction with other `BaseIsoWeek`"""
        ...

    @abstractmethod
    def __sub__(
        self: Self, other: Union[int, timedelta, BaseIsoWeek]
    ) -> Union[int, BaseIsoWeek]:
        """Implementation of subtraction operator."""
        ...

    def __next__(self: Self) -> BaseIsoWeek:
        """Implementation of next operator."""
        return self + 1

    @classmethod
    def range(
        cls: Type[Self],
        start: BaseIsoWeek_T,
        end: BaseIsoWeek_T,
        step: int = 1,
        inclusive: Inclusive_T = "both",
        as_str: bool = True,
    ) -> Generator[Union[str, BaseIsoWeek], None, None]:
        """
        Generates `BaseIsoWeek` (or `str`) between `start` and `end` values with given
        `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or
        `end` week values.

        If `as_str` is flagged as `True`, it will return str values, otherwise it will
        return `BaseIsoWeek` objects.

        Arguments:
            start: starting value. It can be `BaseIsoWeek`, `date`, `datetime` or `str`
                - automatically casted to `BaseIsoWeek`
            end: ending value. It can be `BaseIsoWeek`, `date`, `datetime` or `str`
                - automatically casted to `BaseIsoWeek`
            step: step between generated values, must be positive integer
            inclusive: inclusive type, can be one of "both", "left", "right" or "neither"
            as_str: whether to return `str` or `BaseIsoWeek` object

        Returns:
            generator of `IsoWeeks`/`str` between `start` and `end` values with given
            `step`

        Raises:
            ValueError: if `start` > `end`,
                `inclusive` not one of "both", "left", "right" or "neither",
                `step` is not strictly positive
            TypeError: if `step` is not int

        Usage:
        ```python
        from iso_week_date import IsoWeek

        tuple(IsoWeek.range(
            start="2023-W01",
            end="2023-W07",
            step=2,
            inclusive="both",
            as_str=True)
            ) # ('2023-W01', '2023-W03', '2023-W05', '2023-W07')
        ```
        """

        _start: BaseIsoWeek = cls._cast(start)
        _end: BaseIsoWeek = cls._cast(end)

        if _start > _end:
            raise ValueError(
                f"`start` must be before `end` value, found: {_start} > {_end}"
            )

        if not isinstance(step, int):
            raise TypeError(f"`step` must be integer, found {type(step)}")

        if step < 1:
            raise ValueError(
                f"`step` value must be greater than or equal to 1, found {step}"
            )

        if inclusive not in _inclusive_values:
            raise ValueError(
                f"Invalid `inclusive` value. Must be one of {_inclusive_values}"
            )

        _delta = _end - _start
        range_start = 0 if inclusive in ("both", "left") else 1
        range_end = _delta + 1 if inclusive in ("both", "right") else _delta

        weeks_range: Generator[Union[str, BaseIsoWeek], None, None] = (
            (_start + i).to_string() if as_str else _start + i
            for i in range(range_start, range_end, step)
        )

        return weeks_range
