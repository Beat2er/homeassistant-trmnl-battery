"""TRMNL e-ink display integration."""
import asyncio
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, SCAN_INTERVAL
from .api import TrmnlApiClient

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    {DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA
)

PLATFORMS = ["sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the TRMNL component."""
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up TRMNL from a config entry."""
    api_key = entry.data["api_key"]

    client = TrmnlApiClient(api_key)

    async def async_update_data():
        """Fetch data from API."""
        return await hass.async_add_executor_job(client.get_devices)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=SCAN_INTERVAL),
    )

    await coordinator.async_refresh()

    if not coordinator.data:
        _LOGGER.error("Failed to get initial data from TRMNL API")
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    # Use async_forward_entry_setups instead of async_forward_entry_setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok