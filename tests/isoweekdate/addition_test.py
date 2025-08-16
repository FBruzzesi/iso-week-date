from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeekDate


value: Final[str] = "2025-W02-3"


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W02-4"),
        (-1, "2025-W02-2"),
    ],
)
def test_isoweekdate_addition_scalar(isoweekdate_constructor: type[IsoWeekDate], other: int, expected: str) -> None:
    obj = isoweekdate_constructor(value)
    expected_obj = isoweekdate_constructor(expected)

    assert obj + other == expected_obj
    assert obj.add(other) == expected_obj


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-7, -1, 0, 2, 7), ["2025-W01-3", "2025-W02-2", "2025-W02-3", "2025-W02-5", "2025-W03-3"]),
        ([-7, -1, 0, 2, 7], ["2025-W01-3", "2025-W02-2", "2025-W02-3", "2025-W02-5", "2025-W03-3"]),
    ],
)
def test_isoweekdate_addition_iterable(
    isoweekdate_constructor: type[IsoWeekDate], other: Sequence[int], expected: list[str]
) -> None:
    obj = isoweekdate_constructor(value)
    expected_obj = [isoweekdate_constructor(e) for e in expected]
    assert list(obj + other) == expected_obj
    assert list(obj.add(other)) == expected_obj


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, 2, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_isoweekdate_addition_raise(isoweekdate_constructor: type[IsoWeekDate], other: Any) -> None:
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot add type"):
        obj + other

    with pytest.raises(TypeError, match="Cannot add type"):
        obj.add(other)
