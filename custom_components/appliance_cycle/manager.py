"""Appliance cycle state manager."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant, callback, Event, State
from homeassistant.helpers.event import (
    async_call_later,
    async_track_state_change_event,
    async_track_time_interval,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.util.dt import utcnow

from .const import (
    CONF_APPLIANCE_TYPE,
    CONF_DOOR_SENSOR,
    CONF_POWER_SENSOR,
    DEFAULT_PROFILES,
    DOMAIN,
)


class ApplianceCycleManager:
    """Class handling state machine for one appliance."""

    def __init__(self, hass: HomeAssistant, entry) -> None:
        self.hass = hass
        self.entry = entry
        data = entry.data
        self.name: str = entry.title
        self.appliance_type: str = data[CONF_APPLIANCE_TYPE]
        self.power_entity: str = data[CONF_POWER_SENSOR]
        self.door_entity: str | None = data.get(CONF_DOOR_SENSOR)
        self.profile = data.get(
            "profile", DEFAULT_PROFILES[self.appliance_type]
        )

        self.state: str = "idle"
        self.started_at: datetime | None = None
        self.finished_at: datetime | None = None
        self.last_runtime: float | None = None
        self.door_is_open: bool | None = None
        self.door_last_opened: datetime | None = None

        self._on_timer = None
        self._off_timer = None
        self._ticker_unsub = None
        self._power_unsub = None
        self._door_unsub = None

        self.update_signal = f"{DOMAIN}_{entry.entry_id}_update"

    async def async_setup(self) -> None:
        """Set up listeners."""
        self._power_unsub = async_track_state_change_event(
            self.hass, [self.power_entity], self._power_changed
        )
        if self.door_entity:
            self._door_unsub = async_track_state_change_event(
                self.hass, [self.door_entity], self._door_changed
            )
            door_state = self.hass.states.get(self.door_entity)
            if door_state and door_state.state not in ("unknown", "unavailable"):
                self.door_is_open = door_state.state == STATE_ON
                if self.door_is_open:
                    self.door_last_opened = door_state.last_changed
        self._ticker_unsub = async_track_time_interval(
            self.hass, self._handle_tick, timedelta(seconds=60)
        )

    async def async_unload(self) -> None:
        """Remove listeners."""
        if self._power_unsub:
            self._power_unsub()
        if self._door_unsub:
            self._door_unsub()
        if self._ticker_unsub:
            self._ticker_unsub()
        if self._on_timer:
            self._on_timer()
        if self._off_timer:
            self._off_timer()

    @callback
    def _schedule_update(self) -> None:
        async_dispatcher_send(self.hass, self.update_signal)

    @callback
    def _power_changed(self, event: Event) -> None:
        new_state: State | None = event.data.get("new_state")
        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return
        try:
            power = float(new_state.state)
        except (ValueError, TypeError):
            return

        if self.state == "idle" and power >= self.profile["on_threshold"]:
            if not self._on_timer:
                self._on_timer = async_call_later(
                    self.hass, self.profile["delay_on"], self._confirm_running
                )
        else:
            if self._on_timer and power < self.profile["on_threshold"]:
                self._on_timer()
                self._on_timer = None

        if self.state == "running" and power <= self.profile["off_threshold"]:
            if not self._off_timer:
                delay = self.profile["delay_off"] + self.profile["quiet_end"]
                self._off_timer = async_call_later(
                    self.hass, delay, self._confirm_finished
                )
        else:
            if self._off_timer and power > self.profile["off_threshold"]:
                self._off_timer()
                self._off_timer = None

    @callback
    def _door_changed(self, event: Event) -> None:
        new_state: State | None = event.data.get("new_state")
        if new_state is None or new_state.state in ("unknown", "unavailable"):
            return
        is_open = new_state.state == STATE_ON
        self.door_is_open = is_open
        if is_open:
            self.door_last_opened = utcnow()
            if self.state == "finished":
                self._reset_cycle()
        self._schedule_update()

    @callback
    def _confirm_running(self, _now: datetime) -> None:
        self._on_timer = None
        power_state = self.hass.states.get(self.power_entity)
        if not power_state:
            return
        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            return
        if power < self.profile["on_threshold"]:
            return
        self.state = "running"
        self.started_at = utcnow()
        self._schedule_update()

    @callback
    def _confirm_finished(self, _now: datetime) -> None:
        self._off_timer = None
        power_state = self.hass.states.get(self.power_entity)
        if not power_state:
            return
        try:
            power = float(power_state.state)
        except (ValueError, TypeError):
            return
        if power > self.profile["off_threshold"]:
            return
        if self.started_at is None:
            return
        runtime = (utcnow() - self.started_at).total_seconds()
        if runtime < self.profile["min_run"]:
            self._reset_cycle()
            return
        self.state = "finished"
        self.finished_at = utcnow()
        self.last_runtime = runtime
        if not self.door_entity:
            async_call_later(
                self.hass, self.profile["resume_grace"], self._reset_cycle
            )
        self._schedule_update()

    @callback
    def _handle_tick(self, now: datetime) -> None:
        if self.state == "running":
            self._schedule_update()

    @callback
    def _reset_cycle(self, *_args) -> None:
        self.state = "idle"
        self.started_at = None
        self.finished_at = None
        self._schedule_update()

    # Properties used by entities
    @property
    def run_time_seconds(self) -> float:
        if self.state == "running" and self.started_at:
            return (utcnow() - self.started_at).total_seconds()
        return 0.0

    @property
    def last_runtime_seconds(self) -> float | None:
        return self.last_runtime

    @property
    def finished_at_iso(self) -> str | None:
        if self.finished_at:
            return self.finished_at.isoformat()
        return None

    @property
    def door_open(self) -> bool | None:
        return self.door_is_open

    @property
    def door_last_opened_iso(self) -> str | None:
        if self.door_last_opened:
            return self.door_last_opened.isoformat()
        return None
