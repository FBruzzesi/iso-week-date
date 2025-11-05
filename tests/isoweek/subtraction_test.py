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
        (1, "2025-W01"),
        (0, "2025-W02"),
        (-1, "2025-W03"),
    ],
)
def test_sub_scalar(isoweek_constructor: type[IsoWeek], other: int, expected: str) -> None:
    obj = isoweek_constructor(value)
    expected_obj = isoweek_constructor(expected)

    assert obj - other == expected_obj
    assert obj.sub(other) == expected_obj


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-1, 0, 1, 2), ["2025-W03", "2025-W02", "2025-W01", "2024-W52"]),
        ([-1, 0, 1, 2], ["2025-W03", "2025-W02", "2025-W01", "2024-W52"]),
    ],
)
def test_sub_iterable(isoweek_constructor: type[IsoWeek], other: Sequence[int], expected: list[str]) -> None:
    obj = isoweek_constructor(value)
    expected_obj = [isoweek_constructor(e) for e in expected]
    assert list(obj - other) == expected_obj
    assert list(obj.sub(other)) == expected_obj


@pytest.mark.parametrize(("other", "expected"), (("2025-W01", 1), ("2025-W02", 0), ("2025-W03", -1)))
def test_sub_isoweek(isoweek_constructor: type[IsoWeek], other: str, expected: int) -> None:
    obj = isoweek_constructor(value)
    other_obj = isoweek_constructor(other)

    assert obj - other_obj == expected
    assert obj.sub(other_obj) == expected


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-1, "2025-W02", 1, "2024-W52"), ["2025-W03", 0, "2025-W01", 2]),
        (("2025-W03", 0, "2025-W01", 2), [-1, "2025-W02", 1, "2024-W52"]),
    ],
)
def test_sub_mixed_iter(isoweek_constructor: type[IsoWeek], other: list[int | str], expected: list[str | int]) -> None:
    obj = isoweek_constructor(value)
    other_obj = [e if isinstance(e, int) else isoweek_constructor(e) for e in other]
    expected_obj = [e if isinstance(e, int) else isoweek_constructor(e) for e in expected]
    assert list(obj - other_obj) == expected_obj  # type: ignore[arg-type]
    assert list(obj.sub(other_obj)) == expected_obj  # type: ignore[arg-type]


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_sub_raise(isoweek_constructor: type[IsoWeek], other: Any) -> None:
    obj = isoweek_constructor(value)
    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj - other

    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj.sub(other)
