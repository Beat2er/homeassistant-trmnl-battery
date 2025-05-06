"""TRMNL API client."""
import logging
import requests

from .const import API_ENDPOINT

_LOGGER = logging.getLogger(__name__)

class TrmnlApiClient:
    """TRMNL API client."""

    def __init__(self, api_key):
        """Initialize the API client."""
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        }

    def get_devices(self):
        """Get TRMNL devices information."""
        try:
            response = requests.get(API_ENDPOINT, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json().get("data", [])
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Error fetching TRMNL devices: %s", err)
            return []