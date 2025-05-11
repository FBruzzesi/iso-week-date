from __future__ import annotations

from contextlib import AbstractContextManager
from contextlib import nullcontext as do_not_raise
from datetime import date
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TYPE_CHECKING
from typing import Any
from typing import Literal

import pytest

from iso_week_date import IsoWeek
from iso_week_date import IsoWeekDate
from iso_week_date._base import BaseIsoWeek

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import TypeVar

    T = TypeVar("T", IsoWeek, IsoWeekDate)


class CustomIsoWeek(IsoWeek):
    """Custom IsoWeek class with offset of 1 day"""

    offset_ = timedelta(days=1)


class CustomIsoWeekDate(IsoWeekDate):
    """Custom IsoWeekDate class with offset of 1 day"""

    offset_ = timedelta(days=1)


exception_context = pytest.raises(ValueError, match=r"(Invalid isoweek date format|Invalid week number)")

isoweek = IsoWeek("2023-W01")
customisoweek = CustomIsoWeek("2023-W01")
isoweekdate = IsoWeekDate("2023-W01-1")
customisoweekdate = CustomIsoWeekDate("2023-W01-1")


def test_abstract_class():
    with pytest.raises(TypeError, match="Can't instantiate abstract class BaseIsoWeek"):
        BaseIsoWeek()


def test_subclass_missing_cls_attributes():
    with pytest.raises(ValueError, match=r"The following class attributes are missing: \['_format', '_date_format'\]"):

        class TestSubclass(BaseIsoWeek):
            _pattern = "foo"


@pytest.mark.parametrize(
    ("klass", "value", "context"),
    [
        (IsoWeek, "2023-W01", do_not_raise()),
        (IsoWeek, "2000-W01", do_not_raise()),
        (IsoWeek, "abcd-xyz", exception_context),
        (IsoWeek, "0000-W01", exception_context),
        (IsoWeek, "2023-W00", exception_context),
        (IsoWeek, "2023-W53", exception_context),
        (IsoWeek, "2023-W54", exception_context),
        (IsoWeekDate, "2023-W01-1", do_not_raise()),
        (IsoWeekDate, "2000-W01-1", do_not_raise()),
        (IsoWeekDate, "abcd-xyz-1", exception_context),
        (IsoWeekDate, "0000-W01-1", exception_context),
        (IsoWeekDate, "2023-W00-1", exception_context),
        (IsoWeekDate, "2023-W54-1", exception_context),
        (IsoWeekDate, "2023-W01-0", exception_context),
        (IsoWeekDate, "2023-W01-8", exception_context),
    ],
)
def test_validate(klass: type[T], value: str, context: AbstractContextManager) -> None:
    """Test validate method"""
    with context:
        klass(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (IsoWeek("2023-W01"), IsoWeek("2023-W02")),
        (IsoWeekDate("2023-W01-1"), IsoWeekDate("2023-W01-2")),
    ],
)
def test_next(value: T, expected: T) -> None:
    """Test __next__ method"""
    assert next(value) == expected


def test_str_repr() -> None:
    assert isoweek.__repr__() == f"IsoWeek({isoweek.value_}) with offset {isoweek.offset_}"
    assert str(isoweek) == isoweek.value_

    assert isoweekdate.__repr__() == f"IsoWeekDate({isoweekdate.value_}) with offset {isoweekdate.offset_}"
    assert str(isoweekdate) == isoweekdate.value_


@pytest.mark.parametrize("start", ("2023-W01",))
@pytest.mark.parametrize("n_weeks_out", (52,))
@pytest.mark.parametrize("step", (1, 2, 3))
@pytest.mark.parametrize("inclusive", ("both", "left", "right", "neither"))
@pytest.mark.parametrize("as_str", (True, False))
def test_range_valid(
    start: str,
    n_weeks_out: int,
    step: int,
    inclusive: Literal["both", "left", "right", "neither"],
    as_str: bool,
) -> None:
    """Tests range method of IsoWeek class"""
    _start = IsoWeek(start)
    _end = _start + n_weeks_out

    lenoffset_ = 0 if inclusive == "both" else 1 if inclusive in {"left", "right"} else 2

    _len = (n_weeks_out - lenoffset_) // step + 1
    _range = tuple(IsoWeek.range(_start, _end, step=step, inclusive=inclusive, as_str=as_str))

    assert all(isinstance(w, str if as_str else IsoWeek) for w in _range)
    assert len(_range) == _len


