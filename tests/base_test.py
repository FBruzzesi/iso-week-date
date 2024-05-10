from contextlib import nullcontext as do_not_raise

import pytest

from iso_week_date import IsoWeek, IsoWeekDate

exception_context = pytest.raises(ValueError, match=r"(Invalid isoweek date format|Invalid week number)")


@pytest.mark.parametrize(
    "klass, value, context",
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
def test_validate(klass, value, context):
    """Test validate method"""
    with context:
        klass(value)


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
    _range = tuple(IsoWeek.range(_start, _end, step=step, inclusive=inclusive, as_str=as_str))

    assert all(isinstance(w, str if as_str else IsoWeek) for w in _range)
    assert len(_range) == _len


@pytest.mark.parametrize(
    "kwargs, context",
    [
        ({"start": "2023-W03"}, pytest.raises(ValueError, match="`start` must be before `end` value")),
        ({"end": "2022-W52"}, pytest.raises(ValueError, match="`start` must be before `end` value")),
        ({"step": 1.0}, pytest.raises(TypeError, match="`step` must be integer")),
        ({"step": 0}, pytest.raises(ValueError, match="`step` value must be greater than or equal to 1")),
        ({"inclusive": "invalid"}, pytest.raises(ValueError, match="Invalid `inclusive` value. Must be one of")),
    ],
)
def test_range_invalid(kwargs, context):
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
