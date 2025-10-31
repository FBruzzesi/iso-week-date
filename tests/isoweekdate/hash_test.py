from __future__ import annotations

from typing import Final

from iso_week_date import IsoWeekDate
from tests.conftest import CustomIsoWeekDate

value: Final[str] = "2023-W01-1"


def test_hash(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    """Tests __hash__ method of IsoWeekDate class"""

    obj = isoweekdate_constructor(value)

    # Hash of same object should be equal
    assert hash(obj) == hash(obj)

    # Hash of object with same value should be equal
    obj2 = isoweekdate_constructor(value)
    assert hash(obj) == hash(obj2)

    # Hash of objects with different classes should be different
    if isoweekdate_constructor is IsoWeekDate:
        custom_obj = CustomIsoWeekDate(value)
        assert hash(obj) != hash(custom_obj)
    else:
        regular_obj = IsoWeekDate(value)
        assert hash(obj) != hash(regular_obj)
