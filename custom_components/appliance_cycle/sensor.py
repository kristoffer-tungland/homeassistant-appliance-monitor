"""Sensors for appliance cycle."""

from __future__ import annotations

from datetime import datetime

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from . import _get_entry_data


async def async_setup_entry(hass, entry, async_add_entities):
    manager = _get_entry_data(hass, entry.entry_id)
    sensors = [
        ApplianceRunTimeSensor(manager),
        ApplianceLastRuntimeSensor(manager),
        ApplianceFinishedAtSensor(manager),
        ApplianceStatusSensor(manager),
    ]
    async_add_entities(sensors)


class ApplianceBaseSensor(SensorEntity):
    def __init__(self, manager) -> None:
        self.manager = manager

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                self.manager.update_signal,
                self.async_write_ha_state,
            )
        )


class ApplianceRunTimeSensor(ApplianceBaseSensor):
    _attr_native_unit_of_measurement = "s"
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(self, manager) -> None:
        super().__init__(manager)
        self._attr_name = f"{manager.name} Run Time"
        self._attr_unique_id = f"{manager.entry.entry_id}_run_time"

    @property
    def native_value(self):
        return int(self.manager.run_time_seconds)


class ApplianceLastRuntimeSensor(ApplianceBaseSensor):
    _attr_native_unit_of_measurement = "s"
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(self, manager) -> None:
        super().__init__(manager)
        self._attr_name = f"{manager.name} Last Runtime"
        self._attr_unique_id = f"{manager.entry.entry_id}_last_runtime"

    @property
    def native_value(self):
        return int(self.manager.last_runtime_seconds or 0)


class ApplianceFinishedAtSensor(ApplianceBaseSensor):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, manager) -> None:
        super().__init__(manager)
        self._attr_name = f"{manager.name} Finished At"
        self._attr_unique_id = f"{manager.entry.entry_id}_finished_at"

    @property
    def native_value(self):
        if self.manager.finished_at_iso:
            return datetime.fromisoformat(self.manager.finished_at_iso)
        return None


class ApplianceStatusSensor(ApplianceBaseSensor):
    def __init__(self, manager) -> None:
        super().__init__(manager)
        self._attr_name = f"{manager.name} Status"
        self._attr_unique_id = f"{manager.entry.entry_id}_status"

    @property
    def native_value(self):
        state = self.manager.state
        if self.manager.door_open:
            return "Open"
        if state == "running":
            seconds = int(self.manager.run_time_seconds)
            mins, secs = divmod(seconds, 60)
            hours, mins = divmod(mins, 60)
            if hours:
                return f"{hours}h {mins:02d}m"
            return f"{mins}m"
        if state == "finished":
            return "Finished"
        return "Idle"
