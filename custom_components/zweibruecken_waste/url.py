"""Source helpers for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from hashlib import sha256


def is_inline_ics(source: str) -> bool:
    """Return if the source contains raw ICS calendar text."""

    return "BEGIN:VCALENDAR" in source


def normalize_ics_source(source: str) -> str:
    """Normalize user-provided ICS URLs or raw ICS calendar text."""

    normalized_source = source.strip()
    if normalized_source.lower().startswith("webcal://"):
        return f"https://{normalized_source[9:]}"
    return normalized_source


def normalize_ics_url(ics_url: str) -> str:
    """Normalize user-provided ICS calendar URLs."""

    return normalize_ics_source(ics_url)


def source_display_name(source: str) -> str:
    """Return a compact display value for the configured ICS source."""

    if is_inline_ics(source):
        return "Inline ICS calendar"
    return source


def source_unique_id(source: str) -> str:
    """Return a stable unique id for a URL or inline ICS calendar."""

    if is_inline_ics(source):
        digest = sha256(source.encode("utf-8")).hexdigest()
        return f"inline_ics_{digest}"
    return source
