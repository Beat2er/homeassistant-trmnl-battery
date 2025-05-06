"""Config flow for TRMNL integration."""
import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .api import TrmnlApiClient
from .const import DOMAIN

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
                api_key = user_input["api_key"]

                # Create API client and verify connection
                client = TrmnlApiClient(api_key)
                devices = await self.hass.async_add_executor_job(client.get_devices)

                if not devices:
                    raise InvalidAuth

                # Success - create entry
                return self.async_create_entry(
                    title="TRMNL Devices",
                    data={"api_key": api_key}
                )

            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Show form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_key"): str,
                }
            ),
            errors=errors,
        )

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""