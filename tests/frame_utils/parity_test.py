"""Cross-backend parity tests.

`pandas_utils` and `polars_utils` expose deliberately parallel APIs, but they are implemented and
tested independently, so a semantic divergence between them is invisible to either module's own
test file. These tests assert the two backends agree on the same inputs.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any

import pytest

pytest.importorskip("pandas")
pytest.importorskip("polars")

import pandas as pd
import polars as pl
from polars.exceptions import InvalidOperationError

from iso_week_date import IsoWeek, pandas_utils, polars_utils
from iso_week_date._utils import LONG_YEAR_WEEKS, is_long_year, weeks_of_year

if TYPE_CHECKING:
    from collections.abc import Callable

pytestmark = [pytest.mark.pandas, pytest.mark.polars]


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["2023-W01", "2023-W02"], True),
        (["2023-W01"], True),
        (["abcd-Wxy", "2023-W02"], False),
        (["0000-W01"], False),
        (["2023-W00"], False),
        (["2023-W54"], False),
        # The cases that used to diverge: nulls (polars said True, pandas said False) and a trailing
        # newline (pandas said True, polars said False). Both now agree, and nulls are skipped.
        (["2023-W01", None], True),
        ([None], True),
        ([], True),
        (["nope", None], False),
        (["2023-W01\n"], False),
        (["2023-W01 "], False),
        ([" 2023-W01"], False),
    ],
)
def test_is_isoweek_series_parity(values: list[str | None], expected: bool) -> None:
    pandas_result = pandas_utils.is_isoweek_series(pd.Series(values, dtype="object"))
    polars_result = polars_utils.is_isoweek_series(pl.Series(values, dtype=pl.String))

    assert pandas_result == polars_result, f"backends disagree on {values!r}"
    assert pandas_result == expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["2023-W01-1", "2023-W02-7"], True),
        (["abcd-Wxy-1"], False),
        (["2023-W01-0"], False),
        (["2023-W01-8"], False),
        (["2023-W01-1", None], True),
        ([None], True),
        (["nope", None], False),
        (["2023-W01-1\n"], False),
    ],
)
def test_is_isoweekdate_series_parity(values: list[str | None], expected: bool) -> None:
    pandas_result = pandas_utils.is_isoweekdate_series(pd.Series(values, dtype="object"))
    polars_result = polars_utils.is_isoweekdate_series(pl.Series(values, dtype=pl.String))

    assert pandas_result == polars_result, f"backends disagree on {values!r}"
    assert pandas_result == expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        (["2023-W01", "2023-W02"], True),
        (["2023-W01", "nope"], False),
    ],
)
def test_is_isoweek_series_parity_for_dictionary_encoded_strings(values: list[str], expected: bool) -> None:
    """pandas `category` and polars `Categorical` / `Enum` hold plain strings, so both read content.

    This is the case where the backends disagreed outright: `str.contains` rejects these dtypes and
    the failure was swallowed, so polars answered `False` for every one of them.
    """
    assert pandas_utils.is_isoweek_series(pd.Series(values, dtype="category")) is expected
    assert polars_utils.is_isoweek_series(pl.Series(values, dtype=pl.Categorical)) is expected
    assert polars_utils.is_isoweek_series(pl.Series(values, dtype=pl.Enum(values))) is expected


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        # An all-null column is missing data in both, with no explicit string dtype spelled out.
        ([None, None], True),
        # Non-`str` values are malformed data in both. They failed in opposite directions: polars
        # swallowed a dtype error into `False` (right answer, wrong reason) while pandas turned
        # `str.fullmatch`'s `NaN` into a truthy `True`.
        ([["2023-W01"], ["2023-W02"]], False),
        ([{"a": 1}], False),
        ([1, 2, 3], False),
    ],
)
def test_is_isoweek_series_parity_beyond_string_columns(values: list[Any], expected: bool) -> None:
    """The backends agree on columns whose values are not plain strings."""
    pandas_result = pandas_utils.is_isoweek_series(pd.Series(values))
    polars_result = polars_utils.is_isoweek_series(pl.Series(values))

    assert pandas_result == polars_result, f"backends disagree on {values!r}"
    assert pandas_result is expected


def test_conversions_propagate_nulls_identically() -> None:
    """Both backends must place nulls in the same positions after a conversion."""
    dates = [date(2023, 1, 2), None, date(2023, 1, 9)]

    pandas_isoweek = pandas_utils.datetime_to_isoweek(pd.Series(dates, dtype="datetime64[ns]"))
    polars_isoweek = polars_utils.datetime_to_isoweek(pl.Series(dates))

    assert pandas_isoweek.isna().tolist() == [v is None for v in polars_isoweek.to_list()]
    assert pandas_isoweek.dropna().tolist() == [v for v in polars_isoweek.to_list() if v is not None]

    pandas_back = pandas_utils.isoweek_to_datetime(pd.Series(["2023-W01", None], dtype="object"))
    polars_back = polars_utils.isoweek_to_datetime(pl.Series(["2023-W01", None]))

    assert pandas_back.isna().tolist() == [v is None for v in polars_back.to_list()]


@pytest.mark.parametrize(
    "values",
    [
        ["2023-W01", "2023-W02"],
        ["2023-W01\n"],
        ["2023-W01 "],
        [" 2023-W01"],
        ["nope"],
        ["0000-W01"],
        ["2023-W54"],
        ["2023-W00"],
        # Well-formed but not on the calendar: only long ISO years have a week 53.
        ["2023-W53"],
        ["2021-W53"],
        ["2022-W53"],
        ["2020-W53"],
        ["0001-W52"],
        ["9999-W52"],
        ["2020-W53", "2023-W53"],
    ],
)
def test_is_isoweek_series_agrees_with_the_scalar_class(values: list[str]) -> None:
    """Both backends must accept exactly the strings `IsoWeek` accepts, and nothing else.

    The scalar class is the reference rather than the shared pattern alone, so the two vectorised
    week-count implementations cannot drift from `weeks_of_year`, and the pandas (Python `re`) and
    polars (Rust `regex`) engines cannot drift from `_validate` on which strings are well-formed.
    A check that disagreed here would be useless as a precondition: the conversions reject exactly
    what `IsoWeek` rejects.
    """
    expected = all(_is_valid_isoweek(value) for value in values)

    assert pandas_utils.is_isoweek_series(pd.Series(values, dtype="object")) is expected
    assert polars_utils.is_isoweek_series(pl.Series(values, dtype=pl.String)) is expected


def _is_valid_isoweek(value: str) -> bool:
    """Whether the scalar class accepts `value`."""
    try:
        IsoWeek(value)
    except ValueError:
        return False
    return True


@pytest.mark.parametrize(
    "vectorised",
    [
        pytest.param(lambda years: is_long_year(pd.Series(years)).tolist(), id="pandas-series"),
        pytest.param(lambda years: is_long_year(pl.Series(years, dtype=pl.Int32)).to_list(), id="polars-series"),
        pytest.param(
            lambda years: (
                pl.DataFrame({"year": pl.Series(years, dtype=pl.Int32)})
                .select(long=is_long_year(pl.col("year")))["long"]
                .to_list()
            ),
            id="polars-expr",
        ),
    ],
)
def test_is_long_year_vectorises_without_drifting_from_the_scalar(
    vectorised: Callable[[list[int]], list[bool]],
) -> None:
    """One implementation serves the scalar class and both backends, so it must vectorise faithfully.

    `is_long_year` is written with `|` instead of `or` precisely so the dataframe modules can reuse it
    rather than keeping their own copy. What could still go wrong is the vectorising: integer width,
    floor-division or modulo semantics differing from Python's. All 9999 representable years are
    compared rather than sampled, since the disagreements would be sparse and year-specific.
    """
    years = list(range(1, 10_000))
    expected = [weeks_of_year(year) == LONG_YEAR_WEEKS for year in years]

    assert vectorised(years) == expected


@pytest.mark.parametrize("value", ["2023-W53", "2021-W53", "2022-W53"])
def test_is_isoweek_series_rejects_weeks_the_year_does_not_have(value: str) -> None:
    """The format is necessary but not sufficient, and the checks now enforce both halves.

    These values match the pattern (weeks 01-53 are syntactically valid) but name a week their year
    does not have. The checks used to answer `True` while `isoweek_to_datetime` raised on the very
    same input, so a caller who guarded the conversion with the check still crashed.
    """
    with pytest.raises(ValueError, match="Invalid week number"):
        IsoWeek(value)

    assert pandas_utils.is_isoweek_series(pd.Series([value], dtype="object")) is False
    assert polars_utils.is_isoweek_series(pl.Series([value], dtype=pl.String)) is False

    with pytest.raises(ValueError, match="does not exist in ISO year"):
        pandas_utils.isoweek_to_datetime(pd.Series([value], dtype="object"))
    with pytest.raises(InvalidOperationError, match="conversion from `str` to `date` failed"):
        polars_utils.isoweek_to_datetime(pl.Series([value], dtype=pl.String))


@pytest.mark.parametrize("value", ["2020-W53", "2015-W53", "2026-W53"])
def test_is_isoweek_series_accepts_week_53_of_a_long_year(value: str) -> None:
    """The calendar rule must not over-reject: a week 53 that exists is still valid."""
    assert IsoWeek(value).week == 53  # noqa: PLR2004

    assert pandas_utils.is_isoweek_series(pd.Series([value], dtype="object")) is True
    assert polars_utils.is_isoweek_series(pl.Series([value], dtype=pl.String)) is True
