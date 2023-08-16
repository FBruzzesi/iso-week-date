from contextlib import nullcontext as do_not_raise
from datetime import date, datetime, timedelta

import pytest

from iso_week import IsoWeek

isoweek = IsoWeek("2023-W01")


class CustomWeek(IsoWeek):
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
    Tests conversion "to" methods of IsoWeek class: to_str, to_compact, to_date, to_datetime
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
