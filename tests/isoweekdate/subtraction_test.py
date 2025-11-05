from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeekDate


value: Final[str] = "2025-W02-3"


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W02-2"),
        (0, "2025-W02-3"),
        (-1, "2025-W02-4"),
    ],
)
def test_sub_scalar(isoweekdate_constructor: type[IsoWeekDate], other: int, expected: str) -> None:
    obj = isoweekdate_constructor(value)
    expected_obj = isoweekdate_constructor(expected)

    assert obj - other == expected_obj
    assert obj.sub(other) == expected_obj


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-1, 0, 1, 7), ["2025-W02-4", "2025-W02-3", "2025-W02-2", "2025-W01-3"]),
        ([-1, 0, 1, 7], ["2025-W02-4", "2025-W02-3", "2025-W02-2", "2025-W01-3"]),
    ],
)
def test_sub_iterable(isoweekdate_constructor: type[IsoWeekDate], other: Sequence[int], expected: list[str]) -> None:
    obj = isoweekdate_constructor(value)
    expected_obj = [isoweekdate_constructor(e) for e in expected]
    assert list(obj - other) == expected_obj
    assert list(obj.sub(other)) == expected_obj


@pytest.mark.parametrize(("other", "expected"), (("2025-W02-2", 1), ("2025-W02-3", 0), ("2025-W03-1", -5)))
def test_sub_isoweek(isoweekdate_constructor: type[IsoWeekDate], other: str, expected: int) -> None:
    obj = isoweekdate_constructor(value)
    other_obj = isoweekdate_constructor(other)

    assert obj - other_obj == expected
    assert obj.sub(other_obj) == expected


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        ((-1, "2025-W02-3", 1, "2025-W02-1"), ["2025-W02-4", 0, "2025-W02-2", 2]),
        (["2025-W02-4", 0, "2025-W02-2", 2], [-1, "2025-W02-3", 1, "2025-W02-1"]),
    ],
)
def test_sub_mixed_iter(
    isoweekdate_constructor: type[IsoWeekDate], other: list[int | str], expected: list[str | int]
) -> None:
    obj = isoweekdate_constructor(value)
    other_obj = [e if isinstance(e, int) else isoweekdate_constructor(e) for e in other]
    expected_obj = [e if isinstance(e, int) else isoweekdate_constructor(e) for e in expected]
    assert list(obj - other_obj) == expected_obj  # type: ignore[arg-type]
    assert list(obj.sub(other_obj)) == expected_obj  # type: ignore[arg-type]


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_sub_raise(isoweekdate_constructor: type[IsoWeekDate], other: Any) -> None:
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj - other

    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj.sub(other)
