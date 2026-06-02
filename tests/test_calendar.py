"""Tests for the Zweibruecken waste calendar parser."""

from __future__ import annotations

from datetime import date

from custom_components.zweibruecken_waste.calendar import (
    classify_waste_type,
    parse_ics_collections,
)
from custom_components.zweibruecken_waste.const import (
    WASTE_BIO,
    WASTE_PAPER,
    WASTE_RESIDUAL,
    WASTE_YELLOW,
)


SAMPLE_ICS = """BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
SUMMARY:Biotonne
DTSTART;VALUE=DATE:20260601
END:VEVENT
BEGIN:VEVENT
SUMMARY:Biotonne
DTSTART;VALUE=DATE:20260603
END:VEVENT
BEGIN:VEVENT
SUMMARY:Papiertonne
DTSTART;VALUE=DATE:20260604
END:VEVENT
BEGIN:VEVENT
SUMMARY:Gelbe Tonne
DTSTART;TZID=Europe/Berlin:20260605T060000
END:VEVENT
BEGIN:VEVENT
SUMMARY:Restabfall
DTSTART:20260606T060000
END:VEVENT
END:VCALENDAR
"""


def test_parse_ics_collections_returns_next_collection_per_waste_type() -> None:
    """The parser should ignore past events and choose the next future date."""

    result = parse_ics_collections(SAMPLE_ICS, today=date(2026, 6, 2))

    assert result[WASTE_BIO] is not None
    assert result[WASTE_BIO].collection_date == date(2026, 6, 3)
    assert result[WASTE_PAPER] is not None
    assert result[WASTE_PAPER].collection_date == date(2026, 6, 4)
    assert result[WASTE_YELLOW] is not None
    assert result[WASTE_YELLOW].collection_date == date(2026, 6, 5)
    assert result[WASTE_RESIDUAL] is not None
    assert result[WASTE_RESIDUAL].collection_date == date(2026, 6, 6)


def test_classify_waste_type_handles_common_names() -> None:
    """Common waste names should map to stable internal types."""

    assert classify_waste_type("Bioabfall") == WASTE_BIO
    assert classify_waste_type("Altpapier") == WASTE_PAPER
    assert classify_waste_type("Gelber Sack") == WASTE_YELLOW
    assert classify_waste_type("Schwarze Tonne") == WASTE_RESIDUAL


def test_parse_ics_rejects_non_calendar_text() -> None:
    """Non-ICS content should fail validation."""

    try:
        parse_ics_collections("not a calendar", today=date(2026, 6, 2))
    except ValueError as err:
        assert str(err) == "not_ics"
    else:
        raise AssertionError("Expected ValueError")
