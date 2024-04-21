from contextlib import nullcontext as do_not_raise

import pytest
from pydantic import BaseModel
from pydantic_core import ValidationError

from iso_week_date.pydantic import IsoWeek_T, IsoWeekDate_T


@pytest.mark.parametrize(
    "cls,value,context",
    [
        (IsoWeek_T, "2024-W01", do_not_raise()),
        (IsoWeek_T, "2024-W01-1", pytest.raises(ValidationError)),
        (IsoWeek_T, "2024-W53", pytest.raises(ValidationError)),
        (IsoWeek_T, "abc", pytest.raises(ValidationError)),
        (IsoWeekDate_T, "2024-W01-1", do_not_raise()),
        (IsoWeekDate_T, "2024-W01", pytest.raises(ValidationError)),
        (IsoWeekDate_T, "2024-W53", pytest.raises(ValidationError)),
        (IsoWeekDate_T, "abc", pytest.raises(ValidationError)),
    ],
)
def test_pydantic(cls, value, context):
    """Tests pydantic compatible types"""

    class TestModel(BaseModel):
        """Pydantic model for testing"""

        value: cls

    with context:
        TestModel(value=value)
