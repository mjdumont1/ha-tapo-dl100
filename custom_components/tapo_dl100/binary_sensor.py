"""Binary sensor platform for Tapo DL100."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import Dl100Coordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DL100 binary sensor entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: Dl100Coordinator = data["coordinator"]
    async_add_entities(
        [
            Dl100LowBatteryBinarySensor(entry, coordinator),
            Dl100JammedBinarySensor(entry, coordinator),
        ]
    )


class Dl100LowBatteryBinarySensor(CoordinatorEntity[Dl100Coordinator], BinarySensorEntity):
    """Low battery binary sensor for a Tapo DL100 lock."""

    _attr_has_entity_name = True
    _attr_translation_key = "low_battery"
    _attr_device_class = BinarySensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_low_battery"
        self._attr_name = f"{entry.data[CONF_NAME]} Low Battery"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.at_low_battery)


class Dl100JammedBinarySensor(CoordinatorEntity[Dl100Coordinator], BinarySensorEntity):
    """Jammed status problem binary sensor for a Tapo DL100 lock."""

    _attr_has_entity_name = True
    _attr_translation_key = "jammed"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_jammed"
        self._attr_name = f"{entry.data[CONF_NAME]} Jammed"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.is_jammed)
