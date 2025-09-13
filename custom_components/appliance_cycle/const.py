"""Constants for appliance_cycle integration."""

from __future__ import annotations

DOMAIN = "appliance_cycle"

CONF_POWER_SENSOR = "power_sensor"
CONF_DOOR_SENSOR = "door_sensor"
CONF_APPLIANCE_TYPE = "appliance_type"

APPLIANCE_TYPES = ["washer", "dryer", "dishwasher"]

DEFAULT_PROFILES = {
    "washer": {
        "on_threshold": 15.0,
        "off_threshold": 8.0,
        "delay_on": 90,
        "delay_off": 300,
        "quiet_end": 120,
        "min_run": 300,
        "resume_grace": 180,
    },
    "dryer": {
        "on_threshold": 80.0,
        "off_threshold": 25.0,
        "delay_on": 60,
        "delay_off": 180,
        "quiet_end": 90,
        "min_run": 240,
        "resume_grace": 180,
    },
    "dishwasher": {
        "on_threshold": 20.0,
        "off_threshold": 8.0,
        "delay_on": 120,
        "delay_off": 420,
        "quiet_end": 180,
        "min_run": 600,
        "resume_grace": 240,
    },
}
