from __future__ import annotations

import json
import re
from typing import Any

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
        # A `$`-anchored pattern matches just before a trailing newline, so these must be rejected
        # explicitly. See `iso_week_date._utils.match_isoweek`.
        (T_ISOWeek, "2024-W01\n", "Invalid iso week pattern"),
        (T_ISOWeek, "2024-W01 ", "Invalid iso week pattern"),
        (T_ISOWeekDate, "2024-W01-1\n", "Invalid iso week date pattern"),
    ],
)
def test_pydantic_invalid(klass: type, value: str, err_msg: str) -> None:
    """Tests pydantic compatible types."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    with pytest.raises(ValidationError, match=err_msg):
        TestModel(value=value)


@pytest.mark.parametrize("klass", [T_ISOWeek, T_ISOWeekDate])
@pytest.mark.parametrize("value", [None, 1, 2.5, ["2024-W01"], {"a": 1}, object()])
def test_pydantic_non_str_raises_validation_error(klass: type, value: Any) -> None:
    """Non-`str` input must surface as pydantic's `ValidationError`, never a bare `TypeError`.

    The validator runs after `str_schema()` so that pydantic rejects the wrong type first. As a
    "before" validator it received the raw object and `re` raised `TypeError`, escaping the
    `ValidationError` contract every caller wraps model construction in.
    """

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        TestModel(value=value)


@pytest.mark.parametrize(("klass", "value"), [(T_ISOWeek, b"2024-W01"), (T_ISOWeekDate, b"2024-W01-1")])
def test_pydantic_coerces_bytes_like_a_plain_str_field(klass: type, value: bytes) -> None:
    """`bytes` input is coerced, because `str_schema()` coerces it in pydantic's lax mode.

    This is deliberate rather than incidental: these types are `str` subclasses, so they follow
    whatever a plain `str` field does and then add the pattern check on top.
    """

    class PlainModel(BaseModel):
        """Reference model using a plain `str` field."""

        value: str

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    assert TestModel(value=value).value == PlainModel(value=value).value  # type: ignore[arg-type]


@pytest.mark.parametrize(("klass", "value"), [(T_ISOWeek, "2024-W01"), (T_ISOWeekDate, "2024-W01-1")])
def test_pydantic_validate_json(klass: type, value: str) -> None:
    """JSON validation goes through the same schema and must behave identically."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    assert TestModel.model_validate_json(json.dumps({"value": value})).value == value

    with pytest.raises(ValidationError, match="Input should be a valid string"):
        TestModel.model_validate_json(json.dumps({"value": None}))


@pytest.mark.parametrize(("klass", "value"), [(T_ISOWeek, "2024-W01"), (T_ISOWeekDate, "2024-W01-1")])
def test_pydantic_json_schema_is_a_string(klass: type, value: str) -> None:
    """The generated JSON schema must still describe a string."""

    class TestModel(BaseModel):
        """Pydantic model for testing."""

        value: klass  # type: ignore[valid-type]

    assert TestModel.model_json_schema()["properties"]["value"]["type"] == "string"
    assert isinstance(TestModel(value=value).value, klass)
