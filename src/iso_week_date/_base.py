from __future__ import annotations

import re
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from enum import Enum
from itertools import pairwise
from typing import TYPE_CHECKING, ClassVar, Literal, overload

from iso_week_date._utils import classproperty, format_err_msg, is_int, match_isoweek, weeks_of_year

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable
    from datetime import tzinfo

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

    Note:
        Values are backed by `datetime.date`, so the representable range is ISO years `0001` to
        `9999`. Arithmetic that steps outside it surfaces the standard library's own error rather than
        a domain one: `OverflowError` from `timedelta` (`next`, `previous`, `+`, `-`, `weeksout`,
        `daysout`) and `ValueError` from `strptime` (`days`, `nth`, `to_date`, `to_datetime`). This is
        left as is on purpose: a bounds check on every arithmetic call would cost every caller
        something to protect a range essentially nobody reaches.

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
        if (parsed := match_isoweek(cls._pattern, value)) is None:
            raise ValueError(format_err_msg(cls._format, value))

        year, week = parsed

        if (weeks_in_year := weeks_of_year(year)) < week:
            msg = f"Invalid week number. Year {year} has only {weeks_in_year} weeks."
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
    def _compact_pattern(cls: type[Self]) -> re.Pattern[str]:  # type: ignore[misc] # noqa: N805
        """Returns compiled compact pattern.

        Derived from `_pattern` by dropping the dashes between its groups, so the two cannot drift
        apart. `re.compile` caches internally, so repeated access returns the same object.
        """
        return re.compile(cls._pattern.pattern.replace(")-(", ")("))

    @classproperty
    def _compact_format(cls: type[Self]) -> str:  # type: ignore[misc]  # noqa: N805
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
    def from_string(cls: type[Self], _str: str, /) -> Self:
        """Parse a string object in `_pattern` format."""
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)
        return cls(_str)

    @classmethod
    def from_compact(cls: type[Self], _str: str, /) -> Self:
        """Parse a string object in `_compact_format` format.

        Since values are validated in the initialization method, our goal in this method is to "add" the dashes in the
        appropriate places. To achieve this we:

        * First check that the string matches `_compact_pattern`.
        * Split the string in 3 parts.
        * Remove (filter) empty values.
        * Finally join them with a dash in between.

        Matching `_compact_pattern` rather than only checking the length reports a malformed value in
        terms of the compact format the caller actually passed. Left to the dashed `_validate`, a
        value such as `"2025W0x"` was rejected against the `YYYY-WNN` pattern instead. The week
        number is still checked against the year's week count by `__init__`.
        """
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)

        compact_format = cls._compact_format
        if match_isoweek(cls._compact_pattern, _str) is None:
            msg = format_err_msg(compact_format, _str)
            raise ValueError(msg)

        split_idx = (0, 4, 7, None)
        value = "-".join(filter(None, (_str[i:j] for i, j in pairwise(split_idx))))
        return cls(value)

    @classmethod
    def from_date(cls: type[Self], _date: date, /) -> Self:
        """Parse a date object to `_format` after adjusting by `offset_`."""
        if not isinstance(_date, date):
            msg = f"Expected `date` type, found {type(_date)}"
            raise TypeError(msg)

        new_instance = cls.__new__(cls)
        new_instance.value_ = cls._format_isocalendar(_date - cls.offset_)
        return new_instance

    @classmethod
    def from_datetime(cls: type[Self], _datetime: datetime, /) -> Self:
        """Parse a datetime object to `_format` after adjusting by `offset_`."""
        if not isinstance(_datetime, datetime):
            msg = f"Expected `datetime` type, found {type(_datetime)}"
            raise TypeError(msg)

        new_instance = cls.__new__(cls)
        new_instance.value_ = cls._format_isocalendar(_datetime - cls.offset_)
        return new_instance

    @classmethod
    def _format_isocalendar(cls: type[Self], _date: date, /) -> str:
        """Renders `_date` in the `_format` of the class, from its ISO calendar components.

        The components are zero-padded here rather than delegated to `strftime("%G")`, because
        `%G` padding is platform dependent: on glibc with Python < 3.14, `date(1, 1, 1)` renders as
        `"1-W01"` instead of `"0001-W01"`. Since `from_date`/`from_datetime` build the instance via
        `cls.__new__` and deliberately skip `_validate`, such a value would be stored unchecked and
        only surface later as a confusing failure in `year`, `to_values()` or `to_compact()`.
        """
        year, week, weekday = _date.isocalendar()
        return cls._format.replace("YYYY", f"{year:04d}").replace("NN", f"{week:02d}").replace("D", str(weekday))

    @classmethod
    @abstractmethod
    def from_today(cls: type[Self], time_zone: tzinfo | None = None) -> Self:
        """Instantiates class from today's date."""

    @classmethod
    def _cast(cls: type[Self], value: str | date | datetime | Self) -> Self:
        """Tries to cast from different types.

        * `str`: string matching `_pattern`.
        * `date`: casted to ISO Week by calling `.from_date()` method.
        * `datetime`: casted to ISO Week by calling `.from_datetime()` method.
        * `ISOWeek`-like: value will be returned as is.

        Arguments:
            value: Value to be casted to ISO Week object.

        Returns:
            `ISOWeek`-like object

        Raises:
            NotImplementedError: If `value` is not of type `str`, `date`, `datetime` or `ISOWeek`-like.
        """
        match value:
            case str():
                return cls.from_string(value)
            case datetime():
                return cls.from_datetime(value)
            case date():
                return cls.from_date(value)
            case _ if isinstance(value, cls):
                return value
            case _:
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

        A `ValueError` here means the date is out of range rather than the format is wrong: `value` is
        built from an already validated `value_` and an already validated weekday. `9999-W52-7` is a
        valid ISO week date whose Sunday falls in year 10000, and a non-zero `offset_` can push a
        boundary value out the same way. See the note on year bounds in `BaseIsoWeek`.
        """
        return datetime.strptime(value, "%G-W%V-%u") + self.offset_

    def to_values(self: Self) -> tuple[int, ...]:
        """Converts `value_` to a tuple of integers (year, week, [weekday])."""
        return tuple(int(v.replace("W", "")) for v in self.value_.split("-"))

    @overload
    @abstractmethod
    def __add__(self: Self, other: int) -> Self: ...

    @overload
    @abstractmethod
    def __add__(self: Self, other: Iterable[int]) -> Generator[Self, None, None]: ...

    @overload
    @abstractmethod
    def __add__(self: Self, other: int | Iterable[int]) -> Self | Generator[Self, None, None]: ...

    @abstractmethod
    def __add__(self: Self, other: int | Iterable[int]) -> Self | Generator[Self, None, None]:
        """Implementation of addition operator."""
        ...

    def next(self: Self) -> Self:
        """Method equivalent of adding 1 to the current value."""
        return self + 1

    @overload
    @abstractmethod
    def __sub__(self: Self, other: int) -> Self: ...

    @overload
    @abstractmethod
    def __sub__(self: Self, other: Self) -> int: ...

    @overload
    @abstractmethod
    def __sub__(self: Self, other: Iterable[int]) -> Generator[Self, None, None]: ...

    @overload
    @abstractmethod
    def __sub__(self: Self, other: Iterable[Self]) -> Generator[int, None, None]: ...

    @overload
    @abstractmethod
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
        """Check if `self` is between `lower_bound` and `upper_bound`.

        Arguments:
            lower_bound: Lower bound to compare with.
            upper_bound: Upper bound to compare with.
            inclusive: Inclusive type, can be one of "both", "left", "right" or "neither".

        Returns:
            True if `self` is between `lower_bound` and `upper_bound`, False otherwise.
        """
        match inclusive:
            case "both":
                return lower_bound <= self <= upper_bound
            case "left":
                return lower_bound <= self < upper_bound
            case "right":
                return lower_bound < self <= upper_bound
            case "neither":
                return lower_bound < self < upper_bound
            case _:  # pragma: no cover
                msg = f"Invalid `inclusive` value. Must be one of {_inclusive_values}"
                raise ValueError(msg)

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: str | date | datetime | Self,
        end: str | date | datetime | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: Literal[True] = True,
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

                * `start > end`.
                * `inclusive` not one of "both", "left", "right" or "neither".
                * `step` is not strictly positive.
            TypeError: If `step` is not an int (`bool` is not accepted).

        Examples:
            The generated values sit on a grid anchored at `start`, and `inclusive` removes the two
            endpoints from it. With `step` greater than 1 the grid may not land on `end` at all, in
            which case there is no `end` for `inclusive` to keep or drop:

            >>> from iso_week_date import IsoWeek
            >>>
            >>> tuple(IsoWeek.range("2025-W01", "2025-W05", step=2, inclusive="both"))
            ('2025-W01', '2025-W03', '2025-W05')
            >>> tuple(IsoWeek.range("2025-W01", "2025-W05", step=2, inclusive="left"))
            ('2025-W01', '2025-W03')
            >>> tuple(IsoWeek.range("2025-W01", "2025-W05", step=2, inclusive="right"))
            ('2025-W03', '2025-W05')
            >>> tuple(IsoWeek.range("2025-W01", "2025-W05", step=2, inclusive="neither"))
            ('2025-W03',)
            >>> tuple(IsoWeek.range("2025-W01", "2025-W06", step=2, inclusive="right"))
            ('2025-W03', '2025-W05')
        """
        _start = cls._cast(start)
        _end = cls._cast(end)

        if _start > _end:
            msg = f"`start` must be before `end` value, found: {_start} > {_end}"
            raise ValueError(msg)

        if not is_int(step):
            msg = f"`step` must be integer, found {type(step)}"
            raise TypeError(msg)

        if step < 1:
            msg = f"`step` value must be greater than or equal to 1, found {step}"
            raise ValueError(msg)

        if inclusive not in _inclusive_values:
            msg = f"Invalid `inclusive` value. Must be one of {_inclusive_values}"
            raise ValueError(msg)

        _delta = _end - _start

        # The grid is anchored at `start` and stepped from there, and `inclusive` then filters the
        # two endpoints out of it. Moving the anchor instead (`range(1, ...)` for a start-exclusive
        # call) shifted every generated value off the grid, so `inclusive="right"` dropped `end`
        # along with `start` for any `step > 1` and never honoured the endpoint it names.
        skip_start = inclusive in {"right", "neither"}
        skip_end = inclusive in {"left", "neither"}

        weeks_range: Generator[str | Self, None, None] = (
            (_start + i).to_string() if as_str else _start + i
            for i in range(0, _delta + 1, step)
            if not (skip_start and i == 0) and not (skip_end and i == _delta)
        )

        return weeks_range
