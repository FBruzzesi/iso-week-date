from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Final

import pytest

if TYPE_CHECKING:
    from iso_week_date import IsoWeek

value: Final[str] = "2023-W01"


@pytest.mark.parametrize(
    ("weekday", "expected_exception", "err_msg"),
    [
        (1, None, None),
        (1.0, TypeError, "`weekday` must be an integer"),
        (-1, ValueError, "Weekday must be between 1 and 7"),
        (8, ValueError, "Weekday must be between 1 and 7"),
        # `int` lookalikes must be rejected up front rather than interpolated into the value and
        # failing later as an opaque strptime error. `bool` is the sharp edge: `isinstance(True, int)`
        # holds and `True in range(1, 8)` holds, so it used to reach strptime as the string "True".
        (True, TypeError, "`weekday` must be an integer"),
        (False, TypeError, "`weekday` must be an integer"),
        ("1", TypeError, "`weekday` must be an integer"),
        (Decimal(1), TypeError, "`weekday` must be an integer"),
    ],
)
def test_to_datetime_raise(
    isoweek_constructor: type[IsoWeek],
    weekday: Any,
    expected_exception: type[Exception] | None,
    err_msg: str | None,
) -> None:
    """Tests to_datetime method of IsoWeek class"""
    obj = isoweek_constructor(value)
    context = pytest.raises(expected_exception, match=err_msg) if expected_exception else do_not_raise()
    with context:
        obj.to_datetime(weekday)
