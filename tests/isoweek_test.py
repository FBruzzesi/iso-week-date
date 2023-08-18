from contextlib import nullcontext as do_not_raise
from datetime import date, datetime, timedelta
from typing import Generator, Iterable

import pytest

from iso_week import IsoWeek

isoweek = IsoWeek("2023-W01")


class CustomWeek(IsoWeek):
    """Custom IsoWeek class with offset of 1 day"""

    _offset = timedelta(days=1)


customweek = CustomWeek("2023-W01")


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        ("2023-W01", do_not_raise(), ""),
        ("abcd-xyz", pytest.raises(ValueError), "Invalid isoweek format"),
        ("0000-W01", pytest.raises(ValueError), "Invalid year number"),
        ("2023-W54", pytest.raises(ValueError), "Invalid week number"),
    ],
)
def test_init(capsys, value, context, err_msg):
    """Tests __init__ and _validate methods of IsoWeek class"""

    with context:
        IsoWeek(value, _validate=True)

        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


def test_properties():
    """Tests properties of IsoWeek class, namely year, week and days"""

    assert isoweek.year == 2023
    assert isoweek.week == 1
    days = isoweek.days
    assert len(days) == 7
    assert all([isinstance(day, date) for day in days])


@pytest.mark.parametrize(
    "n, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "n must be an integer"),
        (-1, pytest.raises(ValueError), "n must be between 1 and 7"),
        (8, pytest.raises(ValueError), "n must be between 1 and 7"),
    ],
)
def test_nth(capsys, n, context, err_msg):
    """Tests nth method of IsoWeek class"""
    with context:
        isoweek.nth(n)

        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


def test_str_repr():
    """Tests __repr__ and __str__ methods of IsoWeek class"""
    assert isoweek.__repr__() == f"IsoWeek({isoweek.value}) with offset {isoweek._offset}"
    assert str(isoweek) == isoweek.value


@pytest.mark.parametrize(
    "other, comparison_op",
    [
        ("2023-W01", "__eq__"),
        ("2023-W01", "__le__"),
        ("2023-W01", "__ge__"),
        ("2023-W02", "__ne__"),
        ("2023-W02", "__lt__"),
        ("2023-W02", "__le__"),
        ("2022-W52", "__ne__"),
        ("2022-W52", "__gt__"),
        ("2022-W52", "__ge__"),
    ],
)
def test_comparisons_true(other, comparison_op):
    """Tests comparison methods of IsoWeek class"""
    _other = IsoWeek(other)
    assert getattr(isoweek, comparison_op)(_other)


@pytest.mark.parametrize(
    "other, comparison_op",
    [
        ("2023-W01", "__ne__"),
        ("2023-W01", "__lt__"),
        ("2023-W01", "__gt__"),
        ("2023-W02", "__eq__"),
        ("2023-W02", "__gt__"),
        ("2023-W02", "__ge__"),
        ("2022-W52", "__eq__"),
        ("2022-W52", "__lt__"),
        ("2022-W52", "__le__"),
    ],
)
def test_comparisons_false(other, comparison_op):
    """Tests comparison methods of IsoWeek class"""
    _other = IsoWeek(other)
    assert not getattr(isoweek, comparison_op)(_other)


@pytest.mark.parametrize(
    "other", ["2023-W01", datetime(2023, 1, 1), date(2023, 1, 1), 123, 42.0, customweek]
)
def test_eq_other_types(other):
    """Tests __eq__ method of IsoWeek class with other types"""
    assert not isoweek == other


@pytest.mark.parametrize(
    "comparison_op",
    ("__lt__", "__le__", "__gt__", "__ge__"),
)
def test_different_offsets(capsys, comparison_op):
    """Tests comparison operators with different offsets"""
    with pytest.raises(TypeError):
        getattr(isoweek, comparison_op)(customweek)

        sys_out, _ = capsys.readouterr()
        assert "Cannot compare IsoWeek's with different offsets" in sys_out


