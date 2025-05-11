from __future__ import annotations

import re
from pathlib import Path

import iso_week_date as iwd


def test_version_matches_pyproject() -> None:
    """Tests version is same of pyproject"""
    with Path("pyproject.toml").open(encoding="utf-8") as file:
        content = file.read()
        pyproject_version = re.search(r'version = "(.*)"', content).group(1)  # type: ignore[union-attr]

    assert iwd.__version__ == pyproject_version
