"""Data update coordinator for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from aiohttp import ClientError

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .calendar import WasteCalendarData, parse_ics_calendar_data
from .const import (
    CONF_ICS_URL,
    CONF_SCAN_INTERVAL_HOURS,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
)
from .url import is_inline_ics, normalize_ics_source

_LOGGER = logging.getLogger(__name__)


class ZweibrueckenWasteCoordinator(DataUpdateCoordinator[WasteCalendarData]):
    """Fetch and parse waste collection appointments from an ICS feed."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""

        interval_hours = entry.options.get(
            CONF_SCAN_INTERVAL_HOURS,
            entry.data.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=interval_hours),
            config_entry=entry,
        )
        self._ics_source = normalize_ics_source(entry.data[CONF_ICS_URL])

    async def _async_update_data(self) -> WasteCalendarData:
        """Fetch data from the configured calendar."""

        if is_inline_ics(self._ics_source):
            try:
                return parse_ics_calendar_data(self._ics_source)
            except ValueError as err:
                raise UpdateFailed("ICS feed could not be parsed") from err

        session = async_get_clientsession(self.hass)
        try:
            async with session.get(self._ics_source, timeout=30) as response:
                if response.status >= 400:
                    raise UpdateFailed(f"ICS feed returned HTTP {response.status}")
                ics_text = await response.text()
        except TimeoutError as err:
            raise UpdateFailed("Timed out while fetching the ICS feed") from err
        except ClientError as err:
            raise UpdateFailed("Could not fetch the ICS feed") from err

        try:
            return parse_ics_calendar_data(ics_text)
        except ValueError as err:
            raise UpdateFailed("ICS feed could not be parsed") from err
