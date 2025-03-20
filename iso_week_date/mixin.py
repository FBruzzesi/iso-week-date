from __future__ import annotations

from datetime import date
from datetime import datetime
from datetime import timedelta
from typing import TYPE_CHECKING
from typing import ClassVar
from typing import Protocol
from typing import runtime_checkable

from iso_week_date._utils import classproperty
from iso_week_date._utils import format_err_msg

if TYPE_CHECKING:  # pragma: no cover
    import re

    from typing_extensions import Self


@runtime_checkable
class IsoWeekProtocol(Protocol):  # pragma: no cover
    """Protocol for `BaseIsoWeek`."""

    value_: str
    _pattern: ClassVar[re.Pattern[str]]

    _format: ClassVar[str]
    _date_format: ClassVar[str]

    offset_: ClassVar[timedelta] = timedelta(days=0)

    def __init__(self: Self, value: str) -> None:
        """Init takes a string value which will be validated."""
        ...

    @property
    def name(self: Self) -> str:
        """Property that returns the class name."""
        ...

    @classmethod
    def _validate(cls: type[IsoWeekProtocol], value: str) -> str:
        """Classmethod that validates the string passed as input."""
        ...

    @classproperty
    def _compact_pattern(cls: type[IsoWeekProtocol]) -> re.Pattern[str]:  # noqa: N805
        """Classproperty that returns the compiled compact pattern."""
        ...

    @classproperty
    def _compact_format(cls: type[IsoWeekProtocol]) -> str:  # noqa: N805
        """Classproperty that returns the compact format as string."""
        ...


class ParserMixin(IsoWeekProtocol):
    """Mixin that handles conversion from types.

    `ParserMixin` implements `from_*` (class) methods to parse from:

    - `str`: string matching `pattern`, will be validated.
    - `str`: string matching `compact_pattern`, will be validated.
    - `date`: casted to ISO Week `_date_format` using `.strftime()` method after applying `offset_`.
    - `datetime`:casted to ISO Week `_date_format` using `.strftime()` method after applying `offset_`.

    Additionally, it implements `._cast()` class method that automatically casts to ISOWeek-like type from the by
    calling the appropriate method for parsing.
    """

    @classmethod
    def from_string(cls: type[Self], _str: str) -> Self:
        """Parse a string object in `_pattern` format."""
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)
        return cls(_str)

    @classmethod
    def from_compact(cls: type[Self], _str: str) -> Self:
        """Parse a string object in `_compact_format` format.

        Since values are validated in the initialization method, our goal in this method is to "add" the dashes in the
        appropriate places. To achieve this we:

        - First check that the length of the string is correct (either 7 or 8).
        - Split the string in 3 parts.
        - Remove (filter) empty values.
        - Finally join them with a dash in between.
        """
        if not isinstance(_str, str):
            msg = f"Expected `str` type, found {type(_str)}"
            raise TypeError(msg)

        if len(_str) != len(cls._compact_format):
            raise ValueError(format_err_msg(cls._compact_format, _str))

        split_idx = (0, 4, 7, None)
        value = "-".join(filter(None, (_str[i:j] for i, j in zip(split_idx[:-1], split_idx[1:]))))
        return cls(value)

    @classmethod
    def from_date(cls: type[Self], _date: date) -> Self:
        """Parse a date object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_date, date):
            msg = f"Expected `date` type, found {type(_date)}"
            raise TypeError(msg)
        return cls((_date - cls.offset_).strftime(cls._date_format))

    @classmethod
    def from_datetime(cls: type[Self], _datetime: datetime) -> Self:
        """Parse a datetime object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_datetime, datetime):
            msg = f"Expected `datetime` type, found {type(_datetime)}"
            raise TypeError(msg)

        return cls((_datetime - cls.offset_).strftime(cls._date_format))

    @classmethod
    def from_today(cls: type[Self]) -> Self:  # pragma: no cover
        """Instantiates class from today's date."""
        return cls.from_date(date.today())

    @classmethod
    def from_values(cls: type[Self], year: int, week: int, weekday: int = 1) -> Self:
        """Parse year, week and weekday values to `_format` format."""
        value = (
            cls._format.replace("YYYY", str(year).zfill(4))
            .replace("NN", str(week).zfill(2))
            .replace("D", str(weekday).zfill(1))
        )
        return cls(value)

    @classmethod
    def _cast(cls: type[Self], value: str | date | datetime | IsoWeekProtocol) -> Self:
        """Tries to cast from different types.

        - `str`: string matching `_pattern`.
        - `date`: casted to ISO Week by calling `.from_date()` method.
        - `datetime`: casted to ISO Week by calling `.from_datetime()` method.
        - `ISOWeek`-like: value will be returned as is.

        Arguments:
            value: Value to be casted to ISO Week object.

        Returns:
            `ISOWeek`-like object

        Raises:
            NotImplementedError: If `value` is not of type `str`, `date`, `datetime` or `ISOWeek`-like.

        Examples:
        ```py
        from datetime import date
        from iso_week_date import IsoWeek

        IsoWeek._cast("2023-W01")  # IsoWeek("2023-W01")
        ```
        """
        if isinstance(value, str):
            return cls.from_string(value)
        elif isinstance(value, datetime):
            return cls.from_datetime(value)
        elif isinstance(value, date):
            return cls.from_date(value)
        elif isinstance(value, cls):
            return value
        else:
            msg = f"Cannot cast type {type(value)} into {cls.__name__}"
            raise NotImplementedError(msg)


