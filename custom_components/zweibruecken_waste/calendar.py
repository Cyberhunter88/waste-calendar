"""ICS parsing helpers for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import re
import unicodedata

from .const import WASTE_TYPE_KEYWORDS, WASTE_TYPES


@dataclass(frozen=True, slots=True)
class WasteCollection:
    """A normalized waste collection event."""

    collection_date: date
    summary: str
    waste_type: str


def parse_ics_collections(ics_text: str, today: date | None = None) -> dict[str, WasteCollection | None]:
    """Return the next collection per waste type from raw ICS content."""

    if not ics_text or "BEGIN:VCALENDAR" not in ics_text:
        raise ValueError("not_ics")

    today = today or date.today()
    next_by_type: dict[str, WasteCollection | None] = {waste_type: None for waste_type in WASTE_TYPES}

    for event in _iter_events(ics_text):
        summary = event.get("SUMMARY", "")
        event_date = _event_date(event)
        if event_date is None or event_date < today:
            continue

        waste_type = classify_waste_type(summary)
        if waste_type is None:
            continue

        collection = WasteCollection(event_date, summary, waste_type)
        current = next_by_type[waste_type]
        if current is None or collection.collection_date < current.collection_date:
            next_by_type[waste_type] = collection

    return next_by_type


def classify_waste_type(summary: str) -> str | None:
    """Classify an event summary into one of the supported waste types."""

    normalized = _normalize_text(summary)
    for waste_type, keywords in WASTE_TYPE_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return waste_type
    return None


def _iter_events(ics_text: str) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for line in _unfold_ics_lines(ics_text):
        if line == "BEGIN:VEVENT":
            current = {}
            continue
        if line == "END:VEVENT":
            if current is not None:
                events.append(current)
            current = None
            continue
        if current is None or ":" not in line:
            continue

        raw_name, value = line.split(":", 1)
        name = raw_name.split(";", 1)[0].upper()
        current[name] = _unescape_ics_text(value.strip())

    return events


def _unfold_ics_lines(ics_text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in ics_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if raw_line.startswith((" ", "\t")) and lines:
            lines[-1] += raw_line[1:]
        elif raw_line:
            lines.append(raw_line.strip())
    return lines


def _event_date(event: dict[str, str]) -> date | None:
    value = event.get("DTSTART")
    if value is None:
        return None

    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").date()

    value = value.rstrip("Z")
    for fmt in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M"):
        try:
            parsed = datetime.strptime(value, fmt)
            if value.endswith("Z"):
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.date()
        except ValueError:
            continue

    return None


def _normalize_text(value: str) -> str:
    value = value.casefold()
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    value = value.replace("ß", "ss")
    return re.sub(r"\s+", " ", value)


def _unescape_ics_text(value: str) -> str:
    return (
        value.replace(r"\n", "\n")
        .replace(r"\N", "\n")
        .replace(r"\,", ",")
        .replace(r"\;", ";")
        .replace(r"\\", "\\")
    )
