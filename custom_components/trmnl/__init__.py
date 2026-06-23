"""TRMNL e-ink display integration."""
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_API_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_API_BASE_URL,
)
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
    api_key = entry.data[CONF_API_KEY]
    api_base_url = entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    client = TrmnlApiClient(api_key, api_base_url)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        # update_method will be set after coordinator initialization
        update_interval=timedelta(seconds=scan_interval),
    )

    async def async_update_data():
        """Fetch device data from the API."""
        try:
            return await hass.async_add_executor_job(client.get_devices)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API for devices: {err}")

    coordinator.update_method = async_update_data
    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_success:
        # No need to log error here, async_config_entry_first_refresh does it
        return False

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client,
    }

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Use async_forward_entry_setups instead of async_forward_entry_setup
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
