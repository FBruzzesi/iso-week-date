from __future__ import annotations

from collections.abc import Generator
from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeekDate

value: Final[str] = "2023-W01-1"


@pytest.mark.parametrize(
    ("n_days", "step", "context"),
    [
        (1, 1, do_not_raise()),
        (1, 2, do_not_raise()),
        (10, 1, do_not_raise()),
        (1.0, 1, pytest.raises(TypeError, match="`n_weeks` must be integer")),
        (0, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
        (-2, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
    ],
)
def test_daysout(
    isoweekdate_constructor: type[IsoWeekDate],
    n_days: int,
    step: int,
    context: Any,
) -> None:
    """Tests daysout method of IsoWeekDate class"""
    obj = isoweekdate_constructor(value)
    with context:
        r = obj.daysout(n_days, step=step)
        assert isinstance(r, Generator)
