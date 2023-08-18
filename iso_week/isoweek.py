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
    Represents ISO Week date format and implement multiple methods to work directly
    with it instead of going back and forth between `date`, `datetime` and `str` objects.

    Attributes:
        value: iso-week string of format "YYYY-WNN" where:

            - YYYY is between 0001 and 9999
            - NN is between 01 and 53
    """

    offset_: ClassVar[timedelta] = timedelta(days=0)
    __slots__ = ("value_",)

    def __init__(self: Self, value: str, __validate: bool = True) -> None:
        self.value_ = self._validate(value) if __validate else value

    @staticmethod
    def _validate(value: str) -> str:
        """
        Validates week format, which must match "YYYY-WNN" pattern and where:

        - YYYY is a year between 0001 and 9999
        - NN is a week number between 1 and 53

        This (static)method is called during initialization (if `__validate` argument is
        flagged as `True`) and can be called directly to validate a string.

        Arguments:
            value: iso-week string to validate

        Returns:
            unchanged value if string is valid

        Raises:
            ValueError: if string format is invalid or week number is out of range

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek._validate("2023-W01") # -> "2023-W01"
        IsoWeek._validate("2023-W00") # -> ValueError
        ```
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
        """
        Returns week number as integer.

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").week  # -> 1
        ```
        """
        return int(self.value_[-2:])

    @property
    def year(self: Self) -> int:
        """
        Returns year number as integer.

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").year # -> 2023
        ```
        """
        return int(self.value_[:4])

    @property
    def days(self: Self) -> Tuple[date, ...]:
        """
        Returns tuple of days (as date) in the ISO week.

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").days  # -> (date(2023, 1, 2), ..., date(2023, 1, 8))
        ```
        """
        return tuple(self.to_date(weekday) for weekday in range(1, 8))

    def nth(self: Self, n: int) -> date:
        """
        Returns Nth day of the week using the ISO week weekday numbering convention
        (1=First day, 2=Second day, ..., 7=Last day).

        Remark that the weekday is not the same as the day of the week. The weekday
        is a number between 1 and 7.

        Arguments:
            n: day number between 1 and 7

        Returns:
            `date` object representing the Nth day of the week

        Raises:
            TypeError: if `n` is not an integer
            ValueError: if `n` is not between 1 and 7

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").nth(1)  # -> date(2023, 1, 2)
        IsoWeek("2023-W01").nth(7)  # -> date(2023, 1, 8)
        ```
        """

        if not isinstance(n, int):
            raise TypeError(f"n must be an integer, found {type(n)}")
        if n not in range(1, 8):
            raise ValueError(f"n must be between 1 and 7, found {n}")

        return self.days[n - 1]

    def __repr__(self: Self) -> str:
        """Custom representation."""
        return f"IsoWeek({self.value_}) with offset {self.offset_}"

    def __str__(self: Self) -> str:
        """String conversion operator, returns iso-week string value ignoring offset."""
        return self.value_

    def __eq__(self: Self, other: Any) -> bool:
        """
        Equality operator.

        Two IsoWeek objects are considered equal if and only if they have the same offset
        and the same value.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are equal, `False` otherwise

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") == IsoWeek("2023-W01")  # -> True
        IsoWeek("2023-W01") == IsoWeek("2023-W02")  # -> False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") == CustomIsoWeek("2023-W01")  # -> False
        ```
        """
        if isinstance(other, IsoWeek):
            return self.offset_ == other.offset_ and self.value_ == other.value_
        else:
            return False

    def __ne__(self: Self, other: Any) -> bool:
        """
        Inequality operator.

        Two IsoWeek objects are considered equal if and only if they have the same offset
        and the same value.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are _not_ equal, `False` otherwise

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") != IsoWeek("2023-W01")  # -> False
        IsoWeek("2023-W01") != IsoWeek("2023-W02")  # -> True

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") != CustomIsoWeek("2023-W01")  # -> True
        ```
        """
        return not self.__eq__(other)

    def __lt__(self: Self, other: IsoWeek) -> bool:
        """
        Less than operator.

        Comparing two IsoWeek objects is only possible if they have the same offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than other, `False` otherwise

        Raises:
            TypeError: if `other` is not an `IsoWeek` object
            TypeError: if `other` is an `IsoWeek` object with different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") < IsoWeek("2023-W02")  # -> True
        IsoWeek("2023-W02") < IsoWeek("2023-W01")  # -> False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") < CustomIsoWeek("2023-W01")  # -> TypeError
        IsoWeek("2023-W01") < "2023-W01"  # -> TypeError
        ```
        """
        if isinstance(other, IsoWeek):
            if self.offset_ == other.offset_:
                return self.value_ < other.value_
            else:
                raise TypeError("Cannot compare IsoWeek's with different offsets")
        else:
            raise TypeError(
                f"Cannot compare `IsoWeek` with `{type(other)}` object, "
                "only `IsoWeek` objects are supported"
            )

    def __le__(self: Self, other: IsoWeek) -> bool:
        """
        Less than or equal operator.

        Comparing two IsoWeek objects is only possible if they have the same offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than or equal to other, `False` otherwise

        Raises:
            TypeError: if `other` is not an `IsoWeek` object
            TypeError: if `other` is an `IsoWeek` object with different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") <= IsoWeek("2023-W01")  # -> True
        IsoWeek("2023-W02") <= IsoWeek("2023-W01")  # -> False

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") <= CustomIsoWeek("2023-W01")  # -> TypeError
        IsoWeek("2023-W01") <= "2023-W01"  # -> TypeError
        ```
        """
        return self.__lt__(other) or self.__eq__(other)

    def __gt__(self: Self, other: IsoWeek) -> bool:
        """Greater than operator.

        Comparing two IsoWeek objects is only possible if they have the same offset.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is greater than other, `False` otherwise

        Raises:
            TypeError: if `other` is not an `IsoWeek` object
            TypeError: if `other` is an `IsoWeek` object with different offset

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") >= IsoWeek("2023-W02")  # -> False
        IsoWeek("2023-W01") >= IsoWeek("2023-W01")  # -> True

        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)

        IsoWeek("2023-W01") >= CustomIsoWeek("2023-W01")  # -> TypeError
        IsoWeek("2023-W01") >= "2023-W01"  # -> TypeError
        ```
        """
        return not self.__le__(other)

    def __ge__(self: Self, other: IsoWeek) -> bool:
        """
         Greater than or equal operator.

         Comparing two IsoWeek objects is only possible if they have the same offset.

         If that's the case than it's enough to compare their values (as `str`) due to its
         lexicographical order.

         Arguments:
             other: object to compare with

         Returns:
             `True` if self is greater than or equal to `other`, `False` otherwise

        Raises:
             TypeError: if `other` is not an `IsoWeek` object
             TypeError: if `other` is an `IsoWeek` object with different offset

         Usage:
         ```py
         from datetime import timedelta
         from iso_week import IsoWeek

         IsoWeek("2023-W01") > IsoWeek("2023-W02")  # -> False
         IsoWeek("2023-W02") > IsoWeek("2023-W01")  # -> True

         class CustomIsoWeek(IsoWeek):
             offset_ = timedelta(days=1)

         IsoWeek("2023-W01") > CustomIsoWeek("2023-W01")  # -> TypeError
         IsoWeek("2023-W01") > "2023-W01"  # -> TypeError
         ```
        """
        return not self.__lt__(other)

    def to_str(self: Self) -> str:
        """
        Convert IsoWeek to string object. It is equivalent to calling str(iso_week_obj).

        Returns:
            IsoWeek in string format YYYY-WNN

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").to_str()  # -> "2023-W01"
        ```
        """
        return str(self)

    def to_compact(self: Self) -> str:
        """
        Convert IsoWeek to string object in compact format YYYYWNN

        Returns:
            IsoWeek in string format YYYYWNN

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").to_compact()  # -> "2023W01"
        ```
        """
        return str(self).replace("-", "")

    def to_datetime(self: Self, weekday: int = 1) -> datetime:
        """
        Convert IsoWeek to datetime object with the given weekday. If no weekday is
        provided then the first day of the week is used.

        Remark that the weekday is not the same as the day of the week. The weekday
        is a number between 1 and 7.

        Arguments:
            weekday: weekday to use. It must be an integer between 1 and 7, where 1 is
                the first day of the week and 7 is the last day of the week

        Returns:
            weekday of given IsoWeek as datetime

        Raises:
            TypeError: if `weekday` is not an integer
            ValueError: if `weekday` is not between 1 and 7

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").to_datetime()  # -> datetime.datetime(2023, 1, 2, 0, 0)
        IsoWeek("2023-W01").to_datetime(3)  # -> datetime.datetime(2023, 1, 4, 0, 0)
        ```
        """

        if not isinstance(weekday, int):
            raise TypeError(
                f"weekday must be an integer between 1 and 7, found {type(weekday)}"
            )
        if weekday not in range(1, 8):
            raise ValueError(
                f"Invalid weekday. Weekday must be between 1 and 7, found {weekday}"
            )

        return datetime.strptime(f"{self.value_}-{weekday}", "%G-W%V-%u") + self.offset_

    def to_date(self: Self, weekday: int = 1) -> date:
        """
        Convert IsoWeek to date object with the given weekday. If no weekday is
        provided then the first day of the week is used.

        Remark that the weekday is not the same as the day of the week. The weekday
        is a number between 1 and 7.

        Arguments:
            weekday: weekday to use. It must be an integer between 1 and 7, where 1 is
                the first day of the week and 7 is the last day of the week

        Returns:
            weekday of given IsoWeek as date

        Raises:
            TypeError: if `weekday` is not an integer
            ValueError: if `weekday` is not between 1 and 7

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek("2023-W01").to_date()  # -> datetime.date(2023, 1, 2)
        IsoWeek("2023-W01").to_date(3)  # -> datetime.date(2023, 1, 4)
        ```
        """
        return self.to_datetime(weekday).date()

    @classmethod
    def from_str(cls: Type[IsoWeek], _str: str) -> IsoWeek:
        """
        Instantiate IsoWeek object from string in format YYYY-WNN

        Arguments:
            _str: string in format YYYY-WNN

        Returns:
            IsoWeek object

        Raises:
            TypeError: if `_str` is not a string object

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek.from_str("2023-W01")  # -> IsoWeek("2023-W01")
        ```
        """
        if not isinstance(_str, str):
            raise TypeError(f"Expected string object, found {type(_str)}")
        return cls(_str, True)

    @classmethod
    def from_compact(cls: Type[IsoWeek], _str: str) -> IsoWeek:
        """
        Instantiate IsoWeek object from string in format YYYYWNN

        Arguments:
            _str: string in format YYYYWNN

        Returns:
            IsoWeek object

        Raises:
            TypeError: if `_str` is not a string object

        Usage:
        ```py
        from iso_week import IsoWeek

        IsoWeek.from_compact("2023W01")  # -> IsoWeek("2023-W01")
        ```
        """
        return cls.from_str(_str[:4] + "-" + _str[4:])

    @classmethod
    def from_datetime(cls: Type[IsoWeek], _datetime: datetime) -> IsoWeek:
        """
        Instantiate IsoWeek object from datetime object

        Arguments:
            _datetime: datetime object

        Returns:
            IsoWeek object

        Raises:
            TypeError: if `_datetime` is not a datetime object

        Usage:
        ```py
        from datetime import datetime
        from iso_week import IsoWeek

        IsoWeek.from_datetime(datetime(2023, 1, 2, 12, 0))  # -> IsoWeek("2023-W01")
        ```
        """
        if not isinstance(_datetime, datetime):
            raise TypeError(f"Expected datetime object, found {type(_datetime)}")
        year, week, _ = (_datetime - cls.offset_).isocalendar()
        return cls(f"{year}-W{week:02d}", False)

    @classmethod
    def from_date(cls: Type[IsoWeek], _date: date) -> IsoWeek:
        """
        Instantiate IsoWeek object from date object

        Arguments:
            _date: date object

        Returns:
            IsoWeek object

        Raises:
            TypeError: if `_date` is not a date object

        Usage:
        ```py
        from datetime import date
        from iso_week import IsoWeek

        IsoWeek.from_datetime(date(2023, 1, 2))  # -> IsoWeek("2023-W01")
        ```
        """
        if not isinstance(_date, date):
            raise TypeError(f"Expected date object, found {type(_date)}")
        year, week, _ = (_date - cls.offset_).isocalendar()
        return cls(f"{year}-W{week:02d}", False)

    @classmethod
    def from_today(cls: Type[IsoWeek]) -> IsoWeek:  # pragma: no cover
        """Instantiate IsoWeek from today's date"""
        return cls.from_date(date.today())

    def __add__(self: Self, other: Union[int, timedelta]) -> IsoWeek:
        """
        It supports addition with the following two types:

        - int: interpreted as number of weeks to be added to the IsoWeek value
        - timedelta: converts IsoWeek to datetime (first day of week), adds timedelta and
            converts back to IsoWeek object

        Arguments:
            other: object to add to IsoWeek

        Returns:
            new IsoWeek object with the result of the addition

        Raises:
            TypeError: if `other` is not int or timedelta

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") + 1  # -> IsoWeek("2023-W02")
        IsoWeek("2023-W01") + timedelta(weeks=2)  # -> IsoWeek("2023-W03")
        IsoWeek("2023-W01") + timedelta(hours=1234) # -> IsoWeek("2023-W08")
        ```
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
    def __sub__(self: Self, other: Union[int, timedelta]) -> IsoWeek:  # pragma: no cover
        """Annotation for subtraction with int and timedelta"""
        ...

    @overload
    def __sub__(self: Self, other: IsoWeek) -> int:  # pragma: no cover
        """Annotation for subtraction with other IsoWeek"""
        ...

    def __sub__(self: Self, other: Union[int, timedelta, IsoWeek]) -> Union[int, IsoWeek]:
        """
        It supports substraction with the following two types:

        - int: interpreted as number of weeks to be subtracted to the IsoWeek value
        - IsoWeek: will result in the difference between values in weeks (int type)

        Arguments:
            other: object to subtract to IsoWeek

        Returns:
            results from the subtraction, can be int or IsoWeek

        Raises:
            TypeError: if `other` is not int, timedelta or IsoWeek

        Usage:
        ```py
        from datetime import timedelta
        from iso_week import IsoWeek

        IsoWeek("2023-W01") - 1  # -> IsoWeek("2022-W52")
        IsoWeek("2023-W01") - timedelta(weeks=2)  # -> IsoWeek("2022-W51")
        IsoWeek("2023-W01") - timedelta(hours=1234) # -> IsoWeek("2023-W45")

        IsoWeek("2023-W01") - IsoWeek("2022-W52")  # -> 1
        IsoWeek("2023-W01") - IsoWeek("2022-W51")  # -> 2
        ```
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(weeks=other))
        if isinstance(other, timedelta):
            return self.from_date(self.to_datetime() - other)
        elif isinstance(other, IsoWeek) and self.offset_ == other.offset_:
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

        - str: value must match "YYYY-WNN" pattern where:

            - YYYY is the year number between 0001 and 9999
            - NN is the week number between 1 and 53.

        - date: value will be converted to IsoWeek
        - datetime: value will be converted to IsoWeek
        - IsoWeek: value will be returned as is

        Arguments:
            value: value to be casted to IsoWeek

        Returns:
            IsoWeek object

        Raises:
            NotImplementedError: if `value` is not str, date, datetime or IsoWeek

        Usage:
        ```py
        from datetime import date
        from iso_week import IsoWeek

        IsoWeek._automatic_cast("2023-W01")  # -> IsoWeek("2023-W01")
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

    def weeksout(
        self: Self,
        n_weeks: int,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[Union[str, IsoWeek], None, None]:
        """
        Generate range of IsoWeeks (or str) from one week to `n_weeks` ahead of current
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

        tuple(iso.weeksout(4)) # -> ('2023-W02', '2023-W03', '2023-W04', '2023-W05')
        tuple(iso.weeksout(6, step=2))  # -> ('2023-W02', '2023-W04', '2023-W06')
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
        Generates IsoWeeks (or str) between `start` and `end` weeks with given `step`.

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
            generator of IsoWeeks/str between start and end weeks with given step

        Raises:
            ValueError: if `week_start` > `week_end`,
                `inclusive` not one of "both", "left", "right" or "neither",
                `step` is not strictly positive
            TypeError: if `step` is not int

        Usage:
        ```python
        from iso_week import IsoWeek

        start, end = "2023-W01", "2023-W07"

        tuple(IsoWeek.range(
            start,
            end,
            step=2,
            inclusive="both",
            as_str=True)
            ) # -> ('2023-W01', '2023-W03', '2023-W05', '2023-W07')
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

        Usage:
        ```python
        from datetime import date
        from iso_week import IsoWeek

        date(2023, 1, 1) in IsoWeek("2023-W01")  # -> False
        date(2023, 1, 2) in IsoWeek("2023-W01")  # -> True
        ```
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            _other = self._automatic_cast(other)
            return self.__eq__(_other)
        else:
            raise TypeError(f"Cannot compare type {type(other)} with IsoWeek")

    @overload
    def contains(self: Self, other: IsoWeek_T) -> bool:  # pragma: no cover
        """Annotation for contains method on IsoWeek possible types"""
        ...

    @overload
    def contains(
        self: Self, other: Iterable[IsoWeek_T]
    ) -> Iterable[bool]:  # pragma: no cover
        """Annotation for contains method on Iterator of IsoWeek possible types"""
        ...

    def contains(
        self: Self, other: Union[IsoWeek_T, Iterable[IsoWeek_T]]
    ) -> Union[IsoWeek_T, Iterable[IsoWeek_T]]:
        """
        Check if self contains other. Other can be a single value or an iterable of
        values. If other is an iterable, returns an iterable of bools.

        Arguments:
            other: IsoWeek, date, datetime or str, or an iterable of those types

        Returns:
            boolean or iterable of booleans

        Raises:
            TypeError: if other is not IsoWeek, date, datetime or str, or an iterable
                of those types

        Usage:
        ```python
        from datetime import date
        from iso_week import IsoWeek

        IsoWeek("2023-W01").contains(
            (date(2023, 1, 1), date(2023, 1, 2))
            )  # -> (False, True)
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            return other in self
        elif isinstance(other, Iterable):
            return tuple(_other in self for _other in other)
        else:
            raise TypeError(f"Cannot compare type {type(other)} with IsoWeek")
