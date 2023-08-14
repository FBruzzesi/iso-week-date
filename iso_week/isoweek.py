from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import (
    Any,
    ClassVar,
    Dict,
    Final,
    Generator,
    Iterable,
    List,
    Literal,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    overload,
)

import numpy as np
import pandas as pd

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

IsoWeek_T = TypeVar("IsoWeek_T", date, datetime, str, "IsoWeek")

InclusiveType = Literal["both", "left", "right", "neither"]
_inclusive_values = get_args(InclusiveType)

ReturnType = Literal["dict", "generator", "list", "set", "tuple", "pandas", "numpy"]
_return_values = get_args(ReturnType)

RETURN_TYPE_TO_FUNC = {
    "dict": lambda t: {i: e for i, e in enumerate(t)},
    "generator": lambda t: t,
    "list": list,
    "set": set,
    "tuple": tuple,
    "pandas": pd.Series,
    "numpy": np.array,
}

WeekRangeType = Union[
    Dict[int, "IsoWeek"],
    Generator["IsoWeek", None, None],
    List["IsoWeek"],
    Set["IsoWeek"],
    Tuple["IsoWeek", ...],
    pd.Series,
    np.ndarray,
]

ISOWEEK_PATTERN: Final[re.Pattern] = re.compile(r"^(\d{4})-W(\d{2})$")


