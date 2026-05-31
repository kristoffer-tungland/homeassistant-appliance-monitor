"""Test harness bootstrap for Home Assistant imports."""

from __future__ import annotations

import importlib.util
from datetime import datetime, timezone
import sys
import types


def _install_homeassistant_stubs() -> None:
    if "homeassistant" in sys.modules:
        return
    if importlib.util.find_spec("homeassistant") is not None:
        return

    homeassistant = types.ModuleType("homeassistant")
    config_entries = types.ModuleType("homeassistant.config_entries")
    core = types.ModuleType("homeassistant.core")
    const = types.ModuleType("homeassistant.const")
    helpers = types.ModuleType("homeassistant.helpers")
    helpers_event = types.ModuleType("homeassistant.helpers.event")
    helpers_dispatcher = types.ModuleType("homeassistant.helpers.dispatcher")
    helpers_entity = types.ModuleType("homeassistant.helpers.entity")
    helpers_selector = types.ModuleType("homeassistant.helpers.selector")
    util = types.ModuleType("homeassistant.util")
    util_dt = types.ModuleType("homeassistant.util.dt")

    class ConfigFlow:
        def __init_subclass__(cls, **kwargs):
            return super().__init_subclass__()

    class OptionsFlow:
        config_entry = None

    class ConfigEntry:
        pass

    class HomeAssistant:
        pass

    class Event:
        pass

    class State:
        pass

    class Platform:
        BINARY_SENSOR = "binary_sensor"
        SENSOR = "sensor"

    class DeviceInfo(dict):
        pass

    def callback(func):
        return func

    def selector(config):
        return config

    def async_call_later(*_args, **_kwargs):
        return lambda: None

    def async_track_state_change_event(*_args, **_kwargs):
        return lambda: None

    def async_track_time_interval(*_args, **_kwargs):
        return lambda: None

    def async_dispatcher_send(*_args, **_kwargs):
        return None

    def utcnow():
        return datetime.now(timezone.utc)

    config_entries.ConfigFlow = ConfigFlow
    config_entries.OptionsFlow = OptionsFlow
    config_entries.ConfigEntry = ConfigEntry
    core.HomeAssistant = HomeAssistant
    core.Event = Event
    core.State = State
    core.callback = callback
    const.Platform = Platform
    const.STATE_ON = "on"
    helpers_event.async_call_later = async_call_later
    helpers_event.async_track_state_change_event = async_track_state_change_event
    helpers_event.async_track_time_interval = async_track_time_interval
    helpers_dispatcher.async_dispatcher_send = async_dispatcher_send
    helpers_entity.DeviceInfo = DeviceInfo
    helpers_selector.selector = selector
    util_dt.utcnow = utcnow

    homeassistant.config_entries = config_entries
    homeassistant.core = core
    homeassistant.const = const
    homeassistant.helpers = helpers
    homeassistant.util = util
    helpers.event = helpers_event
    helpers.dispatcher = helpers_dispatcher
    helpers.entity = helpers_entity
    helpers.selector = helpers_selector
    util.dt = util_dt

    sys.modules["homeassistant"] = homeassistant
    sys.modules["homeassistant.config_entries"] = config_entries
    sys.modules["homeassistant.core"] = core
    sys.modules["homeassistant.const"] = const
    sys.modules["homeassistant.helpers"] = helpers
    sys.modules["homeassistant.helpers.event"] = helpers_event
    sys.modules["homeassistant.helpers.dispatcher"] = helpers_dispatcher
    sys.modules["homeassistant.helpers.entity"] = helpers_entity
    sys.modules["homeassistant.helpers.selector"] = helpers_selector
    sys.modules["homeassistant.util"] = util
    sys.modules["homeassistant.util.dt"] = util_dt


_install_homeassistant_stubs()
