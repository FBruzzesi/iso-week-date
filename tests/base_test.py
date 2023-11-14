from contextlib import nullcontext as do_not_raise

import pytest

from iso_week_date import IsoWeek, IsoWeekDate


@pytest.mark.parametrize(
    "_cls, value, context",
    [
        (IsoWeek, "2023-W01", do_not_raise()),
        (IsoWeek, "2000-W01", do_not_raise()),
        (IsoWeek, "abcd-xyz", pytest.raises(ValueError)),
        (IsoWeek, "0000-W01", pytest.raises(ValueError)),
        (IsoWeek, "2023-W00", pytest.raises(ValueError)),
        (IsoWeek, "2023-W53", pytest.raises(ValueError)),
        (IsoWeek, "2023-W54", pytest.raises(ValueError)),
        (IsoWeekDate, "2023-W01-1", do_not_raise()),
        (IsoWeekDate, "2000-W01-1", do_not_raise()),
        (IsoWeekDate, "abcd-xyz-1", pytest.raises(ValueError)),
        (IsoWeekDate, "0000-W01-1", pytest.raises(ValueError)),
        (IsoWeekDate, "2023-W00-1", pytest.raises(ValueError)),
        (IsoWeekDate, "2023-W54-1", pytest.raises(ValueError)),
        (IsoWeekDate, "2023-W01-0", pytest.raises(ValueError)),
        (IsoWeekDate, "2023-W01-8", pytest.raises(ValueError)),
    ],
)
def test_validate(_cls, value, context):
    """Test validate method"""
    with context as exc_info:
        _cls._validate(value)

    if exc_info:
        assert ("Invalid isoweek date format" in str(exc_info.value)) or ("Invalid week number" in str(exc_info.value))


@pytest.mark.parametrize(
    "value, expected",
    [
        (IsoWeek("2023-W01"), IsoWeek("2023-W02")),
        (IsoWeekDate("2023-W01-1"), IsoWeekDate("2023-W01-2")),
    ],
)
def test_next(value, expected):
    """Test __next__ method"""
    assert next(value) == expected


@pytest.mark.parametrize("start", ("2023-W01",))
@pytest.mark.parametrize("n_weeks_out", (52,))
@pytest.mark.parametrize("step", (1, 2, 3))
@pytest.mark.parametrize("inclusive", ("both", "left", "right", "neither"))
@pytest.mark.parametrize("as_str", (True, False))
def test_range_valid(start, n_weeks_out, step, inclusive, as_str):
    """Tests range method of IsoWeek class"""

    _start = IsoWeek(start)
    _end = _start + n_weeks_out

    lenoffset_ = 0 if inclusive == "both" else 1 if inclusive in ("left", "right") else 2

    _len = (n_weeks_out - lenoffset_) // step + 1
    _range = tuple(IsoWeek.range(_start, _end, step, inclusive, as_str))

    assert all(isinstance(w, str if as_str else IsoWeek) for w in _range)
    assert len(_range) == _len


@pytest.mark.parametrize(
    "kwargs, context, err_msg",
    [
        (
            {"start": "2023-W03"},
            pytest.raises(ValueError),
            "`start` must be before `end` value",
        ),
        (
            {"end": "2022-W52"},
            pytest.raises(ValueError),
            "`start` must be before `end` value",
        ),
        ({"step": 1.0}, pytest.raises(TypeError), "`step` must be integer"),
        (
            {"step": 0},
            pytest.raises(ValueError),
            "`step` value must be greater than or equal to 1",
        ),
        (
            {"inclusive": "invalid"},
            pytest.raises(ValueError),
            "Invalid `inclusive` value. Must be one of",
        ),
    ],
)
def test_range_invalid(kwargs, context, err_msg):
    """Tests range method of IsoWeek class with invalid arguments"""
    DEFAULT_KWARGS = {
        "start": "2023-W01",
        "end": "2023-W02",
        "step": 1,
        "inclusive": "both",
    }

    kwargs = {**DEFAULT_KWARGS, **kwargs}

    with context as exc_info:
        IsoWeek.range(**kwargs)

    if exc_info:
        assert err_msg in str(exc_info.value)
