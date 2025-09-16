"""Config flow for appliance cycle."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector

from .const import (
    APPLIANCE_TYPES,
    CONF_APPLIANCE_TYPE,
    CONF_DOOR_SENSOR,
    CONF_POWER_SENSOR,
    DEFAULT_PROFILES,
    DOMAIN,
)


class ApplianceCycleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            profile = DEFAULT_PROFILES[user_input[CONF_APPLIANCE_TYPE]].copy()
            data = {
                CONF_APPLIANCE_TYPE: user_input[CONF_APPLIANCE_TYPE],
                CONF_POWER_SENSOR: user_input[CONF_POWER_SENSOR],
                CONF_DOOR_SENSOR: user_input.get(CONF_DOOR_SENSOR),
                "profile": profile,
            }
            title = user_input["name"]
            return self.async_create_entry(title=title, data=data)

        schema = vol.Schema(
            {
                vol.Required("name"): str,
                vol.Required(CONF_APPLIANCE_TYPE): vol.In(APPLIANCE_TYPES),
                vol.Required(CONF_POWER_SENSOR): selector(
                    {"entity": {"domain": ["sensor"]}}
                ),
                vol.Optional(CONF_DOOR_SENSOR): selector(
                    {"entity": {"domain": ["binary_sensor"]}}
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Options for Appliance Cycle."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.config_entry.data["profile"].update(user_input)
            return self.async_create_entry(title="", data={})
        profile = DEFAULT_PROFILES[
            self.config_entry.data[CONF_APPLIANCE_TYPE]
        ].copy()
        profile.update(self.config_entry.data.get("profile", {}))
        schema = vol.Schema(
            {
                vol.Required(
                    "on_threshold", default=profile.get("on_threshold")
                ): vol.Coerce(float),
                vol.Required(
                    "off_threshold", default=profile.get("off_threshold")
                ): vol.Coerce(float),
                vol.Required("delay_on", default=profile.get("delay_on")): int,
                vol.Required(
                    "start_grace", default=profile.get("start_grace", 0)
                ): int,
                vol.Required(
                    "delay_off", default=profile.get("delay_off")
                ): int,
                vol.Required(
                    "quiet_end", default=profile.get("quiet_end")
                ): int,
                vol.Required("min_run", default=profile.get("min_run")): int,
                vol.Required(
                    "resume_grace", default=profile.get("resume_grace")
                ): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
