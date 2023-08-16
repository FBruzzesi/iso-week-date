from importlib import metadata

from iso_week.isoweek import IsoWeek

__title__ = __name__
__version__ = metadata.version(__title__)

__all__ = ("IsoWeek",)
