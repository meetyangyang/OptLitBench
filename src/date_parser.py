from __future__ import annotations

import re
from dataclasses import dataclass

MONTH_NAMES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]
MONTH_LOOKUP = {name.lower(): idx for idx, name in enumerate(MONTH_NAMES, start=1)}


@dataclass(frozen=True)
class ParsedDate:
    year: int
    month: int | None
    year_month: str | None
    source: str


def _extract_esaim_year(path_text: str) -> int | None:
    match = re.search(r"esaim-cocv[\\/]+(\d+)[\\/]+", path_text, flags=re.IGNORECASE)
    if not match:
        return None
    volume = int(match.group(1))
    # ESAIM:COCV volume 1 corresponds to 1996.
    return 1995 + volume


def parse_date_from_path(path_text: str, journal_name: str = "") -> ParsedDate | None:
    normalized = path_text.replace("\\", "/")
    years = [int(value) for value in re.findall(r"(?:19|20)\d{2}", normalized)]
    year = years[-1] if years else None
    source = "path_year"

    if year is None and journal_name.lower() == "esaim-cocv":
        year = _extract_esaim_year(normalized)
        source = "esaim_volume"

    if year is None or year < 1960 or year > 2035:
        return None

    month = None
    for month_name, month_idx in MONTH_LOOKUP.items():
        if month_name.lower() in normalized.lower():
            month = month_idx
            source = f"{source}+month_name"
            break

    year_month = f"{year}-{month:02d}" if month is not None else None
    return ParsedDate(year=year, month=month, year_month=year_month, source=source)
