from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from typing import Any, ClassVar, Generator, Literal, Type, TypeVar, Union

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

BaseIsoWeek_T = TypeVar("BaseIsoWeek_T", str, date, datetime, "_BaseIsoWeek")


class InclusiveEnum(str, Enum):
    """Inclusive enum"""

    both = "both"
    left = "left"
    right = "right"
    neither = "neither"


_inclusive_values = tuple(e.value for e in InclusiveEnum)
Inclusive_T = Literal[_inclusive_values]  # type: ignore


class _BaseIsoWeek(ABC):
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
        offset_: class variable, stores the offset to be used when converting to
            and from `datetime` and `date` objects
    """

    _pattern: ClassVar[re.Pattern]
    _format: ClassVar[str]
    offset_: ClassVar[timedelta] = timedelta(days=0)

    __slots__ = ("value_",)

    def __init__(self: Self, value: str, __validate: bool = True) -> None:
        """
        Initializes `IsoWeek` object from iso-week string.

        Arguments:
            value: iso-week string to initialize `IsoWeek` object
            __validate: whether to validate iso-week string format or not
        """
        self.value_ = self.validate(value) if __validate else value

    @classmethod
    def validate(cls: Type[Self], value: str) -> str:
        """Validates iso-week string format."""
        _match = re.match(cls._pattern, value)

        if not _match:
            raise ValueError(
                "Invalid isoweek date format. "
                f"Format must match the '{cls._format}' pattern, "
                "where:"
                "\n- YYYY is a year between 0001 and 9999"
                "\n- W is a literal character"
                "\n- NN is a week number between 1 and 53"
                "\n- D is a day number between 1 and 7"
                f"\n but found {value}"
            )

        return value

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
        """Returns pattern."""
        return self._pattern.pattern

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

    def __eq__(self: Self, other: Any) -> bool:
        """
        Equality operator.

        Two `_BaseIsoWeek` objects are considered equal if and only if they have the same
        offset and the same value.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are equal, `False` otherwise

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") == IsoWeek("2023-W01")  # True
        IsoWeek("2023-W01") == IsoWeek("2023-W02")  # False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") == CustomIsoWeek("2023-W01")  # False
        ```
        """
        if isinstance(other, self.__class__):
            return self.offset_ == other.offset_ and self.value_ == other.value_
        else:
            return False

    def __ne__(self: Self, other: Any) -> bool:
        """
        Inequality operator.

        Two `_BaseIsoWeek` objects are considered equal if and only if they have the same
        offset and the same value.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are _not_ equal, `False` otherwise

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") != IsoWeek("2023-W01")  # False
        IsoWeek("2023-W01") != IsoWeek("2023-W02")  # True

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") != CustomIsoWeek("2023-W01")  # True
        ```
        """
        return not self.__eq__(other)

    def __lt__(self: Self, other: _BaseIsoWeek) -> bool:
        """
        Less than operator.

        Comparing two `_BaseIsoWeek` objects is only possible if they have the same
        offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") < IsoWeek("2023-W02")  # True
        IsoWeek("2023-W02") < IsoWeek("2023-W01")  # False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") < CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") < "2023-W01"  # TypeError
        ```
        """
        if isinstance(other, self.__class__):
            if self.offset_ == other.offset_:
                return self.value_ < other.value_
            else:
                raise TypeError(
                    f"Cannot compare `{self.__class__}`'s with different offsets"
                )
        else:
            raise TypeError(
                f"Cannot compare `{self.__class__}` with `{type(other)}` object, "
                f"comparison is supported only with other `{self.__class__}` objects"
            )

    def __le__(self: Self, other: _BaseIsoWeek) -> bool:
        """
        Less than or equal operator.

        Comparing two `_BaseIsoWeek` objects is only possible if they have the same
        offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than or equal to other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") <= IsoWeek("2023-W01")  # True
        IsoWeek("2023-W02") <= IsoWeek("2023-W01")  # False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") <= CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") <= "2023-W01"  # TypeError
        ```
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self: Self, other: _BaseIsoWeek) -> bool:
        """Greater than operator.

        Comparing two `_BaseIsoWeek` objects is only possible if they have the same
        offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is greater than other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") >= IsoWeek("2023-W02")  # False
        IsoWeek("2023-W01") >= IsoWeek("2023-W01")  # True

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") >= CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") >= "2023-W01"  # TypeError
        ```
        """
        return not self.__le__(other)

    def __ge__(self: Self, other: _BaseIsoWeek) -> bool:
        """
        Greater than or equal operator.

        Comparing two `_BaseIsoWeek` objects is only possible if they have the same
        offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
           other: object to compare with

        Returns:
            `True` if self is greater than or equal to `other`, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") > IsoWeek("2023-W02")  # False
        IsoWeek("2023-W02") > IsoWeek("2023-W01")  # True

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") > CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") > "2023-W01"  # TypeError
        ```
        """
        return not self.__lt__(other)

    def to_str(self: Self) -> str:
        """
        Converts `_BaseIsoWeek` to `str` object. It is equivalent to: `str(iso_week_obj)`.

        Returns:
            `_BaseIsoWeek` value in string format `_format`

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_str()  # "2023-W01"
        ```
        """
        return str(self)

    def to_compact(self: Self) -> str:
        """
        Converts `_BaseIsoWeek` to `str` object in compact format, which removes the "-"
        from `_format`.

        Returns:
            `_BaseIsoWeek` value in string format without dashes ("-")

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_compact()  # "2023W01"
        ```
        """
        return str(self).replace("-", "")

    @abstractmethod
    def to_datetime(self: Self, *args, **kwargs) -> datetime:
        """Converts `_BaseIsoWeek` to `datetime` object."""
        ...

    @abstractmethod
    def to_date(self: Self, *args, **kwargs) -> date:
        """Converts `_BaseIsoWeek` to `date` object."""

    @classmethod
    def from_str(cls: Type[Self], _str: str) -> _BaseIsoWeek:
        """
        Instantiates `_BaseIsoWeek` object from `str` in format `_format`.

        Arguments:
            _str: `str` in format `_format`

        Returns:
            `_BaseIsoWeek` object

        Raises:
            TypeError: if `_str` is not a `str` object

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek.from_str("2023-W01")  # IsoWeek("2023-W01")
        ```
        """
        if not isinstance(_str, str):
            raise TypeError(f"Expected string object, found {type(_str)}")
        return cls(_str, True)

    @classmethod
    @abstractmethod
    def from_compact(cls: Type[Self], _str: str) -> _BaseIsoWeek:
        """Instantiates `_BaseIsoWeek` object from `str` in format without dashes "-"."""
        ...

    @classmethod
    @abstractmethod
    def from_datetime(cls: Type[Self], _datetime: datetime) -> _BaseIsoWeek:
        """Instantiates `_BaseIsoWeek` object from `datetime` object."""
        ...

    @classmethod
    @abstractmethod
    def from_date(cls: Type[Self], _date: date) -> _BaseIsoWeek:
        """Instantiates `_BaseIsoWeek` object from `date` object."""

    @classmethod
    def from_today(cls: Type[Self]) -> _BaseIsoWeek:  # pragma: no cover
        """Instantiates IsoWeek from today's date"""
        return cls.from_date(date.today())

    @abstractmethod
    def __add__(self: Self, other: Union[int, timedelta]) -> _BaseIsoWeek:
        """Implementation of addition operator."""
        ...

    @abstractmethod
    def __sub__(
        self: Self, other: Union[int, timedelta, _BaseIsoWeek]
    ) -> Union[int, _BaseIsoWeek]:
        """Implementation of subtraction operator."""
        ...

    @classmethod
    def _automatic_cast(cls: Type[Self], value: BaseIsoWeek_T) -> _BaseIsoWeek:
        """
        Automatically casts to `_BaseIsoWeek` type from the following possible types:

        - `str`: string matching `_pattern`, will be validated
        - `date`: casted to `_BaseIsoWeek` by calling `from_date` method
        - `datetime`: casted to `_BaseIsoWeek` by calling `from_datetime` method
        - `_BaseIsoWeek`: value will be returned as is

        Arguments:
            value: value to be casted to `_BaseIsoWeek`

        Returns:
            `_BaseIsoWeek` object

        Raises:
            NotImplementedError: if `value` is not `str`, `date`, `datetime` or
                `_BaseIsoWeek`

        Usage:
        ```py
        from datetime import date
        from iso_week_date import IsoWeek

        IsoWeek._automatic_cast("2023-W01")  # IsoWeek("2023-W01")
        ```
        """
        if isinstance(value, str):
            return cls.from_str(value)
        elif isinstance(value, datetime):
            return cls.from_datetime(value)
        elif isinstance(value, date):
            return cls.from_date(value)
        elif isinstance(value, cls):
            return value
        else:
            raise NotImplementedError(f"Cannot cast type {type(value)} into IsoWeek")

    @classmethod
    def range(
        cls: Type[Self],
        start: BaseIsoWeek_T,
        end: BaseIsoWeek_T,
        step: int = 1,
        inclusive: Inclusive_T = "both",
        as_str: bool = True,
    ) -> Generator[Union[str, _BaseIsoWeek], None, None]:
        """
        Generates `_BaseIsoWeek` (or `str`) between `start` and `end` values with given
        `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or
        `end` week values.

        If `as_str` is flagged as `True`, it will return str values, otherwise it will
        return `_BaseIsoWeek` objects.

        Arguments:
            start: starting value. It can be `_BaseIsoWeek`, `date`, `datetime` or `str`
                - automatically casted to `_BaseIsoWeek`
            end: ending value. It can be `_BaseIsoWeek`, `date`, `datetime` or `str`
                - automatically casted to `_BaseIsoWeek`
            step: step between generated values, must be positive integer
            inclusive: inclusive type, can be one of "both", "left", "right" or "neither"
            as_str: whether to return `str` or `_BaseIsoWeek` object

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

        _start: _BaseIsoWeek = cls._automatic_cast(start)
        _end: _BaseIsoWeek = cls._automatic_cast(end)

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

        weeks_range = (
            (_start + i).to_str() if as_str else _start + i
            for i in range(range_start, range_end, step)
        )

        return weeks_range
