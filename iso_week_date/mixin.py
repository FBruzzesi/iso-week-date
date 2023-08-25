import re
from datetime import date, datetime, timedelta
from typing import Any, ClassVar, Protocol, Type, TypeVar, runtime_checkable

try:
    from typing import Self
except ImportError:
    from typing_extensions import Self


@runtime_checkable
class IsoWeekProtocol(Protocol):  # pragma: no cover
    """Protocol for `BaseIsoWeek`."""

    value_: str
    _pattern: ClassVar[re.Pattern]

    _format: ClassVar[str]
    _date_format: ClassVar[str]

    offset_: ClassVar[timedelta] = timedelta(days=0)

    def __init__(self, value: str, __validate: bool = True) -> None:
        """Initialization should take a string value and a boolean flag."""
        ...

    @property
    def name(self: Self) -> str:
        """`name` is a property that should return the class name."""
        ...

    @classmethod
    def validate(cls: Type[Self], value: str) -> str:
        """`validate` is a class method that should take one argument."""
        ...

    @classmethod
    def validate_compact(cls: Type[Self], value: str) -> str:
        """`validate_compact` is a class method that should take one argument."""
        ...


IsoWeek_T = TypeVar("IsoWeek_T", str, date, datetime, "IsoWeekProtocol")


class ParserMixin:
    """
    Mixin that implements `from_*` class methods to parse from:

    - `str`: string matching `pattern`, will be validated
    - `str`: string matching `compact_pattern`, will be validated
    - `date`: casted to ISO Week `_date_format` using `.strftime` method after applying
        `offset_`
    - `datetime`:casted to ISO Week `_date_format` using `.strftime` method after applying
        `offset_`

    Additionally, it implements `_cast` class method that automatically casts to
    `IsoWeekProtocol` type from the above type by calling the appropriate method.
    """

    @classmethod
    def from_string(cls: Type[IsoWeekProtocol], _str: str) -> IsoWeekProtocol:
        """Parse a string object in `_pattern` format."""
        if not isinstance(_str, str):
            raise TypeError(f"Expected `str` type, found {type(_str)}.")
        return cls(cls.validate(_str), False)

    @classmethod
    def from_compact(cls: Type[IsoWeekProtocol], _str: str) -> IsoWeekProtocol:
        """Parse a string object in `_compact_pattern` format."""
        if not isinstance(_str, str):
            raise TypeError(f"Expected `str` type, found {type(_str)}.")

        return cls(cls.validate_compact(_str), False)

    @classmethod
    def from_date(cls: Type[IsoWeekProtocol], _date: date) -> IsoWeekProtocol:
        """Parse a date object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_date, date):
            raise TypeError(f"Expected `date` type, found {type(_date)}.")
        return cls((_date - cls.offset_).strftime(cls._date_format), False)

    @classmethod
    def from_datetime(cls: Type[IsoWeekProtocol], _datetime: datetime) -> IsoWeekProtocol:
        """Parse a datetime object to `_date_format` after adjusting by `offset_`."""
        if not isinstance(_datetime, datetime):
            raise TypeError(f"Expected `datetime` type, found {type(_datetime)}.")

        return cls((_datetime - cls.offset_).strftime(cls._date_format), False)

    @classmethod
    def from_today(cls: Type[Self]) -> IsoWeekProtocol:  # pragma: no cover
        """Instantiates class from today's date"""
        return cls.from_date(date.today())

    @classmethod
    def _cast(cls: Type[Self], value: IsoWeek_T) -> IsoWeekProtocol:
        """
        Automatically casts to `IsoWeekProtocol` type from the following possible types:

        - `str`: string matching `_pattern`
        - `date`: casted to ISO Week by calling `from_date` method
        - `datetime`: casted to ISO Week by calling `from_datetime` method
        - `IsoWeekProtocol`: value will be returned as is

        Arguments:
            value: value to be casted to ISO Week object

        Returns:
            `IsoWeekProtocol` object

        Raises:
            NotImplementedError: if `value` is not `str`, `date`, `datetime` or
                `IsoWeekProtocol`

        Usage:
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
            raise NotImplementedError(
                f"Cannot cast type {type(value)} into {cls.__name__}"
            )


class ConverterMixin:
    """
    Mixin that implements `to_*` instance methods to convert to the following types:

    - `str`
    - `date`
    - `datetime`
    """

    def to_string(self: IsoWeekProtocol) -> str:
        """Returns as a string in the classical format."""
        return self.value_

    def to_compact(self: IsoWeekProtocol) -> str:
        """Returns as a string in the compact format."""
        return self.value_.replace("-", "")

    def to_datetime(self: IsoWeekProtocol, value: str) -> datetime:
        """
        Converts `value` to `datetime` object and adds the `offset_`.

        !Warning: `value` must be in "%G-W%V-%u" format.
        In general this is not always the case and we need to manipulate `value_`
        attribute before passing it to `datetime.strptime` method.
        """
        return datetime.strptime(value, "%G-W%V-%u") + self.offset_

    def to_date(self: Self, value: str) -> date:  # pragma: no cover
        """
        Converts `value` to `date` object and adds the `offset_`.

        !Warning: `value` must be in "%G-W%V-%u" format.
        In general this is not always the case and we need to manipulate `value_`
        attribute before passing it to `datetime.strptime` method.
        """
        return self.to_datetime(value).date()


class ComparatorMixin:
    """
    Mixin that implements comparison operators ("==", "!=", "<", "<=", ">", ">=") between
    two ISO Week objects.
    """

    def __eq__(self: IsoWeekProtocol, other: Any) -> bool:
        """
        Equality operator.

        Two ISO Week objects are considered equal if and only if they have the same
        `offset_` and the same `value_`.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are equal, `False` otherwise

        Usage:
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
        else:
            return False

    def __ne__(self: Self, other: Any) -> bool:
        """
        Inequality operator.

        Two ISO Week objects are considered equal if and only if they have the same
        `offset_` and the same `value_`.

        Arguments:
            other: object to compare with

        Returns:
            `True` if objects are _not_ equal, `False` otherwise

        Usage:
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

    def __lt__(self: IsoWeekProtocol, other: IsoWeekProtocol) -> bool:
        """
        Less than operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
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
                raise TypeError(f"Cannot compare `{self.name}`'s with different offsets")
        else:
            raise TypeError(
                f"Cannot compare `{self.name}` with type `{type(other)}`, "
                f"comparison is supported only with other `{self.name}` objects"
            )

    def __le__(self: Self, other: IsoWeekProtocol) -> bool:
        """
        Less than or equal operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is less than or equal to other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
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

    def __gt__(self: Self, other: IsoWeekProtocol) -> bool:
        """Greater than operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
            other: object to compare with

        Returns:
            `True` if self is greater than other, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
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

    def __ge__(self: Self, other: IsoWeekProtocol) -> bool:
        """
        Greater than or equal operator.

        Comparing two ISO Week objects is only possible if they have the same `offset_`.

        If that's the case than it's enough to compare their values (as `str`) due to its
        lexicographical order.

        Arguments:
           other: object to compare with

        Returns:
            `True` if self is greater than or equal to `other`, `False` otherwise

        Raises:
            TypeError: if `other` is not of same type or it has a different offset

        Usage:
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
