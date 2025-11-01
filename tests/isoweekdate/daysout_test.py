from __future__ import annotations

from collections.abc import Generator
from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING
from typing import Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate

value: Final[str] = "2023-W01-1"


@pytest.mark.parametrize(
    ("n_days", "step", "exc_type", "exc_match"),
    [
        (1, 1, None, None),
        (1, 2, None, None),
        (10, 1, None, None),
        (1.0, 1, TypeError, "`n_weeks` must be integer"),
        (0, 1, ValueError, "`n_weeks` must be strictly positive"),
        (-2, 1, ValueError, "`n_weeks` must be strictly positive"),
    ],
)
def test_daysout(
    isoweekdate_constructor: type[IsoWeekDate],
    n_days: int,
    step: int,
    exc_type: type[Exception] | None,
    exc_match: str | None,
) -> None:
    """Tests daysout method of IsoWeekDate class"""
    obj = isoweekdate_constructor(value)
    context = pytest.raises(exc_type, match=exc_match) if exc_type else do_not_raise()
    with context:
        r = obj.daysout(n_days, step=step)
        assert isinstance(r, Generator)
