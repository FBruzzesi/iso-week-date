from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from typing_extensions import assert_type

import iso_week_date as iwd


def test_package_getattr() -> None:
    assert_type(iwd.__version__, str)
    assert_type(iwd.__title__, str)
    assert_type(iwd.__all__, tuple[str, ...])  # type: ignore[assert-type]

    if TYPE_CHECKING:
        bad = iwd.not_real  # type: ignore[attr-defined]
        assert_type(bad, Any)

    with pytest.raises(AttributeError):
        very_bad = iwd.not_real  # type: ignore[attr-defined]  # noqa: F841
