from contextlib import nullcontext as do_not_raise

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError

from iso_week_date.pydantic import T_ISOWeek, T_ISOWeekDate


@pytest.mark.parametrize(
    "cls,value,context",
    [
        (T_ISOWeek, "2024-W01", do_not_raise()),
        (T_ISOWeek, "2024-W01-1", pytest.raises(ValidationError)),
        (T_ISOWeek, "2024-W53", pytest.raises(ValidationError)),
        (T_ISOWeek, "abc", pytest.raises(ValidationError)),
        (T_ISOWeekDate, "2024-W01-1", do_not_raise()),
        (T_ISOWeekDate, "2024-W01", pytest.raises(ValidationError)),
        (T_ISOWeekDate, "2024-W53", pytest.raises(ValidationError)),
        (T_ISOWeekDate, "abc", pytest.raises(ValidationError)),
    ],
)
def test_pydantic(cls, value, context):
    """Tests pydantic compatible types."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: cls

    with context:
        TestModel(value=value)
