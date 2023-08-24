import re
from typing import Final

# We have two cases to consider to match a year between 0001 and 9999:
# 1. 1000-9999: a 4 digit number starting with 1-9 -> "[1-9]\d{3}"
# 2. 0001-0999: a 4 digit number starting with 0 and with at least one non-zero digit
#   in the last 3 digits -> "0\d{2}[1-9]|0\d[1-9]\d|0[1-9]\d{2}"
YEAR_MATCH: Final[str] = r"([1-9]\d{3}|0\d{2}[1-9]|0\d[1-9]\d|0[1-9]\d{2})"

# We have three cases to consider to match a week between 01 and 53:
# 1. 01-09: a 2 digit number starting with 0 and ending with 1-9 -> "0[1-9]"
# 2. 10-49: a 2 digit number starting with 1-4 and ending with 0-9 -> "[1-4]\d"
# 3. 50-53: a 2 digit number starting with 5 and ending with 0-3 -> "5[0-3]"
WEEK_MATCH: Final[str] = r"(0[1-9]|[1-4]\d|5[0-3])"

# Weekday is quite straightforward: we need to match a digit between 1 and 7 -> "[1-7]"
WEEKDAY_MATCH: Final[str] = r"[1-7]"

# Patterns
ISOWEEK_PATTERN: Final[re.Pattern] = re.compile(
    r"^{}-W{}$".format(YEAR_MATCH, WEEK_MATCH)
)

ISOWEEKDATE_PATTERN: Final[re.Pattern] = re.compile(
    r"^{}-W{}-{}$".format(YEAR_MATCH, WEEK_MATCH, WEEKDAY_MATCH)
)