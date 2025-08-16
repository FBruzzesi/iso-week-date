from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

import pytest

from iso_week_date import IsoWeek
from iso_week_date import IsoWeekDate

if TYPE_CHECKING:
    from iso_week_date._base import BaseIsoWeek


class CustomIsoWeek(IsoWeek):
    """Custom IsoWeek class with offset of 1 day"""

    offset_ = timedelta(days=1)


class CustomIsoWeekDate(IsoWeekDate):
    """Custom IsoWeekDate class with offset of 1 day"""

    offset_ = timedelta(days=1)


isoweek_constructors = [IsoWeek, CustomIsoWeek]
isoweekdate_constructors = [IsoWeekDate, CustomIsoWeekDate]


@pytest.fixture(params=isoweek_constructors)
def isoweek_constructor(request: pytest.FixtureRequest) -> type[IsoWeek]:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture(params=isoweekdate_constructors)
def isoweekdate_constructor(request: pytest.FixtureRequest) -> type[IsoWeekDate]:
    return request.param  # type: ignore[no-any-return]


@pytest.fixture(params=[*isoweek_constructors, *isoweekdate_constructors])
def constructor(request: pytest.FixtureRequest) -> type[BaseIsoWeek]:
    return request.param  # type: ignore[no-any-return]
