"""Config flow for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from typing import Any

from aiohttp import ClientError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import selector

from .calendar import parse_ics_collections
from .const import (
    CONF_ICS_URL,
    CONF_SCAN_INTERVAL_HOURS,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    MIN_SCAN_INTERVAL_HOURS,
)
from .url import is_inline_ics, normalize_ics_source, source_unique_id


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ICS_URL): selector.TextSelector(
            selector.TextSelectorConfig(multiline=True)
        ),
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Optional(
            CONF_SCAN_INTERVAL_HOURS,
            default=DEFAULT_SCAN_INTERVAL_HOURS,
        ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_HOURS)),
    }
)


async def async_validate_ics_url(hass: HomeAssistant, ics_url: str) -> None:
    """Validate that an ICS URL is reachable and parseable."""

    normalized_url = normalize_ics_source(ics_url)
    if is_inline_ics(normalized_url):
        try:
            parse_ics_collections(normalized_url)
        except ValueError as err:
            raise InvalidCalendar from err
        return

    session = async_get_clientsession(hass)
    try:
        async with session.get(normalized_url, timeout=30) as response:
            if response.status >= 400:
                raise CannotConnect
            ics_text = await response.text()
    except TimeoutError as err:
        raise CannotConnect from err
    except ClientError as err:
        raise CannotConnect from err

    try:
        parse_ics_collections(ics_text)
    except ValueError as err:
        raise InvalidCalendar from err


class ZweibrueckenWasteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Zweibruecken waste calendar."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}
        if user_input is not None:
            user_input[CONF_ICS_URL] = normalize_ics_source(user_input[CONF_ICS_URL])
            await self.async_set_unique_id(source_unique_id(user_input[CONF_ICS_URL]))
            self._abort_if_unique_id_configured()
            try:
                await async_validate_ics_url(self.hass, user_input[CONF_ICS_URL])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidCalendar:
                errors["base"] = "invalid_calendar"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""

        return ZweibrueckenWasteOptionsFlow(config_entry)


class ZweibrueckenWasteOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""

        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""

        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        scan_interval = self._config_entry.options.get(
            CONF_SCAN_INTERVAL_HOURS,
            self._config_entry.data.get(CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS),
        )
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL_HOURS,
                    default=scan_interval,
                ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL_HOURS)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidCalendar(Exception):
    """Error to indicate the calendar is invalid."""
