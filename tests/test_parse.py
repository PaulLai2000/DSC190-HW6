"""Test suite for nldate parser."""

from datetime import date

import pytest

from nldate import parse


def test_fixed_standard_date() -> None:
    assert parse("2025-12-01") == date(2025, 12, 1)


def test_month_day_year() -> None:
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_today_reference() -> None:
    ref = date(2026, 3, 15)
    assert parse("today", today=ref) == date(2026, 3, 15)


def test_tomorrow_and_yesterday() -> None:
    ref = date(2026, 3, 15)
    assert parse("tomorrow", today=ref) == date(2026, 3, 16)
    assert parse("yesterday", today=ref) == date(2026, 3, 14)


def test_relative_days_before() -> None:
    ref = date(2026, 3, 15)
    assert parse("5 days before December 1st, 2025", today=ref) == date(2025, 11, 26)


def test_relative_compound_after() -> None:
    ref = date(2026, 3, 15)
    assert parse("1 year and 2 months after yesterday", today=ref) == date(2027, 5, 14)


def test_in_x_days() -> None:
    ref = date(2026, 3, 15)
    assert parse("in 3 days", today=ref) == date(2026, 3, 18)


def test_weeks_ago() -> None:
    ref = date(2026, 3, 15)
    assert parse("2 weeks ago", today=ref) == date(2026, 3, 1)


def test_next_weekday() -> None:
    ref = date(2026, 3, 15)
    assert parse("next Tuesday", today=ref) == date(2026, 3, 17)


def test_empty_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse("")


def test_invalid_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse("not a date at all")


def test_whitespace_string_raises_value_error() -> None:
    with pytest.raises(ValueError):
        parse("   ")