def test_to_methods():
    """
    Tests conversion "to" methods of IsoWeek class: to_str, to_compact, to_date,
    to_datetime
    """

    assert isoweek.to_str() == isoweek.value
    assert isoweek.to_compact() == isoweek.value.replace("-", "")

    assert isinstance(isoweek.to_date(), date)
    assert isinstance(isoweek.to_datetime(), datetime)


@pytest.mark.parametrize(
    "weekday, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "weekday must be an integer"),
        (-1, pytest.raises(ValueError), "weekday must be between 1 and 7"),
        (8, pytest.raises(ValueError), "weekday must be between 1 and 7"),
    ],
)
def test_to_datetime_raise(capsys, weekday, context, err_msg):
    """Tests to_datetime method of IsoWeek class"""
    with context:
        isoweek.to_datetime(weekday)

        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize(
    "value, method",
    [
        ("2023-W01", "from_str"),
        ("2023W01", "from_compact"),
        (date(2023, 1, 4), "from_date"),
        (datetime(2023, 1, 4), "from_datetime"),
    ],
)
def test_from_methods(value, method):
    """
    Test conversion "from" methods of IsoWeek class:
    from_str, from_compact, from_date, from_datetime
    """
    assert getattr(IsoWeek, method)(value) == isoweek


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (timedelta(weeks=2), do_not_raise(), ""),
        (1.0, pytest.raises(TypeError), "Cannot add type"),
        ("1", pytest.raises(TypeError), "Cannot add type"),
    ],
)
def test_addition(capsys, value, context, err_msg):
    """Tests addition operator of IsoWeek class"""
    with context:
        isoweek + value
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (1, do_not_raise(), ""),
        (-1, do_not_raise(), ""),
        (timedelta(weeks=2), do_not_raise(), ""),
        (IsoWeek("2023-W01"), do_not_raise(), ""),
        (IsoWeek("2023-W02"), do_not_raise(), ""),
        (IsoWeek("2022-W52"), do_not_raise(), ""),
        (customweek, pytest.raises(TypeError), "Cannot add type"),
        ("1", pytest.raises(TypeError), "Cannot add type"),
    ],
)
def test_subtraction(capsys, value, context, err_msg):
    """Tests subtraction operator of IsoWeek class"""
    with context:
        isoweek - value
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize(
    "value, return_type",
    [
        (1, IsoWeek),
        (IsoWeek("2023-W01"), int),
    ],
)
def test_subtraction_return_type(value, return_type):
    """Tests subtraction operator of IsoWeek class"""
    assert isinstance(isoweek - value, return_type)


@pytest.mark.parametrize(
    "value, context, err_msg",
    [
        (customweek, do_not_raise(), ""),
        ("2023-W01", do_not_raise(), ""),
        (date(2023, 1, 1), do_not_raise(), ""),
        (datetime(2023, 1, 1), do_not_raise(), ""),
        (1, pytest.raises(NotImplementedError), "Cannot cast type"),
    ],
)
def test_automatic_cast(capsys, value, context, err_msg):
    """Tests automatic casting of IsoWeek class"""

    with context:
        r = IsoWeek._automatic_cast(value)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out
        assert isinstance(r, IsoWeek)


