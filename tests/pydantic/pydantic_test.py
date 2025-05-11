from __future__ import annotations

from contextlib import nullcontext as do_not_raise
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError

from iso_week_date.pydantic import T_ISOWeek
from iso_week_date.pydantic import T_ISOWeekDate

if TYPE_CHECKING:
    from contextlib import AbstractContextManager


@pytest.mark.parametrize(
    ("klass", "value", "context"),
    [
        (T_ISOWeek, "2024-W01", do_not_raise()),
        (T_ISOWeek, "2024-W01-1", pytest.raises(ValidationError, match="Invalid iso week pattern")),
        (T_ISOWeek, "abc", pytest.raises(ValidationError, match="Invalid iso week pattern")),
        (
            T_ISOWeek,
            "2024-W53",
            pytest.raises(ValidationError, match="Invalid week number. Year 2024 has only 52 weeks."),
        ),
        (T_ISOWeekDate, "2024-W01-1", do_not_raise()),
        (T_ISOWeekDate, "2024-W01", pytest.raises(ValidationError, match="Invalid iso week date pattern")),
        (T_ISOWeekDate, "abc", pytest.raises(ValidationError, match="Invalid iso week date pattern")),
        (
            T_ISOWeekDate,
            "2024-W53-1",
            pytest.raises(ValidationError, match="Invalid week number. Year 2024 has only 52 weeks."),
        ),
    ],
)
def test_pydantic(klass: type, value: str, context: AbstractContextManager) -> None:
    """Tests pydantic compatible types."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    with context:
        TestModel(value=value)
