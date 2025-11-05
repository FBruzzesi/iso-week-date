from __future__ import annotations

import re

import pytest

pytest.importorskip("pydantic")

from pydantic import BaseModel
from pydantic_core import ValidationError

from iso_week_date.pydantic import T_ISOWeek, T_ISOWeekDate

pytestmark = pytest.mark.pydantic


@pytest.mark.parametrize(
    ("klass", "value"),
    [
        (T_ISOWeek, "2024-W01"),
        (T_ISOWeekDate, "2024-W01-1"),
    ],
)
def test_pydantic_valid(klass: type, value: str) -> None:
    """Tests pydantic compatible types."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    obj = TestModel(value=value)
    assert isinstance(obj, TestModel)
    assert obj.value == value


@pytest.mark.parametrize(
    ("klass", "value", "err_msg"),
    [
        (T_ISOWeek, "2024-W01-1", "Invalid iso week pattern"),
        (T_ISOWeek, "abc", "Invalid iso week pattern"),
        (
            T_ISOWeek,
            "2024-W53",
            re.escape("Invalid week number. Year 2024 has only 52 weeks."),
        ),
        (T_ISOWeekDate, "2024-W01", "Invalid iso week date pattern"),
        (T_ISOWeekDate, "abc", "Invalid iso week date pattern"),
        (
            T_ISOWeekDate,
            "2024-W53-1",
            re.escape("Invalid week number. Year 2024 has only 52 weeks."),
        ),
    ],
)
def test_pydantic_invalid(klass: type, value: str, err_msg: str) -> None:
    """Tests pydantic compatible types."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    with pytest.raises(ValidationError, match=err_msg):
        TestModel(value=value)
