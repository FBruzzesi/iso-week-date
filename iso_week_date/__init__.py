from __future__ import annotations

import typing as _t

from iso_week_date._patterns import ISOWEEK_PATTERN, ISOWEEKDATE_PATTERN
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


if not _t.TYPE_CHECKING:

    def __getattr__(name: str) -> _t.Any:  # noqa: ANN401
        if name == "__version__":
            global __version__  # noqa: PLW0603

            from importlib import metadata  # noqa: PLC0415

            __version__ = metadata.version(__name__)
            return __version__
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
else:  # pragma: no cover
    ...
