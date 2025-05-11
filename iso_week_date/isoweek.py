from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from typing import Generator
from typing import Iterable
from typing import Literal
from typing import overload

from iso_week_date._base import BaseIsoWeek
from iso_week_date._patterns import ISOWEEK__DATE_FORMAT
from iso_week_date._patterns import ISOWEEK__FORMAT
from iso_week_date._patterns import ISOWEEK_PATTERN

if TYPE_CHECKING:
    from typing_extensions import Self


class IsoWeek(BaseIsoWeek):
    """Represents [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in the  _YYYY-WNN_ format.

    The class implements methods and functionalities to work directly with iso week format and avoid moving back and
    forth between `date`, `datetime` and `str` objects.

    Attributes:
        value_: iso-week string of format "YYYY-WNN" where:

            - YYYY is between 0001 and 9999
            - W is a literal character
            - NN is between 01 and 53
    """

    # Class Attributes

    _pattern = ISOWEEK_PATTERN
    _format = ISOWEEK__FORMAT
    _date_format = ISOWEEK__DATE_FORMAT

    # Properties

    @property
    def year(self: Self) -> int:
        """Returns year number as integer.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").year
            2025
        """
        return super().year

    @property
    def week(self: Self) -> int:
        """Returns week number as integer.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").week
            1
        """
        return super().week

    @property
    def quarter(self: Self) -> int:
        """Returns quarter number as integer.

        The first three quarters have 13 weeks, while the last one has either 13 or 14 weeks depending on the year:

        - Q1: weeks from 1 to 13
        - Q2: weeks from 14 to 26
        - Q3: weeks from 27 to 39
        - Q4: weeks from 40 to 52 (or 53 if applicable)

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").quarter
            1
            >>> IsoWeek("2025-W32").quarter
            3
        """
        return super().quarter

    @property
    def days(self: Self) -> tuple[date, ...]:
        """Returns tuple of days (as date) in the ISO week.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> days = IsoWeek("2025-W01").days
            >>> [str(d) for d in days]
            ['2024-12-30', '2024-12-31', '2025-01-01', '2025-01-02', '2025-01-03', '2025-01-04', '2025-01-05']
        """
        return tuple(self.to_date(weekday) for weekday in range(1, 8))

    # Dunder methods

    def __eq__(self: Self, other: object) -> bool:
        """Equality operator.

        Two ISO Week objects are considered equal if and only if they have the same `offset_` and the same `value_`.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if objects are equal, `False` otherwise.

        Examples:
            >>> from datetime import timedelta
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") == IsoWeek("2025-W01")
            True
            >>> IsoWeek("2025-W01") == IsoWeek("2025-W02")
            False
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeek("2025-W01") == CustomIsoWeek("2025-W01")
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") != IsoWeek("2025-W01")
            False
            >>> IsoWeek("2025-W01") != IsoWeek("2025-W02")
            True
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeek("2025-W01") != CustomIsoWeek("2025-W01")
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") < IsoWeek("2025-W02")
            True
            >>> IsoWeek("2025-W02") < IsoWeek("2025-W01")
            False
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeek("2025-W01") < CustomIsoWeek("2025-W01")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeek("2025-W01") < "2025-W01"
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") <= IsoWeek("2025-W02")
            True
            >>> IsoWeek("2025-W02") <= IsoWeek("2025-W01")
            False
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeek("2025-W01") <= CustomIsoWeek("2025-W01")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeek("2025-W01") <= "2025-W01"
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") > IsoWeek("2025-W02")
            False
            >>> IsoWeek("2025-W01") > IsoWeek("2022-W52")
            True
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeek("2025-W01") > CustomIsoWeek("2025-W01")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeek("2025-W01") > "2025-W01"
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01") >= IsoWeek("2025-W02")
            False
            >>> IsoWeek("2025-W01") >= IsoWeek("2025-W01")
            True
            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeek("2025-W01") >= CustomIsoWeek("2025-W01")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeek("2025-W01") >= "2025-W01"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__ge__(other)

    def __hash__(self: Self) -> int:
        """Returns the hash of the object.

        The hash is calculated based on the `value_` attribute and the `offset_` attribute.
        This allows for proper hashing and comparison of IsoWeek objects.

        Returns:
            Hash of the IsoWeek object.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> hash(IsoWeek("2025-W01"))  # doctest: +SKIP
            -8273429449497533691

            >>> class CustomIsoWeek(IsoWeek):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> hash(CustomIsoWeek("2025-W01"))  # doctest: +SKIP
            179726044712929056
        """
        return super().__hash__()

    def __next__(self: Self) -> Self:
        """Returns the next ISO week.

        This is equivalent to adding 1 to the current ISO week.

        Returns:
            Next ISO week.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> next(IsoWeek("2025-W01"))
            IsoWeek(2025-W02) with offset 0:00:00
        """
        return super().__next__()

    def __repr__(self: Self) -> str:
        """Custom representation.

        Returns:
            String representation of the IsoWeek object: class name, value and offset.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01")
            IsoWeek(2025-W01) with offset 0:00:00
        """
        return super().__repr__()

    def __str__(self: Self) -> str:
        """Custom string representation.

        Returns:
            String representation of the IsoWeek object in the format "YYYY-WNN".

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> str(IsoWeek("2025-W01"))
            '2025-W01'
        """
        return super().__str__()

    # from_* methods

    @classmethod
    def from_string(cls: type[Self], _str: str) -> Self:
        """Create an IsoWeek instance from a string in YYYY-WNN format.

        Arguments:
            _str: String in YYYY-WNN format.

        Returns:
            IsoWeek instance.

        Raises:
            TypeError: If `_str` is not a string.
            ValueError: If `_str` does not match the expected format.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_string("2025-W01")
            IsoWeek(2025-W01) with offset 0:00:00
            >>> IsoWeek.from_string("2025-W53")
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        return super().from_string(_str)

    @classmethod
    def from_compact(cls: type[Self], _str: str) -> Self:
        """Create an IsoWeek instance from a compact string in YYYYNN format.

        Arguments:
            _str: String in YYYYNN format.

        Returns:
            IsoWeek instance.

        Raises:
            TypeError: If `_str` is not a string.
            ValueError: If `_str` does not match the expected format.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_compact("2025W01")
            IsoWeek(2025-W01) with offset 0:00:00
            >>> IsoWeek.from_compact("2025W53")
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        return super().from_compact(_str)

    @classmethod
    def from_date(cls: type[Self], _date: date) -> Self:
        """Create an IsoWeek instance from a date object.

        Arguments:
            _date: Date object.

        Returns:
            IsoWeek instance.

        Raises:
            TypeError: If `_date` is not a date object.

        Examples:
            >>> from datetime import date
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_date(date(2024, 12, 30))
            IsoWeek(2025-W01) with offset 0:00:00
        """
        return super().from_date(_date)

    @classmethod
    def from_datetime(cls: type[Self], _datetime: datetime) -> Self:
        """Create an IsoWeek instance from a datetime object.

        Arguments:
            _datetime: Datetime object.

        Returns:
            IsoWeek instance.

        Raises:
            TypeError: If `_datetime` is not a datetime object.

        Examples:
            >>> from datetime import datetime
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_datetime(datetime(2024, 12, 30))
            IsoWeek(2025-W01) with offset 0:00:00
        """
        return super().from_datetime(_datetime)

    @classmethod
    def from_today(cls: type[Self]) -> Self:
        """Create an IsoWeek instance from the current date.

        Returns:
            IsoWeek instance representing the current date.

        Examples:
            >>> from datetime import datetime
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_today() == IsoWeek.from_date(datetime.now().date())
            True
        """
        return cls.from_date(date.today())

    @classmethod
    def from_values(cls: type[Self], year: int, week: int) -> Self:
        """Create an IsoWeek instance from year and week number.

        Arguments:
            year: Year number (YYYY).
            week: Week number (NN).

        Returns:
            IsoWeek instance.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek.from_values(2025, 1)
            IsoWeek(2025-W01) with offset 0:00:00
            >>> IsoWeek.from_values(2025, 53)
            Traceback (most recent call last):
            ValueError: Invalid week number. Year 2025 has only 52 weeks.
        """
        value = cls._format.replace("YYYY", str(year).zfill(4)).replace("NN", str(week).zfill(2))
        return cls(value)

    # to_* methods

    def to_string(self: Self) -> str:
        """Returns as a string in the YYYY-WNN format.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").to_string()
            '2025-W01'
        """
        return super().to_string()

    def to_compact(self: Self) -> str:
        """Returns as a string in the YYYYWNN format.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").to_compact()
            '2025W01'
        """
        return super().to_compact()

    def to_datetime(self: Self, weekday: int = 1) -> datetime:
        """Converts `IsoWeek` to `datetime` object with the given weekday.

        If no weekday is provided then the first day of the week is used.

        !!! info
            Weekday is not the same as the day of the week. The weekday is an integer between 1 and 7.

        Arguments:
            weekday: Weekday to use. It must be an integer between 1 and 7, where 1 is the first day of the week and 7
                is the last day of the week.

        Returns:
            `IsoWeek` value in `datetime` type with the given weekday.

        Raises:
            TypeError: If `weekday` is not an integer.
            ValueError: If `weekday` is not between 1 and 7.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").to_datetime()
            datetime.datetime(2024, 12, 30, 0, 0)
            >>> IsoWeek("2025-W01").to_datetime(3)
            datetime.datetime(2025, 1, 1, 0, 0)
        """
        if not isinstance(weekday, int):
            msg = f"`weekday` must be an integer between 1 and 7, found {type(weekday)}"
            raise TypeError(msg)
        if weekday not in range(1, 8):
            msg = f"Invalid `weekday`. Weekday must be between 1 and 7, found {weekday}"
            raise ValueError(msg)

        return super()._to_datetime(f"{self.value_}-{weekday}")

    def to_date(self: Self, weekday: int = 1) -> date:
        """Converts `IsoWeek` to `date` object with the given `weekday`.

        If no weekday is provided then the first day of the week is used.

        !!! info
            Weekday is not the same as the day of the week. The weekday is an integer between 1 and 7.

        Arguments:
            weekday: Weekday to use. It must be an integer between 1 and 7, where 1 is the first day of the week and 7
                is the last day of the week.

        Returns:
            `IsoWeek` value in `date` type with the given weekday.

        Raises:
            TypeError: If `weekday` is not an integer.
            ValueError: If `weekday` is not between 1 and 7.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").to_date()
            datetime.date(2024, 12, 30)
            >>> IsoWeek("2025-W01").to_date(3)
            datetime.date(2025, 1, 1)
        """
        return self.to_datetime(weekday).date()

    def to_values(self: Self) -> tuple[int, ...]:
        """Returns the year and week as a tuple of integers.

        Returns:
            Tuple of integers representing the year and week.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").to_values()
            (2025, 1)
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

        - `int`: interpreted as number of weeks to be added to the `IsoWeek` value.
        - `Iterable` of `int` : adds each element of the iterable to the `IsoWeek` value and returns
            a generator of `IsoWeek` objects.

        Arguments:
            other: Object to add to `IsoWeek`.

        Returns:
            New `IsoWeek` or generator of `IsoWeek` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int` or `Iterable` of `int`.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> str(IsoWeek("2025-W01") + 1)
            '2025-W02'
            >>> tuple(str(iw) for iw in IsoWeek("2025-W01") + (1, 2, 3))
            ('2025-W02', '2025-W03', '2025-W04')
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(weeks=other))
        elif isinstance(other, Iterable) and all(isinstance(_other, int) for _other in other):
            return (self + _other for _other in other)
        else:
            msg = (f"Cannot add type {type(other)} to `IsoWeek`. Addition is supported with `int` type",)
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

        - `int`: interpreted as number of weeks to be added to the `IsoWeek` value.
        - `Iterable` of `int` : adds each element of the iterable to the `IsoWeek` value and returns
            a generator of `IsoWeek` objects.

        Arguments:
            other: Object to add to `IsoWeek`.

        Returns:
            New `IsoWeek` or generator of `IsoWeek` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int` or `Iterable` of `int`.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> str(IsoWeek("2025-W01").add(1))
            '2025-W02'
            >>> tuple(str(iw) for iw in IsoWeek("2025-W01").add((1, 2, 3)))
            ('2025-W02', '2025-W03', '2025-W04')
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

        - `int`: interpreted as number of weeks to be subtracted to the `IsoWeek` value.
        - `IsoWeek`: will result in the difference between values in weeks (`int` type).
        - `Iterable` of `int` and/or `IsoWeek`: subtracts each element of the iterable to the `IsoWeek`.

        Arguments:
            other: Object to subtract to `IsoWeek`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeek` or Generator of `int` and/or `IsoWeek` depending
                on the type of `other`.

        Raises:
            TypeError: If `other` is not `int`, `IsoWeek` or `Iterable` of those types.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> str(IsoWeek("2025-W01") - 1)
            '2024-W52'
            >>> tuple(str(iw) for iw in IsoWeek("2025-W01") - (1, 2, 3))
            ('2024-W52', '2024-W51', '2024-W50')
            >>> IsoWeek("2025-W01") - IsoWeek("2024-W52")
            1
            >>> IsoWeek("2025-W01") - IsoWeek("2024-W51")
            2
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(weeks=other))
        elif isinstance(other, IsoWeek) and self.offset_ == other.offset_:
            return (self.to_date() - other.to_date()).days // 7
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, IsoWeek)) for _other in other):
            return (self - _other for _other in other)
        else:
            msg = (
                f"Cannot subtract type {type(other)} to `IsoWeek`. "
                "Subtraction is supported with `int` and `IsoWeek` types"
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

        - `int`: interpreted as number of weeks to be subtracted to the `IsoWeek` value.
        - `IsoWeek`: will result in the difference between values in weeks (`int` type).
        - `Iterable` of `int` and/or `IsoWeek`: subtracts each element of the iterable to the `IsoWeek`.

        Arguments:
            other: Object to subtract to `IsoWeek`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeek` or Generator of `int` and/or `IsoWeek` depending
                on the type of `other`.

        Raises:
            TypeError: If `other` is not `int`, `IsoWeek` or `Iterable` of those types.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> str(IsoWeek("2025-W01").sub(1))
            '2024-W52'
            >>> tuple(str(iw) for iw in IsoWeek("2025-W01").sub((1, 2, 3)))
            ('2024-W52', '2024-W51', '2024-W50')
            >>> IsoWeek("2025-W01").sub(IsoWeek("2024-W52"))
            1
            >>> IsoWeek("2025-W01").sub(IsoWeek("2024-W51"))
            2
        """
        return self.__sub__(other)

    def next(self: Self) -> Self:
        """Method equivalent of adding 1 to the current value.

        Returns:
            Next `IsoWeek` object.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").next()
            IsoWeek(2025-W02) with offset 0:00:00
        """
        return super().next()

    def previous(self: Self) -> Self:
        """Method equivalent of subtracting 1 to the current value.

        Returns:
            Previous `IsoWeek` object.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").previous()
            IsoWeek(2024-W52) with offset 0:00:00
        """
        return super().previous()

    # Specific methods

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: date | datetime | str | Self,
        end: date | datetime | str | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: Literal[True],
    ) -> Generator[str, None, None]: ...

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: date | datetime | str | Self,
        end: date | datetime | str | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: Literal[False],
    ) -> Generator[Self, None, None]: ...

    @overload
    @classmethod
    def range(
        cls: type[Self],
        start: date | datetime | str | Self,
        end: date | datetime | str | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: bool = True,
    ) -> Generator[str | Self, None, None]: ...

    @classmethod
    def range(
        cls: type[Self],
        start: date | datetime | str | Self,
        end: date | datetime | str | Self,
        *,
        step: int = 1,
        inclusive: Literal["both", "left", "right", "neither"] = "both",
        as_str: bool = True,
    ) -> Generator[str | Self, None, None]:
        """Generates `IsoWeek` (or `str`) between `start` and `end` values with given `step`.

        `inclusive` parameter can be used to control inclusion of `start` and/or `end` week values.

        If `as_str` is flagged as `True`, it will return str values, otherwise it will return `BaseIsoWeek` objects.

        Arguments:
            start: Starting value. It can be `IsoWeek`, `date`, `datetime` or `str`.
            end: Ending value. It can be `IsoWeek`, `date`, `datetime` or `str`.
            step: Step between generated values, must be positive integer.
            inclusive: Inclusive type, can be one of "both", "left", "right" or "neither".
            as_str: Whether to return `str` or `IsoWeek` object.

        Returns:
            Generator of `IsoWeek` or `str` between `start` and `end` values with given `step`.

        Raises:
            ValueError: If any of the following conditions is met:

                - `start > end`.
                - `inclusive` not one of "both", "left", "right" or "neither".
                - `step` is not strictly positive.
            TypeError: If `step` is not an int.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> tuple(
            ...     IsoWeek.range(
            ...         start="2025-W01",
            ...         end="2025-W07",
            ...         step=2,
            ...         inclusive="both",
            ...         as_str=True,
            ...     )
            ... )
            ('2025-W01', '2025-W03', '2025-W05', '2025-W07')
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").is_before(IsoWeek("2025-W02"))
            True
            >>> IsoWeek("2025-W01").is_before(IsoWeek("2025-W01"))
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").is_after(IsoWeek("2024-W52"))
            True
            >>> IsoWeek("2025-W01").is_after(IsoWeek("2025-W01"))
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
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").is_between(IsoWeek("2024-W52"), IsoWeek("2025-W02"))
            True
            >>> IsoWeek("2025-W01").is_between(IsoWeek("2025-W01"), IsoWeek("2025-W02"), inclusive="neither")
            False
        """
        return super().is_between(lower_bound=lower_bound, upper_bound=upper_bound, inclusive=inclusive)

    def nth(self: Self, n: int) -> date:
        """Returns Nth day of the week using the ISO weekday numbering convention (1=First, 2=Second, ..., 7=Last day).

        !!! info
            Weekday is not the same as the day of the week. The weekday is an integer between 1 and 7.

        Arguments:
            n: Day number between 1 and 7.

        Returns:
            `date` object representing the Nth day of the week.

        Raises:
            TypeError: If `n` is not an integer.
            ValueError: If `n` is not between 1 and 7.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").nth(1)
            datetime.date(2024, 12, 30)
            >>> IsoWeek("2025-W01").nth(7)
            datetime.date(2025, 1, 5)
        """
        if not isinstance(n, int):
            msg = f"`n` must be an integer, found {type(n)}"
            raise TypeError(msg)
        if n not in range(1, 8):
            msg = f"`n` must be between 1 and 7, found {n}"
            raise ValueError(msg)

        return self.days[n - 1]

    @overload
    def weeksout(
        self: Self,
        n_weeks: int,
        *,
        step: int = 1,
        as_str: Literal[True],
    ) -> Generator[str, None, None]: ...

    @overload
    def weeksout(
        self: Self,
        n_weeks: int,
        *,
        step: int = 1,
        as_str: Literal[False],
    ) -> Generator[IsoWeek, None, None]: ...

    @overload
    def weeksout(
        self: Self,
        n_weeks: int,
        *,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[str | IsoWeek, None, None]: ...

    def weeksout(
        self: Self,
        n_weeks: int,
        *,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[str | IsoWeek, None, None]:
        """Generate range of `IsoWeek` (or `str`) from one to `n_weeks` ahead of current `value`, with given `step`.

        If `as_str` is flagged as `True`, it will return `str` values, otherwise it will return `IsoWeek` objects.

        Arguments:
            n_weeks: Number of weeks to be generated from current value.
            step: Step between weeks, must be positive integer.
            as_str: Whether to return str or IsoWeek object.

        Returns:
            Generator of `IsoWeek`s (or `str`s) from one week to `n_weeks` ahead of current `value` with given `step`.

        Raises:
            TypeError: If `n_weeks` and/or `step` is not int.
            ValueError: If `n_weeks` and/or `step` is not strictly positive.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> isoweek = IsoWeek("2025-W01")
            >>>
            >>> tuple(isoweek.weeksout(4))
            ('2025-W02', '2025-W03', '2025-W04', '2025-W05')
            >>> tuple(isoweek.weeksout(4, step=2))
            ('2025-W02', '2025-W04')
        """
        if not isinstance(n_weeks, int):
            msg = f"`n_weeks` must be an integer, found {type(n_weeks)} type"
            raise TypeError(msg)

        if n_weeks <= 0:
            msg = f"`n_weeks` must be strictly positive, found {n_weeks}"
            raise ValueError(msg)

        start, end = (self + 1), (self + n_weeks)
        return self.range(start, end, step=step, inclusive="both", as_str=as_str)

    def __contains__(self: Self, other: Any) -> bool:  # noqa: ANN401
        """Checks if self contains `other`.

        Arguments:
            other: `IsoWeek`, `date`, `datetime` or `str`.

        Returns:
            `True` if self week contains other, `False` otherwise.

        Raises:
            TypeError: If other is not `IsoWeek`, `date`, `datetime` or `str`.

        Examples:
            >>> from datetime import date
            >>> from iso_week_date import IsoWeek
            >>>
            >>> date(2025, 1, 2) in IsoWeek("2025-W01")
            True
            >>> date(2025, 1, 7) in IsoWeek("2025-W01")
            False
        """
        if isinstance(other, (date, datetime, str, self.__class__)):
            _other = self._cast(other)
            return self.__eq__(_other)
        else:
            msg = f"Cannot compare type `{type(other)}` with IsoWeek"
            raise TypeError(msg)

    @overload
    def contains(self: Self, other: date | datetime | str | Self) -> bool: ...

    @overload
    def contains(self: Self, other: Iterable[date | datetime | str | Self]) -> tuple[bool, ...]: ...

    @overload
    def contains(
        self: Self,
        other: date | datetime | str | Self | Iterable[date | datetime | str | Self],
    ) -> bool | tuple[bool, ...]: ...

    def contains(
        self: Self, other: date | datetime | str | Self | Iterable[date | datetime | str | Self]
    ) -> bool | tuple[bool, ...]:
        """Checks if self contains `other`. `other` can be a single value or an iterable of values.

        In case of an iterable, the method returns a tuple of boolean values.

        Arguments:
            other: `IsoWeek`, `date`, `datetime` or `str`, or an iterable of those types.

        Returns:
            Boolean or iterable of booleans, where each boolean indicates whether self contains the corresponding value
                in the iterable.

        Raises:
            TypeError: If other is not IsoWeek, date, datetime or str, or an iterable of those types.

        Examples:
            >>> from datetime import date
            >>> from iso_week_date import IsoWeek
            >>>
            >>> IsoWeek("2025-W01").contains([date(2025, 1, 1), date(2025, 1, 6)])
            (True, False)
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            return other in self
        elif isinstance(other, Iterable):
            return tuple(_other in self for _other in other)
        else:
            msg = f"Cannot compare type `{type(other)}` with `IsoWeek`"
            raise TypeError(msg)

    def replace(
        self: Self,
        *,
        year: int | None = None,
        week: int | None = None,
    ) -> Self:
        """Replaces the year and/or week of the `IsoWeek` object.

        Arguments:
            year: Year to replace. If `None`, it will not be replaced.
            week: Week to replace. If `None`, it will not be replaced.

        Returns:
            New `IsoWeek` object with the replaced values.

        Examples:
            >>> from iso_week_date import IsoWeek
            >>>
            >>> isoweek = IsoWeek("2025-W01")
            >>> isoweek.replace(year=2022)
            IsoWeek(2022-W01) with offset 0:00:00
            >>> isoweek.replace(week=2)
            IsoWeek(2025-W02) with offset 0:00:00
            >>> isoweek.replace(year=2022, week=2)
            IsoWeek(2022-W02) with offset 0:00:00
        """
        # Validation of year and week is done in the constructor of the `IsoWeek` class,
        # so we can safely use them here without additional checks.
        return self.from_values(
            year=year if year is not None else self.year,
            week=week if week is not None else self.week,
        )
