from __future__ import annotations

from typing import Final

from iso_week_date import IsoWeek
from tests.conftest import CustomIsoWeek

value: Final[str] = "2023-W01"


def test_hash(isoweek_constructor: type[IsoWeek]) -> None:
    """Tests __hash__ method of IsoWeek class"""

    obj = isoweek_constructor(value)

    # Hash of same object should be equal
    assert hash(obj) == hash(obj)

    # Hash of object with same value should be equal
    obj2 = isoweek_constructor(value)
    assert hash(obj) == hash(obj2)

    # Hash of objects with different classes should be different
    if isoweek_constructor is IsoWeek:
        custom_obj = CustomIsoWeek(value)
        assert hash(obj) != hash(custom_obj)
    else:
        regular_obj = IsoWeek(value)
        assert hash(obj) != hash(regular_obj)
