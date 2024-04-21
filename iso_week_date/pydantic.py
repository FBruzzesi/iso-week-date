from __future__ import annotations

import re
from typing import Any

from iso_week_date._patterns import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
from iso_week_date._utils import weeks_of_year

try:
    from pydantic import GetCoreSchemaHandler
    from pydantic_core import PydanticCustomError, core_schema
except ImportError:  # pragma: no cover
    raise ImportError(
        "pydantic>=2.4.0 is required for this module, install it with `python -m pip install pydantic>=2.4.0`"
        " or `python -m pip install iso-week-date[pydantic]`"
    )


class IsoWeek_T(str):
    """IsoWeek_T parses iso week in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    Examples:
    ```py
    from pydantic import BaseModel
    from iso_week_date.pydantic import IsoWeek_T

    class Model(BaseModel):
        isoweek: IsoWeek_T

    model = Model(isoweek="2024-W01")
    print(model)
    # isoweek='2024-W01'

    _ = Model(isoweek="2024-W53")
    # ValidationError: 1 validation error for Model
    # isoweek
    #   Invalid week number. Year 2024 has only 52 weeks. [type=IsoWeek_T, input_value='2024-W53', input_type=str]

    _ = Model(isoweek="abc")
    # ValidationError: 1 validation error for Model
    # isoweek
    #   Invalid iso week pattern [type=IsoWeek_T, input_value='abc', input_type=str]
    ```

    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[IsoWeek_T], source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema with the IsoWeek pattern validation.

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
    def _validate(cls, __input_value: str, _: core_schema.ValidationInfo) -> IsoWeek_T:
        """Validates iso week string format against ISOWEEK_PATTERN."""
        _match = re.match(ISOWEEK_PATTERN, __input_value)

        if not _match:
            raise PydanticCustomError("IsoWeek_T", "Invalid iso week pattern")

        year, week = int(_match.group(1)), int(_match.group(2)[1:])

        if weeks_of_year(year) < week:
            raise PydanticCustomError(
                "IsoWeek_T", f"Invalid week number. Year {year} has only {weeks_of_year(year)} weeks."
            )

        return cls(__input_value)


class IsoWeekDate_T(str):
    """IsoWeekDate_T parses iso week date in the [ISO 8601](https://en.wikipedia.org/wiki/ISO_week_date) format.

    Examples:
    ```py
    from pydantic import BaseModel
    from iso_week_date.pydantic import IsoWeekDate_T

    class Model(BaseModel):
        isoweekdate: IsoWeekDate_T

    model = Model(isoweekdate="2024-W01-1")
    print(model)
    # isoweekdate='2024-W01-1'

    _ = Model(isoweekdate="2024-W53-1")
    # ValidationError: 1 validation error for Model
    # isoweekdate
    #   Invalid week number. Year 2024 has only 52 weeks. [type=type=IsoWeekDate_T, input_value='2024-W53-1', input_type=str]

    _ = Model(isoweekdate="abc")
    # ValidationError: 1 validation error for Model
    # isoweekdate
    #   Invalid iso week pattern [type=type=IsoWeekDate_T, input_value='abc', input_type=str]
    ```
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls: type[IsoWeekDate_T], source: type[Any], handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema with the IsoWeekDate pattern validation.

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
    def _validate(cls, __input_value: str, _: core_schema.ValidationInfo) -> IsoWeek_T:
        """Validates iso week date string format against ISOWEEKDATE_PATTERN."""
        _match = re.match(ISOWEEKDATE_PATTERN, __input_value)

        if not _match:
            raise PydanticCustomError("IsoWeekDate_T", "Invalid iso week date pattern")

        year, week, day = int(_match.group(1)), int(_match.group(2)[1:]), int(_match.group(3))

        if weeks_of_year(year) < week:
            raise PydanticCustomError(
                "IsoWeekDate_T", f"Invalid week number. Year {year} has only {weeks_of_year(year)} weeks."
            )

        if day not in range(1, 8):
            raise PydanticCustomError("IsoWeekDate_T", "Invalid day number. Day should be between 1 and 7 (inclusive)")

        return cls(__input_value)
