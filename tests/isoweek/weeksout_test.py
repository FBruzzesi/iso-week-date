from __future__ import annotations

from collections.abc import Generator
from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING, Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("n_weeks", "step", "expected_exception", "err_msg"),
    [
        (1, 1, None, None),
        (1, 2, None, None),
        (10, 1, None, None),
        (1.0, 1, TypeError, "`n_weeks` must be an integer"),
        (0, 1, ValueError, "`n_weeks` must be strictly positive"),
        (-2, 1, ValueError, "`n_weeks` must be strictly positive"),
    ],
)
def test_weeksout(
    isoweek_constructor: type[IsoWeek],
    n_weeks: float,
    step: int,
    expected_exception: type[Exception] | None,
    err_msg: str | None,
) -> None:
    """Tests weeksout method of IsoWeek class"""
    obj = isoweek_constructor(value)
    context = pytest.raises(expected_exception, match=err_msg) if expected_exception else do_not_raise()
    with context:
        r = obj.weeksout(n_weeks, step=step)  # type: ignore[call-overload]
        assert isinstance(r, Generator)
