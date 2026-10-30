"""The Zweibruecken waste calendar integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .const import CONF_ENABLE_CALENDAR, DOMAIN

_PLATFORMS = "zweibruecken_waste_platforms"

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant


DEFAULT_PLATFORMS = ["sensor"]


def _platforms_for_entry(entry: ConfigEntry) -> list[str]:
    """Return platforms enabled for a config entry."""

    platforms = list(DEFAULT_PLATFORMS)
    if entry.options.get(
        CONF_ENABLE_CALENDAR,
        entry.data.get(CONF_ENABLE_CALENDAR, False),
    ):
        platforms.append("calendar")
    return platforms


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Zweibruecken waste calendar from a config entry."""

    from homeassistant.core import callback
    from homeassistant.helpers.event import async_track_time_change
    from homeassistant.util import dt as dt_util

    from .calendar import calendar_data_for_day
    from .coordinator import ZweibrueckenWasteCoordinator

    coordinator = ZweibrueckenWasteCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    platforms = _platforms_for_entry(entry)
    hass.data.setdefault(_PLATFORMS, {})[entry.entry_id] = platforms
    await hass.config_entries.async_forward_entry_setups(entry, platforms)

    @callback
    def update_day(_now) -> None:
        coordinator.data = calendar_data_for_day(coordinator.data.events, dt_util.now().date())
        coordinator.async_update_listeners()

    entry.async_on_unload(async_track_time_change(hass, update_day, hour=0, minute=0, second=0))
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, hass.data[_PLATFORMS][entry.entry_id])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data[_PLATFORMS].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload a config entry after options changed."""

    await hass.config_entries.async_reload(entry.entry_id)