class IsoWeek:
    """
    Represents IsoWeek date format and implement multiple methods to work directly
    with it instead of going back and forth between date, datetime and string types.

    Attributes:
        value: iso-week string of format "YYYY-WXY" where XY is a week number between
            0 and 53
    """

    _offset: ClassVar[timedelta] = timedelta(days=0)
    __slots__ = ("value",)

    def __init__(self: Self, value: str) -> None:
        self.value = self._validate(value)

    @property
    def week(self: Self) -> int:
        """Week number"""
        return int(self.value[-2:])

    @property
    def year(self: Self) -> int:
        """Year number"""
        return int(self.value[:4])

    def __repr__(self: Self) -> str:
        """Representation"""
        return f"IsoWeek({self.value}) with offset {self._offset}"

    def __str__(self: Self) -> str:
        """String representation"""
        return self.value

    def __eq__(self: Self, other: Any) -> bool:
        """Equality operator"""
        if isinstance(other, IsoWeek):
            return self._offset == other._offset and self.value == other.value
        else:
            return False

    def __ne__(self: Self, other: Any) -> bool:
        """Inequality operator"""
        return not self.__eq__(other)

    def __lt__(self: Self, other: IsoWeek) -> bool:
        """Less than operator"""
        if self._offset == other._offset:
            return self.value < other.value
        else:
            raise TypeError("Cannot compare IsoWeeks with different offsets")

    def __le__(self: Self, other: IsoWeek) -> bool:
        """Less than or equal operator"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self: Self, other: IsoWeek) -> bool:
        """Greater than operator"""
        return not self.__le__(other)

    def __ge__(self: Self, other: IsoWeek) -> bool:
        """Greater than or equal operator"""
        return not self.__lt__(other)

    def _validate(self: Self, value: str) -> str:
        """
        Validate week format, must match "YYYY-WXY" pattern where XY is a week number
        between 0 and 53.

        Arguments:
            value: iso-week string to validate

        Returns:
            unchanged value if string is valid

        Raises:
            ValueError: if string format is invalid or week number is out of range
        """
        _match = re.match(ISOWEEK_PATTERN, value)

        if not _match:
            raise ValueError(
                f"Invalid week format: {value}. Make sure that it matches "
                "'YYYY-WXY' pattern"
            )

        if not 0 <= int(_match.group(2)) <= 53:
            raise ValueError(f"Invalid week number: {_match.group(2)}")

        return value

    def to_str(self: Self) -> str:
        """Convert IsoWeek to string object"""
        return str(self)

    def to_datetime(self: Self, weekday: int = 1) -> datetime:
        """Convert IsoWeek to datetime object"""
        if weekday not in range(1, 8):
            raise ValueError(f"Invalid weekday: {weekday}")

        return datetime.strptime(f"{self.value}-{weekday}", "%G-W%V-%u") + self._offset

    def to_date(self: Self, weekday: int = 1) -> date:
        """Convert IsoWeek to date object"""
        return self.to_datetime(weekday).date()

    @classmethod
    def from_str(cls: Type[IsoWeek], _str: str) -> IsoWeek:
        """Create IsoWeek from string object"""
        return cls(_str)

    @classmethod
    def from_datetime(cls: Type[IsoWeek], _datetime: datetime) -> IsoWeek:
        """Create IsoWeek from datetime object"""
        year, week, _ = (_datetime - cls._offset).isocalendar()
        return cls(f"{year}-W{week:02d}")

    @classmethod
    def from_date(cls: Type[IsoWeek], _date: date) -> IsoWeek:
        """Create IsoWeek from date object"""
        year, week, _ = (_date - cls._offset).isocalendar()
        return cls(f"{year}-W{week:02d}")

    @classmethod
    def from_today(cls: Type[IsoWeek]) -> IsoWeek:
        """Create IsoWeek from today's date"""
        return cls.from_date(date.today())

    def __add__(self: Self, other: int | timedelta) -> IsoWeek:
        """
        It supports addition with the following two types:

        - int: interpreted as number of weeks to be added to the IsoWeek value
        - timedelta: converts IsoWeek to datetime, adds timedelta and converts back to
            IsoWeek object

        Raises:
            TypeError: if `other` is not int or timedelta
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(weeks=other))
        elif isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() + other)
        else:
            raise TypeError(
                f"Cannot add type {type(other)}, only int and timedelta are supported"
            )

    @overload
    def __sub__(self: Self, other: int) -> IsoWeek:
        ...

    @overload
    def __sub__(self: Self, other: IsoWeek) -> int:
        ...

    def __sub__(self: Self, other):
        """
        It supports substraction with the following two types:

        - int: interpreted as number of weeks to be subtracted to the IsoWeek value
        - IsoWeek: will result in the difference between values in weeks (int type)

        Raises:
            TypeError: if `other` is not int or IsoWeek
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(weeks=other))
        elif isinstance(other, IsoWeek):
            return (self.to_date() - other.to_date()).days // 7
        else:
            raise TypeError(f"Cannot subtract type {type(other)}")

    @classmethod
    def _automatic_cast(cls: Type[IsoWeek], value: IsoWeek_T) -> IsoWeek:
        """
        Automatic cast to IsoWeek type from the following possible types:

        - str: value must match "YYYY-WXY" pattern where XY is a week number
            between 0 and 53.
        - date: value will be converted to IsoWeek
        - datetime: value will be converted to IsoWeek
        - IsoWeek: value will be returned as is
        """
        if isinstance(value, str):
            return cls(value)
        elif isinstance(value, date):
            return cls.from_date(value)
        elif isinstance(value, datetime):
            return cls.from_datetime(value)
        elif isinstance(value, cls):
            return value
        else:
            raise NotImplementedError(f"Cannot cast type {type(value)} into IsoWeek")

    def weeksout(
        self: Self,
        n_weeks: int,
        step: int = 1,
        inclusive: InclusiveType = "both",
        return_type: ReturnType = "tuple",
        as_str: bool = True,
    ) -> WeekRangeType:
        """Return tuple of n_weeks IsoWeeks ahead of value"""
        week_start, week_end = (self + 0), (self + n_weeks)
        return self.range(week_start, week_end, step, inclusive, return_type, as_str)

    @classmethod
    def range(
        cls: Type[IsoWeek],
        week_start: IsoWeek_T,
        week_end: IsoWeek_T,
        step: int = 1,
        inclusive: InclusiveType = "both",
        return_type: ReturnType = "tuple",
        as_str: bool = True,
    ) -> WeekRangeType:
        """
        Return tuple of IsoWeeks between start and end weeks.

        Arguments:
            week_start: start week, can be IsoWeek, date, datetime or str
            week_end: end week, can be IsoWeek, date, datetime or str
            step: step between weeks, must be positive integer
            inclusive: inclusive type, can be "both", "left", "right" or "neither"
            return_type: return type, can be "dict", "generator", "list", "set", "tuple",
                "pandas", "numpy"
            as_str: whether to return str or IsoWeek object

        Returns:
            tuple of IsoWeeks between start and end weeks

        Raises:
            ValueError: if week_start > week_end or inclusive is invalid
        """

        _week_start: IsoWeek = cls._automatic_cast(week_start)
        _week_end: IsoWeek = cls._automatic_cast(week_end)

        if week_start > week_end:
            raise ValueError(f"Invalid range: {_week_start} > {_week_end}")

        if not isinstance(step, int):
            raise TypeError(f"Step must be integer type. Found {type(step)} instead")

        if step < 1:
            raise ValueError("Invalid step value. Must be greater than or equal to 1")

        if inclusive not in _inclusive_values:
            raise ValueError(
                f"Invalid inclusive value: {inclusive}. "
                f"Must be one of {_inclusive_values}"
            )

        if return_type not in _return_values:
            raise ValueError(
                f"Invalid return type: {return_type}. Must be one of {_return_values}"
            )

        weeks_delta = _week_end - _week_start
        _start = 0 if inclusive in ("both", "left") else 1
        _end = weeks_delta + 1 if inclusive in ("both", "right") else weeks_delta

        weeks_range = (
            (_week_start + i).to_str() if as_str else _week_start + i
            for i in range(_start, _end, step)
        )

        _func = RETURN_TYPE_TO_FUNC[return_type]
        return _func(weeks_range)

    def __contains__(self: Self, other: Any) -> bool:
        """
        Check if self contains other.

        Arguments:
            other: IsoWeek, date, datetime or str

        Returns:
            bool: True if self contains other, False otherwise

        Raises:
            TypeError: if other is not IsoWeek, date, datetime or str
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            _other = self._automatic_cast(other)
            return self.__eq__(_other)
        else:
            raise TypeError(f"Cannot compare type {type(other)}")

    @overload
    def contains(self: Self, other: IsoWeek_T) -> bool:
        """Type hinting for contains method on IsoWeek possible types"""
        ...

    @overload
    def contains(self: Self, other: Iterable[IsoWeek_T]) -> Iterable[bool]:
        """Type hinting for contains method on Iterator of IsoWeek possible types"""
        ...

    def contains(self: Self, other):
        """
        Check if self contains other. Other can be a single value or an iterable of
        values. If other is an iterable, returns an iterable of bools.

        Raises:
            TypeError: if other is not IsoWeek, date, datetime or str, or an iterable
                of those types
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            return other in self
        elif isinstance(other, Iterable):
            return tuple(_other in self for _other in other)
        else:
            raise TypeError(f"Cannot compare type {type(other)}")


def datetime_to_isoweek(
    series: pd.Series, offset: pd.Timedelta | int = pd.Timedelta(days=0)
) -> pd.Series:
    """
    Convert datetime series to IsoWeek series

    Arguments:
        series: datetime series
        offset: offset in days or pd.Timedelta

    Returns:
        IsoWeek series
    """
    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset
    return (series + _offset).dt.strftime("%G-W%V")


def isoweek_to_datetime(
    series: pd.Series, offset: pd.Timedelta | int = pd.Timedelta(days=0), weekday: int = 1
) -> pd.Series:
    """
    Convert IsoWeek series to datetime series

    Arguments:
        series: IsoWeek series
        offset: offset in days or pd.Timedelta
        weekday: weekday to use for conversion

    Returns:
        datetime series
    """

    _offset = pd.Timedelta(days=offset) if isinstance(offset, int) else offset

    return pd.to_datetime(series + "-" + f"{weekday}", format="%G-W%V-%w") + _offset
