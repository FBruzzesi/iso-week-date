from contextlib import nullcontext as do_not_raise

import pytest

from iso_week import IsoWeek


@pytest.mark.parametrize(
    "value, context",
    [
        ("2023-W01", do_not_raise()),
        ("2023-W55", pytest.raises(ValueError)),
    ],
)
def test_init(value, context):
    """Tests init method of IsoWeek class."""

    with context:
        IsoWeek(value)