def test_quarters() -> None:
    """Tests quarter property of IsoWeek class"""
    min_quarter, max_quarter = 1, 4
    assert all(
        min_quarter <= w.quarter <= max_quarter for w in IsoWeek.range("2020-W01", "2025-W52", step=1, as_str=False)
    )

    assert all(
        min_quarter <= w.quarter <= max_quarter
        for w in IsoWeekDate.range("2020-W01-1", "2025-W52-7", step=1, as_str=False)
    )


@pytest.mark.parametrize(
    ("kwargs", "context"),
    [
        ({"start": "2023-W03"}, pytest.raises(ValueError, match="`start` must be before `end` value")),
        ({"end": "2022-W52"}, pytest.raises(ValueError, match="`start` must be before `end` value")),
        ({"step": 1.0}, pytest.raises(TypeError, match="`step` must be integer")),
        ({"step": 0}, pytest.raises(ValueError, match="`step` value must be greater than or equal to 1")),
        ({"inclusive": "invalid"}, pytest.raises(ValueError, match="Invalid `inclusive` value. Must be one of")),
    ],
)
def test_range_invalid(kwargs: dict[str, Any], context: AbstractContextManager) -> None:
    """Tests range method of IsoWeek class with invalid arguments"""
    default_kwargs = {
        "start": "2023-W01",
        "end": "2023-W02",
        "step": 1,
        "inclusive": "both",
    }

    kwargs = {**default_kwargs, **kwargs}

    with context:
        IsoWeek.range(**kwargs)


@pytest.mark.parametrize(
    ("klass", "cls_method", "args", "expected"),
    [
        (IsoWeek, "from_string", ("2023-W01",), isoweek),
        (IsoWeek, "from_compact", ("2023W01",), isoweek),
        (IsoWeek, "from_date", (date(2023, 1, 2),), isoweek),
        (IsoWeek, "from_datetime", (datetime(2023, 1, 2, 12, tzinfo=timezone.utc),), isoweek),
        (IsoWeekDate, "from_string", ("2023-W01-1",), isoweekdate),
        (IsoWeekDate, "from_compact", ("2023W011",), isoweekdate),
        (IsoWeekDate, "from_date", (date(2023, 1, 2),), isoweekdate),
        (IsoWeekDate, "from_datetime", (datetime(2023, 1, 2, 12, tzinfo=timezone.utc),), isoweekdate),
        (IsoWeek, "from_values", (2023, 1), isoweek),
        (IsoWeekDate, "from_values", (2023, 1, 1), isoweekdate),
    ],
)
def test_valid_parser(klass: type[T], cls_method: str, args: tuple, expected: T) -> None:
    """Test ParserMixin methods with valid values"""
    assert getattr(klass, cls_method)(*args) == expected
    if cls_method not in {"from_compact", "from_values"}:
        assert klass._cast(*args) == expected


@pytest.mark.parametrize(
    ("klass", "cls_method", "value", "context"),
    [
        (IsoWeekDate, "from_string", 1234, pytest.raises(TypeError, match="Expected `str` type, found")),
        (IsoWeekDate, "from_compact", date(2023, 1, 2), pytest.raises(TypeError, match="Expected `str` type, found")),
        (IsoWeekDate, "from_compact", "2023W0112", pytest.raises(ValueError, match="Invalid isoweek date format")),
        (IsoWeekDate, "from_date", (1, 2, 3, 4), pytest.raises(TypeError, match="Expected `date` type, found")),
        (IsoWeekDate, "from_datetime", "2023-W01", pytest.raises(TypeError, match="Expected `datetime` type, found")),
        (IsoWeek, "_cast", 1234, pytest.raises(NotImplementedError, match="Cannot cast type")),
        (IsoWeek, "_cast", (1, 2, 3, 4), pytest.raises(NotImplementedError, match="Cannot cast type")),
    ],
)
def test_invalid_parser(klass: type[T], cls_method: str, value: Any, context: AbstractContextManager) -> None:
    """Test ParserMixin methods with invalid value types"""
    with context:
        getattr(klass, cls_method)(value)


