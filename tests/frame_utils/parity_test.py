"""Cross-backend parity tests.

`pandas_utils` and `polars_utils` expose deliberately parallel APIs, but they are implemented and
tested independently, so a semantic divergence between them is invisible to either module's own
test file. These tests assert the two backends agree on the same inputs.
"""

from __future__ import annotations

from datetime import date
from typing import Any

import pytest

pytest.importorskip("pandas")
pytest.importorskip("polars")

import pandas as pd
import polars as pl

from iso_week_date import IsoWeek, pandas_utils, polars_utils
from iso_week_date._patterns import ISOWEEK_PATTERN
from iso_week_date._utils import match_isoweek

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
    ],
)
def test_is_isoweek_series_agrees_with_the_scalar_pattern(values: list[str]) -> None:
    """Both backends must accept exactly the strings the shared pattern accepts.

    The reference is `match_isoweek`, the same helper `BaseIsoWeek._validate` uses, so the regex
    engines used by pandas (Python `re`) and polars (Rust `regex`) cannot drift apart from the
    scalar classes on which strings are well-formed.
    """
    expected = all(match_isoweek(ISOWEEK_PATTERN, v) is not None for v in values)

    assert pandas_utils.is_isoweek_series(pd.Series(values, dtype="object")) == expected
    assert polars_utils.is_isoweek_series(pl.Series(values, dtype=pl.String)) == expected


@pytest.mark.parametrize("value", ["2023-W53", "2021-W53", "2022-W53"])
def test_is_isoweek_series_is_a_format_check_not_a_calendar_check(value: str) -> None:
    """Documents a deliberate gap: the helpers check the format, not the week-number-vs-year rule.

    `2023-W53` matches the pattern (weeks 01-53 are syntactically valid) but `IsoWeek("2023-W53")`
    raises, because 2023 has only 52 weeks. Closing the gap would need a vectorised `weeks_of_year`
    in both backends; until then the asymmetry is pinned here so it is a known property rather than
    a surprise, and both backends at least agree on it.
    """
    with pytest.raises(ValueError, match="Invalid week number"):
        IsoWeek(value)

    assert pandas_utils.is_isoweek_series(pd.Series([value], dtype="object")) is True
    assert polars_utils.is_isoweek_series(pl.Series([value], dtype=pl.String)) is True
