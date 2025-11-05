from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate


@pytest.mark.parametrize("isoweek", ("2023-W01", "2023-W02", "2023-W52"))
@pytest.mark.parametrize("weekday", range(1, 8))
def test_property(isoweekdate_constructor: type[IsoWeekDate], isoweek: str, weekday: int) -> None:
    """Tests properties unique of IsoWeekDate class, namely day and isoweek"""
    obj = isoweekdate_constructor(f"{isoweek}-{weekday}")
    assert obj.day == weekday
    assert obj.isoweek == isoweek
