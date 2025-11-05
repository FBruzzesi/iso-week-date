from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeek

value: Final[str] = "2025-W02"


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W03"),
        (0, "2025-W02"),
        (-1, "2025-W01"),
    ],
)
def test_add_scalar(isoweek_constructor: type[IsoWeek], other: int, expected: str) -> None:
    obj = isoweek_constructor(value)
    expected_obj = isoweek_constructor(expected)

    assert obj + other == expected_obj
    assert obj.add(other) == expected_obj


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-1, 0, 1, 2), ["2025-W01", "2025-W02", "2025-W03", "2025-W04"]),
        ([-1, 0, 1, 2], ["2025-W01", "2025-W02", "2025-W03", "2025-W04"]),
    ],
)
def test_add_iterable(isoweek_constructor: type[IsoWeek], other: Sequence[int], expected: list[str]) -> None:
    obj = isoweek_constructor(value)
    expected_obj = [isoweek_constructor(e) for e in expected]
    assert list(obj + other) == expected_obj
    assert list(obj.add(other)) == expected_obj


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, 2, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_add_raise(isoweek_constructor: type[IsoWeek], other: Any) -> None:
    obj = isoweek_constructor(value)
    with pytest.raises(TypeError, match="Cannot add type"):
        _ = obj + other

    with pytest.raises(TypeError, match="Cannot add type"):
        _ = obj.add(other)
