from __future__ import annotations

from collections.abc import Generator
from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("n_weeks", "step", "context"),
    [
        (1, 1, do_not_raise()),
        (1, 2, do_not_raise()),
        (10, 1, do_not_raise()),
        (1.0, 1, pytest.raises(TypeError, match="`n_weeks` must be an integer")),
        (0, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
        (-2, 1, pytest.raises(ValueError, match="`n_weeks` must be strictly positive")),
    ],
)
def test_weeksout(isoweek_constructor: type[IsoWeek], n_weeks: float, step: int, context: Any) -> None:
    """Tests weeksout method of IsoWeek class"""
    obj = isoweek_constructor(value)
    with context:
        r = obj.weeksout(n_weeks, step=step)  # type: ignore[call-overload]
        assert isinstance(r, Generator)
