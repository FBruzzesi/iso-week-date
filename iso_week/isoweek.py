from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import (
    Any,
    ClassVar,
    Final,
    Generator,
    Iterable,
    Literal,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    overload,
)

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

IsoWeek_T = TypeVar("IsoWeek_T", date, datetime, str, "IsoWeek")

InclusiveType = Literal["both", "left", "right", "neither"]
_inclusive_values = get_args(InclusiveType)

ISOWEEK_PATTERN: Final[re.Pattern] = re.compile(r"^(\d{4})-W(\d{2})$")
COMPACT_PATTERN: Final[re.Pattern] = re.compile(r"^(\d{4})W(\d{2})$")


class IsoWeek:
    """
    Represents IsoWeek date format and implement multiple methods to work directly
    with it instead of going back and forth between date, datetime and string types.

    Attributes:
        value: iso-week string of format "YYYY-WNN" where NN is a week number between
            01 and 53
    """

    _offset: ClassVar[timedelta] = timedelta(days=0)
    __slots__ = ("value",)

    def __init__(self: Self, value: str, _validate: bool = True) -> None:
        # TODO: Add warning if _validate is False (?)
        self.value = self._validate(value) if _validate else value

    @staticmethod
    def _validate(value: str) -> str:
        """
        Validate week format, must match "YYYY-WNN" pattern where:
        - YYYY is a year between 0001 and 9999
        - NN is a week number between 1 and 53.

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
                "Invalid isoweek format. Format must match the 'YYYY-WXY' pattern, "
                f"found {value}"
            )

        if not 1 <= int(_match.group(1)) <= 9999:
            raise ValueError(
                "Invalid year number. Year must be between 0001 and 9999 but found "
                f"{_match.group(1)}"
            )

        if not 1 <= int(_match.group(2)) <= 53:
            raise ValueError(
                "Invalid week number. Week must be between 01 and 53 but found "
                f"{_match.group(2)}"
            )

        return value

    @property
    def week(self: Self) -> int:
        """Week number"""
        return int(self.value[-2:])

    @property
    def year(self: Self) -> int:
        """Year number"""
        return int(self.value[:4])

    @property
    def days(self: Self) -> Tuple[date, ...]:
        """Tuple of days in the week"""
        return tuple(self.to_date(weekday) for weekday in range(1, 8))

    def nth(self: Self, n: int) -> date:
        """Nth day of the week"""

        if not isinstance(n, int):
            raise TypeError(f"n must be an integer, found {type(n)}")
        if n not in range(1, 8):
            raise ValueError(f"n must be between 1 and 7, found {n}")

        return self.days[n - 1]

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
            raise TypeError("Cannot compare IsoWeek's with different offsets")

    def __le__(self: Self, other: IsoWeek) -> bool:
        """Less than or equal operator"""
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self: Self, other: IsoWeek) -> bool:
        """Greater than operator"""
        return not self.__le__(other)

    def __ge__(self: Self, other: IsoWeek) -> bool:
        """Greater than or equal operator"""
        return not self.__lt__(other)

    def to_str(self: Self) -> str:
        """Convert IsoWeek to string object"""
        return str(self)

    def to_compact(self: Self) -> str:
        """Convert IsoWeek to string object and compact format YYYYWNN"""
        return str(self).replace("-", "")

    def to_datetime(self: Self, weekday: int = 1) -> datetime:
        """Convert IsoWeek to datetime object"""

        if not isinstance(weekday, int):
            raise TypeError(
                f"weekday must be an integer between 1 and 7, found {type(weekday)}"
            )
        if weekday not in range(1, 8):
            raise ValueError(
                f"Invalid weekday. Weekday must be between 1 and 7, found {weekday}"
            )

        return datetime.strptime(f"{self.value}-{weekday}", "%G-W%V-%u") + self._offset

    def to_date(self: Self, weekday: int = 1) -> date:
        """Convert IsoWeek to date object"""
        return self.to_datetime(weekday).date()

    @classmethod
    def from_str(cls: Type[IsoWeek], _str: str) -> IsoWeek:
        """Create IsoWeek from string object in format YYYY-WNN"""
        return cls(_str)

    @classmethod
    def from_compact(cls: Type[IsoWeek], _str: str) -> IsoWeek:
        """Create IsoWeek from string object in format YYYYWNN"""
        return cls(_str[:4] + "-" + _str[4:])

    @classmethod
    def from_datetime(cls: Type[IsoWeek], _datetime: datetime) -> IsoWeek:
        """Create IsoWeek from datetime object"""
        year, week, _ = (_datetime - cls._offset).isocalendar()
        return cls(f"{year}-W{week:02d}", _validate=False)

    @classmethod
    def from_date(cls: Type[IsoWeek], _date: date) -> IsoWeek:
        """Create IsoWeek from date object"""
        year, week, _ = (_date - cls._offset).isocalendar()
        return cls(f"{year}-W{week:02d}", _validate=False)

    @classmethod
    def from_today(cls: Type[IsoWeek]) -> IsoWeek:  # pragma: no cover
        """Create IsoWeek from today's date"""
        return cls.from_date(date.today())

    def __add__(self: Self, other: Union[int, timedelta]) -> IsoWeek:
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
                f"Cannot add type {type(other)} to IsoWeek. "
                "Addition is supported with int and timedelta objects"
            )

    @overload
    def __sub__(self: Self, other: int) -> IsoWeek:  # pragma: no cover
        ...

    @overload
    def __sub__(self: Self, other: IsoWeek) -> int:  # pragma: no cover
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
        elif isinstance(other, IsoWeek) and self._offset == other._offset:
            return (self.to_date() - other.to_date()).days // 7
        else:
            raise TypeError(
                f"Cannot subtract type {type(other)} to IsoWeek. "
                "Subtraction is supported with int and IsoWeek objects"
                "with the same offset"
            )

    @classmethod
    def _automatic_cast(cls: Type[IsoWeek], value: IsoWeek_T) -> IsoWeek:
        """
        Automatic cast to IsoWeek type from the following possible types:

        - str: value must match "YYYY-WNN" pattern where NN is a week number
            between 1 and 53.
        - date: value will be converted to IsoWeek
        - datetime: value will be converted to IsoWeek
        - IsoWeek: value will be returned as is
        """
        if isinstance(value, str):
            return cls(value, _validate=True)
        elif isinstance(value, datetime):
            return cls.from_datetime(value)
        elif isinstance(value, date):
            return cls.from_date(value)
        elif isinstance(value, cls):
            return value
        else:
            raise NotImplementedError(f"Cannot cast type {type(value)} into IsoWeek")

    def weeksout(
        self: Self,
        n_weeks: int,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[Union[str, IsoWeek], None, None]:
        """
        Return range of IsoWeeks (or str) from one week to `n_weeks` ahead of current
        `value` with given `step`.

        If `as_str` is flagged as True, it will return str values, otherwise it will
        return IsoWeek objects.

        Arguments:
            n_weeks: number of weeks to be generated from current value
            step: step between weeks, must be positive integer
            as_str: whether to return str or IsoWeek object

        Returns:
            generator of IsoWeeks (or str) from one week to `n_weeks` ahead of current
            `value` with given `step`.

        Raises:
            TypeError: if `n_weeks` and/or `step` is not int
            ValueError: if `n_weeks` and/or `step` is not strictly positive

        Usage:
        ```py
        from iso_week import IsoWeek
        iso = IsoWeek("2023-W01")

        tuple(iso.weeksout(6))
        # ('2023-W02', '2023-W03', '2023-W04', '2023-W05', '2023-W06', '2023-W07')

        tuple(iso.weeksout(6, step=2))
        # ('2023-W02', '2023-W04', '2023-W06', )
        ```
        """
        if not isinstance(n_weeks, int):
            raise TypeError(f"n_weeks must be integer, found {type(n_weeks)} type")

        if n_weeks <= 0:
            raise ValueError(f"n_weeks must be strictly positive, found {n_weeks}")

        start, end = (self + 1), (self + n_weeks)
        return self.range(start, end, step, inclusive="both", as_str=as_str)

    @classmethod
    def range(
        cls: Type[IsoWeek],
        start: IsoWeek_T,
        end: IsoWeek_T,
        step: int = 1,
        inclusive: InclusiveType = "both",
        as_str: bool = True,
    ) -> Generator[Union[str, IsoWeek], None, None]:
        """
        Return tuple of IsoWeeks (or str) between `start` and `end` weeks with given
        `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or
        `end` week values.

        If `as_str` is flagged as True, it will return str values, otherwise it will
        return IsoWeek objects.

        Arguments:
            start: start week value. It can be IsoWeek, date, datetime or str
                (in YYYY-WNN format) - automatically casted to IsoWeek
            end: end week value. It can be IsoWeek, date, datetime or str
                (in YYYY-WNN format) - automatically casted to IsoWeek
            step: step between weeks, must be positive integer
            inclusive: inclusive type, can be one of "both", "left", "right" or "neither"
            as_str: whether to return str or IsoWeek object

        Returns:
            generator of IsoWeeks/str between start and end weeks

        Raises:
            ValueError: if `week_start` > `week_end`,
                `inclusive` not one of "both", "left", "right" or "neither",
                `step` is not strictly positive
            TypeError: if `step` is not int

        Usage:
        ```python
        from iso_week import IsoWeek

        start, end = "2023-W01", "2023-W10"
        step = 2
        inclusive = "both"
        as_str = True

        tuple(IsoWeek.range(start, end, step, inclusive, as_str))
        # ('2023-W01', '2023-W03', '2023-W05', '2023-W07', '2023-W09')
        ```
        """

        _start: IsoWeek = cls._automatic_cast(start)
        _end: IsoWeek = cls._automatic_cast(end)

        if _start > _end:
            raise ValueError(f"start must be before end value, found: {_start} > {_end}")

        if not isinstance(step, int):
            raise TypeError(f"step must be integer, found {type(step)}")

        if step < 1:
            raise ValueError(
                f"step value must be greater than or equal to 1, found {step}"
            )

        if inclusive not in _inclusive_values:
            raise ValueError(
                f"Invalid inclusive value. Must be one of {_inclusive_values}"
            )

        _delta = _end - _start
        range_start = 0 if inclusive in ("both", "left") else 1
        range_end = _delta + 1 if inclusive in ("both", "right") else _delta

        weeks_range = (
            (_start + i).to_str() if as_str else _start + i
            for i in range(range_start, range_end, step)
        )

        return weeks_range

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
            raise TypeError(f"Cannot compare type {type(other)} with IsoWeek")

    @overload
    def contains(self: Self, other: IsoWeek_T) -> bool:  # pragma: no cover
        """Type hinting for contains method on IsoWeek possible types"""
        ...

    @overload
    def contains(
        self: Self, other: Iterable[IsoWeek_T]
    ) -> Iterable[bool]:  # pragma: no cover
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
            raise TypeError(f"Cannot compare type {type(other)} with IsoWeek")
