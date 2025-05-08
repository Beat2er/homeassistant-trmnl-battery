"""TRMNL e-ink display integration."""
import asyncio
import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_API_BASE_URL,
    CONF_DEVICE_ACCESS_TOKEN, # Added
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
    device_access_token = entry.data.get(CONF_DEVICE_ACCESS_TOKEN) # Optional
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    client = TrmnlApiClient(api_key, api_base_url, device_access_token) # Updated

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        # update_method will be set after coordinator initialization
        update_interval=timedelta(seconds=scan_interval),
    )
    # Initialize last_rendered_at on the coordinator instance
    coordinator.last_rendered_at = None

    async def async_update_data():
        """Fetch data from API, including devices and current screen info."""
        devices_data = None
        try:
            devices_data = await hass.async_add_executor_job(client.get_devices)
        except Exception as err:
            # If get_devices fails, we consider the whole update failed.
            raise UpdateFailed(f"Error communicating with API for devices: {err}")

        try:
            rendered_at_new = await hass.async_add_executor_job(client.get_current_screen_info)
            if rendered_at_new is not None:
                coordinator.last_rendered_at = rendered_at_new
            # If rendered_at_new is None, coordinator.last_rendered_at remains unchanged.
        except Exception as err:
            # Log a warning if fetching screen info fails, but don't fail the devices update.
            _LOGGER.warning("Error fetching TRMNL current screen info: %s. Proceeding with device data only.", err)
            # We don't re-raise UpdateFailed here, as device data might still be useful.
            # If devices_data is None due to an earlier failure, this won't execute or matter.
        
        # Ensure devices_data is returned, even if screen info failed.
        # If devices_data itself failed, UpdateFailed was already raised.
        if devices_data is None:
            # This case should ideally be covered by the first try-except raising UpdateFailed
            # if get_devices returns None or fails in a way that doesn't raise immediately.
            # However, to be safe, if devices_data is still None here, it's an issue.
            _LOGGER.error("Device data is None after update attempt, this should not happen if get_devices succeeded.")
            raise UpdateFailed("Failed to retrieve device data, and screen info may also have failed.")
            
        return devices_data

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
