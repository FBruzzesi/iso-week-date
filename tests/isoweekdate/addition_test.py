from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Sequence

    from iso_week_date import IsoWeekDate


value: Final[str] = "2025-W02-3"


@pytest.mark.parametrize(
    ("other", "expected"),
    [
        (1, "2025-W02-4"),
        (-1, "2025-W02-2"),
    ],
)
def test_add_scalar(isoweekdate_constructor: type[IsoWeekDate], other: int, expected: str) -> None:
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
def test_add_iterable(isoweekdate_constructor: type[IsoWeekDate], other: Sequence[int], expected: list[str]) -> None:
    obj = isoweekdate_constructor(value)
    expected_obj = [isoweekdate_constructor(e) for e in expected]
    assert list(obj + other) == expected_obj
    assert list(obj.add(other)) == expected_obj


@pytest.mark.parametrize(
    "factory",
    [
        lambda: (i for i in (-7, -1, 0, 2, 7)),
        lambda: map(int, ("-7", "-1", "0", "2", "7")),
        lambda: iter([-7, -1, 0, 2, 7]),
    ],
    ids=["genexp", "map", "list_iterator"],
)
def test_add_one_shot_iterator(
    isoweekdate_constructor: type[IsoWeekDate], factory: Callable[[], Iterator[int]]
) -> None:
    """A one-shot iterator must survive the element type check instead of arriving exhausted."""
    obj = isoweekdate_constructor(value)
    expected = ("2025-W01-3", "2025-W02-2", "2025-W02-3", "2025-W02-5", "2025-W03-3")
    expected_obj = [isoweekdate_constructor(e) for e in expected]

    assert list(obj + factory()) == expected_obj
    assert list(obj.add(factory())) == expected_obj


@pytest.mark.parametrize("factory", [lambda: (i for i in (1, 2.0)), lambda: iter(["1", 2])], ids=["genexp", "iter"])
def test_add_one_shot_iterator_raise(
    isoweekdate_constructor: type[IsoWeekDate], factory: Callable[[], Iterator[Any]]
) -> None:
    """A one-shot iterator with a bad element still raises, and does so eagerly."""
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot add type"):
        _ = obj + factory()


# See `tests/isoweek/addition_test.py`: `bool` is an `int` subclass and must not pass for a day count.
@pytest.mark.parametrize(
    "other",
    [timedelta(weeks=2), (1, 2, timedelta(weeks=2)), 1.0, "1", ("1", 2), True, False, (1, True)],
)
def test_add_raise(isoweekdate_constructor: type[IsoWeekDate], other: Any) -> None:
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot add type"):
        _ = obj + other

    with pytest.raises(TypeError, match="Cannot add type"):
        _ = obj.add(other)
