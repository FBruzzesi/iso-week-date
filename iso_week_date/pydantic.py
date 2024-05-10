from __future__ import annotations

import re
import sys
from typing import TYPE_CHECKING, Any

from iso_week_date._patterns import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
from iso_week_date._utils import parse_version, weeks_of_year

if sys.version_info >= (3, 11):
    from typing import Self  # pragma: no cover
else:
    from typing_extensions import Self  # pragma: no cover

if parse_version("pydantic") < (2, 4, 0):
    raise ImportError(
        "pydantic>=2.4.0 is required for this module, install it with `python -m pip install pydantic>=2.4.0`"
        " or `python -m pip install iso-week-date[pydantic]`",
    )
else:
    from pydantic_core import PydanticCustomError, core_schema

    if TYPE_CHECKING:
        from pydantic import GetCoreSchemaHandler


class T_ISOWeek(str):  # noqa: N801
    """T_ISOWeek parses iso week in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    !!! info "New in version 1.2.0"

    Examples:
    ```py
    from pydantic import BaseModel
    from iso_week_date.pydantic import T_ISOWeek

    class Model(BaseModel):
        isoweek: T_ISOWeek

    model = Model(isoweek="2024-W01")
    print(model)
    # isoweek='2024-W01'

    _ = Model(isoweek="2024-W53")
    # ValidationError: 1 validation error for Model
    # isoweek
    #   Invalid week number. Year 2024 has only 52 weeks. [type=T_ISOWeek, input_value='2024-W53', input_type=str]

    _ = Model(isoweek="abc")
    # ValidationError: 1 validation error for Model
    # isoweek
    #   Invalid iso week pattern [type=T_ISOWeek, input_value='abc', input_type=str]
    ```
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
        return core_schema.with_info_before_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls: type[Self], __input_value: str, _: core_schema.ValidationInfo) -> Self:
        """Validates iso week string format against ISOWEEK_PATTERN."""
        _match = re.match(ISOWEEK_PATTERN, __input_value)

        if not _match:
            raise PydanticCustomError("T_ISOWeek", "Invalid iso week pattern")

        year, week = int(_match.group(1)), int(_match.group(2)[1:])

        if weeks_of_year(year) < week:
            raise PydanticCustomError(
                "T_ISOWeek",
                f"Invalid week number. Year {year} has only {weeks_of_year(year)} weeks.",
            )

        return cls(__input_value)


class T_ISOWeekDate(str):  # noqa: N801
    """T_ISOWeekDate parses iso week date in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    !!! info "New in version 1.2.0"

    Examples:
    ```py
    from pydantic import BaseModel
    from iso_week_date.pydantic import T_ISOWeekDate

    class Model(BaseModel):
        isoweekdate: T_ISOWeekDate

    model = Model(isoweekdate="2024-W01-1")
    print(model)
    # isoweekdate='2024-W01-1'

    _ = Model(isoweekdate="2024-W53-1")
    # ValidationError: 1 validation error for Model
    # isoweekdate
    #   Invalid week number. Year 2024 has only 52 weeks.
    #   [type=type=T_ISOWeekDate, input_value='2024-W53-1', input_type=str]

    _ = Model(isoweekdate="abc")
    # ValidationError: 1 validation error for Model
    # isoweekdate
    #   Invalid iso week pattern [type=type=T_ISOWeekDate, input_value='abc', input_type=str]
    ```
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
        return core_schema.with_info_before_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls: type[Self], __input_value: str, _: core_schema.ValidationInfo) -> Self:
        """Validates iso week date string format against ISOWEEKDATE_PATTERN."""
        _match = re.match(ISOWEEKDATE_PATTERN, __input_value)

        if not _match:
            raise PydanticCustomError("T_ISOWeekDate", "Invalid iso week date pattern")

        year, week = int(_match.group(1)), int(_match.group(2)[1:])

        if weeks_of_year(year) < week:
            raise PydanticCustomError(
                "T_ISOWeekDate",
                f"Invalid week number. Year {year} has only {weeks_of_year(year)} weeks.",
            )

        return cls(__input_value)
