"""Tests for the Zweibruecken waste calendar parser."""

from __future__ import annotations

from datetime import date

from custom_components.zweibruecken_waste.calendar import (
    classify_waste_type,
    format_collection_date,
    parse_ics_calendar_data,
    parse_ics_collections,
)
from custom_components.zweibruecken_waste.const import (
    WASTE_BIO,
    WASTE_PAPER,
    WASTE_RESIDUAL,
    WASTE_YELLOW,
)
from custom_components.zweibruecken_waste.url import (
    normalize_ics_source,
    normalize_ics_url,
    source_display_name,
    source_unique_id,
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


def test_parse_ics_calendar_data_returns_all_upcoming_events() -> None:
    """Calendar data should include every supported upcoming waste event."""

    result = parse_ics_calendar_data(SAMPLE_ICS, today=date(2026, 6, 2))

    assert [event.collection_date for event in result.events] == [
        date(2026, 6, 3),
        date(2026, 6, 4),
        date(2026, 6, 5),
        date(2026, 6, 6),
    ]
    assert result.next_by_type[WASTE_PAPER].collection_date == date(2026, 6, 4)


def test_classify_waste_type_handles_common_names() -> None:
    """Common waste names should map to stable internal types."""

    assert classify_waste_type("Bioabfall") == WASTE_BIO
    assert classify_waste_type("Altpapier") == WASTE_PAPER
    assert classify_waste_type("Gelber Sack") == WASTE_YELLOW
    assert classify_waste_type("Schwarze Tonne") == WASTE_RESIDUAL


def test_format_collection_date_uses_german_order() -> None:
    """Display dates should be day-month-year for German users."""

    assert format_collection_date(date(2026, 6, 17)) == "17.06.2026"


def test_parse_ics_rejects_non_calendar_text() -> None:
    """Non-ICS content should fail validation."""

    try:
        parse_ics_collections("not a calendar", today=date(2026, 6, 2))
    except ValueError as err:
        assert str(err) == "not_ics"
    else:
        raise AssertionError("Expected ValueError")


def test_normalize_ics_url_accepts_webcal_links() -> None:
    """webcal links copied from calendar apps should be fetchable via HTTPS."""

    assert normalize_ics_url("webcal://example.com/calendar.ics") == (
        "https://example.com/calendar.ics"
    )


def test_inline_ics_sources_get_stable_ids_and_compact_display_names() -> None:
    """Inline ICS text should not be exposed as a long sensor source value."""

    inline_source = normalize_ics_source(f"  {SAMPLE_ICS}  ")

    assert source_display_name(inline_source) == "Inline ICS calendar"
    assert source_unique_id(inline_source).startswith("inline_ics_")


def test_inline_ics_sources_keep_multiline_calendar_content() -> None:
    """Pasted ICS file contents should survive trimming and remain parseable."""

    inline_source = normalize_ics_source(f"\r\n{SAMPLE_ICS}\r\n")

    assert inline_source.startswith("BEGIN:VCALENDAR")
    assert inline_source.endswith("END:VCALENDAR")
    assert parse_ics_collections(inline_source, today=date(2026, 6, 2))[WASTE_BIO]
