"""Sensor platform for the Zweibruecken waste calendar integration."""

from __future__ import annotations

from datetime import date
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_DAYS_UNTIL,
    ATTR_IS_TODAY,
    ATTR_IS_TOMORROW,
    ATTR_NEXT_COLLECTION,
    ATTR_SOURCE,
    ATTR_SUMMARY,
    ATTR_WASTE_TYPE,
    CONF_ICS_URL,
    DOMAIN,
    WASTE_TYPE_ENTITY_IDS,
    WASTE_TYPE_ICONS,
    WASTE_TYPE_NAMES,
    WASTE_TYPES,
)
from .coordinator import ZweibrueckenWasteCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up waste collection sensors."""

    coordinator: ZweibrueckenWasteCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        ZweibrueckenWasteSensor(coordinator, entry, waste_type)
        for waste_type in WASTE_TYPES
    )


class ZweibrueckenWasteSensor(CoordinatorEntity[ZweibrueckenWasteCoordinator], SensorEntity):
    """Sensor for one waste collection type."""

    _attr_device_class = SensorDeviceClass.DATE
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ZweibrueckenWasteCoordinator,
        entry: ConfigEntry,
        waste_type: str,
    ) -> None:
        """Initialize the sensor."""

        super().__init__(coordinator)
        self._entry = entry
        self._waste_type = waste_type
        self.entity_description = SensorEntityDescription(
            key=waste_type,
            name=WASTE_TYPE_NAMES[waste_type],
            icon=WASTE_TYPE_ICONS[waste_type],
        )
        self._attr_unique_id = f"{entry.entry_id}_{waste_type}"
        self._attr_suggested_object_id = WASTE_TYPE_ENTITY_IDS[waste_type]

    @property
    def native_value(self) -> date | None:
        """Return the next collection date."""

        collection = self.coordinator.data.get(self._waste_type)
        if collection is None:
            return None
        return collection.collection_date

    @property
    def available(self) -> bool:
        """Return if entity is available."""

        return super().available and self.coordinator.data is not None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra attributes for dashboard cards and automations."""

        collection = self.coordinator.data.get(self._waste_type)
        attrs: dict[str, Any] = {
            ATTR_WASTE_TYPE: WASTE_TYPE_NAMES[self._waste_type],
            ATTR_SOURCE: self._entry.data[CONF_ICS_URL],
        }
        if collection is None:
            attrs.update(
                {
                    ATTR_DAYS_UNTIL: None,
                    ATTR_IS_TODAY: False,
                    ATTR_IS_TOMORROW: False,
                    ATTR_NEXT_COLLECTION: None,
                    ATTR_SUMMARY: None,
                }
            )
            return attrs

        today = date.today()
        days_until = (collection.collection_date - today).days
        attrs.update(
            {
                ATTR_DAYS_UNTIL: days_until,
                ATTR_IS_TODAY: days_until == 0,
                ATTR_IS_TOMORROW: days_until == 1,
                ATTR_NEXT_COLLECTION: collection.collection_date.isoformat(),
                ATTR_SUMMARY: collection.summary,
            }
        )
        return attrs
