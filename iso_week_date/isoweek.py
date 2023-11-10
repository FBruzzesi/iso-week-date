from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from typing import Any, Generator, Iterable, Tuple, TypeVar, Union, overload

from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEK__FORMAT, ISOWEEK_PATTERN
from iso_week_date.base import BaseIsoWeek

if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

IsoWeek_T = TypeVar("IsoWeek_T", date, datetime, str, "IsoWeek")


class IsoWeek(BaseIsoWeek):
    """
    Represents [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date)
    in the  _YYYY-WNN_ format and implements multiple methods to work directly with it
    instead of going back and forth between `date`, `datetime` and `str` objects.

    Attributes:
        value_: iso-week string of format "YYYY-WNN" where:

            - YYYY is between 0001 and 9999
            - W is a literal character
            - NN is between 01 and 53
    """

    _pattern = ISOWEEK_PATTERN

    _format = ISOWEEK__FORMAT
    _date_format = ISOWEEK__DATE_FORMAT

    @property
    def days(self: Self) -> Tuple[date, ...]:
        """
        Returns tuple of days (as date) in the ISO week.

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").days  # (date(2023, 1, 2), ..., date(2023, 1, 8))
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
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").nth(1)  # date(2023, 1, 2)
        IsoWeek("2023-W01").nth(7)  # date(2023, 1, 8)
        ```
        """

        if not isinstance(n, int):
            raise TypeError(f"`n` must be an integer, found {type(n)}")
        if n not in range(1, 8):
            raise ValueError(f"`n` must be between 1 and 7, found {n}")

        return self.days[n - 1]

    @override
    def to_datetime(self: Self, weekday: int = 1) -> datetime:  # type: ignore[override]
        """
        Converts `IsoWeek` to `datetime` object with the given weekday.

        If no weekday is provided then the first day of the week is used.

        Remark that the weekday is not the same as the day of the week. The weekday
        is a number between 1 and 7.

        Arguments:
            weekday: weekday to use. It must be an integer between 1 and 7, where 1 is
                the first day of the week and 7 is the last day of the week

        Returns:
            `IsoWeek` value in `datetime` type with the given weekday

        Raises:
            TypeError: if `weekday` is not an integer
            ValueError: if `weekday` is not between 1 and 7

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_datetime()  # datetime.datetime(2023, 1, 2, 0, 0)
        IsoWeek("2023-W01").to_datetime(3)  # datetime.datetime(2023, 1, 4, 0, 0)
        ```
        """

        if not isinstance(weekday, int):
            raise TypeError(
                f"`weekday` must be an integer between 1 and 7, found {type(weekday)}"
            )
        if weekday not in range(1, 8):
            raise ValueError(
                f"Invalid `weekday`. Weekday must be between 1 and 7, found {weekday}"
            )

        return super().to_datetime(f"{self.value_}-{weekday}")

    @override
    def to_date(self: Self, weekday: int = 1) -> date:  # type: ignore[override]
        """
        Converts `IsoWeek` to `date` object with the given `weekday`.

        If no weekday is provided then the first day of the week is used.

        Remark that the weekday is not the same as the day of the week. The weekday
        is a number between 1 and 7.

        Arguments:
            weekday: weekday to use. It must be an integer between 1 and 7, where 1 is
                the first day of the week and 7 is the last day of the week

        Returns:
            `IsoWeek` value in `date` type with the given weekday

        Raises:
            TypeError: if `weekday` is not an integer
            ValueError: if `weekday` is not between 1 and 7

        Usage:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_date()  # datetime.date(2023, 1, 2)
        IsoWeek("2023-W01").to_date(3)  # datetime.date(2023, 1, 4)
        ```
        """
        return self.to_datetime(weekday).date()

    def __add__(self: Self, other: Union[int, timedelta]) -> IsoWeek:
        """
        It supports addition with the following two types:

        - `int`: interpreted as number of weeks to be added to the `IsoWeek` value
        - `timedelta`: converts `IsoWeek` to datetime (first day of week), adds
            `timedelta` and converts back to `IsoWeek` object

        Arguments:
            other: object to add to `IsoWeek`

        Returns:
            new `IsoWeek` object with the result of the addition

        Raises:
            TypeError: if `other` is not `int` or `timedelta`

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") + 1  # IsoWeek("2023-W02")
        IsoWeek("2023-W01") + timedelta(weeks=2)  # IsoWeek("2023-W03")
        IsoWeek("2023-W01") + timedelta(hours=1234) # IsoWeek("2023-W08")
        ```
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(weeks=other))
        elif isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() + other)
        else:
            raise TypeError(
                f"Cannot add type {type(other)} to `IsoWeek`. "
                "Addition is supported with `int` and `timedelta` types"
            )

    def __sub__(  # type: ignore[override]
        self: Self, other: Union[int, timedelta, IsoWeek]
    ) -> Union[int, IsoWeek]:
        """
        It supports subtraction with the following types:

        - `int`: interpreted as number of weeks to be subtracted to the `IsoWeek` value
        - `timedelta`: converts `IsoWeek` to datetime (first day of week), subtract
            `timedelta` and converts back to `IsoWeek` object
        - `IsoWeek`: will result in the difference between values in weeks (`int` type)

        Arguments:
            other: object to subtract to `IsoWeek`

        Returns:
            results from the subtraction, can be `int` or `IsoWeek`

        Raises:
            TypeError: if `other` is not `int`, `timedelta` or `IsoWeek`

        Usage:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") - 1  # IsoWeek("2022-W52")
        IsoWeek("2023-W01") - timedelta(weeks=2)  # IsoWeek("2022-W51")
        IsoWeek("2023-W01") - timedelta(hours=1234) # IsoWeek("2023-W45")

        IsoWeek("2023-W01") - IsoWeek("2022-W52")  # 1
        IsoWeek("2023-W01") - IsoWeek("2022-W51")  # 2
        ```
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() - timedelta(weeks=other))
        if isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() - other)
        elif isinstance(other, IsoWeek) and self.offset_ == other.offset_:
            return (self.to_date() - other.to_date()).days // 7
        else:
            raise TypeError(
                f"Cannot subtract type {type(other)} to `IsoWeek`. "
                "Subtraction is supported with `int`, `timedelta` and `IsoWeek` types"
            )

    def weeksout(
        self: Self,
        n_weeks: int,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[Union[str, IsoWeek], None, None]:
        """
        Generates range of `IsoWeek`s (or `str`s) from one week to `n_weeks` ahead of
        current `value`, with given `step`.

        If `as_str` is flagged as `True`, it will return `str` values, otherwise it will
        return `IsoWeek` objects.

        Arguments:
            n_weeks: number of weeks to be generated from current value
            step: step between weeks, must be positive integer
            as_str: whether to return str or IsoWeek object

        Returns:
            generator of `IsoWeek`s (or `str`s) from one week to `n_weeks` ahead of
            current `value` with given `step`.

        Raises:
            TypeError: if `n_weeks` and/or `step` is not int
            ValueError: if `n_weeks` and/or `step` is not strictly positive

        Usage:
        ```py
        from iso_week_date import IsoWeek
        iso = IsoWeek("2023-W01")

        tuple(iso.weeksout(4)) # ('2023-W02', '2023-W03', '2023-W04', '2023-W05')
        tuple(iso.weeksout(6, step=2))  # ('2023-W02', '2023-W04', '2023-W06')
        ```
        """
        if not isinstance(n_weeks, int):
            raise TypeError(f"`n_weeks` must be integer, found {type(n_weeks)} type")

        if n_weeks <= 0:
            raise ValueError(f"`n_weeks` must be strictly positive, found {n_weeks}")

        start, end = (self + 1), (self + n_weeks)
        return self.range(start, end, step, inclusive="both", as_str=as_str)

    def __contains__(self: Self, other: Any) -> bool:
        """
        Checks if self contains `other`.

        Arguments:
            other: `IsoWeek`, `date`, `datetime` or `str`

        Returns:
            `True` if self week contains other, `False` otherwise

        Raises:
            TypeError: if other is not `IsoWeek`, `date`, `datetime` or `str`

        Usage:
        ```python
        from datetime import date
        from iso_week_date import IsoWeek

        date(2023, 1, 1) in IsoWeek("2023-W01")  # False
        date(2023, 1, 2) in IsoWeek("2023-W01")  # True
        ```
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            _other = self._cast(other)
            return self.__eq__(_other)
        else:
            raise TypeError(f"Cannot compare type {type(other)} with IsoWeek")

    @overload
    def contains(self: Self, other: IsoWeek_T) -> bool:  # pragma: no cover
        """Annotation for `contains` method on `IsoWeek` possible types"""
        ...

    @overload
    def contains(
        self: Self, other: Iterable[IsoWeek_T]
    ) -> Iterable[bool]:  # pragma: no cover
        """Annotation for `contains` method on `Iterator` of `IsoWeek` possible types"""
        ...

    def contains(
        self: Self, other: Union[Any, Iterable[Any]]
    ) -> Union[bool, Iterable[bool]]:
        """
        Checks if self contains `other`.

        `other` can be a single value or an iterable of values.
        In case of an iterable, the method returns an iterable of boolean values.

        Arguments:
            other: `IsoWeek`, `date`, `datetime` or `str`, or an iterable of those types

        Returns:
            boolean or iterable of booleans

        Raises:
            TypeError: if other is not IsoWeek, date, datetime or str, or an iterable
                of those types

        Usage:
        ```python
        from datetime import date
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").contains(
            (date(2023, 1, 1), date(2023, 1, 2))
            )  # (False, True)
        ```
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            return other in self
        elif isinstance(other, Iterable):
            return tuple(_other in self for _other in other)
        else:
            raise TypeError(f"Cannot compare type {type(other)} with `IsoWeek`")
