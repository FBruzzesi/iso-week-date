from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from typing import Any, Generator, Iterable, Tuple, TypeVar, Union, overload

from iso_week_date._patterns import ISOWEEK__DATE_FORMAT, ISOWEEK__FORMAT, ISOWEEK_PATTERN
from iso_week_date.base import BaseIsoWeek

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover

if sys.version_info >= (3, 12):
    from typing import override  # pragma: no cover
else:
    from typing_extensions import override  # pragma: no cover

IsoWeek_T = TypeVar("IsoWeek_T", date, datetime, str, "IsoWeek")


class IsoWeek(BaseIsoWeek):
    """Represents [ISO Week date](https://en.wikipedia.org/wiki/ISO_week_date) in the  _YYYY-WNN_ format and implements
    methods to work directly with it instead of going back and forth between `date`, `datetime` and `str` objects.

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
        """Returns tuple of days (as date) in the ISO week.

        Examples:
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").days  # (date(2023, 1, 2), ..., date(2023, 1, 8))
        ```
        """
        return tuple(self.to_date(weekday) for weekday in range(1, 8))

    def nth(self: Self, n: int) -> date:
        """Returns Nth day of the week using the ISO week weekday numbering convention
        (1=First day, 2=Second day, ..., 7=Last day).

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
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_datetime()  # datetime.datetime(2023, 1, 2, 0, 0)
        IsoWeek("2023-W01").to_datetime(3)  # datetime.datetime(2023, 1, 4, 0, 0)
        ```
        """

        if not isinstance(weekday, int):
            raise TypeError(f"`weekday` must be an integer between 1 and 7, found {type(weekday)}")
        if weekday not in range(1, 8):
            raise ValueError(f"Invalid `weekday`. Weekday must be between 1 and 7, found {weekday}")

        return super().to_datetime(f"{self.value_}-{weekday}")

    @override
    def to_date(self: Self, weekday: int = 1) -> date:  # type: ignore[override]
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
        ```py
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").to_date()  # datetime.date(2023, 1, 2)
        IsoWeek("2023-W01").to_date(3)  # datetime.date(2023, 1, 4)
        ```
        """
        return self.to_datetime(weekday).date()

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

        - `int`: interpreted as number of weeks to be added to the `IsoWeek` value.
        - `timedelta`: converts `IsoWeek` to datetime (first day of week), adds `timedelta` and converts back to
            `IsoWeek` object.
        - `Iterable` of `int` and/or `timedelta`: adds each element of the iterable to the `IsoWeek` value and returns
            a generator of `IsoWeek` objects.

        Arguments:
            other: Object to add to `IsoWeek`.

        Returns:
            New `IsoWeek` or generator of `IsoWeek` object(s) with the result of the addition.

        Raises:
            TypeError: If `other` is not `int`, `timedelta` or `Iterable` of `int` and/or `timedelta`.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") + 1  # IsoWeek("2023-W02")
        IsoWeek("2023-W01") + timedelta(weeks=2)  # IsoWeek("2023-W03")
        IsoWeek("2023-W01") + timedelta(hours=1234) # IsoWeek("2023-W08")

        tuple(IsoWeek("2023-W01") + (1,2,3)) # (IsoWeek("2023-W02"), IsoWeek("2023-W03"), IsoWeek("2023-W04"))
        ```
        """

        if isinstance(other, int):
            return self.from_date(self.to_date() + timedelta(weeks=other))
        elif isinstance(other, timedelta):
            return self.from_datetime(self.to_datetime() + other)
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, timedelta)) for _other in other):
            return (self + _other for _other in other)
        else:
            raise TypeError(
                f"Cannot add type {type(other)} to `IsoWeek`. " "Addition is supported with `int` and `timedelta` types"
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

        - `int`: interpreted as number of weeks to be subtracted to the `IsoWeek` value.
        - `timedelta`: converts `IsoWeek` to datetime (first day of week), subtract `timedelta` and converts back to
            `IsoWeek` object.
        - `IsoWeek`: will result in the difference between values in weeks (`int` type).
        - `Iterable` of `int`, `timedelta` and/or `IsoWeek`: subtracts each element of the iterable to the `IsoWeek`.

        Arguments:
            other: Object to subtract to `IsoWeek`.

        Returns:
            Results from the subtraction, can be `int`, `IsoWeek` or Generator of `int` and/or `IsoWeek` depending
                on the type of `other`.

        Raises:
            TypeError: If `other` is not `int`, `timedelta`, `IsoWeek` or `Iterable` of those types.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") - 1  # IsoWeek("2022-W52")
        IsoWeek("2023-W01") - timedelta(weeks=2)  # IsoWeek("2022-W51")
        IsoWeek("2023-W01") - timedelta(hours=1234)  # IsoWeek("2023-W45")

        tuple(IsoWeek("2023-W01") - (1,2,3))  # (IsoWeek("2022-W52"), IsoWeek("2022-W51"), IsoWeek("2022-W50"))

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
        elif isinstance(other, Iterable) and all(isinstance(_other, (int, timedelta, IsoWeek)) for _other in other):
            return (self - _other for _other in other)
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
        """Generates range of `IsoWeek`s (or `str`s) from one week to `n_weeks` ahead of current `value`, with given
        `step`.

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
        ```py
        from iso_week_date import IsoWeek
        iso = IsoWeek("2023-W01")

        tuple(iso.weeksout(4)) # ('2023-W02', '2023-W03', '2023-W04', '2023-W05')
        tuple(iso.weeksout(6, step=2))  # ('2023-W02', '2023-W04', '2023-W06')
        ```
        """
        if not isinstance(n_weeks, int):
            raise TypeError(f"`n_weeks` must be an integer, found {type(n_weeks)} type")

        if n_weeks <= 0:
            raise ValueError(f"`n_weeks` must be strictly positive, found {n_weeks}")

        start, end = (self + 1), (self + n_weeks)
        return self.range(start, end, step, inclusive="both", as_str=as_str)

    def __contains__(self: Self, other: Any) -> bool:
        """Checks if self contains `other`.

        Arguments:
            other: `IsoWeek`, `date`, `datetime` or `str`.

        Returns:
            `True` if self week contains other, `False` otherwise.

        Raises:
            TypeError: If other is not `IsoWeek`, `date`, `datetime` or `str`.

        Examples:
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
            raise TypeError(f"Cannot compare type `{type(other)}` with IsoWeek")

    @overload
    def contains(self: Self, other: IsoWeek_T) -> bool:  # pragma: no cover
        """Annotation for `contains` method on `IsoWeek` possible types."""
        ...

    @overload
    def contains(self: Self, other: Iterable[IsoWeek_T]) -> Tuple[bool]:  # pragma: no cover
        """Annotation for `contains` method on `Iterator` of `IsoWeek` possible types."""
        ...

    def contains(self: Self, other: Union[Any, Iterable[Any]]) -> Union[bool, Tuple[bool, ...]]:
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
        ```python
        from datetime import date
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01").contains([date(2023, 1, 1), date(2023, 1, 2)])
        # (False, True)
        ```
        """
        if isinstance(other, (date, datetime, str, IsoWeek)):
            return other in self
        elif isinstance(other, Iterable):
            return tuple(_other in self for _other in other)
        else:
            raise TypeError(f"Cannot compare type `{type(other)}` with `IsoWeek`")
