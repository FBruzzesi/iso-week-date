from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Generator
from typing import Iterable
from typing import Literal
from typing import overload

from iso_week_date._base import BaseIsoWeek
from iso_week_date._patterns import ISOWEEKDATE__DATE_FORMAT
from iso_week_date._patterns import ISOWEEKDATE__FORMAT
from iso_week_date._patterns import ISOWEEKDATE_PATTERN

if TYPE_CHECKING:
    from typing_extensions import Self


class IsoWeekDate(BaseIsoWeek):
    """Represents [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in the  _"YYYY-WNN-D"_ format.

    The class implements methods and functionalities to work directly with iso week date format and avoid moving back
    and forth between `date`, `datetime` and `str` objects.

    Attributes:
        value_: iso-week string of format "YYYY-WNN-D" where:

            - YYYY is between 0001 and 9999
            - W is a literal character
            - NN is between 01 and 53
            - D is between 1 and 7
    """

    # class attributes

    _pattern = ISOWEEKDATE_PATTERN
    _format = ISOWEEKDATE__FORMAT
    _date_format = ISOWEEKDATE__DATE_FORMAT

    # properties

    @property
    def year(self: Self) -> int:
        """Returns year number as integer.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3").year
            2025
        """
        return super().year

    @property
    def week(self: Self) -> int:
        """Returns week number as integer.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3").week
            1
        """
        return super().week

    @property
    def weekday(self: Self) -> int:
        """Returns weekday number as integer.

        Returns:
            `int` with day number as integer corresponding to the `IsoWeekDate`.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3").day
            3
        """
        return int(self.value_[9])

    @property
    def quarter(self: Self) -> int:
        """Returns quarter number as integer.

        The first three quarters have 13 weeks, while the last one has either 13 or 14 weeks depending on the year:

        - Q1: weeks from 1 to 13
        - Q2: weeks from 14 to 26
        - Q3: weeks from 27 to 39
        - Q4: weeks from 40 to 52 (or 53 if applicable)

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3").quarter
            1
            >>> IsoWeekDate("2025-W32-4").quarter
            3
        """
        return super().quarter

    day = weekday  # Alias for backward compatibility
    """Alias for `weekday` property."""

    @property
    def isoweek(self: Self) -> str:
        """Returns iso-week string value.

        Returns:
            `str` with iso-week string value (YYYY-WNN format) corresponding to the `IsoWeekDate`.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1").isoweek
            '2025-W01'
        """
        return self.value_[:8]

    # dunder methods

    def __eq__(self: Self, other: object) -> bool:
        """Equality operator.

        Two ISO Week objects are considered equal if and only if they have the same `offset_` and the same `value_`.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if objects are equal, `False` otherwise.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") == IsoWeekDate("2025-W01-3")
            True
            >>> IsoWeekDate("2025-W01-3") == IsoWeekDate("2025-W02-1")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeekDate("2025-W01-3") == CustomIsoWeekDate("2025-W01-3")
            False
        """
        return super().__eq__(other)

    def __ne__(self: Self, other: object) -> bool:
        """Inequality operator.

        Two ISO Week objects are considered equal if and only if they have the same `offset_` and the same `value_`.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if objects are _not_ equal, `False` otherwise.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") != IsoWeekDate("2025-W01-3")
            False
            >>> IsoWeekDate("2025-W01-3") != IsoWeekDate("2025-W02-1")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeekDate("2025-W01-3") != CustomIsoWeekDate("2025-W01-3")
            True
        """
        return super().__ne__(other)

    def __lt__(self: Self, other: Self | object) -> bool:
        """Less than operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its lexicographical order.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if self is less than other, `False` otherwise.

        Raises:
            TypeError: If `other` is not of same type or it has a different offset.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") < IsoWeekDate("2025-W02-1")
            True
            >>> IsoWeekDate("2025-W02-7") < IsoWeekDate("2025-W01-3")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2025-W01-3") < CustomIsoWeekDate("2025-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2025-W01-3") < "2025-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__lt__(other)

    def __le__(self: Self, other: Self | object) -> bool:
        """Less than or equal operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its lexicographical order.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if self is less than or equal to other, `False` otherwise.

        Raises:
            TypeError: If `other` is not of same type or it has a different offset.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") <= IsoWeekDate("2025-W02-1")
            True
            >>> IsoWeekDate("2025-W02-7") <= IsoWeekDate("2025-W01-3")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2025-W01-3") <= CustomIsoWeekDate("2025-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2025-W01-3") <= "2025-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__le__(other)

    def __gt__(self: Self, other: Self | object) -> bool:
        """Greater than operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its lexicographical order.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if self is greater than other, `False` otherwise.

        Raises:
            TypeError: If `other` is not of same type or it has a different offset.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") > IsoWeekDate("2025-W02-1")
            False
            >>> IsoWeekDate("2025-W01-3") > IsoWeekDate("2024-W52-7")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2025-W01-3") > CustomIsoWeekDate("2025-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2025-W01-3") > "2025-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__gt__(other)

    def __ge__(self: Self, other: Self | object) -> bool:
        """Greater than or equal operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its lexicographical order.

        Arguments:
           other: Object to compare with.

        Returns:
            `True` if self is greater than or equal to `other`, `False` otherwise.

        Raises:
            TypeError: If `other` is not of same type or it has a different offset.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-3") >= IsoWeekDate("2025-W02-1")
            False
            >>> IsoWeekDate("2025-W01-3") >= IsoWeekDate("2025-W01-2")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2025-W01-3") >= CustomIsoWeekDate("2025-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2025-W01-3") >= "2025-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__ge__(other)

    def __hash__(self: Self) -> int:
        """Returns the hash of the object.

        The hash is calculated based on the `value_` attribute and the `offset_` attribute.
        This allows for proper hashing and comparison of IsoWeekDate objects.

        Returns:
            Hash of the IsoWeekDate object.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> hash(IsoWeekDate("2025-W01-3"))  # doctest: +SKIP
            -7997434344089344162

            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> hash(CustomIsoWeekDate("2025-W01-3"))  # doctest: +SKIP
            455721150121118585
        """
        return super().__hash__()

    def __next__(self: Self) -> Self:
        """Returns the next ISO week date.

        This is equivalent to adding 1 to the current ISO week date.

        Returns:
            Next ISO week date.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> next(IsoWeekDate("2025-W01-4"))
            IsoWeekDate(2025-W01-5) with offset 0:00:00
        """
        return super().__next__()

    def __repr__(self: Self) -> str:
        """Custom representation.

        Returns:
            String representation of the IsoWeekDate object: class name, value and offset.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1")
            IsoWeekDate(2025-W01-1) with offset 0:00:00
        """
        return super().__repr__()

    def __str__(self: Self) -> str:
        """Custom string representation.

        Returns:
            String representation of the IsoWeekDate object in the format "YYYY-WNN-D".

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> str(IsoWeekDate("2025-W01-1"))
            '2025-W01-1'
        """
        return super().__str__()

    # from_* methods

    @classmethod
    def from_string(cls: type[Self], _str: str) -> Self:
        """Create an IsoWeekDate instance from a string in YYYY-WNN-D format.

        Arguments:
            _str: String in YYYY-WNN-D format.

        Returns:
            IsoWeekDate instance.

        Raises:
            TypeError: If `_str` is not a string.
            ValueError: If `_str` does not match the expected format.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_string("2025-W01-4")
            IsoWeekDate(2025-W01-4) with offset 0:00:00
            >>> IsoWeekDate.from_string("2025-W53-1")
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        return super().from_string(_str)

    @classmethod
    def from_compact(cls: type[Self], _str: str) -> Self:
        """Create an IsoWeekDate instance from a compact string in YYYYNND format.

        Arguments:
            _str: String in YYYYNND format.

        Returns:
            IsoWeekDate instance.

        Raises:
            TypeError: If `_str` is not a string.
            ValueError: If `_str` does not match the expected format.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_compact("2025W013")
            IsoWeekDate(2025-W01-3) with offset 0:00:00
            >>> IsoWeekDate.from_compact("2025W537")
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        return super().from_compact(_str)

    @classmethod
    def from_date(cls: type[Self], _date: date) -> Self:
        """Create an IsoWeekDate instance from a date object.

        Arguments:
            _date: Date object.

        Returns:
            IsoWeekDate instance.

        Raises:
            TypeError: If `_date` is not a date object.

        Examples:
            >>> from datetime import date
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_date(date(2024, 12, 31))
            IsoWeekDate(2025-W01-2) with offset 0:00:00
        """
        return super().from_date(_date)

    @classmethod
    def from_datetime(cls: type[Self], _datetime: datetime) -> Self:
        """Create an IsoWeekDate instance from a datetime object.

        Arguments:
            _datetime: Datetime object.

        Returns:
            IsoWeekDate instance.

        Raises:
            TypeError: If `_datetime` is not a datetime object.

        Examples:
            >>> from datetime import datetime
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_datetime(datetime(2024, 12, 31))
            IsoWeekDate(2025-W01-2) with offset 0:00:00
        """
        return super().from_datetime(_datetime)

    @classmethod
    def from_today(cls: type[Self]) -> Self:
        """Create an IsoWeekDate instance from the current date.

        Returns:
            IsoWeekDate instance representing the current date.

        Examples:
            >>> from datetime import datetime
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_today() == IsoWeekDate.from_date(datetime.now().date())
            True
        """
        return cls.from_date(date.today())

    @classmethod
    def from_values(cls: type[Self], year: int, week: int, weekday: int) -> Self:
        """Create an IsoWeekDate instance from year and week number.

        Arguments:
            year: Year number (YYYY).
            week: Week number (NN).
            weekday: Weekday number (D).

        Returns:
            IsoWeekDate instance.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate.from_values(year=2025, week=1, weekday=4)
            IsoWeekDate(2025-W01-4) with offset 0:00:00
            >>> IsoWeekDate.from_values(2025, 53, 1)
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        value = (
            cls._format.replace("YYYY", str(year).zfill(4)).replace("NN", str(week).zfill(2)).replace("D", str(weekday))
        )
        return cls(value)

    # to_* methods

    def to_string(self: Self) -> str:
        """Returns as a string in the YYYY-WNN-D format.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-4").to_string()
            '2025-W01-4'
        """
        return super().to_string()

    def to_compact(self: Self) -> str:
        """Returns as a string in the YYYYWNN format.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-5").to_compact()
            '2025W015'
        """
        return super().to_compact()

    def to_datetime(self: Self) -> datetime:
        """Converts `IsoWeekDate` to `datetime` object.

        Returns:
            `datetime` corresponding to the `IsoWeekDate`.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1").to_datetime()
            datetime.datetime(2024, 12, 30, 0, 0)
            >>> IsoWeekDate("2025-W01-4").to_datetime()
            datetime.datetime(2025, 1, 2, 0, 0)
        """
        return super()._to_datetime(self.value_)

    def to_date(self: Self) -> date:
        """Converts `IsoWeekDate` to `date` object.

        Returns:
            `date` corresponding to the `IsoWeekDate`.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1").to_date()
            datetime.date(2024, 12, 30)
            >>> IsoWeekDate("2025-W01-3").to_date()
            datetime.date(2025, 1, 1)
        """
        return self.to_datetime().date()

    def to_values(self: Self) -> tuple[int, ...]:
        """Returns the year, week and weekday as a tuple of integers.

        Returns:
            Tuple of integers representing the year and week.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-4").to_values()
            (2025, 1, 4)
        """
        return super().to_values()

    # arithmetic operations

    @overload
    def __add__(self: Self, other: int) -> Self: ...

    @overload
    def __add__(
        self: Self,
        other: Iterable[int],
    ) -> Generator[Self, None, None]: ...

    @overload
    def __add__(
        self: Self,
        other: int | Iterable[int],
    ) -> Self | Generator[Self, None, None]: ...

    def __add__(
        self: Self,
        other: int | Iterable[int],
    ) -> Self | Generator[Self, None, None]:
        """Addition operation.

        It supports addition with the following types:

        - `int`: interpreted as number of days to be added to the `IsoWeekDate` value.
        - `Iterable` of `int`: adds each element of the iterable to the `IsoWeekDate` value and
            returns a generator of `IsoWeekDate` objects.

        Arguments:
            other: Object to add to `IsoWeekDate`.

        Returns:
            New `IsoWeekDate` or generator of `IsoWeekDate` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int` or `Iterable` of `int`.

        Examples:
        >>> from iso_week_date import IsoWeekDate
        >>>
        >>> str(IsoWeekDate("2025-W01-1") + 1)
        '2025-W01-2'
        >>> tuple(str(iwd) for iwd in IsoWeekDate("2025-W01-1") + (1, 2))
        ('2025-W01-2', '2025-W01-3')
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(days=other))
        elif isinstance(other, Iterable) and all(isinstance(_other, int) for _other in other):
            return (self + _other for _other in other)
        else:
            msg = (f"Cannot add type {type(other)} to `IsoWeekDate`. Addition is supported with `int` type",)
            raise TypeError(msg)

    @overload
    def add(self: Self, other: int) -> Self: ...

    @overload
    def add(
        self: Self,
        other: Iterable[int],
    ) -> Generator[Self, None, None]: ...

    @overload
    def add(
        self: Self,
        other: int | Iterable[int],
    ) -> Self | Generator[Self, None, None]: ...

    def add(self: Self, other: int | Iterable[int]) -> Self | Generator[Self, None, None]:
        """Method equivalent of addition operator `self + other`.

        It supports addition with the following types:

        - `int`: interpreted as number of days to be added to the `IsoWeekDate` value.
        - `Iterable` of `int`: adds each element of the iterable to the `IsoWeekDate` value and
            returns a generator of `IsoWeekDate` objects.

        Arguments:
            other: Object to add to `IsoWeekDate`.

        Returns:
            New `IsoWeekDate` or generator of `IsoWeekDate` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int` or `Iterable` of `int`.

        Examples:
        >>> from iso_week_date import IsoWeekDate
        >>>
        >>> str(IsoWeekDate("2025-W01-1") + 1)
        '2025-W01-2'
        >>> tuple(str(iwd) for iwd in IsoWeekDate("2025-W01-1") + (1, 2))
        ('2025-W01-2', '2025-W01-3')
        """
        return self.__add__(other)

    @overload
    def __sub__(self: Self, other: int) -> Self: ...

    @overload
    def __sub__(self: Self, other: Self) -> int: ...

    @overload
    def __sub__(
        self: Self,
        other: Iterable[int],
    ) -> Generator[Self, None, None]: ...

    @overload
    def __sub__(self: Self, other: Iterable[Self]) -> Generator[int, None, None]: ...

    @overload
    def __sub__(
        self: Self,
        other: int | Self | Iterable[int | Self],
    ) -> int | Self | Generator[int | Self, None, None]: ...

    def __sub__(
        self: Self,
        other: int | Self | Iterable[int | Self],
    ) -> int | Self | Generator[int | Self, None, None]:
        """Subtraction operation.

        It supports subtraction with the following types:

        - `int`: interpreted as number of days to be subtracted to the `IsoWeekDate` value.
        - `IsoWeekDate`: will result in the difference between values in days (`int` type).
        - `Iterable` of `int` and/or `IsoWeekDate`: subtracts each element of the iterable to the
            `IsoWeekDate`.

        Arguments:
            other: Object to subtract to `IsoWeekDate`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeekDate` or Generator of `int` and/or `IsoWeekDate`
                depending on the type of `other`.

        Raises:
            TypeError: If `other` is not `int`, `IsoWeekDate` or `Iterable` of those types.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> str(IsoWeekDate("2025-W01-1") - 1)
            '2024-W52-7'
            >>> tuple(str(iwd) for iwd in IsoWeekDate("2025-W01-1") - (1, 2))
            ('2024-W52-7', '2024-W52-6')
            >>> IsoWeekDate("2025-W01-1") - IsoWeekDate("2024-W52-3")
            5
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(days=other))
        elif isinstance(other, IsoWeekDate) and self.offset_ == other.offset_:
            return (self.to_date() - other.to_date()).days
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, IsoWeekDate)) for _other in other):
            return (self - _other for _other in other)
        else:
            msg = (
                f"Cannot subtract type {type(other)} to `IsoWeekDate`. "
                "Subtraction is supported with `int` and `IsoWeekDate` types",
            )
            raise TypeError(msg)

    @overload
    def sub(self: Self, other: int) -> Self: ...

    @overload
    def sub(self: Self, other: Self) -> int: ...

    @overload
    def sub(
        self: Self,
        other: Iterable[int],
    ) -> Generator[Self, None, None]: ...

    @overload
    def sub(self: Self, other: Iterable[Self]) -> Generator[int, None, None]: ...

    @overload
    def sub(
        self: Self,
        other: int | Self | Iterable[int | Self],
    ) -> int | Self | Generator[int | Self, None, None]: ...

    def sub(
        self: Self,
        other: int | Self | Iterable[int | Self],
    ) -> int | Self | Generator[int | Self, None, None]:
        """Method equivalent of subtraction operator `self - other`.

        It supports subtraction with the following types:

        - `int`: interpreted as number of days to be subtracted to the `IsoWeekDate` value.
        - `IsoWeekDate`: will result in the difference between values in days (`int` type).
        - `Iterable[int | IsoWeekDate]`: subtracts each element of the iterable to the `IsoWeekDate`.

        Arguments:
            other: Object to subtract to `IsoWeekDate`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeekDate` or Generator of `int` and/or `IsoWeekDate`
                depending on the type of `other`.

        Raises:
            TypeError: If `other` is not `int`, `IsoWeekDate` or `Iterable` of those types.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> str(IsoWeekDate("2025-W01-1") - 1)
            '2024-W52-7'
            >>> tuple(str(iwd) for iwd in IsoWeekDate("2025-W01-1") - (1, 2))
            ('2024-W52-7', '2024-W52-6')
            >>> IsoWeekDate("2025-W01-1") - IsoWeekDate("2024-W52-3")
            5
        """
        return self.__sub__(other)

    def next(self: Self) -> Self:
        """Method equivalent of adding 1 to the current value.

        Returns:
            Next `IsoWeekDate` object.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-5").next()
            IsoWeekDate(2025-W01-6) with offset 0:00:00
        """
        return super().next()

    def previous(self: Self) -> Self:
        """Method equivalent of subtracting 1 to the current value.

        Returns:
            Previous `IsoWeekDate` object.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1").previous()
            IsoWeekDate(2024-W52-7) with offset 0:00:00
        """
        return super().previous()

    # Specific methods

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
        """Generates `IsoWeekDate` (or `str`) between `start` and `end` values with given `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or `end` week values.

        If `as_str` is flagged as `True`, it will return str values, otherwise it will return `BaseIsoWeek` objects.

        Arguments:
            start: Starting value. It can be `IsoWeekDate`, `date`, `datetime` or `str`.
            end: Ending value. It can be `IsoWeekDate`, `date`, `datetime` or `str`.
            step: Step between generated values, must be positive integer.
            inclusive: Inclusive type, can be one of "both", "left", "right" or "neither".
            as_str: Whether to return `str` or `IsoWeekDate` object.

        Returns:
            Generator of `IsoWeekDate` or `str` between `start` and `end` values with given `step`.

        Raises:
            ValueError: If any of the following conditions is met:

                - `start > end`.
                - `inclusive` not one of "both", "left", "right" or "neither".
                - `step` is not strictly positive.
            TypeError: If `step` is not an int.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> tuple(
            ...     IsoWeekDate.range(
            ...         start="2025-W01-1",
            ...         end="2025-W01-7",
            ...         step=2,
            ...         inclusive="both",
            ...         as_str=True,
            ...     )
            ... )
            ('2025-W01-1', '2025-W01-3', '2025-W01-5', '2025-W01-7')
        """
        return super().range(
            start=start,
            end=end,
            step=step,
            inclusive=inclusive,
            as_str=as_str,
        )

    def is_before(self: Self, other: Self | object) -> bool:
        """Checks if `self` is before `other`.

        Arguments:
            other: Other object to compare with.

        Returns:
            True if `self` is before `other`, False otherwise.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-1").is_before(IsoWeekDate("2025-W02-4"))
            True
            >>> IsoWeekDate("2025-W01-5").is_before(IsoWeekDate("2025-W01-1"))
            False
        """
        return super().is_before(other)

    def is_after(self: Self, other: Self | object) -> bool:
        """Checks if `self` is after `other`.

        Arguments:
            other: Other object to compare with.

        Returns:
            True if `self` is after `other`, False otherwise.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-6").is_after(IsoWeekDate("2024-W52-1"))
            True
            >>> IsoWeekDate("2025-W01-3").is_after(IsoWeekDate("2025-W01-5"))
            False
        """
        return super().is_after(other)

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

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2025-W01-4").is_between(IsoWeekDate("2024-W52-1"), IsoWeekDate("2025-W02-3"))
            True
            >>> IsoWeekDate("2025-W01-4").is_between(
            ...     IsoWeekDate("2025-W01-4"), IsoWeekDate("2025-W02-1"), inclusive="neither"
            ... )
            False
        """
        return super().is_between(lower_bound=lower_bound, upper_bound=upper_bound, inclusive=inclusive)

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: Literal[True],
    ) -> Generator[str, None, None]: ...

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: Literal[False],
    ) -> Generator[IsoWeekDate, None, None]: ...

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[str | IsoWeekDate, None, None]: ...

    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[str | IsoWeekDate, None, None]:
        """Generate range of `IsoWeekDate` (or `str`) from one to `n_days` ahead of current `value`, with given `step`.

        If `as_str` is flagged as `True`, it will return `str` values, otherwise it will return `IsoWeekDate` objects.

        Arguments:
            n_days: Number of days to be generated from current value.
            step: Step between days, must be positive integer.
            as_str: Whether to return `str` or `IsoWeekDate` object.

        Returns:
            Generator of `IsoWeekDate`s (or `str`s) from one day to `n_days` ahead of current `value` with given `step`.

        Raises:
            TypeError: If `n_days` and/or `step` is not int.
            ValueError: If `n_days` and/or `step` is not strictly positive.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> iwd = IsoWeekDate("2025-W01-1")
            >>> tuple(iwd.daysout(3))
            ('2025-W01-2', '2025-W01-3', '2025-W01-4')
            >>> tuple(iwd.daysout(6, step=2))
            ('2025-W01-2', '2025-W01-4', '2025-W01-6')
        """
        if not isinstance(n_days, int):
            msg = f"`n_weeks` must be integer, found {type(n_days)} type"
            raise TypeError(msg)

        if n_days <= 0:
            msg = f"`n_weeks` must be strictly positive, found {n_days}"
            raise ValueError(msg)

        start, end = (self + 1), (self + n_days)
        return self.range(start, end, step=step, inclusive="both", as_str=as_str)

    def replace(
        self: Self,
        *,
        year: int | None = None,
        week: int | None = None,
        weekday: int | None = None,
    ) -> Self:
        """Replaces the year, week and/or weekday of the `IsoWeekDate` object.

        Arguments:
            year: Year to replace. If `None`, it will not be replaced.
            week: Week to replace. If `None`, it will not be replaced.
            weekday: Weekday to replace. If `None`, it will not be replaced.

        Returns:
            New `IsoWeekDate` object with the replaced values.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> iwd = IsoWeekDate("2025-W01-1")
            >>> iwd.replace(year=2024)
            IsoWeekDate(2024-W01-1) with offset 0:00:00
            >>> iwd.replace(week=2)
            IsoWeekDate(2025-W02-1) with offset 0:00:00
            >>> iwd.replace(year=2024, weekday=6)
            IsoWeekDate(2024-W01-6) with offset 0:00:00
        """
        # Validation of year and week is done in the constructor of the `IsoWeekDate` class,
        # so we can safely use them here without additional checks.
        return self.from_values(
            year=year if year is not None else self.year,
            week=week if week is not None else self.week,
            weekday=weekday if weekday is not None else self.weekday,
        )
