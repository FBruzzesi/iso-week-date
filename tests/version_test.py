from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from typing_extensions import Any, assert_type

import iso_week_date as iwd


def test_version_matches_pyproject() -> None:
    """Tests version is same of pyproject"""
    with Path("pyproject.toml").open(encoding="utf-8") as file:
        content = file.read()
        pyproject_version = re.search(r'version = "(.*)"', content).group(1)  # type: ignore[union-attr]

    assert iwd.__version__ == pyproject_version


def test_package_getattr() -> None:
    assert_type(iwd.__version__, str)
    assert_type(iwd.__title__, str)
    assert_type(iwd.__all__, tuple[str, ...])  # type: ignore[assert-type]

    if TYPE_CHECKING:
        bad = iwd.not_real  # type: ignore[attr-defined]
        assert_type(bad, Any)

    with pytest.raises(AttributeError):
        very_bad = iwd.not_real  # type: ignore[attr-defined]  # noqa: F841
