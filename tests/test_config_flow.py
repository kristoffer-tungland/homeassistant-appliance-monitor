"""Tests for appliance cycle config/options flow."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

from voluptuous.schema_builder import UNDEFINED

from custom_components.appliance_cycle import config_flow
from custom_components.appliance_cycle.const import (
    CONF_APPLIANCE_TYPE,
    CONF_DOOR_SENSOR,
    CONF_POWER_SENSOR,
)


def _build_entry(*, door_sensor):
    return SimpleNamespace(
        data={
            CONF_APPLIANCE_TYPE: "washer",
            CONF_POWER_SENSOR: "sensor.washer_power",
            CONF_DOOR_SENSOR: door_sensor,
            "profile": {},
        },
        options={},
    )


def _get_door_sensor_key(schema):
    for key in schema.schema:
        if getattr(key, "schema", None) == CONF_DOOR_SENSOR:
            return key
    raise AssertionError("Door sensor field not found in options schema")


def test_options_schema_has_no_default_when_door_sensor_not_set():
    flow = config_flow.OptionsFlowHandler()
    flow.config_entry = _build_entry(door_sensor=None)
    flow.async_show_form = lambda *, step_id, data_schema: {
        "step_id": step_id,
        "data_schema": data_schema,
    }

    result = asyncio.run(flow.async_step_init())
    door_sensor_key = _get_door_sensor_key(result["data_schema"])

    assert door_sensor_key.default is UNDEFINED


def test_options_schema_uses_existing_door_sensor_default():
    flow = config_flow.OptionsFlowHandler()
    flow.config_entry = _build_entry(door_sensor="binary_sensor.washer_door")
    flow.async_show_form = lambda *, step_id, data_schema: {
        "step_id": step_id,
        "data_schema": data_schema,
    }

    result = asyncio.run(flow.async_step_init())
    door_sensor_key = _get_door_sensor_key(result["data_schema"])

    assert door_sensor_key.default is not UNDEFINED
    assert door_sensor_key.default() == "binary_sensor.washer_door"