@pytest.mark.parametrize("iso_obj", [isoweek, isoweekdate])
def test_converter(iso_obj: T) -> None:
    """Tests to_* methods"""
    min_matches = 2
    assert iso_obj.to_string() == iso_obj.value_
    assert iso_obj.to_compact() == iso_obj.value_.replace("-", "")

    _values = iso_obj.to_values()
    assert len(_values) >= min_matches
    assert all(isinstance(v, int) for v in _values)

    assert isinstance(iso_obj.to_date(), date)
    assert isinstance(iso_obj.to_datetime(), datetime)


@pytest.mark.parametrize(
    ("value", "other", "comparison_op", "expected"),
    [
        (isoweek, "2023-W01", "__eq__", True),
        (isoweek, "2023-W02", "__ne__", True),
        (isoweek, "2023-W01", "__le__", True),
        (isoweek, "2023-W02", "__le__", True),
        (isoweek, "2023-W01", "__ge__", True),
        (isoweek, "2022-W52", "__ge__", True),
        (isoweek, "2023-W02", "__lt__", True),
        (isoweek, "2022-W52", "__gt__", True),
        (isoweekdate, "2023-W02-1", "__eq__", False),
        (isoweekdate, "2023-W01-1", "__ne__", False),
        (isoweekdate, "2022-W52-1", "__le__", False),
        (isoweekdate, "2023-W02-1", "__ge__", False),
        (isoweekdate, "2023-W01-1", "__lt__", False),
        (isoweekdate, "2022-W52-1", "__lt__", False),
        (isoweekdate, "2023-W01-1", "__gt__", False),
        (isoweekdate, "2023-W02-1", "__gt__", False),
    ],
)
def test_comparisons(value: T, other: str | T, comparison_op: str, expected: bool) -> None:
    """Tests comparison methods of ISO Week classes"""
    _other = value.__class__._cast(other)
    assert getattr(value, comparison_op)(_other) == expected


@pytest.mark.parametrize(
    "other",
    ["2023-W01", datetime(2023, 1, 1, tzinfo=timezone.utc), date(2023, 1, 1), 123, 42.0, customisoweek],
)
def test_eq_other_types(other: Any) -> None:
    """Tests __eq__ method of IsoWeek class with other types"""
    assert isoweek != other


@pytest.mark.parametrize(
    ("other", "comparison_op"),
    [
        ("2023-W01", "__lt__"),
        ("abc", "__gt__"),
        (123, "__ge__"),
        (list("abc"), "__le__"),
    ],
)
def test_comparisons_invalid_type(other: Any, comparison_op: str) -> None:
    """Tests comparison methods of IsoWeek class with invalid types"""
    err_msg = "Cannot compare `IsoWeek` with type"
    with pytest.raises(TypeError) as exc_info:
        getattr(isoweek, comparison_op)(other)

    assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    "comparison_op",
    [
        "__lt__",
        "__gt__",
        "__ge__",
        "__le__",
    ],
)
def test_comparisons_invalid_offset(comparison_op: str) -> None:
    """Tests comparison methods of IsoWeek class with invalid arguments"""
    err_msg = "Cannot compare `IsoWeek`'s with different offsets"
    with pytest.raises(TypeError) as exc_info:
        getattr(isoweek, comparison_op)(customisoweek)

    assert err_msg in str(exc_info.value)


@pytest.mark.parametrize(
    ("obj", "fmt"),
    [
        (isoweek, "YYYYWNN"),
        (customisoweek, "YYYYWNN"),
        (isoweekdate, "YYYYWNND"),
        (customisoweekdate, "YYYYWNND"),
    ],
)
def test_compact_format(obj: BaseIsoWeek, fmt: str):
    assert obj._compact_format == fmt


def test_from_today():
    assert IsoWeek.from_today() == IsoWeek.from_date(datetime.now().date())
    assert IsoWeekDate.from_today() == IsoWeekDate.from_date(datetime.now().date())


def test_is_before() -> None:
    """Tests is_before method of IsoWeek class"""
    assert isoweek.is_before(isoweek + 1)
    assert not isoweekdate.is_before(isoweekdate - 1)

    assert customisoweekdate.is_before(customisoweekdate + 1)
    assert not customisoweek.is_before(customisoweek - 1)


def test_is_after() -> None:
    """Tests is_after method of IsoWeek class"""
    assert not isoweekdate.is_after(isoweekdate + 1)
    assert isoweek.is_after(isoweek - 1)

    assert not customisoweek.is_after(customisoweek + 1)
    assert customisoweekdate.is_after(customisoweekdate - 1)
