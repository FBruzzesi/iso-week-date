from __future__ import annotations

from typing import Literal

from iso_week_date._patterns import ISOWEEK_PATTERN
from iso_week_date._patterns import ISOWEEKDATE_PATTERN
from iso_week_date.isoweek import IsoWeek
from iso_week_date.isoweekdate import IsoWeekDate

__title__ = __name__
__version__: str

__all__ = (
    "ISOWEEKDATE_PATTERN",
    "ISOWEEK_PATTERN",
    "IsoWeek",
    "IsoWeekDate",
)


def __getattr__(name: Literal["__version__"]) -> str:  # type: ignore[misc]
    if name == "__version__":
        global __version__  # noqa: PLW0603

        from importlib.metadata import version

        __version__ = version(__name__)
        return __version__
    else:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
