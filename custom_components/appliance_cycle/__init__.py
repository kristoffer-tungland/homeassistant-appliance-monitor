"""Appliance cycle integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .manager import ApplianceCycleManager

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


def _get_entry_data(
    hass: HomeAssistant, entry_id: str
) -> ApplianceCycleManager:
    return hass.data[DOMAIN][entry_id]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up integration from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    manager = ApplianceCycleManager(hass, entry)
    await manager.async_setup()
    hass.data[DOMAIN][entry.entry_id] = manager
    await hass.config_entries.async_forward_entry_setups(
        entry, PLATFORMS
    )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    manager: ApplianceCycleManager = hass.data[DOMAIN].pop(entry.entry_id)
    await manager.async_unload()
    return True
