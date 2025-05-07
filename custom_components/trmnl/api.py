"""TRMNL API client."""
import logging
import requests

from .const import DEFAULT_API_BASE_URL # Updated import

_LOGGER = logging.getLogger(__name__)

class TrmnlApiClient:
    """TRMNL API client."""

    def __init__(self, api_key: str, api_base_url: str = DEFAULT_API_BASE_URL): # Updated parameter
        """Initialize the API client."""
        self.api_key = api_key
        # Ensure base_url doesn't have a trailing slash for consistent joining
        self.api_base_url = api_base_url.rstrip('/')
        self.headers = {
            "accept": "application/json",
            "access-token": self.api_key # Updated header for all requests
        }

    def get_devices(self):
        """Get TRMNL devices information."""
        devices_endpoint = f"{self.api_base_url}/api/devices" # Construct full URL
        try:
            response = requests.get(devices_endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL devices from %s: %s", devices_endpoint, err)
            # Re-raise the exception so the coordinator can handle it
            raise
        except ValueError as err: # Catch JSON decoding errors
            _LOGGER.error("Error decoding JSON from TRMNL devices from %s: %s", devices_endpoint, err)
            raise


    def get_current_screen_info(self):
        """Get TRMNL current screen information."""
        current_screen_endpoint = f"{self.api_base_url}/api/current_screen" # Construct full URL
        try:
            # Now uses self.headers which is already configured with access-token
            response = requests.get(current_screen_endpoint, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get("rendered_at")
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            # Re-raise the exception so the coordinator can handle it
            raise
        except ValueError as err: # Catch JSON decoding errors
            _LOGGER.error("Error decoding JSON from TRMNL current screen info from %s: %s", current_screen_endpoint, err)
            raise
