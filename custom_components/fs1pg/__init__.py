"""FS1PG integration."""
from __future__ import annotations

from typing import Any
import logging
from datetime import timedelta

from homeassistant.const import Platform
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_MAC_ADDR, DOMAIN

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SWITCH, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    device_mac: str = entry.data[CONF_MAC_ADDR]
    _LOGGER.debug("Using device_mac: %s", device_mac)

    hass.data.setdefault(DOMAIN, {})
    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    _LOGGER.debug("Unload: %s", hass.data[DOMAIN])

    return unload_ok