@pytest.mark.parametrize("start", (IsoWeek("2023-W01"),))
@pytest.mark.parametrize("n_weeks_out", (52,))
@pytest.mark.parametrize("step", (1, 2, 3))
@pytest.mark.parametrize("inclusive", ("both", "left", "right", "neither"))
@pytest.mark.parametrize("as_str", (True, False))
def test_range_valid(start, n_weeks_out, step, inclusive, as_str):
    """Tests range method of IsoWeek class"""

    _start = IsoWeek._automatic_cast(start)
    _end = start + n_weeks_out

    len_offset = 0 if inclusive == "both" else 1 if inclusive in ("left", "right") else 2

    _len = (n_weeks_out - len_offset) // step + 1
    _range = tuple(IsoWeek.range(_start, _end, step, inclusive, as_str))

    assert all(isinstance(w, str if as_str else IsoWeek) for w in _range)
    assert len(_range) == _len


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"start": IsoWeek("2023-W03")},
            pytest.raises(ValueError),
            "start must be before end value",
        ),
        (
            {"end": IsoWeek("2022-W52")},
            pytest.raises(ValueError),
            "start must be before end value",
        ),
        ({"step": 1.0}, pytest.raises(TypeError), "step must be an integer"),
        (
            {"step": 0},
            pytest.raises(ValueError),
            "step value must be greater than or equal to 1",
        ),
        ({"inclusive": "invalid"}, pytest.raises(ValueError), "inclusive must be one of"),
    ],
)
def test_range_invalid(capsys, kwargs, context, err_msg):
    """Tests range method of IsoWeek class with invalid arguments"""
    DEFAULT_KWARGS = {
        "start": "2023-W01",
        "end": "2023-W02",
        "step": 1,
        "inclusive": "both",
    }

    kwargs = {**DEFAULT_KWARGS, **kwargs}

    with context:
        IsoWeek.range(**kwargs)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out


@pytest.mark.parametrize(
    "n_weeks, step, context, err_msg",
    [
        (1, 1, do_not_raise(), ""),
        (1, 2, do_not_raise(), ""),
        (10, 1, do_not_raise(), ""),
        (1.0, 1, pytest.raises(TypeError), "n_weeks must be an integer"),
        (0, 1, pytest.raises(ValueError), "n_weeks must be strictly positive"),
        (-2, 1, pytest.raises(ValueError), "n_weeks must be strictly positive"),
    ],
)
def test_weeksout(capsys, n_weeks, step, context, err_msg):
    """Tests weeksout method of IsoWeek class"""

    with context:
        r = isoweek.weeksout(n_weeks, step)
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out
        assert isinstance(r, Generator)


@pytest.mark.parametrize(
    "other, expected, context, err_msg",
    [
        (IsoWeek("2023-W01"), True, do_not_raise(), ""),
        (IsoWeek("2023-W02"), False, do_not_raise(), ""),
        ("2023-W01", True, do_not_raise(), ""),
        ("2023-W02", False, do_not_raise(), ""),
        (date(2023, 1, 4), True, do_not_raise(), ""),
        (date(2023, 1, 1), False, do_not_raise(), ""),
        (datetime(2023, 1, 4), True, do_not_raise(), ""),
        (datetime(2023, 1, 1), False, do_not_raise(), ""),
        (tuple(), None, pytest.raises(TypeError), "Cannot compare type"),
        (123, None, pytest.raises(TypeError), "Cannot compare type"),
    ],
)
def test__contains__(capsys, other, expected, context, err_msg):
    """Tests __contains__ method of IsoWeek class"""

    with context:
        r = other in isoweek
        sys_out, _ = capsys.readouterr()
        assert err_msg in sys_out
        assert r == expected


@pytest.mark.parametrize(
    "other, expected, context, err_msg",
    [
        (isoweek.days, tuple(True for _ in isoweek.days), do_not_raise(), ""),
        (isoweek.days[0], True, do_not_raise(), ""),
        (isoweek.days[1] + timedelta(weeks=52), False, do_not_raise(), ""),
        ((1, 2, 3), None, pytest.raises(TypeError), "Cannot compare type"),
        (123, None, pytest.raises(TypeError), "Cannot compare type"),
    ],
)
def test_contains_method(capsys, other, expected, context, err_msg):
    """Tests contains method of IsoWeek class"""

    with context:
        r = isoweek.contains(other)

        if isinstance(other, (date, datetime, str, IsoWeek)):
            assert isinstance(r, bool)
            assert r == expected

        elif isinstance(other, Iterable):
            len(other) == len(r)
            assert all(isinstance(v, bool) for v in r)
            assert r == expected

        else:
            sys_out, _ = capsys.readouterr()
            assert err_msg in sys_out
