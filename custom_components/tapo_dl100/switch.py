"""Switch platform for Tapo DL100."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
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
    """Set up DL100 switch entities."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator: Dl100Coordinator = data["coordinator"]
    async_add_entities(
        [
            Dl100AutoLockSwitch(entry, coordinator),
            Dl100SpeakerSwitch(entry, coordinator),
            Dl100DoorjamAlarmSwitch(entry, coordinator),
            Dl100PinScramblingSwitch(entry, coordinator),
        ]
    )


class Dl100AutoLockSwitch(CoordinatorEntity[Dl100Coordinator], SwitchEntity):
    """Switch to toggle the lock's internal hardware auto-lock timer."""

    _attr_has_entity_name = True
    _attr_translation_key = "auto_lock"
    _attr_icon = "mdi:timer-lock"

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_auto_lock"
        self._attr_name = f"{entry.data[CONF_NAME]} Auto-Lock"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.auto_lock_enabled is not None
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.auto_lock_enabled)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_auto_lock(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_auto_lock(False)
        await self.coordinator.async_request_refresh()


class Dl100SpeakerSwitch(CoordinatorEntity[Dl100Coordinator], SwitchEntity):
    """Switch to toggle lock audio beeps and prompt sounds."""

    _attr_has_entity_name = True
    _attr_translation_key = "speaker"
    _attr_icon = "mdi:volume-high"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_speaker"
        self._attr_name = f"{entry.data[CONF_NAME]} Speaker"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.speaker_enabled is not None
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.speaker_enabled)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_speaker(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_speaker(False)
        await self.coordinator.async_request_refresh()


class Dl100DoorjamAlarmSwitch(CoordinatorEntity[Dl100Coordinator], SwitchEntity):
    """Switch to toggle deadbolt motor jam audible siren."""

    _attr_has_entity_name = True
    _attr_translation_key = "jam_siren"
    _attr_icon = "mdi:alarm-light"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_jam_siren"
        self._attr_name = f"{entry.data[CONF_NAME]} Jam Siren"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.doorjam_alarm_enabled is not None
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.doorjam_alarm_enabled)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_doorjam_alarm(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_doorjam_alarm(False)
        await self.coordinator.async_request_refresh()


class Dl100PinScramblingSwitch(CoordinatorEntity[Dl100Coordinator], SwitchEntity):
    """Switch to toggle anti-peep random digit keypad PIN scrambling."""

    _attr_has_entity_name = True
    _attr_translation_key = "pin_scrambling"
    _attr_icon = "mdi:dialpad"
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, entry: ConfigEntry, coordinator: Dl100Coordinator) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_pin_scrambling"
        self._attr_name = f"{entry.data[CONF_NAME]} PIN Scrambling"

    @property
    def available(self) -> bool:
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.coordinator.data.pin_scrambling_enabled is not None
        )

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return bool(self.coordinator.data.pin_scrambling_enabled)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_pin_scrambling(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.api.set_pin_scrambling(False)
        await self.coordinator.async_request_refresh()
