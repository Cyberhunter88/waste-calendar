"""ICS parsing helpers for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
import re
import unicodedata

from .const import (
    DOMAIN,
    WASTE_TYPE_KEYWORDS,
    WASTE_TYPE_NAMES,
    WASTE_TYPES,
)


@dataclass(frozen=True, slots=True)
class WasteCollection:
    """A normalized waste collection event."""

    collection_date: date
    summary: str
    waste_type: str


@dataclass(frozen=True, slots=True)
class WasteCalendarData:
    """Parsed waste collections for sensors and calendar entities."""

    next_by_type: dict[str, WasteCollection | None]
    events: list[WasteCollection]


def format_collection_date(collection_date: date) -> str:
    """Return a German display date for Home Assistant sensor states."""

    return collection_date.strftime("%d.%m.%Y")


def format_collection_state(collection_date: date, today: date | None = None) -> str:
    """Return the sensor state shown in Home Assistant tiles."""

    today = today or date.today()
    if (collection_date - today).days == 1:
        return "Morgen"
    return format_collection_date(collection_date)


def parse_ics_calendar_data(ics_text: str, today: date | None = None) -> WasteCalendarData:
    """Return all upcoming collection events and the next collection per type."""

    events = parse_ics_collection_events(ics_text, today=today)
    next_by_type: dict[str, WasteCollection | None] = {waste_type: None for waste_type in WASTE_TYPES}

    for collection in events:
        current = next_by_type[collection.waste_type]
        if current is None or collection.collection_date < current.collection_date:
            next_by_type[collection.waste_type] = collection

    return WasteCalendarData(next_by_type=next_by_type, events=events)


def parse_ics_collections(ics_text: str, today: date | None = None) -> dict[str, WasteCollection | None]:
    """Return the next collection per waste type from raw ICS content."""

    return parse_ics_calendar_data(ics_text, today=today).next_by_type


def parse_ics_collection_events(ics_text: str, today: date | None = None) -> list[WasteCollection]:
    """Return all upcoming collection events from raw ICS content."""

    if not ics_text or "BEGIN:VCALENDAR" not in ics_text:
        raise ValueError("not_ics")

    today = today or date.today()
    collections: list[WasteCollection] = []

    for event in _iter_events(ics_text):
        summary = event.get("SUMMARY", "")
        event_date = _event_date(event)
        if event_date is None or event_date < today:
            continue

        waste_type = classify_waste_type(summary)
        if waste_type is None:
            continue

        collections.append(WasteCollection(event_date, summary, waste_type))

    return sorted(collections, key=lambda collection: collection.collection_date)


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    """Set up the optional Home Assistant calendar entity."""

    from homeassistant.components.calendar import CalendarEntity, CalendarEvent
    from homeassistant.helpers.update_coordinator import CoordinatorEntity

    class ZweibrueckenWasteCalendar(
        CoordinatorEntity,
        CalendarEntity,
    ):
        """Calendar containing all upcoming waste collection appointments."""

        _attr_has_entity_name = True
        _attr_name = "Abfalltermine"
        _attr_icon = "mdi:calendar-recycle"

        def __init__(self) -> None:
            """Initialize the calendar entity."""

            super().__init__(hass.data[DOMAIN][entry.entry_id])
            self._attr_unique_id = f"{entry.entry_id}_calendar"
            self._attr_suggested_object_id = "abfalltermine"

        @property
        def event(self):
            """Return the current or next upcoming waste collection event."""

            collection = _next_collection(self.coordinator.data.events)
            if collection is None:
                return None
            return _calendar_event(CalendarEvent, collection)

        async def async_get_events(self, hass, start_date, end_date):
            """Return waste collection events within a datetime range."""

            start = start_date.date()
            end = end_date.date()
            return [
                _calendar_event(CalendarEvent, collection)
                for collection in self.coordinator.data.events
                if start <= collection.collection_date < end
            ]

    async_add_entities([ZweibrueckenWasteCalendar()])


def _next_collection(events: list[WasteCollection]) -> WasteCollection | None:
    today = date.today()
    for collection in events:
        if collection.collection_date >= today:
            return collection
    return None


def _calendar_event(calendar_event_cls, collection: WasteCollection):
    end_date = collection.collection_date + timedelta(days=1)
    waste_type_name = WASTE_TYPE_NAMES[collection.waste_type]
    return calendar_event_cls(
        start=collection.collection_date,
        end=end_date,
        summary=waste_type_name,
        description=collection.summary,
        uid=f"{collection.waste_type}-{collection.collection_date.isoformat()}",
    )


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
