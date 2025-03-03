from __future__ import annotations

from importlib import metadata

from iso_week_date._patterns import ISOWEEK_PATTERN
from iso_week_date._patterns import ISOWEEKDATE_PATTERN
from iso_week_date.isoweek import IsoWeek
from iso_week_date.isoweekdate import IsoWeekDate

__title__ = __name__
__version__ = metadata.version(__title__)

__all__ = (
    "ISOWEEKDATE_PATTERN",
    "ISOWEEK_PATTERN",
    "IsoWeek",
    "IsoWeekDate",
)
