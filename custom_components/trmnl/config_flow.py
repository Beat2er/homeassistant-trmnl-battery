"""Config flow for TRMNL integration."""
import logging
import voluptuous as vol
import requests # Added for specific exception handling

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import TrmnlApiClient
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_API_BASE_URL, # Updated
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_API_BASE_URL, # Updated
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class TrmnlFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def _validate_input(self, hass: HomeAssistant, data: dict):
        """Validate the user input allows us to connect."""
        # Construct TrmnlApiClient with the base URL
        client = TrmnlApiClient(data[CONF_API_KEY], data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL))
        try:
            # Test connection by fetching devices
            devices = await hass.async_add_executor_job(client.get_devices)
            # Ensure devices is a list, even if empty. If API returns something else, it's an issue.
            if not isinstance(devices, list):
                _LOGGER.error("API response for devices is not a list: %s", devices)
                raise InvalidAuth("Received malformed data from TRMNL API")
            # Not raising InvalidAuth for empty list, as an account might have no devices yet
            # but still be valid. The check is more about connectivity and auth.
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                _LOGGER.error("Authentication failed with TRMNL API: %s", http_err)
                raise InvalidAuth("Invalid API key or base URL") from http_err
            _LOGGER.error("HTTP error connecting to TRMNL API: %s", http_err)
            raise ConnectionError("Failed to connect to TRMNL API (HTTP error)") from http_err
        except requests.exceptions.RequestException as req_err: # Covers DNS, connection refused, etc.
            _LOGGER.error("Request error connecting to TRMNL API: %s", req_err)
            raise ConnectionError("Failed to connect to TRMNL API (request error)") from req_err
        except Exception as exc: # Catch any other unexpected errors during validation
            _LOGGER.error("Unexpected error validating TRMNL API connection: %s", exc)
            raise ConnectionError(f"An unexpected error occurred: {exc}") from exc

        return {"title": "TRMNL"}


    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Ensure scan_interval is correctly handled if empty or missing
            # and provide default for api_base_url if not provided
            processed_input = {
                CONF_API_KEY: user_input[CONF_API_KEY],
                CONF_API_BASE_URL: user_input.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL).rstrip('/'),
                CONF_SCAN_INTERVAL: user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
            }


            if processed_input[CONF_SCAN_INTERVAL] < MIN_SCAN_INTERVAL:
                errors["base"] = "invalid_scan_interval"
            else:
                try:
                    info = await self._validate_input(self.hass, processed_input)

                    await self.async_set_unique_id(processed_input[CONF_API_KEY])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=info["title"], # Using title from validation
                        data=processed_input
                    )
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except ConnectionError: # Catch connection errors from _validate_input
                    errors["base"] = "cannot_connect" # A more specific error key might be better
                except Exception:  # pylint: disable=broad-except
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
        else: # Show empty form if user_input is None
            processed_input = {}


        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY, default=processed_input.get(CONF_API_KEY)): str,
                    vol.Optional(
                        CONF_API_BASE_URL, default=processed_input.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
                    ): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=processed_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
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
        # Store current values to pre-fill the form and compare for changes
        self.current_api_base_url = self.config_entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
        self.current_scan_interval = self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}
        if user_input is not None:
            updated_data = self.config_entry.data.copy()
            needs_validation = False

            # Process API Base URL
            new_api_base_url = user_input.get(CONF_API_BASE_URL, self.current_api_base_url).rstrip('/')
            if new_api_base_url != self.current_api_base_url:
                updated_data[CONF_API_BASE_URL] = new_api_base_url
                needs_validation = True # API base URL changed, needs re-validation

            # Process Scan Interval
            new_scan_interval = user_input.get(CONF_SCAN_INTERVAL, self.current_scan_interval)
            if new_scan_interval < MIN_SCAN_INTERVAL:
                errors["base"] = "invalid_scan_interval"
            else:
                updated_data[CONF_SCAN_INTERVAL] = new_scan_interval

            if not errors: # Proceed if no scan interval error
                if needs_validation:
                    try:
                        # Validate with potentially new API base URL, using existing API key
                        validation_data = {
                            CONF_API_KEY: self.config_entry.data[CONF_API_KEY],
                            CONF_API_BASE_URL: new_api_base_url
                        }
                        # Re-use the validation logic from the main flow
                        flow_handler = TrmnlFlowHandler()
                        flow_handler.hass = self.hass # Provide hass instance
                        await flow_handler._validate_input(self.hass, validation_data)

                        # If validation passes, create/update the entry
                        return self.async_create_entry(title="", data=updated_data)
                    except InvalidAuth:
                        errors["base"] = "invalid_base_url_auth" # Specific error for options
                    except ConnectionError:
                        errors["base"] = "cannot_connect_options" # Specific error for options
                    except Exception:
                        _LOGGER.exception("Unexpected exception during options validation")
                        errors["base"] = "unknown_options"
                else: # No validation needed, just update scan interval
                    return self.async_create_entry(title="", data=updated_data)


        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_API_BASE_URL,
                        default=self.current_api_base_url,
                    ): str,
                    vol.Optional(
                        CONF_SCAN_INTERVAL,
                        default=self.current_scan_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)),
                }
            ),
            errors=errors,
        )

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class ConnectionError(HomeAssistantError):
    """Error to indicate a connection problem."""
