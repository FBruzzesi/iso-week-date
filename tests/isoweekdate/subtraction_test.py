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


@pytest.mark.parametrize(
    "factory",
    [
        lambda: (i for i in (-1, 0, 1, 7)),
        lambda: map(int, ("-1", "0", "1", "7")),
        lambda: iter([-1, 0, 1, 7]),
    ],
    ids=["genexp", "map", "list_iterator"],
)
def test_sub_one_shot_iterator(
    isoweekdate_constructor: type[IsoWeekDate], factory: Callable[[], Iterator[int]]
) -> None:
    """A one-shot iterator must survive the element type check instead of arriving exhausted."""
    obj = isoweekdate_constructor(value)
    expected = ("2025-W02-4", "2025-W02-3", "2025-W02-2", "2025-W01-3")
    expected_obj = [isoweekdate_constructor(e) for e in expected]

    assert list(obj - factory()) == expected_obj
    assert list(obj.sub(factory())) == expected_obj


def test_sub_one_shot_iterator_of_isoweekdates(isoweekdate_constructor: type[IsoWeekDate]) -> None:
    """The mixed `int`/`IsoWeekDate` iterable branch must handle one-shot iterators too."""
    obj = isoweekdate_constructor(value)
    others = (1, isoweekdate_constructor("2025-W02-1"), -1)

    expected = [isoweekdate_constructor("2025-W02-2"), 2, isoweekdate_constructor("2025-W02-4")]
    assert list(obj - iter(others)) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize("factory", [lambda: (i for i in (1, 2.0)), lambda: iter(["1", 2])], ids=["genexp", "iter"])
def test_sub_one_shot_iterator_raise(
    isoweekdate_constructor: type[IsoWeekDate], factory: Callable[[], Iterator[Any]]
) -> None:
    """A one-shot iterator with a bad element still raises, and does so eagerly."""
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj - factory()


# See `tests/isoweek/addition_test.py`: `bool` is an `int` subclass and must not pass for a day count.
@pytest.mark.parametrize(
    "other",
    [timedelta(weeks=2), (1, timedelta(weeks=2)), 1.0, "1", ("1", 2), True, False, (1, True)],
)
def test_sub_raise(isoweekdate_constructor: type[IsoWeekDate], other: Any) -> None:
    obj = isoweekdate_constructor(value)
    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj - other

    with pytest.raises(TypeError, match="Cannot subtract type"):
        _ = obj.sub(other)
