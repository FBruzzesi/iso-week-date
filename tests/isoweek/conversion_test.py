from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING
from typing import Any
from typing import Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("weekday", "context"),
    [
        (1, do_not_raise()),
        (1.0, pytest.raises(TypeError, match="`weekday` must be an integer")),
        (-1, pytest.raises(ValueError, match="Weekday must be between 1 and 7")),
        (8, pytest.raises(ValueError, match="Weekday must be between 1 and 7")),
    ],
)
def test_to_datetime_raise(isoweek_constructor: type[IsoWeek], weekday: int, context: Any) -> None:
    """Tests to_datetime method of IsoWeek class"""
    obj = isoweek_constructor(value)
    with context:
        obj.to_datetime(weekday)
