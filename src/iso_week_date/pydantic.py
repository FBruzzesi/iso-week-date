from __future__ import annotations

from typing import TYPE_CHECKING, Any

from iso_week_date._patterns import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
from iso_week_date._utils import match_isoweek, require_version, weeks_of_year

require_version("pydantic", minimum="2.4.0", extra="pydantic")

from pydantic_core import PydanticCustomError, core_schema  # noqa: E402

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler
    from typing_extensions import Self


__all__ = (
    "T_ISOWeek",
    "T_ISOWeekDate",
)


class T_ISOWeek(str):  # noqa: N801
    """T_ISOWeek parses iso week in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    !!! info "New in version 1.2.0"

    Examples:
        >>> from pydantic import BaseModel
        >>> from iso_week_date.pydantic import T_ISOWeek
        >>>
        >>> class Model(BaseModel):
        ...     isoweek: T_ISOWeek

        >>> model = Model(isoweek="2024-W01")
        >>> model
        Model(isoweek='2024-W01')

        >>> _ = Model(isoweek="2024-W53")
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Model
        isoweek
          Invalid week number. Year 2024 has only 52 weeks. [type=T_ISOWeek, input_value='2024-W53', input_type=str]

        >>> _ = Model(isoweek="abc")
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Model
        isoweek
          Invalid iso week pattern [type=T_ISOWeek, input_value='abc', input_type=str]
    """

    __slots__ = ()

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[Self],
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Return a Pydantic CoreSchema with the IsoWeek pattern validation.

        Arguments:
            source: The source type to be converted.
            handler: The handler to get the CoreSchema.

        Returns:
            A Pydantic CoreSchema with the IsoWeek pattern validation.
        """
        # The validator runs *after* `str_schema()` on purpose: as a "before" validator it would
        # see raw input of any type and `re` would raise a bare `TypeError` for e.g. `None` or `1`,
        # escaping pydantic's `ValidationError` contract entirely.
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls: type[Self], value: str, /) -> Self:
        """Validates iso week string format against ISOWEEK_PATTERN."""
        if (parsed := match_isoweek(ISOWEEK_PATTERN, value)) is None:
            raise PydanticCustomError("T_ISOWeek", "Invalid iso week pattern")  # noqa: EM101

        year, week = parsed

        if (weeks_in_year := weeks_of_year(year)) < week:
            raise PydanticCustomError(
                "T_ISOWeek",  # noqa: EM101
                "Invalid week number. Year {year} has only {weeks_in_year} weeks.",
                {"year": year, "weeks_in_year": weeks_in_year},
            )

        return cls(value)


class T_ISOWeekDate(str):  # noqa: N801
    """T_ISOWeekDate parses iso week date in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    !!! info "New in version 1.2.0"

    Examples:
        >>> from pydantic import BaseModel
        >>> from iso_week_date.pydantic import T_ISOWeekDate
        >>>
        >>> class Model(BaseModel):
        ...     isoweekdate: T_ISOWeekDate

        >>> model = Model(isoweekdate="2024-W01-1")
        >>> model
        Model(isoweekdate='2024-W01-1')

        >>> _ = Model(isoweekdate="2024-W53-1")
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Model
        isoweekdate
          Invalid week number. Year 2024 has only 52 weeks. [...]

        >>> _ = Model(isoweekdate="abc")
        Traceback (most recent call last):
        ...
        pydantic_core._pydantic_core.ValidationError: 1 validation error for Model
        isoweekdate
          Invalid iso week date pattern [...]
    """

    __slots__ = ()

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[Self],
        source: type[Any],
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Return a Pydantic CoreSchema with the IsoWeekDate pattern validation.

        Arguments:
            source: The source type to be converted.
            handler: The handler to get the CoreSchema.

        Returns:
            A Pydantic CoreSchema with the IsoWeekDate pattern validation.

        """
        # See `T_ISOWeek.__get_pydantic_core_schema__` for why this is an "after" validator.
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls: type[Self], value: str, /) -> Self:
        """Validates iso week date string format against ISOWEEKDATE_PATTERN."""
        if (parsed := match_isoweek(ISOWEEKDATE_PATTERN, value)) is None:
            raise PydanticCustomError("T_ISOWeekDate", "Invalid iso week date pattern")  # noqa: EM101

        year, week = parsed

        if (weeks_in_year := weeks_of_year(year)) < week:
            raise PydanticCustomError(
                "T_ISOWeekDate",  # noqa: EM101
                "Invalid week number. Year {year} has only {weeks_in_year} weeks.",
                {"year": year, "weeks_in_year": weeks_in_year},
            )

        return cls(value)
