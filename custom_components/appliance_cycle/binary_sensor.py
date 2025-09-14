"""Binary sensors for appliance cycle."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import _get_entry_data


async def async_setup_entry(hass, entry, async_add_entities):
    manager = _get_entry_data(hass, entry.entry_id)
    sensors = [ApplianceRunningBinarySensor(manager)]
    if manager.door_entity:
        sensors.append(ApplianceDoorBinarySensor(manager))
    async_add_entities(sensors)


class ApplianceRunningBinarySensor(BinarySensorEntity):
    """Indicates if the appliance is running."""

    def __init__(self, manager) -> None:
        self.manager = manager
        self._attr_name = f"{manager.name} Running"
        self._attr_unique_id = f"{manager.entry.entry_id}_running"
        self._attr_device_class = BinarySensorDeviceClass.RUNNING

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.manager.update_signal,
                self.async_write_ha_state,
            )
        )

    @property
    def is_on(self) -> bool:
        return self.manager.state == "running"

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "appliance_type": self.manager.appliance_type,
            "started_at": (
                self.manager.started_at.isoformat()
                if self.manager.started_at
                else None
            ),
            "finished_at": (
                self.manager.finished_at.isoformat()
                if self.manager.finished_at
                else None
            ),
            "run_time_seconds": self.manager.run_time_seconds,
            "last_runtime_seconds": self.manager.last_runtime_seconds,
        }


class ApplianceDoorBinarySensor(BinarySensorEntity):
    """Indicates if the appliance door is open."""

    def __init__(self, manager) -> None:
        self.manager = manager
        self._attr_name = f"{manager.name} Door"
        self._attr_unique_id = f"{manager.entry.entry_id}_door"
        self._attr_device_class = BinarySensorDeviceClass.DOOR

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.manager.update_signal,
                self.async_write_ha_state,
            )
        )

    @property
    def is_on(self) -> bool:
        return bool(self.manager.door_open)

    @property
    def extra_state_attributes(self) -> dict:
        return {
            "last_opened_at": self.manager.door_last_opened_iso,
        }
