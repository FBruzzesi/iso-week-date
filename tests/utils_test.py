from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError
from typing import TYPE_CHECKING

import pytest

from iso_week_date._patterns import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
from iso_week_date._utils import match_isoweek, require_version, weeks_of_year

if TYPE_CHECKING:
    from collections.abc import Callable


@pytest.mark.parametrize(
    ("year", "expected"),
    [
        (2020, 53),
        (2021, 52),
        (2022, 52),
        (2023, 52),
        (2024, 52),
        (2026, 53),
        (1, 52),
        (9999, 52),
    ],
)
def test_weeks_of_year(year: int, expected: int) -> None:
    assert weeks_of_year(year) == expected


@pytest.mark.parametrize(
    ("pattern", "value", "expected"),
    [
        (ISOWEEK_PATTERN, "2024-W01", (2024, 1)),
        (ISOWEEK_PATTERN, "2024-W53", (2024, 53)),
        (ISOWEEK_PATTERN, "0001-W01", (1, 1)),
        (ISOWEEKDATE_PATTERN, "2024-W01-1", (2024, 1)),
        (ISOWEEKDATE_PATTERN, "0001-W01-7", (1, 1)),
    ],
)
def test_match_isoweek_valid(pattern: re.Pattern[str], value: str, expected: tuple[int, int]) -> None:
    assert match_isoweek(pattern, value) == expected


@pytest.mark.parametrize(
    ("pattern", "value"),
    [
        (ISOWEEK_PATTERN, "abcd-Wxy"),
        (ISOWEEK_PATTERN, "0000-W01"),
        (ISOWEEK_PATTERN, "2024-W54"),
        (ISOWEEK_PATTERN, "2024-W01-1"),
        (ISOWEEKDATE_PATTERN, "2024-W01"),
        (ISOWEEKDATE_PATTERN, "2024-W01-8"),
        # A `$`-anchored pattern also matches just before a trailing newline, so `match_isoweek`
        # must use `fullmatch` to reject these. See the `match_isoweek` docstring.
        (ISOWEEK_PATTERN, "2024-W01\n"),
        (ISOWEEKDATE_PATTERN, "2024-W01-1\n"),
        (ISOWEEK_PATTERN, "2024-W01 "),
        (ISOWEEK_PATTERN, " 2024-W01"),
        (ISOWEEK_PATTERN, "2024-W01\t"),
    ],
)
def test_match_isoweek_invalid(pattern: re.Pattern[str], value: str) -> None:
    assert match_isoweek(pattern, value) is None


def test_require_version_satisfied() -> None:
    """A version at or above the minimum returns without raising."""
    require_version("pytest", minimum="0.0.1", extra="tests")


def test_require_version_too_old(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("importlib.metadata.version", lambda _module: "1.0.3")

    msg = re.escape("dummy>=2.4.0 is required for this module, found dummy==1.0.3")
    with pytest.raises(ImportError, match=msg):
        require_version("dummy", minimum="2.4.0", extra="dummy")


def test_require_version_not_installed(monkeypatch: pytest.MonkeyPatch) -> None:
    def _raise(_module: str) -> str:
        raise PackageNotFoundError(_module)

    monkeypatch.setattr("importlib.metadata.version", _raise)

    msg = re.escape("dummy>=2.4.0 is required for this module, but dummy is not installed.")
    with pytest.raises(ImportError, match=msg):
        require_version("dummy", minimum="2.4.0", extra="dummy")


@pytest.mark.parametrize(
    "installed",
    [
        # Shapes that made the previous hand-rolled parser raise `ValueError` (it stripped
        # non-digits per dotted segment, so an all-alphabetic segment became `int("")`)...
        "2.2.0.dev0+1.g1234567.dirty",
        "3.0.0.dev0+2261.gb1a2c3d4e5",
        "1.6.0.post1+local.build",
        # ...or miscompare it (a two-component version became a 2-tuple, which sorts *below* the
        # 3-tuple minimum, so a perfectly fine install was rejected with a spurious ImportError).
        "2.4",
        "2",
        # ...plus the ordinary shapes, for completeness.
        "1.1.0",
        "3.0.2",
        "3.0.0rc1",
        "2.4.0.post1",
        "2!1.0.0",
    ],
)
def test_require_version_accepts_pep440_shapes(monkeypatch: pytest.MonkeyPatch, installed: str) -> None:
    """Every one of these is >= 1.1.0 under PEP 440 and must not block the import."""
    monkeypatch.setattr("importlib.metadata.version", lambda _module: installed)
    require_version("dummy", minimum="1.1.0", extra="dummy")


@pytest.mark.parametrize(
    ("installed", "minimum"),
    [
        # A dev release precedes its own final release under PEP 440, so these are genuinely too
        # old. Asserted explicitly because the previous parser got the ordering backwards.
        ("2.2.0.dev0+1.g1234567.dirty", "2.2.0"),
        ("2.4.0rc1", "2.4.0"),
        ("2.3", "2.4"),
        ("0.17.9", "0.18.0"),
    ],
)
def test_require_version_pep440_ordering_rejects_older(
    monkeypatch: pytest.MonkeyPatch, installed: str, minimum: str
) -> None:
    monkeypatch.setattr("importlib.metadata.version", lambda _module: installed)
    with pytest.raises(ImportError, match=re.escape(f"found dummy=={installed}")):
        require_version("dummy", minimum=minimum, extra="dummy")


def test_require_version_ignores_unparsable_version(monkeypatch: pytest.MonkeyPatch) -> None:
    """An unparsable version carries no signal, so it must not block the import."""
    monkeypatch.setattr("importlib.metadata.version", lambda _module: "not-a-version")
    require_version("dummy", minimum="2.4.0", extra="dummy")


@pytest.mark.parametrize(
    ("module", "importer"),
    [
        pytest.param("pandas", lambda: __import__("iso_week_date.pandas_utils"), marks=pytest.mark.pandas),
        pytest.param("polars", lambda: __import__("iso_week_date.polars_utils"), marks=pytest.mark.polars),
        pytest.param("pydantic", lambda: __import__("iso_week_date.pydantic"), marks=pytest.mark.pydantic),
    ],
)
def test_optional_module_imports_under_current_versions(module: str, importer: Callable[[], object]) -> None:
    """The installed optional dependency satisfies its declared gate."""
    pytest.importorskip(module)
    assert importer() is not None
