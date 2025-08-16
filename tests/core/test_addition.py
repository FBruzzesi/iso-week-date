from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

    from iso_week_date import IsoWeek
    from iso_week_date import IsoWeekDate


iso_week_value: Final[str] = "2025-W02"
iso_week_date_value: Final[str] = "2025-W02-3"


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W03"),
        (-1, "2025-W01"),
    ],
)
def test_isoweek_addition_scalar(isoweek_constructor: type[IsoWeek], other: int, expected: str) -> None:
    obj = isoweek_constructor(iso_week_value)
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
def test_isoweek_addition_iterable(
    isoweek_constructor: type[IsoWeek], other: Sequence[int], expected: list[str]
) -> None:
    obj = isoweek_constructor(iso_week_value)
    expected_obj = [isoweek_constructor(e) for e in expected]
    assert list(obj + other) == expected_obj
    assert list(obj.add(other)) == expected_obj


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, 2, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_isoweek_addition_raise(isoweek_constructor: type[IsoWeek], other: Any) -> None:
    obj = isoweek_constructor(iso_week_value)
    with pytest.raises(TypeError, match="Cannot add type"):
        obj + other

    with pytest.raises(TypeError, match="Cannot add type"):
        obj.add(other)


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W02-4"),
        (-1, "2025-W02-2"),
    ],
)
def test_isoweekdate_addition_scalar(isoweekdate_constructor: type[IsoWeekDate], other: int, expected: str) -> None:
    obj = isoweekdate_constructor(iso_week_date_value)
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
    obj = isoweekdate_constructor(iso_week_date_value)
    expected_obj = [isoweekdate_constructor(e) for e in expected]
    assert list(obj + other) == expected_obj
    assert list(obj.add(other)) == expected_obj


@pytest.mark.parametrize("other", [timedelta(weeks=2), (1, 2, timedelta(weeks=2)), 1.0, "1", ("1", 2)])
def test_isoweekdate_addition_raise(isoweekdate_constructor: type[IsoWeekDate], other: Any) -> None:
    obj = isoweekdate_constructor(iso_week_date_value)
    with pytest.raises(TypeError, match="Cannot add type"):
        obj + other

    with pytest.raises(TypeError, match="Cannot add type"):
        obj.add(other)
