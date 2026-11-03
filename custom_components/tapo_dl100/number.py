"""Number platform for Tapo DL100."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, PERCENTAGE, EntityCategory, UnitOfTime
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
    """Set up DL100 number entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: Dl100Coordinator = data["coordinator"]
    async_add_entities(
        [
            Dl100AutoLockDelayNumber(entry, coordinator),
            Dl100SpeakerVolumeNumber(entry, coordinator),
        ]
    )


class Dl100AutoLockDelayNumber(CoordinatorEntity[Dl100Coordinator], NumberEntity):
    """Number slider for configuring the physical auto-lock delay."""

    _attr_has_entity_name = True
    _attr_translation_key = "auto_lock_delay"
    _attr_native_min_value = 30
    _attr_native_max_value = 600
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:timer-cog-outline"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_auto_lock_delay"
        self._attr_name = f"{entry.data[CONF_NAME]} Auto-Lock Delay"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.auto_lock_delay is not None
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None or self.coordinator.data.auto_lock_delay is None:
            return None
        return float(self.coordinator.data.auto_lock_delay)

    async def async_set_native_value(self, value: float) -> None:
        enabled = (
            bool(self.coordinator.data.auto_lock_enabled)
            if self.coordinator.data and self.coordinator.data.auto_lock_enabled is not None
            else True
        )
        await self.coordinator.api.set_auto_lock(enabled=enabled, delay_seconds=int(value))
        await self.coordinator.async_request_refresh()


class Dl100SpeakerVolumeNumber(CoordinatorEntity[Dl100Coordinator], NumberEntity):
    """Number slider for configuring lock chime and prompt volume."""

    _attr_has_entity_name = True
    _attr_translation_key = "speaker_volume"
    _attr_native_min_value = 0
    _attr_native_max_value = 100
    _attr_native_step = 5
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:volume-medium"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_speaker_volume"
        self._attr_name = f"{entry.data[CONF_NAME]} Volume"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.speaker_volume is not None
        )

    @property
    def native_value(self) -> float | None:
        if self.coordinator.data is None or self.coordinator.data.speaker_volume is None:
            return None
        return float(self.coordinator.data.speaker_volume)

    async def async_set_native_value(self, value: float) -> None:
        enabled = (
            bool(self.coordinator.data.speaker_enabled)
            if self.coordinator.data and self.coordinator.data.speaker_enabled is not None
            else True
        )
        await self.coordinator.api.set_speaker(enabled=enabled, volume=int(value))
        await self.coordinator.async_request_refresh()
