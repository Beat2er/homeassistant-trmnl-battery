"""TRMNL API client."""
import logging
import requests

from .const import DEFAULT_API_BASE_URL

_LOGGER = logging.getLogger(__name__)

class TrmnlApiClient:
    """TRMNL API client."""

    def __init__(self, api_key: str, api_base_url: str = DEFAULT_API_BASE_URL):
        """Initialize the API client."""
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip('/')

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
