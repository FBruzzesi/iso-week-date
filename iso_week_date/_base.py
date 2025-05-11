from __future__ import annotations

import re
from abc import ABC
from abc import abstractmethod
from datetime import date
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Generator
from typing import Iterable
from typing import Literal
from typing import overload

from iso_week_date._utils import classproperty
from iso_week_date._utils import format_err_msg
from iso_week_date._utils import weeks_of_year

if TYPE_CHECKING:
    from typing_extensions import Self


class InclusiveEnum(str, Enum):
    """Enum describing the Inclusive values."""

    both = "both"
    left = "left"
    right = "right"
    neither = "neither"


_inclusive_values = tuple(e.value for e in InclusiveEnum)


class BaseIsoWeek(ABC):
    """Base abstract class for `IsoWeek` and `IsoWeekDate` classes.

    It defines the common interface for both classes and implements the common methods between them.

    Attributes:
        value_: stores the string value representing the iso-week date in the `_format` format.
        offset_: class variable, stores the offset to be used when converting to and from `datetime` and `date` objects.
        _pattern: class variable, stores the regex pattern to validate iso-week string format. Semiprivate, do not use
            it directly.
        _format: class variable, stores the string format of the iso-week date. Semiprivate, do not use it directly.
        _date_format: class variable, stores the string format with datetime conventions. Semiprivate, do not use it
            directly.
    """

    # class attributes

    offset_: ClassVar[timedelta] = timedelta(days=0)
    _pattern: ClassVar[re.Pattern[str]]
    _format: ClassVar[str]
    _date_format: ClassVar[str]

    __slots__ = ("value_",)

    # dunder methods

    def __init_subclass__(cls: type[Self], /, *args: str, **kwargs: str) -> None:
        """Prevents subclassing `BaseIsoWeek` if required class attributes are not set."""
        cls_vars = ("_pattern", "_format", "_date_format")

        missing_vars = [var for var in cls_vars if not hasattr(cls, var)]
        if missing_vars:
            msg = f"The following class attributes are missing: {missing_vars}"
            raise ValueError(msg)

        super().__init_subclass__(*args, **kwargs)

    def __init__(self: Self, value: str) -> None:
        """Initializes `BaseIsoWeek` object from iso-week string.

        Arguments:
            value: ISO Week string to initialize `BaseIsoWeek` object, must match the `_pattern` pattern of the class,
                otherwise a `ValueError` will be raised.

        Raises:
            ValueError: If `value` does not match the `_pattern` pattern of the class.
        """
        self.value_ = self._validate(value)

    @classmethod
    def _validate(cls: type[Self], value: str) -> str:
        """Validates iso-week string format against `_pattern`."""
        _match = re.match(cls._pattern, value)

        if not _match:
            raise ValueError(format_err_msg(cls._format, value))

        year, week = int(_match.group(1)), int(_match.group(2)[1:])

        if weeks_of_year(year) < week:
            msg = f"Invalid week number. Year {year} has only {weeks_of_year(year)} weeks."
            raise ValueError(msg)

        return value

    def __repr__(self: Self) -> str:
        return f"{self.name}({self.value_}) with offset {self.offset_}"

    def __str__(self: Self) -> str:
        return self.value_

    def __hash__(self: Self) -> int:
        return hash((self.value_, self.offset_))

    def __next__(self: Self) -> Self:
        return self + 1

    def __eq__(self: Self, other: object) -> bool:
        return isinstance(other, self.__class__) and (self.offset_ == other.offset_) and (self.value_ == other.value_)

    def __ne__(self: Self, other: object) -> bool:
        return not self.__eq__(other)

    def __lt__(self: Self, other: Self | object) -> bool:
        if isinstance(other, self.__class__):
            if self.offset_ == other.offset_:
                return self.value_ < other.value_
            else:
                msg = f"Cannot compare `{self.name}`'s with different offsets"
                raise TypeError(msg)
        else:
            msg = (
                f"Cannot compare `{self.name}` with type `{type(other)}`, comparison is supported only with other "
                f"`{self.name}` objects"
            )
            raise TypeError(msg)

    def __le__(self: Self, other: Self | object) -> bool:
        if isinstance(other, self.__class__):
            if self.offset_ == other.offset_:
                return self.value_ <= other.value_
            else:
                msg = f"Cannot compare `{self.name}`'s with different offsets"
                raise TypeError(msg)
        else:
            msg = (
                f"Cannot compare `{self.name}` with type `{type(other)}`, comparison is supported only with other "
                f"`{self.name}` objects"
            )
            raise TypeError(msg)

    def __gt__(self: Self, other: Self | object) -> bool:
        return not self.__le__(other)

    def __ge__(self: Self, other: Self | object) -> bool:
        return not self.__lt__(other)

    # properties

    @classproperty
    def _compact_pattern(  # type: ignore[misc]
        cls: type[Self],  # noqa: N805
    ) -> re.Pattern[str]:
        """Returns compiled compact pattern."""
        return re.compile(cls._pattern.pattern.replace(")-(", ")("))  # pragma: no cover

    @classproperty
    def _compact_format(  # type: ignore[misc]
        cls: type[Self],  # noqa: N805
    ) -> str:
        """Returns compact format as string."""
        return cls._format.replace("-", "")

    @property
    def name(self: Self) -> str:
        """Returns class name."""
        return self.__class__.__name__

    @property
    def year(self: Self) -> int:
        return int(self.value_[:4])

    @property
    def week(self: Self) -> int:
        return int(self.value_[6:8])

    @property
    def quarter(self: Self) -> int:
        return min((self.week - 1) // 13 + 1, 4)

    # from_* methods

    @classmethod
    def from_string(cls: type[Self], _str: str) -> Self:
        """Parse a string object in `_pattern` format."""
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)
        return cls(_str)

    @classmethod
    def from_compact(cls: type[Self], _str: str) -> Self:
        """Parse a string object in `_compact_format` format.

        Since values are validated in the initialization method, our goal in this method is to "add" the dashes in the
        appropriate places. To achieve this we:

        - First check that the length of the string is correct (either 7 or 8).
        - Split the string in 3 parts.
        - Remove (filter) empty values.
        - Finally join them with a dash in between.
        """
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)

        if len(_str) != len(cls._compact_format):
            raise ValueError(format_err_msg(cls._compact_format, _str))

        split_idx = (0, 4, 7, None)
        value = "-".join(filter(None, (_str[i:j] for i, j in zip(split_idx[:-1], split_idx[1:]))))
        return cls(value)

    @classmethod
    def from_date(cls: type[Self], _date: date) -> Self:
        """Parse a date object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_date, date):
            msg = f"Expected `date` type, found {type(_date)}"
            raise TypeError(msg)

        new_instance = cls.__new__(cls)
        new_instance.value_ = (_date - cls.offset_).strftime(cls._date_format)
        return new_instance

    @classmethod
    def from_datetime(cls: type[Self], _datetime: datetime) -> Self:
        """Parse a datetime object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_datetime, datetime):
            msg = f"Expected `datetime` type, found {type(_datetime)}"
            raise TypeError(msg)

        new_instance = cls.__new__(cls)
        new_instance.value_ = (_datetime - cls.offset_).strftime(cls._date_format)
        return new_instance

    @classmethod
    @abstractmethod
    def from_today(cls: type[Self]) -> Self:
        """Instantiates class from today's date."""
        return cls.from_date(date.today())

    @classmethod
    def _cast(cls: type[Self], value: str | date | datetime | BaseIsoWeek) -> Self:
        """Tries to cast from different types.

        - `str`: string matching `_pattern`.
        - `date`: casted to ISO Week by calling `.from_date()` method.
        - `datetime`: casted to ISO Week by calling `.from_datetime()` method.
        - `ISOWeek`-like: value will be returned as is.

        Arguments:
            value: Value to be casted to ISO Week object.

        Returns:
            `ISOWeek`-like object

        Raises:
            NotImplementedError: If `value` is not of type `str`, `date`, `datetime` or `ISOWeek`-like.
        """
        if isinstance(value, str):
            return cls.from_string(value)
        if isinstance(value, datetime):
            return cls.from_datetime(value)
        if isinstance(value, date):
            return cls.from_date(value)
        if isinstance(value, cls):
            return value

        msg = f"Cannot cast type {type(value)} into {cls.__name__}"
        raise NotImplementedError(msg)

    # to_* methods
    def to_string(self: Self) -> str:
        """Returns as a string in the classical format."""
        return self.value_

    def to_compact(self: Self) -> str:
        """Returns as a string in the compact format."""
        return self.value_.replace("-", "")

    def _to_datetime(self: Self, value: str) -> datetime:
        """Converts `value` to `datetime` object and adds the `offset_`.

        !!! warning
            `value` must be in "%G-W%V-%u" format.

            In general this is not always the case and we need to manipulate `value_` attribute before passing it to
            `datetime.strptime` method.
        """
        return datetime.strptime(value, "%G-W%V-%u") + self.offset_

    def to_values(self: Self) -> tuple[int, ...]:
        """Converts `value_` to a tuple of integers (year, week, [weekday])."""
        return tuple(int(v.replace("W", "")) for v in self.value_.split("-"))

    @overload
    def __add__(self: Self, other: int) -> Self: ...

    @overload
    def __add__(self: Self, other: Iterable[int]) -> Generator[Self, None, None]: ...

    @overload
    def __add__(self: Self, other: int | Iterable[int]) -> Self | Generator[Self, None, None]: ...

    @abstractmethod
    def __add__(self: Self, other: int | Iterable[int]) -> Self | Generator[Self, None, None]:
        """Implementation of addition operator."""
        ...

    def next(self: Self) -> Self:
        """Method equivalent of adding 1 to the current value."""
        return self + 1

    @overload
    def __sub__(self: Self, other: int) -> Self: ...

    @overload
    def __sub__(self: Self, other: Self) -> int: ...

    @overload
    def __sub__(self: Self, other: Iterable[int]) -> Generator[Self, None, None]: ...

    @overload
    def __sub__(self: Self, other: Iterable[Self]) -> Generator[int, None, None]: ...

    @overload
    def __sub__(
        self: Self, other: int | Self | Iterable[int | Self]
    ) -> int | Self | Generator[int | Self, None, None]: ...

    @abstractmethod
    def __sub__(self: Self, other: int | Self | Iterable[int | Self]) -> int | Self | Generator[int | Self, None, None]:
        """Implementation of subtraction operator."""
        ...

    def previous(self: Self) -> Self:
        """Method equivalent of subtracting 1 to the current value."""
        return self - 1

    def is_before(self: Self, other: Self | object) -> bool:
        """Checks if `self` is before `other`.

        Arguments:
            other: Other object to compare with.

        Returns:
            True if `self` is before `other`, False otherwise.
        """
        return self < other

    def is_after(self: Self, other: Self | object) -> bool:
        """Checks if `self` is after `other`.

        Arguments:
            other: Other object to compare with.

        Returns:
            True if `self` is after `other`, False otherwise.
        """
        return self > other

    def is_between(
        self: Self,
        lower_bound: Self,
        upper_bound: Self,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
    ) -> bool:
        """Cbeck if `self` is between `lower_bound` and `upper_bound`.

        Arguments:
            lower_bound: Lower bound to compare with.
            upper_bound: Upper bound to compare with.
            inclusive: Inclusive type, can be one of "both", "left", "right" or "neither".

        Returns:
            True if `self` is between `lower_bound` and `upper_bound`, False otherwise.
        """
        if inclusive not in _inclusive_values:  # pragma: no cover
            msg = f"Invalid `inclusive` value. Must be one of {_inclusive_values}"
            raise ValueError(msg)

        if inclusive == "both":  # noqa: SIM116
            return lower_bound <= self <= upper_bound
        elif inclusive == "left":
            return lower_bound <= self < upper_bound
        elif inclusive == "right":
            return lower_bound < self <= upper_bound
        else:
            return lower_bound < self < upper_bound

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: str | date | datetime | Self,
        end: str | date | datetime | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: Literal[True],
    ) -> Generator[str, None, None]: ...

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: str | date | datetime | Self,
        end: str | date | datetime | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: Literal[False],
    ) -> Generator[Self, None, None]: ...

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: str | date | datetime | Self,
        end: str | date | datetime | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: bool = True,
    ) -> Generator[str | Self, None, None]: ...

    @classmethod
    def range(
        cls: type[Self],
        start: str | date | datetime | Self,
        end: str | date | datetime | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: bool = True,
    ) -> Generator[str | Self, None, None]:
        """Generates `BaseIsoWeek` (or `str`) between `start` and `end` values with given `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or `end` week values.

        If `as_str` is flagged as `True`, it will return str values, otherwise it will return `BaseIsoWeek` objects.

        Arguments:
            start: Starting value. It can be `BaseIsoWeek`, `date`, `datetime` or `str`.
            end: Ending value. It can be `BaseIsoWeek`, `date`, `datetime` or `str`.
            step: Step between generated values, must be positive integer.
            inclusive: Inclusive type, can be one of "both", "left", "right" or "neither".
            as_str: Whether to return `str` or `BaseIsoWeek` object.

        Returns:
            Generator of `IsoWeeks`/`str` between `start` and `end` values with given `step`.

        Raises:
            ValueError: If any of the following conditions is met:

                - `start > end`.
                - `inclusive` not one of "both", "left", "right" or "neither".
                - `step` is not strictly positive.
            TypeError: If `step` is not an int.
        """
        _start = cls._cast(start)
        _end = cls._cast(end)

        if _start > _end:
            msg = f"`start` must be before `end` value, found: {_start} > {_end}"
            raise ValueError(msg)

        if not isinstance(step, int):
            msg = f"`step` must be integer, found {type(step)}"
            raise TypeError(msg)

        if step < 1:
            msg = f"`step` value must be greater than or equal to 1, found {step}"
            raise ValueError(msg)

        if inclusive not in _inclusive_values:
            msg = f"Invalid `inclusive` value. Must be one of {_inclusive_values}"
            raise ValueError(msg)

        _delta = _end - _start
        range_start = 0 if inclusive in {"both", "left"} else 1
        range_end = _delta + 1 if inclusive in {"both", "right"} else _delta

        weeks_range: Generator[str | Self, None, None] = (
            (_start + i).to_string() if as_str else _start + i for i in range(range_start, range_end, step)
        )

        return weeks_range