class ConverterMixin(IsoWeekProtocol):
    """Mixin that handles conversion to types.

    `ConverterMixin` implements `to_*` methods to convert to the following types:

    - `str`
    - `date`
    - `datetime`
    """

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
        """
        return datetime.strptime(value, "%G-W%V-%u") + self.offset_

    def _to_date(self: Self, value: str) -> date:  # pragma: no cover
        """Converts `value` to `date` object and adds the `offset_`.

        !!! warning
            `value` must be in "%G-W%V-%u" format.

            In general this is not always the case and we need to manipulate `value_` attribute before passing it to
            `datetime.strptime` method.
        """
        return self._to_datetime(value).date()

    def to_values(self: Self) -> tuple[int, ...]:
        """Converts `value_` to a tuple of integers (year, week, [weekday])."""
        return tuple(int(v.replace("W", "")) for v in self.value_.split("-"))


class ComparatorMixin(IsoWeekProtocol):
    """Mixin that implements comparison operators ("==", "!=", "<", "<=", ">", ">=") between two ISO Week objects."""

    def __eq__(self: Self, other: object) -> bool:
        """Equality operator.

        Two ISO Week objects are considered equal if and only if they have the same `offset_` and the same `value_`.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if objects are equal, `False` otherwise.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") == IsoWeek("2023-W01")  # True
        IsoWeek("2023-W01") == IsoWeek("2023-W02")  # False


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") == CustomIsoWeek("2023-W01")  # False
        ```
        """
        if isinstance(other, self.__class__):
            return (self.offset_ == other.offset_) and (self.value_ == other.value_)
        return False

    def __ne__(self: Self, other: object) -> bool:
        """Inequality operator.

        Two ISO Week objects are considered equal if and only if they have the same `offset_` and the same `value_`.

        Arguments:
            other: Object to compare with.

        Returns:
            `True` if objects are _not_ equal, `False` otherwise.

        Examples:
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") != IsoWeek("2023-W01")  # False
        IsoWeek("2023-W01") != IsoWeek("2023-W02")  # True


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") != CustomIsoWeek("2023-W01")  # True
        ```
        """
        return not self.__eq__(other)

    def __lt__(self: Self, other: Self) -> bool:
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
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") < IsoWeek("2023-W02")  # True
        IsoWeek("2023-W02") < IsoWeek("2023-W01")  # False


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") < CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") < "2023-W01"  # TypeError
        ```
        """
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

    def __le__(self: Self, other: Self) -> bool:
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
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") <= IsoWeek("2023-W01")  # True
        IsoWeek("2023-W02") <= IsoWeek("2023-W01")  # False


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") <= CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") <= "2023-W01"  # TypeError
        ```
        """
        return self.__lt__(other) or self.__eq__(other)

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
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") >= IsoWeek("2023-W02")  # False
        IsoWeek("2023-W01") >= IsoWeek("2023-W01")  # True


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") >= CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") >= "2023-W01"  # TypeError
        ```
        """
        return not self.__le__(other)

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
        ```py
        from datetime import timedelta
        from iso_week_date import IsoWeek

        IsoWeek("2023-W01") > IsoWeek("2023-W02")  # False
        IsoWeek("2023-W02") > IsoWeek("2023-W01")  # True


        class CustomIsoWeek(IsoWeek):
            offset_ = timedelta(days=1)


        IsoWeek("2023-W01") > CustomIsoWeek("2023-W01")  # TypeError
        IsoWeek("2023-W01") > "2023-W01"  # TypeError
        ```
        """
        return not self.__lt__(other)
