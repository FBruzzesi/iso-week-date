from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from typing import Generator, Iterable, TypeVar, Union, overload

from iso_week_date._patterns import ISOWEEKDATE__DATE_FORMAT, ISOWEEKDATE__FORMAT, ISOWEEKDATE_PATTERN
from iso_week_date.base import BaseIsoWeek

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover

if sys.version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

IsoWeekDate_T = TypeVar("IsoWeekDate_T", date, datetime, str, "IsoWeekDate")


class IsoWeekDate(BaseIsoWeek):
    """Represents [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in the  _"YYYY-WNN-D"_ format and
    implements methods to work directly with it instead of going back and forth between `date`, `datetime` and `str`
    objects.

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
    def day(self: Self) -> int:
        """Returns day number as integer.

        Returns:
            `int` with day number as integer corresponding to the `IsoWeekDate`.

        Examples:
        ```py
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1").day  # 1
        ```
        """
        return int(self.value_[9])

    @property
    def isoweek(self: Self) -> str:
        """Returns iso-week string value.

        Returns:
            `str` with iso-week string value (YYYY-WNN format) corresponding to the `IsoWeekDate`.

        Examples:
        ```py
        from iso_week_date import IsoWeekDate

        IsoWeekDate("2023-W01-1").isoweek  # "2023-W01"
        ```
        """
        return self.value_[:8]

    @override
    def to_datetime(self: Self) -> datetime:  # type: ignore[override]
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

        return super().to_datetime(self.value_)

    @override
    def to_date(self: Self) -> date:  # type: ignore[override]
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
    def __add__(self: Self, other: Union[int, timedelta]) -> Self:  # pragma: no cover
        """Implementation of addition operator."""
        ...

    @overload
    def __add__(self: Self, other: Iterable[Union[int, timedelta]]) -> Generator[Self, None, None]:  # pragma: no cover
        """Implementation of addition operator."""
        ...

    def __add__(
        self: Self, other: Union[int, timedelta, Iterable[Union[int, timedelta]]]
    ) -> Union[Self, Generator[Self, None, None]]:
        """It supports addition with the following types:

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

        tuple(IsoWeekDate("2023-W01-1") + (1,2)) # (IsoWeekDate("2023-W01-2"), IsoWeekDate("2023-W01-3"))
        ```
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(days=other))
        elif isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() + other)
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, timedelta)) for _other in other):
            return (self + _other for _other in other)
        else:
            raise TypeError(
                f"Cannot add type {type(other)} to `IsoWeekDate`. "
                "Addition is supported with `int` and `timedelta` types"
            )

    @overload
    def __sub__(self: Self, other: Union[int, timedelta]) -> Self:  # pragma: no cover
        """Annotation for subtraction with `int` and `timedelta`"""
        ...

    @overload
    def __sub__(self: Self, other: Self) -> int:  # pragma: no cover
        """Annotation for subtraction with other `BaseIsoWeek`"""
        ...

    @overload
    def __sub__(self: Self, other: Iterable[Union[int, timedelta]]) -> Generator[Self, None, None]:  # pragma: no cover
        """Annotation for subtraction with other `BaseIsoWeek`"""
        ...

    @overload
    def __sub__(self: Self, other: Iterable[Self]) -> Generator[int, None, None]:  # pragma: no cover
        """Annotation for subtraction with other `Self`"""
        ...

    def __sub__(
        self: Self, other: Union[int, timedelta, Self, Iterable[Union[int, timedelta, Self]]]
    ) -> Union[int, Self, Generator[Union[int, Self], None, None]]:
        """It supports subtraction with the following types:

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

        tuple(IsoWeekDate("2023-W01-1") - (1,2))  # (IsoWeekDate("2022-W52-7"), IsoWeekDate("2022-W52-6"))

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
            raise TypeError(
                f"Cannot subtract type {type(other)} to `IsoWeekDate`. "
                "Subtraction is supported with `int`, `timedelta` and `IsoWeekDate` types"
            )

    def daysout(
        self: Self,
        n_days: int,
        step: int = 1,
        as_str: bool = True,
    ) -> Generator[Union[str, IsoWeekDate], None, None]:
        """Generates range of `IsoWeekDate`s (or `str`s) from one day to `n_days` ahead of current `value`, with given
        `step`.

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

        tuple(iso.daysout(3)) # ('2023-W01-2', '2023-W01-3', '2023-W01-4')
        tuple(iso.daysout(6, step=2)) # ('2023-W01-2', '2023-W01-4', '2023-W01-6')
        ```
        """
        if not isinstance(n_days, int):
            raise TypeError(f"`n_weeks` must be integer, found {type(n_days)} type")

        if n_days <= 0:
            raise ValueError(f"`n_weeks` must be strictly positive, found {n_days}")

        start, end = (self + 1), (self + n_days)
        return self.range(start, end, step, inclusive="both", as_str=as_str)
