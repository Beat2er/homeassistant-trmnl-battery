"""Config flow for TRMNL integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import TrmnlApiClient
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_API_ENDPOINT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_API_ENDPOINT,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class TrmnlFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                api_key = user_input[CONF_API_KEY]
                api_endpoint = user_input.get(CONF_API_ENDPOINT, DEFAULT_API_ENDPOINT)
                scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

                if scan_interval < MIN_SCAN_INTERVAL:
                    errors["base"] = "invalid_scan_interval"
                    raise ValueError("Scan interval too low")


                # Create API client and verify connection
                client = TrmnlApiClient(api_key, api_endpoint)
                devices = await self.hass.async_add_executor_job(client.get_devices)

                if not devices:
                    raise InvalidAuth

                # Success - create entry
                return self.async_create_entry(
                    title="TRMNL Devices",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_API_ENDPOINT: api_endpoint,
                        CONF_SCAN_INTERVAL: scan_interval,
                    }
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except ValueError: # Handle scan interval error
                pass # Error already set
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(
                        CONF_API_ENDPOINT, default=DEFAULT_API_ENDPOINT
                    ): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TrmnlOptionsFlowHandler(config_entry)


class TrmnlOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TRMNL options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            try:
                scan_interval = user_input.get(CONF_SCAN_INTERVAL)
                if scan_interval < MIN_SCAN_INTERVAL:
                    errors["base"] = "invalid_scan_interval"
                    raise ValueError("Scan interval too low")

                # Validate API endpoint if changed
                api_endpoint = user_input.get(CONF_API_ENDPOINT)
                if api_endpoint != self.config_entry.data.get(CONF_API_ENDPOINT):
                    client = TrmnlApiClient(self.config_entry.data[CONF_API_KEY], api_endpoint)
                    devices = await self.hass.async_add_executor_job(client.get_devices)
                    if not devices:
                        raise InvalidAuth("Failed to connect with new API endpoint")


                return self.async_create_entry(title="", data=user_input)

            except InvalidAuth:
                errors["base"] = "invalid_endpoint_auth" # Differentiate from initial setup auth error
            except ValueError:
                pass # Error already set
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception during options flow")
                errors["base"] = "unknown"


        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_ENDPOINT,
                        default=self.config_entry.data.get(CONF_API_ENDPOINT, DEFAULT_API_ENDPOINT),
                    ): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
