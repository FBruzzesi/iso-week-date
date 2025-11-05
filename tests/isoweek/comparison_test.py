from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("lower_bound_offset", "upper_bound_offset", "inclusive", "expected"),
    [
        (0, 1, "both", True),
        (0, 1, "right", False),
        (0, 1, "left", True),
        (0, 1, "neither", False),
    ],
)
def test_is_between(
    isoweek_constructor: type[IsoWeek],
    lower_bound_offset: int,
    upper_bound_offset: int,
    inclusive: Literal["both", "left", "right", "neither"],
    expected: bool,
) -> None:
    """Tests is_between method of IsoWeek class"""
    obj = isoweek_constructor(value)
    lower_bound = obj + lower_bound_offset
    upper_bound = obj + upper_bound_offset

    assert obj.is_between(lower_bound, upper_bound, inclusive=inclusive) == expected
