"""TRMNL API client."""
import logging
import requests

from .const import DEFAULT_API_BASE_URL

_LOGGER = logging.getLogger(__name__)

class TrmnlApiClient:
    """TRMNL API client."""

    def __init__(self, api_key: str, api_base_url: str = DEFAULT_API_BASE_URL, device_access_token: str | None = None):
        """Initialize the API client."""
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')
        self.device_access_token = device_access_token

        # Headers for /api/devices (main API key)
        self.main_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_devices(self):
        """Get TRMNL devices information."""
        devices_endpoint = f"{self.api_base_url}/api/devices"
        try:
            response = requests.get(devices_endpoint, headers=self.main_headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL devices from %s: %s", devices_endpoint, err)
            raise
        except ValueError as err: # Catch JSON decoding errors
            _LOGGER.error("Error decoding JSON from TRMNL devices from %s: %s", devices_endpoint, err)
            raise

    def get_current_screen_info(self):
        """Get TRMNL current screen information."""
        if not self.device_access_token:
            _LOGGER.debug("Device access token not configured; skipping current_screen_info fetch.")
            return None # Or raise a specific error if preferred, e.g., NotConfiguredError

        current_screen_endpoint = f"{self.api_base_url}/api/current_screen"
        # Headers for /api/current_screen (device access token)
        screen_info_headers = {
            "accept": "application/json",
            "access-token": self.device_access_token
        }
        try:
            response = requests.get(current_screen_endpoint, headers=screen_info_headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rendered_at")
        except requests.exceptions.HTTPError as http_err:
            # Specifically log 401 for this token as it's different from the main one
            if http_err.response.status_code == 401:
                 _LOGGER.error(
                    "Authentication failed for current_screen_info (device access token) from %s: %s",
                    current_screen_endpoint,
                    http_err
                )
            else:
                _LOGGER.error(
                    "Error fetching TRMNL current screen info from %s: %s",
                    current_screen_endpoint,
                    http_err
                )
            raise # Re-raise to be handled by coordinator
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            raise
        except ValueError as err: # Catch JSON decoding errors
            _LOGGER.error("Error decoding JSON from TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            raise
