"""Natural language date parser package."""

import re
from datetime import date, datetime

import dateparser  # type: ignore[import-untyped]
from dateutil.relativedelta import relativedelta


def _parse_offset_expression(text: str, today: date) -> date | None:
    """Parse relative offset expressions like '5 days before Dec 1, 2025' or '1 year after today'."""
    pattern = r"^(.*?)\s+(before|prior to|after|from|since)\s+(.*)$"
    match = re.match(pattern, text, re.IGNORECASE)
    if not match:
        return None

    delta_part, direction, base_part = match.groups()
    direction = direction.lower()

    base_date = parse(base_part, today=today)

    units = re.findall(
        r"(\d+|a|an|one|two|three|four|five|six|seven|eight|nine|ten)\s*(years?|months?|weeks?|days?)",
        delta_part,
        re.IGNORECASE,
    )
    if not units:
        return None

    word_to_num = {
        "a": 1,
        "an": 1,
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
        "six": 6,
        "seven": 7,
        "eight": 8,
        "nine": 9,
        "ten": 10,
    }

    kwargs: dict[str, int] = {}
    for amount_str, unit in units:
        amount_str = amount_str.lower()
        amount = (
            word_to_num[amount_str] if amount_str in word_to_num else int(amount_str)
        )
        unit = unit.lower()
        if not unit.endswith("s"):
            unit += "s"
        kwargs[unit] = kwargs.get(unit, 0) + amount

    delta = relativedelta(
        years=kwargs.get("years", 0),
        months=kwargs.get("months", 0),
        weeks=kwargs.get("weeks", 0),
        days=kwargs.get("days", 0),
    )
    if direction in ("before", "prior to"):
        return base_date - delta
    return base_date + delta


def parse(s: str, today: date | None = None) -> date:
    """Parse natural language string into a datetime.date object.

    Raises ValueError if input cannot be parsed or is empty.
    """
    if not s or not s.strip():
        raise ValueError("Input date string cannot be empty.")

    cleaned = s.strip()
    ref_date = today if today is not None else date.today()
    ref_datetime = datetime(ref_date.year, ref_date.month, ref_date.day)

    # 1. Handle relative offset expressions
    offset_result = _parse_offset_expression(cleaned, ref_date)
    if offset_result is not None:
        return offset_result

    # 2. General natural language parsing using dateparser
    settings = {
        "RELATIVE_BASE": ref_datetime,
        "PREFER_DATES_FROM": "current_period",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }
    parsed_dt = dateparser.parse(cleaned, settings=settings)

    if parsed_dt is None:
        raise ValueError(f"Could not parse date string: {s!r}")

    return parsed_dt.date()


__all__ = ["parse"]
