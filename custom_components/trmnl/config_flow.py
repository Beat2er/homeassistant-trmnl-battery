"""Config flow for TRMNL integration."""
import logging
import voluptuous as vol
import requests

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

from .api import TrmnlApiClient
from .const import (
    DOMAIN,
    CONF_API_KEY,
    CONF_SCAN_INTERVAL,
    CONF_API_BASE_URL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_API_BASE_URL,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class TrmnlFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TRMNL."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def _validate_input(self, hass: HomeAssistant, data: dict):
        """Validate the user input allows us to connect."""
        client = TrmnlApiClient(
            data[CONF_API_KEY],
            data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL),
        )
        try:
            devices = await hass.async_add_executor_job(client.get_devices)
            if not isinstance(devices, list):
                _LOGGER.error("API response for devices is not a list: %s", devices)
                raise InvalidAuth("Received malformed data from TRMNL API")
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 401:
                _LOGGER.error("Authentication failed with TRMNL API (main key): %s", http_err)
                raise InvalidAuth("Invalid API key or base URL") from http_err
            _LOGGER.error("HTTP error connecting to TRMNL API: %s", http_err)
            raise ConnectionError("Failed to connect to TRMNL API (HTTP error)") from http_err
        except requests.exceptions.RequestException as req_err:
            _LOGGER.error("Request error connecting to TRMNL API: %s", req_err)
            raise ConnectionError("Failed to connect to TRMNL API (request error)") from req_err
        except Exception as exc:
            _LOGGER.error("Unexpected error validating TRMNL API connection: %s", exc)
            raise ConnectionError(f"An unexpected error occurred: {exc}") from exc

        return {"title": "TRMNL"} # Default title, can be customized if needed

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        # Pre-fill with empty strings for optional fields if user_input is None (first show)
        current_api_key = ""
        current_api_base_url = DEFAULT_API_BASE_URL
        current_scan_interval = DEFAULT_SCAN_INTERVAL

        if user_input is not None:
            current_api_key = user_input.get(CONF_API_KEY, "")
            current_api_base_url = user_input.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL).rstrip('/')
            current_scan_interval = user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

            processed_input = {
                CONF_API_KEY: current_api_key,
                CONF_API_BASE_URL: current_api_base_url,
                CONF_SCAN_INTERVAL: current_scan_interval,
            }

            if processed_input[CONF_SCAN_INTERVAL] < MIN_SCAN_INTERVAL:
                errors["base"] = "invalid_scan_interval"
            else:
                try:
                    info = await self._validate_input(self.hass, processed_input)
                except InvalidAuth:
                    errors["base"] = "invalid_auth"
                except ConnectionError:
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected exception")
                    errors["base"] = "unknown"
                else:
                    # set_unique_id + abort_if_unique_id_configured must run OUTSIDE the
                    # broad try/except above: AbortFlow inherits from Exception, so the
                    # bare `except Exception` would swallow the duplicate-entry abort and
                    # surface it as "unknown error" instead of "already configured".
                    await self.async_set_unique_id(processed_input[CONF_API_KEY])
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(title=info["title"], data=processed_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY, default=current_api_key): str,
                    vol.Optional(CONF_API_BASE_URL, default=current_api_base_url): str,
                    vol.Optional(CONF_SCAN_INTERVAL, default=current_scan_interval): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return TrmnlOptionsFlowHandler()

class TrmnlOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle TRMNL options."""

    async def async_step_init(self, user_input=None):
        errors = {}
        # `self.config_entry` is provided by Home Assistant (read-only property).
        current_api_base_url = self.config_entry.data.get(CONF_API_BASE_URL, DEFAULT_API_BASE_URL)
        current_scan_interval = self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

        if user_input is not None:
            updated_data = self.config_entry.data.copy()
            needs_main_api_validation = False

            # Process API Base URL
            new_api_base_url = user_input.get(CONF_API_BASE_URL, current_api_base_url).rstrip('/')
            if new_api_base_url != current_api_base_url:
                updated_data[CONF_API_BASE_URL] = new_api_base_url
                needs_main_api_validation = True

            # Process Scan Interval
            new_scan_interval = user_input.get(CONF_SCAN_INTERVAL, current_scan_interval)
            if new_scan_interval < MIN_SCAN_INTERVAL:
                errors["base"] = "invalid_scan_interval"
            else:
                updated_data[CONF_SCAN_INTERVAL] = new_scan_interval

            if not errors:
                if needs_main_api_validation:
                    try:
                        # Validate with potentially new API base URL, using existing main API key
                        validation_data = {
                            CONF_API_KEY: self.config_entry.data[CONF_API_KEY], # Main key
                            CONF_API_BASE_URL: new_api_base_url
                        }
                        flow_handler = TrmnlFlowHandler()
                        flow_handler.hass = self.hass
                        await flow_handler._validate_input(self.hass, validation_data)
                        # If validation passes, create/update the entry
                        return self.async_create_entry(title="", data=updated_data)
                    except InvalidAuth:
                        errors["base"] = "invalid_base_url_auth"
                    except ConnectionError:
                        errors["base"] = "cannot_connect_options"
                    except Exception:
                        _LOGGER.exception("Unexpected exception during options validation")
                        errors["base"] = "unknown_options"
                else: # No main API validation needed, just update data
                    return self.async_create_entry(title="", data=updated_data)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_API_BASE_URL, default=current_api_base_url): str,
                    vol.Optional(CONF_SCAN_INTERVAL, default=current_scan_interval): vol.All(
                        vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL)
                    ),
                }
            ),
            errors=errors,
        )

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

class ConnectionError(HomeAssistantError):
    """Error to indicate a connection problem."""
