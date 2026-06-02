"""Constants for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "zweibruecken_waste"

DEFAULT_NAME = "Waste Calendar"
DEFAULT_SCAN_INTERVAL_HOURS = 12
MIN_SCAN_INTERVAL_HOURS = 1
DEFAULT_SCAN_INTERVAL = timedelta(hours=DEFAULT_SCAN_INTERVAL_HOURS)

CONF_ICS_URL = "ics_url"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"
CONF_ENABLE_CALENDAR = "enable_calendar"

ATTR_DAYS_UNTIL = "days_until"
ATTR_IS_TODAY = "is_today"
ATTR_IS_TOMORROW = "is_tomorrow"
ATTR_NEXT_COLLECTION = "next_collection"
ATTR_SOURCE = "source"
ATTR_SUMMARY = "summary"
ATTR_WASTE_TYPE = "waste_type"

WASTE_BIO = "bio"
WASTE_PAPER = "paper"
WASTE_YELLOW = "yellow"
WASTE_RESIDUAL = "residual"

WASTE_TYPES = (WASTE_BIO, WASTE_PAPER, WASTE_YELLOW, WASTE_RESIDUAL)

WASTE_TYPE_NAMES = {
    WASTE_BIO: "Bioabfall",
    WASTE_PAPER: "Papier",
    WASTE_YELLOW: "Gelbe Tonne",
    WASTE_RESIDUAL: "Restmuell",
}

WASTE_TYPE_ICONS = {
    WASTE_BIO: "mdi:leaf",
    WASTE_PAPER: "mdi:newspaper-variant-outline",
    WASTE_YELLOW: "mdi:recycle",
    WASTE_RESIDUAL: "mdi:trash-can-outline",
}

WASTE_TYPE_ENTITY_IDS = {
    WASTE_BIO: "bioabfall",
    WASTE_PAPER: "papier",
    WASTE_YELLOW: "gelbe_tonne",
    WASTE_RESIDUAL: "restmuell",
}

WASTE_TYPE_KEYWORDS = {
    WASTE_BIO: (
        "biotonne",
        "bioabfall",
        "bio-abfall",
        "biomuell",
        "biomull",
        "bio",
    ),
    WASTE_PAPER: (
        "papiertonne",
        "altpapier",
        "papier",
        "pappe",
    ),
    WASTE_YELLOW: (
        "gelbe tonne",
        "gelber sack",
        "gelbe saecke",
        "gelbe sacke",
        "gelb",
    ),
    WASTE_RESIDUAL: (
        "restabfalltonne",
        "restabfall",
        "restmuell",
        "restmull",
        "schwarze tonne",
        "schwarz",
    ),
}
