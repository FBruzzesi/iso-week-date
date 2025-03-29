from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Generator
from typing import Iterable
from typing import Literal
from typing import TypeVar
from typing import overload

from iso_week_date._base import BaseIsoWeek
from iso_week_date._patterns import ISOWEEKDATE__DATE_FORMAT
from iso_week_date._patterns import ISOWEEKDATE__FORMAT
from iso_week_date._patterns import ISOWEEKDATE_PATTERN

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Self

IsoWeekDate_T = TypeVar("IsoWeekDate_T", date, datetime, str, "IsoWeekDate")


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

    _pattern = ISOWEEKDATE_PATTERN

    _format = ISOWEEKDATE__FORMAT
    _date_format = ISOWEEKDATE__DATE_FORMAT

    @property
    def year(self: Self) -> int:
        """Returns year number as integer.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2023-W01-3").year
            2023
        """
        return super().year

    @property
    def week(self: Self) -> int:
        """Returns week number as integer.

        Examples:
            >>> from iso_week_date import IsoWeekDate
            >>>
            >>> IsoWeekDate("2023-W01-3").week
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
            >>> IsoWeekDate("2023-W01-3").day
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
            >>> IsoWeekDate("2023-W01-3").quarter
            1
            >>> IsoWeekDate("2023-W32-4").quarter
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
            >>> IsoWeekDate("2023-W01-1").isoweek
            '2023-W01'
        """
        return self.value_[:8]

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
            >>> IsoWeekDate("2023-W01-3") == IsoWeekDate("2023-W01-3")
            True
            >>> IsoWeekDate("2023-W01-3") == IsoWeekDate("2023-W02-1")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeekDate("2023-W01-3") == CustomIsoWeekDate("2023-W01-3")
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
            >>> IsoWeekDate("2023-W01-3") != IsoWeekDate("2023-W01-3")
            False
            >>> IsoWeekDate("2023-W01-3") != IsoWeekDate("2023-W02-1")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>>
            >>> IsoWeekDate("2023-W01-3") != CustomIsoWeekDate("2023-W01-3")
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
            >>> IsoWeekDate("2023-W01-3") < IsoWeekDate("2023-W02-1")
            True
            >>> IsoWeekDate("2023-W02-7") < IsoWeekDate("2023-W01-3")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2023-W01-3") < CustomIsoWeekDate("2023-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2023-W01-3") < "2023-W01-3"
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
            >>> IsoWeekDate("2023-W01-3") <= IsoWeekDate("2023-W02-1")
            True
            >>> IsoWeekDate("2023-W02-7") <= IsoWeekDate("2023-W01-3")
            False
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2023-W01-3") <= CustomIsoWeekDate("2023-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2023-W01-3") <= "2023-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__le__(other)

    def __gt__(self: Self, other: Self) -> bool:
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
            >>> IsoWeekDate("2023-W01-3") > IsoWeekDate("2023-W02-1")
            False
            >>> IsoWeekDate("2023-W01-3") > IsoWeekDate("2022-W52-7")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2023-W01-3") > CustomIsoWeekDate("2023-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2023-W01-3") > "2023-W01-3"
            Traceback (most recent call last):
            TypeError: ...
        """
        return super().__gt__(other)

    def __ge__(self: Self, other: Self) -> bool:
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
            >>> IsoWeekDate("2023-W01-3") >= IsoWeekDate("2023-W02-1")
            False
            >>> IsoWeekDate("2023-W01-3") >= IsoWeekDate("2023-W01-2")
            True
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> IsoWeekDate("2023-W01-3") >= CustomIsoWeekDate("2023-W01-3")
            Traceback (most recent call last):
            TypeError: ...
            >>> IsoWeekDate("2023-W01-3") >= "2023-W01-3"
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
            >>> hash(IsoWeekDate("2023-W01-3"))
            1194338214299428910
            >>> class CustomIsoWeekDate(IsoWeekDate):
            ...     offset_ = timedelta(days=1)
            >>> hash(CustomIsoWeekDate("2023-W01-3"))
            -4400892982215291831
        """
        return super().__hash__()

    def to_datetime(self: Self) -> datetime:
        """Converts `IsoWeekDate` to `datetime` object.

        Returns:
            `datetime` corresponding to the `IsoWeekDate`.

        Examples:
        ```py
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1").to_datetime()  # datetime.datetime(2023, 1, 2, 0, 0)
        IsoWeekDate("2023-W01-3").to_datetime()  # datetime.datetime(2023, 1, 4, 0, 0)
        ```
        """
        return super()._to_datetime(self.value_)

    def to_date(self: Self) -> date:
        """Converts `IsoWeekDate` to `date` object.

        Returns:
            `date` corresponding to the `IsoWeekDate`.

        Examples:
        ```py
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1").to_date()  # datetime.date(2023, 1, 2)
        IsoWeekDate("2023-W01-3").to_date()  # datetime.date(2023, 1, 4)
        ```
        """
        return self.to_datetime().date()

    @overload
    def __add__(self: Self, other: int | timedelta) -> Self: ...  # pragma: no cover

    @overload
    def __add__(
        self: Self,
        other: Iterable[int | timedelta],
    ) -> Generator[Self, None, None]: ...  # pragma: no cover

    @overload
    def __add__(
        self: Self,
        other: int | timedelta | Iterable[int | timedelta],
    ) -> Self | Generator[Self, None, None]: ...  # pragma: no cover

    def __add__(
        self: Self,
        other: int | timedelta | Iterable[int | timedelta],
    ) -> Self | Generator[Self, None, None]:
        """Addition operation.

        It supports addition with the following types:

        - `int`: interpreted as number of days to be added to the `IsoWeekDate` value.
        - `timedelta`: converts `IsoWeekDate` to `datetime`, adds `timedelta` and converts back to `IsoWeekDate` object.
        - `Iterable` of `int` and/or `timedelta`: adds each element of the iterable to the `IsoWeekDate` value and
            returns a generator of `IsoWeekDate` objects.

        Arguments:
            other: Object to add to `IsoWeekDate`.

        Returns:
            New `IsoWeekDate` or generator of `IsoWeekDate` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int`, `timedelta` or `Iterable` of `int` and/or `timedelta`.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1") + 1  # IsoWeekDate("2023-W01-2")
        IsoWeekDate("2023-W01-1") + timedelta(weeks=2)  # IsoWeekDate("2023-W03-1")

        tuple(IsoWeekDate("2023-W01-1") + (1, 2))
        # (IsoWeekDate("2023-W01-2"), IsoWeekDate("2023-W01-3"))
        ```
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(days=other))
        elif isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() + other)
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, timedelta)) for _other in other):
            return (self + _other for _other in other)
        else:
            msg = (
                f"Cannot add type {type(other)} to `IsoWeekDate`. "
                "Addition is supported with `int` and `timedelta` types",
            )
            raise TypeError(msg)

    @overload
    def __sub__(self: Self, other: int | timedelta) -> Self: ...  # pragma: no cover

    @overload
    def __sub__(self: Self, other: Self) -> int: ...  # pragma: no cover

    @overload
    def __sub__(
        self: Self,
        other: Iterable[int | timedelta],
    ) -> Generator[Self, None, None]: ...  # pragma: no cover

    @overload
    def __sub__(self: Self, other: Iterable[Self]) -> Generator[int, None, None]: ...  # pragma: no cover

    @overload
    def __sub__(
        self: Self,
        other: int | timedelta | Self | Iterable[int | timedelta | Self],
    ) -> int | Self | Generator[int | Self, None, None]: ...  # pragma: no cover

    def __sub__(
        self: Self,
        other: int | timedelta | Self | Iterable[int | timedelta | Self],
    ) -> int | Self | Generator[int | Self, None, None]:
        """Subtraction operation.

        It supports subtraction with the following types:

        - `int`: interpreted as number of days to be subtracted to the `IsoWeekDate` value.
        - `timedelta`: converts `IsoWeekDate` to `datetime`, subtracts `timedelta` and converts back to `IsoWeekDate`
            object.
        - `IsoWeekDate`: will result in the difference between values in days (`int` type).
        - `Iterable` of `int`, `timedelta` and/or `IsoWeekDate`: subtracts each element of the iterable to the
            `IsoWeekDate`.

        Arguments:
            other: Object to subtract to `IsoWeekDate`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeekDate` or Generator of `int` and/or `IsoWeekDate`
                depending on the type of `other`.


        Raises:
            TypeError: If `other` is not `int`, `timedelta`, `IsoWeekDate` or `Iterable` of those types.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1") - 1  # IsoWeekDate("2022-W52-7")
        IsoWeekDate("2023-W01-1") - timedelta(weeks=2)  # IsoWeekDate("2022-W51-1")

        tuple(IsoWeekDate("2023-W01-1") - (1, 2))
        # (IsoWeekDate("2022-W52-7"), IsoWeekDate("2022-W52-6"))

        IsoWeekDate("2023-W01-1") - IsoWeekDate("2022-W52-3")  # 5
        ```
        """
        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(days=other))
        if isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() - other)
        elif isinstance(other, IsoWeekDate) and self.offset_ == other.offset_:
            return (self.to_date() - other.to_date()).days
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, timedelta, IsoWeekDate)) for _other in other):
            return (self - _other for _other in other)
        else:
            msg = (
                f"Cannot subtract type {type(other)} to `IsoWeekDate`. "
                "Subtraction is supported with `int`, `timedelta` and `IsoWeekDate` types",
            )
            raise TypeError(msg)

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: Literal[True],
    ) -> Generator[str, None, None]: ...  # pragma: no cover

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: Literal[False],
    ) -> Generator[IsoWeekDate, None, None]: ...  # pragma: no cover

    @overload
    def daysout(
        self: Self,
        n_days: int,
        *,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[str | IsoWeekDate, None, None]: ...  # pragma: no cover

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
        ```py
        from iso_week_date import IsoWeekDate

        iso = IsoWeekDate("2023-W01-1")

        tuple(iso.daysout(3))  # ('2023-W01-2', '2023-W01-3', '2023-W01-4')
        tuple(iso.daysout(6, step=2))  # ('2023-W01-2', '2023-W01-4', '2023-W01-6')
        ```
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
        ```python
        from iso_week_date import IsoWeekDate

        iso = IsoWeekDate("2023-W01-1")
        iso.replace(year=2022)  # IsoWeekDate("2022-W01-1")
        iso.replace(week=2)  # IsoWeekDate("2023-W02-1")
        iso.replace(year=2022, weekday=6)  # IsoWeekDate("2022-W01-6")
        ```
        """
        # Validation of year and week is done in the constructor of the `IsoWeekDate` class,
        # so we can safely use them here without additional checks.
        return self.from_values(
            year=year if year is not None else self.year,
            week=week if week is not None else self.week,
            weekday=weekday if weekday is not None else self.weekday,
        )
